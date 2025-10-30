from fastapi import APIRouter, Depends
from app.core.auth import get_current_user, CurrentUser

router = APIRouter()


@router.get("/me", response_model=CurrentUser)
async def read_users_me(current_user: CurrentUser = Depends(get_current_user)):
    """Получение данных о текущем пользователе."""
    return current_user
