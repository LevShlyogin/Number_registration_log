from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.repositories.equipment import EquipmentRepository
from app.models.equipment import Equipment


class EquipmentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = EquipmentRepository(session)

    async def create(self, data: dict) -> Equipment:
        # Проверяем дубли перед созданием
        await self._check_duplicates(data)
        
        try:
            eq = await self.repo.create(data)
            await self.session.commit()
            return eq
        except IntegrityError as e:
            await self.session.rollback()
            if "ix_equipment_unique_attributes" in str(e):
                raise HTTPException(
                    status_code=409, 
                    detail="Объект с такими атрибутами уже существует."
                )
            raise

    async def get(self, id_: int) -> Equipment | None:
        return await self.repo.get(id_)

    async def search(
        self, 
        station_object: str | None = None,
        station_no: str | None = None,
        label: str | None = None,
        factory_no: str | None = None,
        order_no: str | None = None,
        q: str | None = None
    ) -> list[Equipment]:
        """Поиск оборудования по различным критериям"""
        return await self.repo.search(
            station_object=station_object,
            station_no=station_no,
            label=label,
            factory_no=factory_no,
            order_no=order_no,
            q=q
        )

    async def _check_duplicates(self, data: dict) -> None:
        """Проверка на дубли оборудования"""
        # Если все поля пустые - считаем объект уникальным
        if not any([
            data.get('station_object'),
            data.get('station_no'),
            data.get('label'),
            data.get('factory_no')
        ]):
            return
        
        # Проверяем существование дубля
        existing = await self.repo.find_duplicate(
            station_object=data.get('station_object'),
            station_no=data.get('station_no'),
            label=data.get('label'),
            factory_no=data.get('factory_no')
        )
        
        if existing:
            raise HTTPException(
                status_code=409,
                detail="Объект с такими атрибутами уже существует."
            )
