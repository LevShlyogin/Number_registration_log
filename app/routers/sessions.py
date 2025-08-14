from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import lifespan_session
from app.core.auth import get_current_user, CurrentUser
from app.schemas.sessions import SessionStart, SessionOut, ReserveResult
from app.services.reservation import ReservationService
from app.services.reservation import ReservationService
from app.services.reservation import ReservationService
from app.core.config import settings
from app.repositories.sessions import SessionsRepository
from app.models.session import SessionStatus

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=ReserveResult)
async def start_session(
    payload: SessionStart,
    session: AsyncSession = Depends(lifespan_session),
    user: CurrentUser = Depends(get_current_user),
):
    svc = ReservationService(session)
    ttl = payload.ttl_seconds or settings.default_ttl_seconds
    session_id, reserved = await svc.start_session(
        user_id=user.id, equipment_id=payload.equipment_id, requested_count=payload.requested_count, ttl_seconds=ttl
    )
    return ReserveResult(session_id=session_id, reserved_numbers=reserved)


@router.post("/{session_id}/cancel", response_model=dict)
async def cancel_session(
    session_id: str,
    session: AsyncSession = Depends(lifespan_session),
    user: CurrentUser = Depends(get_current_user),
):
    svc = ReservationService(session)
    released = await svc.cancel_session(session_id)
    return {"released": released}


@router.get("/{session_id}", response_model=SessionOut)
async def get_session(
    session_id: str,
    session: AsyncSession = Depends(lifespan_session),
    user: CurrentUser = Depends(get_current_user),
):
    repo = SessionsRepository(session)
    sess = await repo.get(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    return sess
