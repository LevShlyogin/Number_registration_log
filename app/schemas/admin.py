from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import datetime


class AdminReserveSpecific(BaseModel):
    equipment_id: int
    numbers: list[int] = Field(min_length=1)


class GoldenSuggestOut(BaseModel):
    golden_numbers: list[int]


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


class AdminDocumentRow(BaseModel):
    """
    Схема для одной строки в ответе для админской панели.
    Объединяет данные из нескольких таблиц.
    """
    id: int  # ID из таблицы Document
    doc_no: str  # Отформатированный номер
    reg_date: datetime | str  # Дата регистрации
    doc_name: str
    note: str | None

    # Данные связанного оборудования
    eq_id: int  # ID из таблицы Equipment
    eq_type: str
    factory_no: str | None
    order_no: str | None
    label: str | None
    station_no: str | None
    station_object: str | None

    username: str

    class Config:
        from_attributes = True
