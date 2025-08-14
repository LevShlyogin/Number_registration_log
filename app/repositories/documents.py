from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document


class DocumentsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict) -> Document:
        doc = Document(**data)
        self.session.add(doc)
        await self.session.flush()
        return doc

    async def get_by_numeric(self, numeric: int) -> Document | None:
        res = await self.session.execute(select(Document).where(Document.numeric == numeric))
        return res.scalars().first()

    async def get(self, id_: int) -> Document | None:
        res = await self.session.execute(select(Document).where(Document.id == id_))
        return res.scalars().first()
