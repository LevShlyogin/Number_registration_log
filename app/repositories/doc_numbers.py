from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.doc_number import DocNumber, DocNumStatus


class DocNumbersRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def release_expired(self, now: datetime | None = None) -> int:
        now = now or datetime.utcnow()
        res = await self.session.execute(
            update(DocNumber)
            .where(and_(DocNumber.status == DocNumStatus.reserved, DocNumber.expires_at < now))
            .values(status=DocNumStatus.released, released_at=now, expires_at=None, reserved_by=None, session_id=None)
            .returning(DocNumber.id)
        )
        return len(res.fetchall())

    async def fetch_released_for_update(self, base_start: int, limit: int, skip_golden: bool = True) -> list[DocNumber]:
        stmt = (
            select(DocNumber)
            .where(DocNumber.status == DocNumStatus.released, DocNumber.numeric >= base_start)
            .order_by(DocNumber.numeric.asc())
            .with_for_update(skip_locked=True)
            .limit(limit * 2)
        )
        res = await self.session.execute(stmt)
        nums = res.scalars().all()
        if skip_golden:
            nums = [n for n in nums if n.numeric % 100 != 0]
        return nums[:limit]

    async def reserve_existing(self, numbers: list[DocNumber], user_id: int, session_id: str, ttl_seconds: int) -> list[int]:
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=ttl_seconds)
        reserved = []
        for row in numbers:
            await self.session.execute(
                update(DocNumber)
                .where(DocNumber.id == row.id)
                .values(
                    status=DocNumStatus.reserved,
                    reserved_by=user_id,
                    session_id=session_id,
                    reserved_at=now,
                    expires_at=expires_at,
                    released_at=None,
                )
            )
            reserved.append(row.numeric)
        return reserved

    async def create_and_reserve_new(self, candidates: list[int], user_id: int, session_id: str, ttl_seconds: int) -> list[int]:
        from sqlalchemy.exc import IntegrityError

        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=ttl_seconds)
        reserved = []
        for num in candidates:
            dn = DocNumber(
                numeric=num,
                is_golden=(num % 100 == 0),
                status=DocNumStatus.reserved,
                reserved_by=user_id,
                session_id=session_id,
                reserved_at=now,
                expires_at=expires_at,
            )
            self.session.add(dn)
            try:
                await self.session.flush()
            except IntegrityError:
                # кто-то успел занять параллельно — просто пропустим
                await self.session.rollback()
                # re-attach session: workaround to keep trans usable
                await self.session.begin()
                continue
            reserved.append(num)
        return reserved

    async def reserve_specific_numbers(self, numbers: list[int], user_id: int, session_id: str, ttl_seconds: int) -> list[int]:
        # резервирование конкретных номеров (для админа)
        now = datetime.utcnow()
        from sqlalchemy.exc import IntegrityError

        reserved: list[int] = []
        for num in numbers:
            # попробуем найти существующую запись
            res = await self.session.execute(select(DocNumber).where(DocNumber.numeric == num).with_for_update())
            row = res.scalars().first()
            if row:
                if row.status == DocNumStatus.assigned:
                    continue
                if row.status == DocNumStatus.reserved:
                    # пропускаем
                    continue
                if row.status == DocNumStatus.released:
                    row.status = DocNumStatus.reserved
                    row.reserved_by = user_id
                    row.session_id = session_id
                    row.reserved_at = now
                    row.expires_at = now + timedelta(seconds=ttl_seconds)
                    row.released_at = None
                    reserved.append(num)
            else:
                dn = DocNumber(
                    numeric=num,
                    is_golden=(num % 100 == 0),
                    status=DocNumStatus.reserved,
                    reserved_by=user_id,
                    session_id=session_id,
                    reserved_at=now,
                    expires_at=now + timedelta(seconds=ttl_seconds),
                )
                self.session.add(dn)
                try:
                    await self.session.flush()
                except IntegrityError:
                    await self.session.rollback()
                    await self.session.begin()
                    continue
                reserved.append(num)
        return reserved

    async def get_reserved_for_session(self, session_id: str) -> list[DocNumber]:
        res = await self.session.execute(
            select(DocNumber).where(DocNumber.session_id == session_id, DocNumber.status == DocNumStatus.reserved).order_by(DocNumber.numeric.asc())
        )
        return res.scalars().all()

    async def mark_assigned(self, numbers: list[int]) -> None:
        now = datetime.utcnow()
        await self.session.execute(
            update(DocNumber)
            .where(DocNumber.numeric.in_(numbers))
            .values(status=DocNumStatus.assigned, assigned_at=now, expires_at=None)
        )

    async def release_session(self, session_id: str) -> int:
        from sqlalchemy import update
        now = datetime.utcnow()
        res = await self.session.execute(
            update(DocNumber)
            .where(DocNumber.session_id == session_id, DocNumber.status == DocNumStatus.reserved)
            .values(
                status=DocNumStatus.released,
                released_at=now,
                reserved_by=None,
                session_id=None,
                expires_at=None,
            )
            .returning(DocNumber.id)
        )
        return len(res.fetchall())
