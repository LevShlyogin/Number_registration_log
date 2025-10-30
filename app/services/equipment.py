from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.repositories.equipment import EquipmentRepository
from app.models.equipment import Equipment


class EquipmentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = EquipmentRepository(session)

    async def create(self, data: dict) -> Equipment:
        factory_no = data.get("factory_no")
        # Проверяем на дубликат только если factory_no передан
        if factory_no:
            query = select(Equipment).where(Equipment.factory_no == factory_no)
            result = await self.session.execute(query)
            existing_equipment = result.scalars().first()
            if existing_equipment:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Оборудование с заводским номером '{factory_no}' уже существует."
                )
        
        try:
            # await self._check_duplicates(data)
            eq = await self.repo.create(data)
            await self.session.commit()
            await self.session.refresh(eq)
            return eq
        except IntegrityError as e:
            await self.session.rollback()
            
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Объект с такими атрибутами уже существует."
            )

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
        """Проверка на дубликаты перед созданием"""
        # Если все 4 поля пустые, то дубликатов быть не может
        if not any([data.get('station_object'), data.get('station_no'), 
                   data.get('label'), data.get('factory_no')]):
            return
        
        # Иначе проверяем на дубликаты
        duplicate = await self.repo.find_duplicate(
            station_object=data.get('station_object'),
            station_no=data.get('station_no'),
            label=data.get('label'),
            factory_no=data.get('factory_no')
        )
        
        if duplicate:
            raise HTTPException(
                status_code=409, 
                detail="Объект с такими атрибутами уже существует."
            )
    
    async def get_all(self, limit: int = 100) -> list[Equipment]:
        """Получение всех записей оборудования с лимитом"""
        return await self.repo.get_all(limit=limit)
