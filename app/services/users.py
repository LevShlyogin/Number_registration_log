from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.users import UsersRepository
from app.models.user import User


class UsersService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = UsersRepository(session)

    async def get_or_create_by_username(self, username: str) -> User:
        user = await self.repo.get_by_username(username)
        if not user:
            user = await self.repo.create(username)
            await self.session.commit()
        return user
