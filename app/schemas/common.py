from __future__ import annotations

from pydantic import BaseModel, Field


class Message(BaseModel):
    message: str


class IDResponse(BaseModel):
    id: int | str


class Pagination(BaseModel):
    limit: int = Field(20, ge=1, le=500)
    offset: int = Field(0, ge=0)
