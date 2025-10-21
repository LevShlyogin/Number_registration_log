from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import CITEXT

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.equipment import Equipment


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (
        UniqueConstraint("doc_name", "note", "equipment_id", name="uq_documents_name_note_equipment"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    numeric: Mapped[int] = mapped_column(unique=True, nullable=False)
    reg_date: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
    doc_name: Mapped[str] = mapped_column(CITEXT, nullable=False)
    note: Mapped[str | None] = mapped_column(CITEXT, nullable=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id", ondelete="RESTRICT"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    equipment: Mapped["Equipment"] = relationship("Equipment", back_populates="documents", lazy="joined")
