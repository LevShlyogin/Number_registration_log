from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import func, DateTime


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
