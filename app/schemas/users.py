from pydantic import BaseModel, ConfigDict


class UserInResponse(BaseModel):
    """
    Схема для представления данных пользователя в ответах API.
    Содержит только публичную информацию.
    """
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)