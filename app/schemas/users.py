from pydantic import BaseModel


class UserInResponse(BaseModel):
    """
    Схема для представления данных пользователя в ответах API.
    Содержит только публичную информацию.
    """
    id: int
    username: str

    class Config:
        from_attributes = True
