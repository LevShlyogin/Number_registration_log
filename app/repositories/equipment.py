from __future__ import annotations

from sqlalchemy import select, func, or_, and_
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

    async def search(
        self,
        station_object: str | None = None,
        station_no: str | None = None,
        label: str | None = None,
        factory_no: str | None = None,
        q: str | None = None
    ) -> list[Equipment]:
        """Поиск оборудования по различным критериям"""
        stmt = select(Equipment)
        conditions = []
        
        # Поиск по отдельным полям
        if station_object:
            conditions.append(Equipment.station_object.ilike(f"%{station_object}%"))
        if station_no:
            conditions.append(Equipment.station_no.ilike(f"%{station_no}%"))
        if label:
            conditions.append(Equipment.label.ilike(f"%{label}%"))
        if factory_no:
            conditions.append(Equipment.factory_no.ilike(f"%{factory_no}%"))
        
        # Поиск по "сборной" строке
        if q:
            q_conditions = [
                Equipment.station_object.ilike(f"%{q}%"),
                Equipment.station_no.ilike(f"%{q}%"),
                Equipment.label.ilike(f"%{q}%"),
                Equipment.factory_no.ilike(f"%{q}%")
            ]
            conditions.append(or_(*q_conditions))
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        stmt = stmt.order_by(Equipment.id.desc()).limit(50)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def find_duplicate(
        self,
        station_object: str | None = None,
        station_no: str | None = None,
        label: str | None = None,
        factory_no: str | None = None
    ) -> Equipment | None:
        """Поиск дубля оборудования"""
        conditions = []
        
        if station_object:
            conditions.append(Equipment.station_object.ilike(station_object))
        if station_no:
            conditions.append(Equipment.station_no.ilike(station_no))
        if label:
            conditions.append(Equipment.label.ilike(label))
        if factory_no:
            conditions.append(Equipment.factory_no.ilike(factory_no))
        
        # Если все поля пустые - дубля нет
        if not conditions:
            return None
        
        # Ищем по комбинации заполненных полей
        stmt = select(Equipment).where(and_(*conditions))
        res = await self.session.execute(stmt)
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
