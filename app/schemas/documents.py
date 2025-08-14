from __future__ import annotations

from pydantic import BaseModel, Field
from datetime import datetime


class DocumentAssignOne(BaseModel):
    session_id: str
    doc_name: str = Field(min_length=1)
    note: str = Field(min_length=1)


class DocumentOut(BaseModel):
    id: int
    numeric: int
    formatted_no: str
    reg_date: datetime
    doc_name: str
    note: str
    equipment_id: int
    user_id: int

    class Config:
        from_attributes = True
