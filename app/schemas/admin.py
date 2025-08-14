from __future__ import annotations

from pydantic import BaseModel, Field


class AdminReserveSpecific(BaseModel):
    equipment_id: int
    numbers: list[int] = Field(min_length=1)


class GoldenSuggestOut(BaseModel):
    golden_numbers: list[int]
