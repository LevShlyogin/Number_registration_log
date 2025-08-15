from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, CurrentUser
from app.core.config import settings
from app.core.db import lifespan_session
from app.repositories.sessions import SessionsRepository
from app.schemas.sessions import ReserveResult
from app.services.reservation import ReservationService

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_class=HTMLResponse)
async def start_session(
    request: Request,
    equipment_id: int = Form(...),
    requested_count: int = Form(1),
    ttl_seconds: int | None = Form(None),
    session: AsyncSession = Depends(lifespan_session),
    user: CurrentUser = Depends(get_current_user),
):
    svc = ReservationService(session)
    ttl = ttl_seconds or settings.default_ttl_seconds
    session_id, reserved = await svc.start_session(
        user_id=user.id, equipment_id=equipment_id, requested_count=requested_count, ttl_seconds=ttl
    )
    if request.headers.get("Hx-Request") == "true":
        pretty = ", ".join(str(n) for n in reserved) or "—"
        html = f'<div class="badge">Сессия: <b>{session_id}</b><br/>Зарезервировано: {pretty}</div>'
        return HTMLResponse(html)
    return JSONResponse(ReserveResult(session_id=session_id, reserved_numbers=reserved).model_dump())


@router.post("/{session_id}/cancel", response_model=dict)
async def cancel_session(
    session_id: str,
    session: AsyncSession = Depends(lifespan_session),
    user: CurrentUser = Depends(get_current_user),
):
    svc = ReservationService(session)
    released = await svc.cancel_session(session_id)
    return {"released": released}


@router.get("/{session_id}")
async def get_session(
    session_id: str,
    session: AsyncSession = Depends(lifespan_session),
    user: CurrentUser = Depends(get_current_user),
):
    repo = SessionsRepository(session)
    sess = await repo.get(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    return JSONResponse(
        {
            "id": sess.id,
            "user_id": sess.user_id,
            "equipment_id": sess.equipment_id,
            "requested_count": sess.requested_count,
            "status": sess.status.value,
            "ttl_seconds": sess.ttl_seconds,
            "created_at": sess.created_at.isoformat(),
            "expires_at": sess.expires_at.isoformat(),
        }
    )