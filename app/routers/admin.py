from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import lifespan_session
from app.core.auth import get_current_user, CurrentUser
from app.schemas.admin import AdminReserveSpecific, GoldenSuggestOut
from app.services.admin import AdminService
from app.services.reservation import ReservationService
from app.core.config import settings

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/golden-suggest", response_model=GoldenSuggestOut)
async def golden_suggest(
    limit: int = 10,
    session=Depends(lifespan_session),
    user: CurrentUser = Depends(get_current_user),
):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Только админ.")
    svc = AdminService(session)
    nums = await svc.suggest_golden(limit=limit)
    return GoldenSuggestOut(golden_numbers=nums)


@router.post("/reserve-specific", response_model=dict)
async def reserve_specific(
    payload: AdminReserveSpecific,
    session=Depends(lifespan_session),
    user: CurrentUser = Depends(get_current_user),
):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Только админ.")
    svc = ReservationService(session)
    session_id = await svc.admin_reserve_specific(
        user_id=user.id, equipment_id=payload.equipment_id, numbers=payload.numbers, ttl_seconds=settings.default_ttl_seconds
    )
    return {"session_id": session_id}
