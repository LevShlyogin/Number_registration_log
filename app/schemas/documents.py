from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentAssignOne(BaseModel):
    """Схема для запроса на назначение номера."""
    session_id: str
    doc_name: str = Field(min_length=1)
    note: str | None = None
    numeric: int


class DocumentOut(BaseModel):
    """Базовая схема для представления документа."""
    id: int
    numeric: int
    formatted_no: str
    reg_date: datetime
    doc_name: str
    note: str | None
    equipment_id: int
    user_id: int

    class Config:
        from_attributes = True
