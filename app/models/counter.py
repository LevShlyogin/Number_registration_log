from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import BigInteger, DateTime, func

from app.models.base import Base


class DocCounter(Base):
    __tablename__ = "doc_counter"

    id: Mapped[int] = mapped_column(primary_key=True)
    base_start: Mapped[int] = mapped_column(BigInteger, nullable=False, default=1)
    next_normal_start: Mapped[int] = mapped_column(BigInteger, nullable=False, default=1)
    updated_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
