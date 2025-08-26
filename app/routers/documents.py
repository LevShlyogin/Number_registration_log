from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import lifespan_session
from app.core.auth import get_current_user, CurrentUser
from app.services.documents import DocumentsService
from app.utils.numbering import format_doc_no

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/assign-one", response_class=HTMLResponse)
async def assign_one(
    request: Request,
    session_id: str = Form(...),
    doc_name: str = Form(...),
    note: str | None = Form(None),
    session: AsyncSession = Depends(lifespan_session),
    user: CurrentUser = Depends(get_current_user),
):
    svc = DocumentsService(session)
    try:
        res = await svc.assign_one(
            session_id=session_id, user_id=user.id, doc_name=doc_name, note=note, is_admin=user.is_admin
        )
    except ValueError as e:
        # Для HTMX вернем читаемую плашку об ошибке
        if request.headers.get("Hx-Request") == "true":
            return HTMLResponse(f'<div class="badge" style="color:#b00">Ошибка: {e}</div>', status_code=409)
        raise HTTPException(status_code=409, detail=str(e))

    created = res.get("created")
    if request.headers.get("Hx-Request") == "true":
        if created:
            # Возвращаем HTML строку таблицы для wizard
            equipment = created["equipment"]
            user_info = created["user"]
            
            html = f"""
            <tr>
                <td>{created["formatted_no"]}</td>
                <td>{created["reg_date"].strftime('%d.%m.%Y %H:%M')}</td>
                <td>{created["doc_name"]}</td>
                <td>{created["note"] or ''}</td>
                <td>{equipment.eq_type}</td>
                <td>{equipment.factory_no or '-'}</td>
                <td>{equipment.order_no or '-'}</td>
                <td>{equipment.label or '-'}</td>
                <td>{equipment.station_no or '-'}</td>
                <td>{equipment.station_object or '-'}</td>
                <td>{user_info.username if user_info else '-'}</td>
            </tr>
            """
            return HTMLResponse(html)
        # нет зарезервированных или только "00" при обычном пользователе
        return HTMLResponse(f'<div class="badge" style="color:#b00">{res.get("message")}</div>', status_code=200)
    return JSONResponse(res)
<<<<<<< Current (Your changes)
=======


@router.patch("/{document_id}")
async def edit_document(
    document_id: int,
    doc_name: str | None = Form(None),
    note: str | None = Form(None),
    session: AsyncSession = Depends(lifespan_session),
    user: CurrentUser = Depends(get_current_user),
):
    """Редактирование документа (только для админов)"""
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Только админ.")
    
    svc = DocumentsService(session)
    try:
        result = await svc.edit_document_admin(
            document_id=document_id,
            username=user.username,
            doc_name=doc_name,
            note=note
        )
        return JSONResponse(result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{document_id}")
async def get_document(
    document_id: int,
    session: AsyncSession = Depends(lifespan_session),
    user: CurrentUser = Depends(get_current_user),
):
    """Получение документа для редактирования (только для админов)"""
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
>>>>>>> Incoming (Background Agent changes)
