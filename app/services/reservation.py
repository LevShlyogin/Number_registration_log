from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.doc_number import DocNumber, DocNumStatus
from app.models.session import SessionStatus, Session
from app.repositories.counter import CounterRepository
from app.repositories.doc_numbers import DocNumbersRepository
from app.repositories.sessions import SessionsRepository
from app.utils.numbering import is_golden


class ReservationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.sessions_repo = SessionsRepository(session)
        self.numbers_repo = DocNumbersRepository(session)
        self.counter_repo = CounterRepository(session)

    async def reserve_golden_numbers(self, *, user_id: int, equipment_id: int, quantity: int, ttl_seconds: int) -> \
    tuple[str, list[int]]:
        candidates = await self._find_free_golden_numbers(quantity)

        if len(candidates) < quantity:
            raise ValueError(f"Не удалось найти {quantity} свободных 'золотых' номеров.")

        sess = await self.sessions_repo.create(
            user_id=user_id, equipment_id=equipment_id, requested_count=len(candidates), ttl_seconds=ttl_seconds
        )
        reserved = await self.numbers_repo.reserve_specific_numbers(candidates, user_id, sess.id, ttl_seconds)

        await self.session.commit()
        return sess.id, reserved

    async def start_session(self, *, user_id: int, equipment_id: int, requested_count: int, ttl_seconds: int) -> tuple[
        str, list[int]]:
        sess = await self.sessions_repo.create(
            user_id=user_id, equipment_id=equipment_id, requested_count=requested_count, ttl_seconds=ttl_seconds
        )
        reserved = await self._reserve_for_session(
            session_id=sess.id, user_id=user_id, count=requested_count, ttl_seconds=ttl_seconds, is_admin=False
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

    async def add_numbers_to_session(self, *, session_id: str, user_id: int, requested_count: int | None,
                                     numbers: list[int] | None, quantity_golden: int | None = None, is_admin: bool) -> \
            list[int]:
        sess = await self.sessions_repo.get(session_id)
        if not sess:
            raise ValueError("Сессия не найдена.")

        ttl = sess.ttl_seconds
        new_expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        await self.session.execute(update(Session).where(Session.id == session_id).values(expires_at=new_expires_at))
        await self.session.execute(
            update(DocNumber).where(DocNumber.session_id == session_id).values(expires_at=new_expires_at))

        newly_reserved = []
        if requested_count:
            newly_reserved = await self._reserve_for_session(
                session_id=session_id, user_id=user_id, count=requested_count, ttl_seconds=ttl, is_admin=is_admin
            )
        elif numbers:
            newly_reserved = await self.numbers_repo.reserve_specific_numbers(numbers, user_id, session_id, ttl)
        elif quantity_golden:
            if not is_admin:
                raise ValueError("Только администраторы могут резервировать 'золотые' номера.")

            candidates = await self._find_free_golden_numbers(quantity_golden)

            if len(candidates) < quantity_golden:
                raise ValueError(f"Не удалось найти {quantity_golden} свободных 'золотых' номеров.")

            newly_reserved = await self.numbers_repo.reserve_specific_numbers(candidates, user_id, session_id, ttl)

        await self.session.commit()
        return newly_reserved

    async def _find_free_golden_numbers(self, quantity: int) -> list[int]:
        counter = await self.counter_repo.get_for_update()

        start_point = max(counter.next_normal_start, counter.base_start)
        start_golden = ((start_point + 99) // 100) * 100

        stmt = select(DocNumber.numeric).where(
            DocNumber.status.in_([DocNumStatus.assigned, DocNumStatus.reserved])
        )
        result = await self.session.execute(stmt)
        occupied_numbers = set(result.scalars().all())

        candidates = []
        current_check = start_golden
        while len(candidates) < quantity:
            if current_check not in occupied_numbers:
                candidates.append(current_check)

            current_check += 100
            if current_check > 999900: break

        return candidates

    async def cancel_session(self, session_id: str) -> int:
        await self.sessions_repo.set_status(session_id, SessionStatus.cancelled)
        released = await self.numbers_repo.release_session(session_id)
        await self.session.commit()
        return released
