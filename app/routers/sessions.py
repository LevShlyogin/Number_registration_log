from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.core.auth import get_current_user, CurrentUser
from app.core.config import settings
from app.core.db import lifespan_session
from app.repositories.doc_numbers import DocNumbersRepository
from app.repositories.sessions import SessionsRepository
from app.schemas.sessions import SessionStart, ReserveResult
from app.services.reservation import ReservationService

router = APIRouter()


@router.post("/reserve", response_model=ReserveResult)
async def start_session_and_reserve(
        payload: SessionStart,
        session: AsyncSession = Depends(lifespan_session),
        user: CurrentUser = Depends(get_current_user),
):
    """Создает сессию и резервирует номера. Всегда возвращает JSON."""
    svc = ReservationService(session)
    ttl = payload.ttl_seconds or settings.default_ttl_seconds
    session_id, reserved_numbers = await svc.start_session(
        user_id=user.id,
        equipment_id=payload.equipment_id,
        requested_count=payload.requested_count,
        ttl_seconds=ttl
    )
    return ReserveResult(session_id=session_id, reserved_numbers=reserved_numbers)


@router.post("/{session_id}/complete", response_model=dict)
async def complete_session(
        session_id: str,
        session: AsyncSession = Depends(lifespan_session),
        user: CurrentUser = Depends(get_current_user),
):
    """Завершение сессии с освобождением неназначенных номеров"""
    numbers_repo = DocNumbersRepository(session)
    sessions_repo = SessionsRepository(session)

    released_count = await numbers_repo.release_session(session_id)

    await sessions_repo.set_status(session_id, "completed")
    await session.commit()

    return {"success": True, "message": "Сессия завершена", "released_count": released_count}


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


@router.get("/{session_id}/reserved")
async def get_reserved_numbers(
        session_id: str,
        session: AsyncSession = Depends(lifespan_session),
        user: CurrentUser = Depends(get_current_user),
):
    """Получение списка зарезервированных номеров для сессии"""
    numbers_repo = DocNumbersRepository(session)
    reserved = await numbers_repo.get_reserved_for_session(session_id)

    if not reserved:
        return {"reserved": [], "message": "Нет зарезервированных номеров"}

    # Форматируем номера для отображения
    formatted_numbers = []
    for num in reserved:
        formatted_numbers.append({
            "numeric": num.numeric,
            "is_golden": num.is_golden,
            "formatted": f"УТЗ-{num.numeric:06d}"
        })

    return {"reserved": formatted_numbers, "count": len(formatted_numbers)}
