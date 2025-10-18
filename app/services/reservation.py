from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.sessions import SessionsRepository
from app.repositories.doc_numbers import DocNumbersRepository
from app.repositories.counter import CounterRepository
from app.models.session import SessionStatus
from app.utils.numbering import is_golden


class ReservationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.sessions_repo = SessionsRepository(session)
        self.numbers_repo = DocNumbersRepository(session)
        self.counter_repo = CounterRepository(session)

    async def start_session(self, *, user_id: int, equipment_id: int, requested_count: int, ttl_seconds: int) -> tuple[
        str, list[int]]:
        # создаем сессию
        sess = await self.sessions_repo.create(
            user_id=user_id, equipment_id=equipment_id, requested_count=requested_count, ttl_seconds=ttl_seconds
        )
        # резерв
        reserved = await self._reserve_for_session(
            session_id=sess.id, user_id=user_id, count=requested_count, is_admin=False, ttl_seconds=ttl_seconds
        )
        await self.session.commit()
        return sess.id, reserved

    async def _reserve_for_session(self, *, session_id: str, user_id: int, count: int, is_admin: bool,
                                   ttl_seconds: int) -> list[int]:
        await self.numbers_repo.release_expired()
        counter = await self.counter_repo.get_for_update()
        base_start = counter.base_start
        reserved_total: list[int] = []

        # 1) released pool
        released_pick = await self.numbers_repo.fetch_released_for_update(
            base_start=base_start, limit=count, skip_golden=not is_admin
        )
        if released_pick:
            reserved = await self.numbers_repo.reserve_existing(released_pick, user_id, session_id, ttl_seconds)
            reserved_total.extend(reserved)

        need_more = count - len(reserved_total)
        if need_more > 0:
            # 2) generate new
            candidate = max(counter.next_normal_start, base_start)
            new_candidates: list[int] = []
            while len(new_candidates) < need_more:
                if not is_admin and is_golden(candidate):
                    candidate += 1
                    continue
                new_candidates.append(candidate)
                candidate += 1
            # записываем новые номера
            reserved = await self.numbers_repo.create_and_reserve_new(
                new_candidates, user_id=user_id, session_id=session_id, ttl_seconds=ttl_seconds
            )
            reserved_total.extend(reserved)
            # продвижение next_normal_start
            counter.next_normal_start = candidate

        return sorted(reserved_total)

    async def admin_reserve_specific(self, *, user_id: int, equipment_id: int, numbers: list[int], ttl_seconds: int) -> \
    tuple[str, list[int]]:
        sess = await self.sessions_repo.create(
            user_id=user_id, equipment_id=equipment_id, requested_count=len(numbers), ttl_seconds=ttl_seconds
        )
        await self.numbers_repo.release_expired()
        await self.counter_repo.get_for_update()
        reserved = await self.numbers_repo.reserve_specific_numbers(numbers, user_id, sess.id, ttl_seconds)
        if not reserved:
            await self.session.rollback()
            raise ValueError("Не удалось зарезервировать ни один из указанных номеров (возможно, они уже заняты).")
        await self.session.commit()
        return sess.id, reserved

    async def cancel_session(self, session_id: str) -> int:
        await self.sessions_repo.set_status(session_id, SessionStatus.cancelled)
        released = await self.numbers_repo.release_session(session_id)
        await self.session.commit()
        return released
