from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB

from app.models.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    doc_number: Mapped[int]
    changed_at: Mapped["DateTime"] = mapped_column(DateTime(timezone=True), server_default=func.now())
    username: Mapped[str]
    diff: Mapped[dict] = mapped_column(JSONB)
