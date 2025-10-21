from __future__ import annotations

from datetime import datetime, timedelta
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError

from app.repositories.doc_numbers import DocNumbersRepository
from app.repositories.sessions import SessionsRepository

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def start_scheduler(session_factory):
    if scheduler.running:
        logger.warning("Scheduler is already running.")
        return

    scheduler.add_job(
        _cleanup_expired,
        IntervalTrigger(seconds=60),
        args=[session_factory],
        id="cleanup-expired",
        next_run_time=datetime.utcnow() + timedelta(seconds=10),
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started.")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler shut down.")


async def _cleanup_expired(session_factory):
    try:
        async with session_factory() as session:
            ok = await _tables_exist(session)
            if not ok:
                logger.info("TTL cleanup: tables not ready yet, skipping this run")
                return

            now = datetime.utcnow()
            srepo = SessionsRepository(session)
            nrepo = DocNumbersRepository(session)
            await srepo.expire_old(now)
            await nrepo.release_expired(now)
            await session.commit()
            logger.info("TTL cleanup job finished successfully.")
    except ProgrammingError as e:
        logger.warning("TTL cleanup skipped (DB not ready): %s", e)
    except Exception:
        logger.exception("TTL cleanup job failed")


async def _tables_exist(session: AsyncSession) -> bool:
    q = text(
        "select to_regclass('public.sessions') as s, to_regclass('public.doc_numbers') as d"
    )
    res = await session.execute(q)
    s, d = res.fetchone() or (None, None)
    return bool(s and d)
