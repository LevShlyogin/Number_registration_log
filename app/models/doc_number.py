from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, ForeignKey, DateTime, func, Enum, Boolean
import enum

from app.models.base import Base


class DocNumStatus(str, enum.Enum):
    reserved = "reserved"
    assigned = "assigned"
    released = "released"


class DocNumber(Base):
    __tablename__ = "doc_numbers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    numeric: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    is_golden: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[DocNumStatus] = mapped_column(Enum(DocNumStatus, name="docnum_status"), nullable=False)
    reserved_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    session_id: Mapped[str | None] = mapped_column(ForeignKey("sessions.id", ondelete="SET NULL"))
    reserved_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
    assigned_at: Mapped["DateTime | None"] = mapped_column(DateTime(timezone=True), nullable=True)
    released_at: Mapped["DateTime | None"] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped["DateTime | None"] = mapped_column(DateTime(timezone=True), nullable=True)
