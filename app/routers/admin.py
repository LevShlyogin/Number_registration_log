from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import lifespan_session
from app.core.auth import get_current_user, CurrentUser
from app.services.admin import AdminService
from app.services.reservation import ReservationService
from app.core.config import settings
from app.schemas.admin import GoldenSuggestOut, AdminReserveSpecific  # Импортируем схемы

router = APIRouter()


@router.get("/check-access", response_model=dict)
async def check_access(
        user: CurrentUser = Depends(get_current_user),
):
    """Проверка, является ли текущий пользователь администратором."""
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещен")
    return {"is_admin": True}


@router.get("/golden-suggest", response_model=GoldenSuggestOut)
async def golden_suggest(
        limit: int = 10,
        session: AsyncSession = Depends(lifespan_session),
        user: CurrentUser = Depends(get_current_user),
):
    """Предлагает свободные 'золотые' номера (только для админов)."""
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещен")
    svc = AdminService(session)
    nums = await svc.suggest_golden(limit=limit)
    return GoldenSuggestOut(golden_numbers=nums)


@router.post("/reserve-specific", response_model=dict)
async def reserve_specific(
        payload: AdminReserveSpecific,  # <--- Принимаем Pydantic модель (JSON)
        session: AsyncSession = Depends(lifespan_session),
        user: CurrentUser = Depends(get_current_user),
):
    """Резервирует конкретные номера для оборудования (только для админов)."""
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещен")

    svc = ReservationService(session)
    try:
        session_id = await svc.admin_reserve_specific(
            user_id=user.id,
            equipment_id=payload.equipment_id,
            numbers=payload.numbers,
            ttl_seconds=settings.default_ttl_seconds
        )
        return {"session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
