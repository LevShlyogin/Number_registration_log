from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.equipment import EquipmentRepository
from app.models.equipment import Equipment


class EquipmentService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = EquipmentRepository(session)

    async def create(self, data: dict) -> Equipment:
        eq = await self.repo.create(data)
        await self.session.commit()
        return eq

    async def get(self, id_: int) -> Equipment | None:
        return await self.repo.get(id_)
