from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import get_current_user, CurrentUser

router = APIRouter()


@router.get("/check-access", response_model=dict)
async def check_access(
        user: CurrentUser = Depends(get_current_user),
):
    """Проверка, является ли текущий пользователь администратором."""
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещен")
    return {"is_admin": True}
