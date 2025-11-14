"""Replace unique constraint with index for document uniqueness

Revision ID: 13c426e84b5f
Revises: 156932104802
Create Date: 2025-11-12 19:50:02.110517
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '13c426e84b5f'
down_revision = '156932104802'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Удаляем старый unique по doc_name/note/equipment_id
    op.drop_constraint(op.f('uq_documents_name_note_equipment'), 'documents', type_='unique')

    # Создаём уникальный индекс на (doc_name, equipment_id, coalesce(note,''))
    op.create_index(
        'ix_documents_unique_name_note_equipment',
        'documents',
        ['doc_name', 'equipment_id', sa.literal_column("coalesce(note, '')")],
        unique=True,
    )

    # Убедимся, что уникальность factory_no обеспечена ИНДЕКСОМ, а не отдельным констрейнтом.
    # Идём аккуратно:
    # 1) Если уже есть constraint uq_equipment_factory_no – оставляем его, просто не создаём ничего.
    # 2) Если его нет – создаём индекс (если его тоже нет).
    conn = op.get_bind()

    # Проверка наличия констрейнта
    constraint_exists = conn.execute(
        sa.text("""
            SELECT 1
            FROM pg_constraint
            WHERE conname = 'uq_equipment_factory_no'
        """)
    ).scalar() is not None

    # Проверка наличия индекса
    index_exists = conn.execute(
        sa.text("""
            SELECT 1
            FROM pg_indexes
            WHERE tablename = 'equipment' AND indexname = 'ix_equipment_factory_no'
        """)
    ).scalar() is not None

    # Если нет ни constraint, ни индекса – создаём индекс
    if not constraint_exists and not index_exists:
        op.create_index(
            'ix_equipment_factory_no',
            'equipment',
            ['factory_no'],
            unique=True,
        )

    # НИЧЕГО не создаём с именем uq_equipment_factory_no – он уже существует в БД

def downgrade() -> None:
    conn = op.get_bind()

    # Пытаемся удалить индекс, только если он действительно есть
    index_exists = conn.execute(
        sa.text("""
            SELECT 1
            FROM pg_indexes
            WHERE tablename = 'equipment' AND indexname = 'ix_equipment_factory_no'
        """)
    ).scalar() is not None

    if index_exists:
        op.drop_index('ix_equipment_factory_no', table_name='equipment')

    # Констрейнт uq_equipment_factory_no – трогать НЕ обязательно, если он создаётся в 156932...
    # Но если в autogenerate он появлялся – можно также защититься:
    constraint_exists = conn.execute(
        sa.text("""
            SELECT 1 FROM pg_constraint WHERE conname = 'uq_equipment_factory_no'
        """)
    ).scalar() is not None

    if constraint_exists:
        op.drop_constraint('uq_equipment_factory_no', 'equipment', type_='unique')

    op.drop_index('ix_documents_unique_name_note_equipment', table_name='documents')
    op.create_unique_constraint(
        op.f('uq_documents_name_note_equipment'),
        'documents',
        ['doc_name', 'note', 'equipment_id'],
        postgresql_nulls_not_distinct=False,
    )