from __future__ import annotations

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.equipment import Equipment


class EquipmentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict) -> Equipment:
        eq = Equipment(**data)
        self.session.add(eq)
        await self.session.flush()
        return eq

    async def get(self, id_: int) -> Equipment | None:
        res = await self.session.execute(select(Equipment).where(Equipment.id == id_))
        return res.scalars().first()

    async def list_distinct(self, field: str, q: str | None = None, station_object: str | None = None) -> list[str]:
        col = getattr(Equipment, field)
        stmt = select(func.distinct(col))
        if q:
            stmt = stmt.where(col.ilike(f"%{q}%"))
        if station_object and field == "station_no":
            stmt = stmt.where(Equipment.station_object == station_object)
        if station_object and field == "label":
            stmt = stmt.where(Equipment.station_object == station_object)
        res = await self.session.execute(stmt.order_by(col.asc()).limit(20))
        return [row[0] for row in res.fetchall() if row[0]]
