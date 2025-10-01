from __future__ import annotations

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.auth import get_current_user, CurrentUser
from app.core.db import lifespan_session
from app.schemas.equipment import EquipmentCreate, EquipmentOut
from app.services.equipment import EquipmentService

router = APIRouter()


def clean_param(p: str | None) -> str | None:
    if p is None: return None
    stripped = p.strip()
    return stripped if stripped else None


@router.get("/search", response_model=List[EquipmentOut])
async def search_equipment(
        station_object: str | None = Query(None),
        station_no: str | None = Query(None),
        label: str | None = Query(None),
        factory_no: str | None = Query(None),
        order_no: str | None = Query(None),
        q: str | None = Query(None),
        session: AsyncSession = Depends(lifespan_session),
        user: CurrentUser = Depends(get_current_user),
):
    """Поиск оборудования. Всегда возвращает JSON."""
    svc = EquipmentService(session)
    results = await svc.search(
        station_object=clean_param(station_object),
        station_no=clean_param(station_no),
        label=clean_param(label),
        factory_no=clean_param(factory_no),
        order_no=clean_param(order_no),
        q=clean_param(q)
    )
    return results


@router.post("", response_model=EquipmentOut, status_code=status.HTTP_201_CREATED)
async def create_equipment(
        eq_in: EquipmentCreate,
        session: AsyncSession = Depends(lifespan_session),
        user: CurrentUser = Depends(get_current_user),
):
    """Создание нового объекта оборудования. Всегда работает с JSON."""
    try:
        svc = EquipmentService(session)
        eq = await svc.create(eq_in.model_dump())
        return eq
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")
