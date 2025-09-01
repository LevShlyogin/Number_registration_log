from __future__ import annotations
from pydantic import BaseModel, Field

class AdminReserveSpecific(BaseModel):
    equipment_id: int
    numbers: list[int] = Field(min_length=1)

class GoldenSuggestOut(BaseModel):
    golden_numbers: list[int]

#Схема для редактирования документа и оборудования
class AdminDocumentUpdate(BaseModel):
    # Поля из Document
    doc_name: str | None = None
    note: str | None = None
    
    # Поля из Equipment
    eq_type: str | None = None
    station_object: str | None = None
    station_no: str | None = None
    factory_no: str | None = None
    order_no: str | None = None
    label: str | None = None

    class Config:
        from_attributes = True
