from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import lifespan_session
from app.services.users import UsersService
from app.core.config import settings


class CurrentUser(BaseModel):
    id: int
    username: str
    is_admin: bool


async def get_current_user(
    x_user: str | None = Header(default=None, alias="X-User"),
    session: AsyncSession = Depends(lifespan_session),
) -> CurrentUser:
    if not x_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется заголовок X-User (Имя пользователя в системе).",
        )
    svc = UsersService(session)
    user = await svc.get_or_create_by_username(x_user)
    return CurrentUser(id=user.id, username=user.username, is_admin=user.username in settings.admin_users)
