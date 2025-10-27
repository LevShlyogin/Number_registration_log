from __future__ import annotations

from pydantic import BaseModel, Field
import re 
from pydantic import BaseModel, Field, field_validator


class EquipmentCreate(BaseModel):
    eq_type: str = Field(min_length=1)
    factory_no: str | None = None
    order_no: str | None = None
    label: str | None = None
    station_no: str | None = None
    station_object: str | None = None
    notes: str | None = None

    @field_validator("factory_no")
    @classmethod
    def validate_factory_no(cls, v: str | None) -> str | None:
        """Проверка: не более 5 символов и только цифры."""
        if v is None:
            return v  # Пропускаем, если значение не передано
        if not v.isdigit():
            raise ValueError("Заводской номер должен содержать только цифры")
        if len(v) > 5:
            raise ValueError("Длина заводского номера не может превышать 5 символов")
        return v

    @field_validator("order_no")
    @classmethod
    def validate_order_no(cls, v: str | None) -> str | None:
        """Проверка: шаблон 5 цифр - 2 цифры - 5 цифр."""
        if v is None:
            return v  # Пропускаем, если значение не передано
        if not re.match(r"^\d{5}-\d{2}-\d{5}$", v):
            raise ValueError("Номер заказа должен соответствовать шаблону XXXXX-XX-XXXXX")
        return v
    
    @field_validator("station_no")
    @classmethod
    def validate_station_no(cls, v: str | None) -> str | None:
        """Проверка: не более 2 символов и только цифры."""
        if v is None:
            return v  # Пропускаем, если значение не передано
        if not v.isdigit():
            raise ValueError("Станционный номер должен содержать только цифры")
        if len(v) > 2:
            raise ValueError("Длина станционного номера не может превышать 2 символов")
        return v


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
