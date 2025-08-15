"""init schema

Revision ID: 0001_init
Revises:
Create Date: 2025-08-14 00:00:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS citext;")

    # создаём типы ENUM один раз, безопасно (checkfirst)
    docnum_status = postgresql.ENUM("reserved", "assigned", "released", name="docnum_status")
    docnum_status.create(op.get_bind(), checkfirst=True)

    session_status = postgresql.ENUM("active", "cancelled", "completed", "expired", name="session_status")
    session_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", postgresql.CITEXT(), nullable=False, unique=True),
        sa.Column("last_name", sa.String(), nullable=True),
        sa.Column("first_name", sa.String(), nullable=True),
        sa.Column("middle_name", sa.String(), nullable=True),
        sa.Column("department", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "equipment",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("eq_type", sa.String(length=200), nullable=False),
        sa.Column("factory_no", sa.String(length=200), nullable=True),
        sa.Column("order_no", sa.String(length=200), nullable=True),
        sa.Column("label", sa.String(length=200), nullable=True),
        sa.Column("station_no", sa.String(length=200), nullable=True),
        sa.Column("station_object", sa.String(length=200), nullable=True),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "doc_counter",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("base_start", sa.BigInteger(), nullable=False, server_default="1"),
        sa.Column("next_normal_start", sa.BigInteger(), nullable=False, server_default="1"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "sessions",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("equipment_id", sa.Integer(), sa.ForeignKey("equipment.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("requested_count", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "active", "cancelled", "completed", "expired",
                name="session_status",
                create_type=False,  # не создавать тип заново
            ),
            nullable=False,
        ),
        sa.Column("ttl_seconds", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "doc_numbers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("numeric", sa.BigInteger(), nullable=False, unique=True),
        sa.Column("is_golden", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "status",
            postgresql.ENUM(
                "reserved", "assigned", "released",
                name="docnum_status",
                create_type=False,  # не создавать тип заново
            ),
            nullable=False,
        ),
        sa.Column("reserved_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("session_id", sa.String(), sa.ForeignKey("sessions.id", ondelete="SET NULL")),
        sa.Column("reserved_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("released_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("numeric", sa.BigInteger(), nullable=False, unique=True),
        sa.Column("reg_date", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("doc_name", postgresql.CITEXT(), nullable=False),
        sa.Column("note", postgresql.CITEXT(), nullable=False),
        sa.Column("equipment_id", sa.Integer(), sa.ForeignKey("equipment.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.UniqueConstraint("doc_name", "note", "equipment_id", name="uq_documents_name_note_equipment"),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("document_id", sa.Integer(), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("doc_number", sa.BigInteger(), nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("diff", postgresql.JSONB(), nullable=False),
    )

    # bootstrap single row for counter
    op.execute(
        "INSERT INTO doc_counter (id, base_start, next_normal_start) "
        "VALUES (1, 1, 1) ON CONFLICT (id) DO NOTHING;"
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("documents")
    op.drop_table("doc_numbers")
    op.drop_table("sessions")
    op.drop_table("doc_counter")
    op.drop_table("equipment")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS docnum_status;")
    op.execute("DROP TYPE IF EXISTS session_status;")
    op.execute("DROP EXTENSION IF EXISTS citext;")