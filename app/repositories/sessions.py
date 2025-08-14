from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session, SessionStatus


class SessionsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, *, user_id: int, equipment_id: int, requested_count: int, ttl_seconds: int) -> Session:
        now = datetime.utcnow()
        sess = Session(
            user_id=user_id,
            equipment_id=equipment_id,
            requested_count=requested_count,
            ttl_seconds=ttl_seconds,
            expires_at=now + timedelta(seconds=ttl_seconds),
            status=SessionStatus.active,
        )
        self.session.add(sess)
        await self.session.flush()
        return sess

    async def get(self, session_id: str) -> Session | None:
        res = await self.session.execute(select(Session).where(Session.id == session_id))
        return res.scalars().first()

    async def set_status(self, session_id: str, status: SessionStatus) -> None:
        await self.session.execute(update(Session).where(Session.id == session_id).values(status=status))

    async def expire_old(self, now: datetime) -> int:
        res = await self.session.execute(
            update(Session)
            .where(Session.status == SessionStatus.active, Session.expires_at < now)
            .values(status=SessionStatus.expired)
            .returning(Session.id)
        )
        return len(res.fetchall())
