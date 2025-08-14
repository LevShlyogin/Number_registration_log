from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, DateTime, func, Integer, Enum
import enum
import uuid

from app.models.base import Base


class SessionStatus(str, enum.Enum):
    active = "active"
    cancelled = "cancelled"
    completed = "completed"
    expired = "expired"


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id", ondelete="RESTRICT"), nullable=False)
    requested_count: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[SessionStatus] = mapped_column(Enum(SessionStatus, name="session_status"), default=SessionStatus.active)
    ttl_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), nullable=False)
