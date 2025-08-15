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


def start_scheduler(session_factory):
    scheduler = AsyncIOScheduler()
    # стартуем через 60 секунд, чтобы миграции точно успели
    scheduler.add_job(
        _cleanup_expired,
        IntervalTrigger(seconds=60),
        args=[session_factory],
        id="cleanup-expired",
        next_run_time=datetime.utcnow() + timedelta(seconds=60),
        max_instances=1,
        coalesce=True,
        replace_existing=True,
    )
    scheduler.start()


async def _cleanup_expired(session_factory):
    try:
        async with session_factory() as session:  # type: AsyncSession
            # проверка наличия нужных таблиц
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
    except ProgrammingError as e:
        # если вдруг миграции еще не применены — тихо пропускаем
        logger.warning("TTL cleanup skipped (DB not ready): %s", e)
    except Exception as e:
        logger.exception("TTL cleanup job failed: %s", e)


async def _tables_exist(session: AsyncSession) -> bool:
    q = text(
        "select to_regclass('public.sessions') as s, to_regclass('public.doc_numbers') as d"
    )
    res = await session.execute(q)
    s, d = res.fetchone()
    return bool(s and d)
