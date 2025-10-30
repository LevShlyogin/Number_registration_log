from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import lifespan_session
from app.services.users import UsersService


class CurrentUser(BaseModel):
    id: int
    username: str
    is_admin: bool


async def get_current_user(
        x_user: str | None = Header(default=None, alias="X-User"),
        session: AsyncSession = Depends(lifespan_session),
) -> CurrentUser:
    """
    ВРЕМЕННАЯ ЗАГЛУШКА ДЛЯ РАЗРАБОТКИ.
    Всегда возвращает пользователя 'dev_user' с правами администратора.
    """
    dev_username = "dev_user"
    svc = UsersService(session)
    user = await svc.get_or_create_by_username(dev_username)

    return CurrentUser(id=user.id, username=user.username, is_admin=True)

async def get_current_admin_user(
    current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """
    Получает текущего пользователя и проверяет, является ли он администратором.
    Если пользователь не администратор, выбрасывает исключение HTTPException 403.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для выполнения этого действия.",
        )
    return current_user