"""Add equipment uniqueness constraint

Revision ID: 0002
Revises: 0001
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создаем уникальный индекс на комбинацию полей оборудования
    # Используем LOWER и COALESCE для регистронезависимого сравнения
    op.execute("""
        CREATE UNIQUE INDEX ix_equipment_unique_attributes 
        ON equipment (
            LOWER(COALESCE(station_object, '')), 
            LOWER(COALESCE(station_no, '')), 
            LOWER(COALESCE(label, '')), 
            LOWER(COALESCE(factory_no, ''))
        )
        WHERE station_object IS NOT NULL 
           OR station_no IS NOT NULL 
           OR label IS NOT NULL 
           OR factory_no IS NOT NULL
    """)


def downgrade() -> None:
    op.drop_index('ix_equipment_unique_attributes', table_name='equipment')
