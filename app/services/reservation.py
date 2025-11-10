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


def _next_golden_start(base: int) -> int:
    """Первый кратный 100 номер, не меньше base."""
    return ((base + 99) // 100) * 100


class ReservationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.sessions_repo = SessionsRepository(session)
        self.numbers_repo = DocNumbersRepository(session)
        self.counter_repo = CounterRepository(session)

    async def reserve_golden_for_session(
        self, *, session_id: str, user_id: int, count: int, ttl_seconds: int
    ) -> list[int]:
        """
        Резерв 'золотых' номеров строго 'сверху':
        - старт = ceil(max(base_start, next_normal_start) / 100) * 100
        - released берём только >= старт и только кратные 100
        - если не хватило — генерируем шагом 100
        - normal-счётчик (next_normal_start) не двигаем
        """
        await self.numbers_repo.release_expired()

        counter = await self.counter_repo.get_for_update()
        base = max(counter.base_start, counter.next_normal_start or counter.base_start)
        start = _next_golden_start(base)

        # 1) Заберём released-пул (золотые, >= start)
        released_pick = await self.numbers_repo.fetch_released_for_update(
            base_start=start, limit=count, skip_golden=False
        )
        released_pick = [n for n in released_pick if n.numeric % 100 == 0]

        reserved_total: list[int] = []
        if released_pick:
            reserved_total.extend(
                await self.numbers_repo.reserve_existing(released_pick, user_id, session_id, ttl_seconds)
            )

        # 2) Если не хватило — создаём кандидатов (шаг 100)
        need_more = count - len(reserved_total)
        if need_more > 0:
            cand: list[int] = []
            n = start
            while len(cand) < need_more:
                cand.append(n)
                n += 100

            created = await self.numbers_repo.create_and_reserve_new(
                cand, user_id=user_id, session_id=session_id, ttl_seconds=ttl_seconds
            )
            reserved_total.extend(created)

        return sorted(reserved_total)

    async def start_session(
        self, *, user_id: int, equipment_id: int, requested_count: int, ttl_seconds: int
    ) -> tuple[str, list[int]]:
        """Старт обычной сессии и резерв обычных номеров."""
        sess = await self.sessions_repo.create(
            user_id=user_id,
            equipment_id=equipment_id,
            requested_count=requested_count,
            ttl_seconds=ttl_seconds,
        )
        reserved = await self._reserve_for_session(
            session_id=sess.id, user_id=user_id, count=requested_count, ttl_seconds=ttl_seconds, is_admin=False
        )
        await self.session.commit()
        return sess.id, reserved

    async def _reserve_for_session(
        self, *, session_id: str, user_id: int, count: int, is_admin: bool, ttl_seconds: int
    ) -> list[int]:
        """Резерв обычных номеров (не 'золотых' для не-админов)."""
        await self.numbers_repo.release_expired()
        counter = await self.counter_repo.get_for_update()
        base_start = counter.base_start
        reserved_total: list[int] = []

        # 1) Забираем released пул (для не-админов — без 'золотых')
        released_pick = await self.numbers_repo.fetch_released_for_update(
            base_start=base_start, limit=count, skip_golden=not is_admin
        )
        if released_pick:
            reserved = await self.numbers_repo.reserve_existing(released_pick, user_id, session_id, ttl_seconds)
            reserved_total.extend(reserved)

        # 2) Генерация новых (пропуская 'золотые' для не-админов)
        need_more = count - len(reserved_total)
        if need_more > 0:
            candidate = max(counter.next_normal_start, base_start)
            new_candidates: list[int] = []
            while len(new_candidates) < need_more:
                if not is_admin and is_golden(candidate):
                    candidate += 1
                    continue
                new_candidates.append(candidate)
                candidate += 1

            reserved = await self.numbers_repo.create_and_reserve_new(
                new_candidates, user_id=user_id, session_id=session_id, ttl_seconds=ttl_seconds
            )
            reserved_total.extend(reserved)

            # Продвигаем normal-счётчик
            counter.next_normal_start = candidate

        return sorted(reserved_total)

    async def admin_reserve_specific(
        self, *, user_id: int, equipment_id: int, numbers: list[int], ttl_seconds: int
    ) -> tuple[str, list[int]]:
        """
        Админ резервирует конкретные номера списком.
        Гард: если это 'золотые' — не даём резервить ниже стартовой сотни (ceil(base/100)*100).
        """
        if numbers and all(n % 100 == 0 for n in numbers):
            counter = await self.counter_repo.get_for_update()
            base = max(counter.base_start, counter.next_normal_start or counter.base_start)
            min_golden = _next_golden_start(base)
            numbers = [n for n in numbers if n >= min_golden]
            if not numbers:
                await self.session.rollback()
                raise ValueError(f"Все переданные 'золотые' номера ниже {min_golden}")

        sess = await self.sessions_repo.create(
            user_id=user_id, equipment_id=equipment_id, requested_count=len(numbers), ttl_seconds=ttl_seconds
        )
        reserved = await self.numbers_repo.reserve_specific_numbers(numbers, user_id, sess.id, ttl_seconds)
        if not reserved:
            await self.session.rollback()
            raise ValueError("Не удалось зарезервировать ни один из указанных номеров (возможно, они уже заняты).")

        await self.session.commit()
        return sess.id, reserved

    async def add_numbers_to_session(
        self,
        *,
        session_id: str,
        user_id: int,
        requested_count: int | None,
        numbers: list[int] | None,
        is_admin: bool,
        golden_requested_count: int | None = None,
    ) -> list[int]:
        """
        Докинуть номера в открытую сессию:
        - requested_count: обычные номера
        - numbers: резерв конкретных номеров
        - golden_requested_count: 'золотые' номера (только для админов)
        """
        sess = await self.sessions_repo.get(session_id)
        if not sess:
            raise ValueError("Сессия не найдена.")

        ttl = sess.ttl_seconds
        new_expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        await self.session.execute(update(Session).where(Session.id == session_id).values(expires_at=new_expires_at))

        newly_reserved: list[int] = []

        if requested_count:
            newly_reserved.extend(
                await self._reserve_for_session(
                    session_id=session_id,
                    user_id=user_id,
                    count=requested_count,
                    ttl_seconds=ttl,
                    is_admin=is_admin,
                )
            )

        if numbers:
            # продлеваем TTL уже зарезервированных в этой сессии
            await self.session.execute(
                update(DocNumber).where(DocNumber.session_id == session_id).values(expires_at=new_expires_at)
            )
            newly_reserved.extend(
                await self.numbers_repo.reserve_specific_numbers(numbers, user_id, session_id, ttl)
            )

        if golden_requested_count:
            # 'золотые' — только для админов
            if not is_admin:
                raise ValueError("Резерв 'золотых' номеров доступен только администраторам.")
            newly_reserved.extend(
                await self.reserve_golden_for_session(
                    session_id=session_id, user_id=user_id, count=golden_requested_count, ttl_seconds=ttl
                )
            )

        await self.session.commit()
        return sorted(newly_reserved)

    async def cancel_session(self, session_id: str) -> int:
        await self.sessions_repo.set_status(session_id, SessionStatus.cancelled)
        released = await self.numbers_repo.release_session(session_id)
        await self.session.commit()
        return released
        