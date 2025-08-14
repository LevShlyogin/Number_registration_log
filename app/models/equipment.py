from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from app.models.base import Base, TimestampMixin


class Equipment(Base, TimestampMixin):
    __tablename__ = "equipment"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    eq_type: Mapped[str] = mapped_column(String(200), nullable=False)
    factory_no: Mapped[str | None] = mapped_column(String(200))
    order_no: Mapped[str | None] = mapped_column(String(200))
    label: Mapped[str | None] = mapped_column(String(200))
    station_no: Mapped[str | None] = mapped_column(String(200))
    station_object: Mapped[str | None] = mapped_column(String(200))
    notes: Mapped[str | None] = mapped_column(String(500))
