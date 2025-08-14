from __future__ import annotations

from pydantic import BaseModel, Field


class EquipmentCreate(BaseModel):
    eq_type: str = Field(min_length=1)
    factory_no: str | None = None
    order_no: str | None = None
    label: str | None = None
    station_no: str | None = None
    station_object: str | None = None
    notes: str | None = None


class EquipmentOut(BaseModel):
    id: int
    eq_type: str
    factory_no: str | None
    order_no: str | None
    label: str | None
    station_no: str | None
    station_object: str | None
    notes: str | None

    class Config:
        from_attributes = True
