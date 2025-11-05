"""ensure unique factory_no idempotent

Revision ID: 156932104802
Revises: 55344096801e
Create Date: 2025-11-05 12:39:43.506410
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '156932104802'
down_revision = '55344096801e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
