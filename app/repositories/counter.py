from __future__ import annotations

from sqlalchemy import select, update, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.counter import DocCounter


class CounterRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_for_update(self) -> DocCounter:
        res = await self.session.execute(
            select(DocCounter).where(DocCounter.id == 1).with_for_update()
        )
        counter = res.scalars().first()
        if not counter:
            counter = DocCounter(id=1, base_start=1, next_normal_start=1)
            self.session.add(counter)
            await self.session.flush()
        return counter

    async def set_after_import(self, base_start: int) -> None:
        await self.session.execute(
            update(DocCounter).where(DocCounter.id == 1).values(base_start=base_start, next_normal_start=base_start)
        )
