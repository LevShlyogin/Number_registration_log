from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.doc_number import DocNumber
from app.repositories.sessions import SessionsRepository
from app.repositories.doc_numbers import DocNumbersRepository
from app.repositories.counter import CounterRepository
from app.models.session import SessionStatus, Session

from app.utils.numbering import is_golden

MAX_DOCUMENT_NUMBER = 999999

class ReservationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.sessions_repo = SessionsRepository(session)
        self.numbers_repo = DocNumbersRepository(session)
        self.counter_repo = CounterRepository(session)

    async def reserve_golden_numbers(
        self, *, user_id: int, equipment_id: int, quantity: int, ttl_seconds: int
    ) -> tuple[str, list[int]]:
        """
        Находит и резервирует указанное количество свободных 'золотых' номеров,
        учитывая максимальный предел.
        """
        counter = await self.counter_repo.get_for_update()
        
        # 1. Определяем, откуда начинать поиск
        search_start = max(counter.base_start, counter.next_normal_start)
        
        # Находим первого 'золотого' кандидата после точки старта
        current_candidate = (search_start + 99) // 100 * 100
        if current_candidate < search_start:
            current_candidate += 100
        
        found_numbers = []
        batch_size = quantity * 2
        
        # 2. Ищем свободные номера пачками, пока не наберем достаточно или не достигнем предела
        while len(found_numbers) < quantity and current_candidate <= MAX_DOCUMENT_NUMBER:
            candidates_batch = []
            batch_end = current_candidate + (batch_size * 100)
            
            temp_candidate = current_candidate
            while temp_candidate < batch_end and len(candidates_batch) < batch_size:
                if temp_candidate > MAX_DOCUMENT_NUMBER:
                    break
                candidates_batch.append(temp_candidate)
                temp_candidate += 100
            
            if not candidates_batch:
                break

            existing_in_batch = await self.numbers_repo.find_existing_from_list(candidates_batch)
            
            for num in candidates_batch:
                if num not in existing_in_batch:
                    found_numbers.append(num)
                    if len(found_numbers) == quantity:
                        break
            
            current_candidate = candidates_batch[-1] + 100
            if len(found_numbers) == quantity:
                break

        # 3. Теперь проверка на нехватку будет работать корректно
        if len(found_numbers) < quantity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Не удалось найти {quantity} свободных золотых номеров. Найдено только {len(found_numbers)}."
            )
        
        # 4. Резервируем найденные номера
        numbers_to_reserve = found_numbers[:quantity]
        return await self.admin_reserve_specific(
            user_id=user_id,
            equipment_id=equipment_id,
            numbers=numbers_to_reserve,
            ttl_seconds=ttl_seconds
        )

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

    async def admin_reserve_specific(self, *, user_id: int, equipment_id: int, numbers: list[int], ttl_seconds: int) -> \
            tuple[str, list[int]]:
        sess = await self.sessions_repo.create(
            user_id=user_id, equipment_id=equipment_id, requested_count=len(numbers), ttl_seconds=ttl_seconds
        )
        reserved = await self.numbers_repo.reserve_specific_numbers(numbers, user_id, sess.id, ttl_seconds)
        if not reserved:
            await self.session.rollback()
            raise ValueError("Не удалось зарезервировать ни один из указанных номеров (возможно, они уже заняты).")
        await self.session.commit()
        return sess.id, reserved

    async def add_numbers_to_session(self, *, session_id: str, user_id: int, requested_count: int | None,
                                     numbers: list[int] | None, is_admin: bool) -> list[int]:
        sess = await self.sessions_repo.get(session_id)
        if not sess:
            raise ValueError("Сессия не найдена.")

        ttl = sess.ttl_seconds
        new_expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        await self.session.execute(update(Session).where(Session.id == session_id).values(expires_at=new_expires_at))

        newly_reserved = []
        if requested_count:  # Добавляем обычные номера
            newly_reserved = await self._reserve_for_session(
                session_id=session_id, user_id=user_id, count=requested_count, ttl_seconds=ttl, is_admin=is_admin
            )
        elif numbers:
            await self.session.execute(
                update(DocNumber).where(DocNumber.session_id == session_id).values(expires_at=new_expires_at))
            newly_reserved = await self.numbers_repo.reserve_specific_numbers(numbers, user_id, session_id, ttl)

        await self.session.commit()
        return newly_reserved

    async def cancel_session(self, session_id: str) -> int:
        await self.sessions_repo.set_status(session_id, SessionStatus.cancelled)
        released = await self.numbers_repo.release_session(session_id)
        await self.session.commit()
        return released
