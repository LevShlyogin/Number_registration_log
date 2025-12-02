from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import lifespan_session
from app.services.users import UsersService

# Указываем URL логина (для Swagger UI)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8001/auth/login")


class CurrentUser(BaseModel):
    id: int
    username: str
    is_admin: bool


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        session: AsyncSession = Depends(lifespan_session),
) -> CurrentUser:
    """
    Проверяет JWT токен, извлекает username и находит пользователя в БД.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    svc = UsersService(session)
    user = await svc.get_or_create_by_username(username)

    is_admin = user.username.lower() in [u.lower() for u in settings.admin_users]

    return CurrentUser(id=user.id, username=user.username, is_admin=is_admin)


async def get_current_admin_user(
        current_user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для выполнения этого действия.",
        )
    return current_user