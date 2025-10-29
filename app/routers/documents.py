from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.core.db import lifespan_session
from app.core.auth import get_current_user, CurrentUser
from app.services.documents import DocumentsService
from app.schemas.admin import AdminDocumentUpdate
from app.schemas.documents import DocumentAssignOne, GoldenNumberReservationRequest, GoldenNumberReservationResponse
from app.schemas.responses import AssignNumberOut, CreatedDocumentInfo
from app.services.reservation import ReservationService
from app.utils.numbering import format_doc_no

router = APIRouter()

@router.post(
    "/reserve-golden",
    response_model=GoldenNumberReservationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Зарезервировать 'золотые' номера"
)
async def reserve_golden_numbers(
    payload: GoldenNumberReservationRequest,
    session: AsyncSession = Depends(lifespan_session),
    user: CurrentUser = Depends(get_current_user),
):
    """
    Резервирует указанное количество свободных номеров, заканчивающихся на '00'.
    Доступно только для администраторов.
    """
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Эта операция доступна только администраторам."
        )

    svc = ReservationService(session)
    try:
        session_id, reserved_numbers = await svc.reserve_golden_numbers(
            user_id=user.id,
            equipment_id=payload.equipment_id,
            quantity=payload.quantity,
            ttl_seconds=payload.ttl_seconds
        )
        return GoldenNumberReservationResponse(
            session_id=session_id,
            reserved_numbers=reserved_numbers
        )
    except HTTPException as e:
        raise e
    except ValueError as e: # Отлов ошибки от admin_reserve_specific
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.post("/assign-one", response_model=AssignNumberOut)
async def assign_one(
        payload: DocumentAssignOne,
        session: AsyncSession = Depends(lifespan_session),
        user: CurrentUser = Depends(get_current_user),
):
    svc = DocumentsService(session)
    try:
        result_dict = await svc.assign_one(
            session_id=payload.session_id,
            user_id=user.id,
            doc_name=payload.doc_name,
            note=payload.note,
            is_admin=user.is_admin,
            numeric=payload.numeric
        )

        if result_dict.get("created") is None:
            message = result_dict.get("message", "Не удалось назначить номер.")
            status_code = status.HTTP_403_FORBIDDEN if "ХХХХ00" in message else status.HTTP_400_BAD_REQUEST

            raise HTTPException(
                status_code=status_code,
                detail=message
            )

        created_info = CreatedDocumentInfo.model_validate(result_dict['created'])
        response_obj = AssignNumberOut(created=created_info, message=result_dict['message'])
        return response_obj.model_dump()

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.patch("/{document_id}", response_model=dict)
async def edit_document(
        document_id: int,
        data: AdminDocumentUpdate,
        session: AsyncSession = Depends(lifespan_session),
        user: CurrentUser = Depends(get_current_user),
):
    """Редактирование документа (только для админов)."""
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Только админ.")

    svc = DocumentsService(session)
    try:
        result = await svc.edit_document_admin(
            document_id=document_id,
            username=user.username,
            data=data
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{document_id}")
async def get_document(
        document_id: int,
        session: AsyncSession = Depends(lifespan_session),
        user: CurrentUser = Depends(get_current_user),
):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Только админ.")

    from app.repositories.documents import DocumentsRepository
    repo = DocumentsRepository(session)
    doc = await repo.get(document_id)

    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден.")

    return JSONResponse({
        "id": doc.id,
        "doc_name": doc.doc_name,
        "note": doc.note,
        "numeric": doc.numeric,
        "formatted_no": format_doc_no(doc.numeric),
        "reg_date": doc.reg_date.isoformat() if doc.reg_date else None
    })
