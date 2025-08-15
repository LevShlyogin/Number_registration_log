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
    note: str = Form(...),
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
            return HTMLResponse(
                f'<div class="badge">Документ создан: № <b>{format_doc_no(created["numeric"])}</b></div>'
            )
        # нет зарезервированных или только “00” при обычном пользователе
        return HTMLResponse(f'<div class="badge" style="color:#b00">{res.get("message")}</div>', status_code=200)
    return JSONResponse(res)
