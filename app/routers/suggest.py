from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select, func
from app.core.db import lifespan_session
from app.models.document import Document
from app.repositories.equipment import EquipmentRepository

router = APIRouter(prefix="/suggest", tags=["suggest"])


@router.get("/doc-names", response_model=list[str])
async def suggest_doc_names(q: str | None = None, session: AsyncSession = Depends(lifespan_session)):
    stmt = select(func.distinct(Document.doc_name))
    if q:
        stmt = stmt.where(Document.doc_name.ilike(f"%{q}%"))
    stmt = stmt.order_by(Document.doc_name.asc()).limit(20)
    res = await session.execute(stmt)
    return [r[0] for r in res.fetchall() if r[0]]


@router.get("/equipment/{field}", response_model=list[str])
async def suggest_equipment_field(
    field: str,
    q: str | None = None,
    station_object: str | None = None,
    session: AsyncSession = Depends(lifespan_session),
):
    repo = EquipmentRepository(session)
    allowed = {"eq_type", "factory_no", "order_no", "label", "station_no", "station_object"}
    if field not in allowed:
        return []
    vals = await repo.list_distinct(field, q=q, station_object=station_object)
    return vals
