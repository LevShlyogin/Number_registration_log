from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.core.db import lifespan_session
from app.core.auth import get_current_user, CurrentUser
from app.services.documents import DocumentsService
from app.schemas.admin import AdminDocumentUpdate
from app.schemas.documents import DocumentAssignOne
from app.utils.numbering import format_doc_no

router = APIRouter()


@router.post("/assign-one", response_model=dict)
async def assign_one(
        payload: DocumentAssignOne,
        session: AsyncSession = Depends(lifespan_session),
        user: CurrentUser = Depends(get_current_user),
):
    """Назначает один номер из сессии. Всегда возвращает JSON."""
    svc = DocumentsService(session)
    try:
        res = await svc.assign_one(
            session_id=payload.session_id,
            user_id=user.id,
            doc_name=payload.doc_name,
            note=payload.note,
            is_admin=user.is_admin
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


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
