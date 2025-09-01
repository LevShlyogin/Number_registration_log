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
        order_no: str | None = None,
        q: str | None = None
    ) -> list[Equipment]:
        stmt = select(Equipment)
        conditions = []

        # Поиск по частичному совпадению для текстовых полей
        if station_object: conditions.append(Equipment.station_object.ilike(f"%{station_object}%"))
        
        # Точное совпадение для идентификаторов
        if station_no: conditions.append(Equipment.station_no == station_no)
        if factory_no: conditions.append(Equipment.factory_no == factory_no)
        if order_no: conditions.append(Equipment.order_no == order_no)
        if label: conditions.append(Equipment.label == label) # Маркировку тоже лучше искать точно

        # Глобальный поиск по всем полям
        if q:
            # Используем ilike для глобального поиска, так как это более ожидаемое поведение
            q_conditions = [
                Equipment.station_object.ilike(f"%{q}%"),
                Equipment.station_no.ilike(f"%{q}%"),
                Equipment.label.ilike(f"%{q}%"),
                Equipment.factory_no.ilike(f"%{q}%"),
                Equipment.order_no.ilike(f"%{q}%")
            ]
            conditions.append(or_(*q_conditions))

        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        stmt = stmt.order_by(Equipment.id.desc()).limit(50)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    # Метод find_duplicate тоже стоит исправить для консистентности
    async def find_duplicate(
        self,
        station_object: str | None = None,
        station_no: str | None = None,
        label: str | None = None,
        factory_no: str | None = None
    ) -> Equipment | None:
        """Поиск дубликата оборудования"""
        stmt = select(Equipment)
        conditions = []
        
        # Точное сравнение для предотвращения ложных срабатываний
        if station_object: conditions.append(Equipment.station_object == station_object)
        if station_no: conditions.append(Equipment.station_no == station_no)
        if label: conditions.append(Equipment.label == label)
        if factory_no: conditions.append(Equipment.factory_no == factory_no)
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
            stmt = stmt.limit(1)
            res = await self.session.execute(stmt)
            return res.scalars().first()
        
        return None
    
    async def get_all(self, limit: int = 100) -> list[Equipment]:
        """Получение всех записей оборудования с лимитом"""
        stmt = select(Equipment).order_by(Equipment.id.desc()).limit(limit)
        res = await self.session.execute(stmt)
        return res.scalars().all()

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