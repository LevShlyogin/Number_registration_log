from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.counter import CounterRepository
from app.repositories.doc_numbers import DocNumbersRepository
from app.utils.numbering import is_golden


class AdminService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.counter_repo = CounterRepository(session)
        self.numbers_repo = DocNumbersRepository(session)

    async def suggest_golden(self, limit: int = 10) -> list[int]:
        counter = await self.counter_repo.get_for_update()
        base = counter.base_start
        start = ((max(counter.next_normal_start, base) + 99) // 100) * 100  # ближайший кратный 100
        # соберем кандидатов, исключив занятые/зарезервированные
        # т.к. doc_numbers хранит только появлявшиеся номера, то "отсутствующий" — свободен
        # соберем из уже существующих released и несуществующие
        existing_reserved_or_assigned = set()
        from sqlalchemy import select
        from app.models.doc_number import DocNumber, DocNumStatus

        res = await self.session.execute(
            select(DocNumber.numeric, DocNumber.status)
            .where(DocNumber.numeric >= base, DocNumber.is_golden.is_(True))
        )
        for numeric, status in res.fetchall():
            if status in (DocNumStatus.assigned, DocNumStatus.reserved):
                existing_reserved_or_assigned.add(numeric)

        candidates = []
        cur = start
        while len(candidates) < limit:
            if is_golden(cur) and cur not in existing_reserved_or_assigned:
                candidates.append(cur)
            cur += 100
        return candidates
