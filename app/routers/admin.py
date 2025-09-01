from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import lifespan_session
from app.core.auth import get_current_user, CurrentUser
from app.services.admin import AdminService
from app.services.reservation import ReservationService
from app.core.config import settings
from app.schemas.admin import GoldenSuggestOut

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/check-access")
async def check_access(
    user: CurrentUser = Depends(get_current_user),
):
    """Проверка прав администратора"""
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Только админ.")
    return JSONResponse({"is_admin": True})


@router.get("/golden-suggest")
async def golden_suggest(
    request: Request,
    limit: int = 10,
    session: AsyncSession = Depends(lifespan_session),
    user: CurrentUser = Depends(get_current_user),
):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Только админ.")
    svc = AdminService(session)
    nums = await svc.suggest_golden(limit=limit)
    if request.headers.get("Hx-Request") == "true":
        items = "".join(f'<li class="golden-number">{n:06d}</li>' for n in nums)
        return HTMLResponse(f"<ul>{items}</ul>")
    return JSONResponse(GoldenSuggestOut(golden_numbers=nums).model_dump())


@router.post("/reserve-specific")
async def reserve_specific(
    request: Request,
    equipment_id: int = Form(...),
    numbers: str = Form(...),  # "100, 200,300"
    session: AsyncSession = Depends(lifespan_session),
    user: CurrentUser = Depends(get_current_user),
):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Только админ.")
    # распарсим CSV в список int
    raw = [p.strip() for p in numbers.replace(";", ",").split(",") if p.strip()]
    try:
        nums = [int(p) for p in raw]
    except ValueError:
        raise HTTPException(status_code=400, detail="Некорректный формат номеров. Используйте числа через запятую.")

    svc = ReservationService(session)
    sess_id = await svc.admin_reserve_specific(
        user_id=user.id, equipment_id=equipment_id, numbers=nums, ttl_seconds=settings.default_ttl_seconds
    )
    if request.headers.get("Hx-Request") == "true":
        pretty = ", ".join(str(n) for n in nums)
        return HTMLResponse(f'<div class="badge">Создана админ‑сессия: <b>{sess_id}</b><br/>Номера: {pretty}</div>')
    return JSONResponse({"session_id": sess_id})