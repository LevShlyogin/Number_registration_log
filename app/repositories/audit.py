from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog


class AuditRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, *, document_id: int, doc_number: int, username: str, diff: dict) -> None:
        log = AuditLog(document_id=document_id, doc_number=doc_number, username=username, diff=diff)
        self.session.add(log)
        await self.session.flush()
