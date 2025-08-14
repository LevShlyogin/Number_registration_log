from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UsersRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_username(self, username: str) -> User | None:
        res = await self.session.execute(select(User).where(User.username == username))
        return res.scalars().first()

    async def create(self, username: str) -> User:
        user = User(username=username)
        self.session.add(user)
        await self.session.flush()
        return user
