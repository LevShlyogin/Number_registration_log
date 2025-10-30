from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, UniqueConstraint
from sqlalchemy.dialects.postgresql import CITEXT
from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.document import Document


class Equipment(Base, TimestampMixin):
    __tablename__ = "equipment"
    __table_args__ = (
        UniqueConstraint('factory_no', name='uq_equipment_factory_no'),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    eq_type: Mapped[str] = mapped_column(String(200), nullable=False)
    factory_no: Mapped[str | None] = mapped_column(CITEXT, unique=True, index=True)
    order_no: Mapped[str | None] = mapped_column(CITEXT)
    label: Mapped[str | None] = mapped_column(CITEXT)
    station_no: Mapped[str | None] = mapped_column(CITEXT)
    station_object: Mapped[str | None] = mapped_column(CITEXT)
    notes: Mapped[str | None] = mapped_column(String(500))

    # Используем строковую ссылку на модель вместо прямого импорта
    documents: Mapped[list["Document"]] = relationship("Document", back_populates="equipment")
