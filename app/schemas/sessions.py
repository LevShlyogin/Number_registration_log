from __future__ import annotations

from pydantic import BaseModel, Field
from datetime import datetime


class SessionStart(BaseModel):
    equipment_id: int
    requested_count: int = Field(1, ge=1, le=1000)
    ttl_seconds: int | None = None


class SessionOut(BaseModel):
    id: str
    user_id: int
    equipment_id: int
    requested_count: int
    status: str
    ttl_seconds: int
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True


class ReserveResult(BaseModel):
    session_id: str
    reserved_numbers: list[int]


class AddNumbers(BaseModel):
    requested_count: int | None = None
    numbers: list[int] | None = None
