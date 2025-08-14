from __future__ import annotations

from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.doc_numbers import DocNumbersRepository
from app.repositories.sessions import SessionsRepository


def start_scheduler(session_factory):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(_cleanup_expired, IntervalTrigger(seconds=60), args=[session_factory], id="cleanup-expired")
    scheduler.start()


async def _cleanup_expired(session_factory):
    async with session_factory() as session:  # type: AsyncSession
        now = datetime.utcnow()
        srepo = SessionsRepository(session)
        nrepo = DocNumbersRepository(session)
        await srepo.expire_old(now)
        await nrepo.release_expired(now)
        await session.commit()
