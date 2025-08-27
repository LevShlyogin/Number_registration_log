from __future__ import annotations
# ### ДОБАВЛЕНО ###
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import CITEXT
from app.models.base import Base, TimestampMixin

# ### ДОБАВЛЕНО ###
# Импортируем Document для type hinting в relationship
from app.models.document import Document

class Equipment(Base, TimestampMixin):
    __tablename__ = "equipment"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    eq_type: Mapped[str] = mapped_column(String(200), nullable=False)
    factory_no: Mapped[str | None] = mapped_column(CITEXT)
    order_no: Mapped[str | None] = mapped_column(CITEXT)
    label: Mapped[str | None] = mapped_column(CITEXT)
    station_no: Mapped[str | None] = mapped_column(CITEXT)
    station_object: Mapped[str | None] = mapped_column(CITEXT)
    notes: Mapped[str | None] = mapped_column(String(500))

    #Обратная связь с документами
    documents: Mapped[list["Document"]] = relationship(back_populates="equipment")
