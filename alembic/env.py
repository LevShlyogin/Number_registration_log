from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

from app.core.config import settings
from app.models.base import Base
from app.models import user, equipment, counter, session, doc_number, document, audit

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- Устанавливаем URL базы данных ---
# Эта секция теперь устойчива и к тестам, и к обычному запуску.
if not config.get_main_option("sqlalchemy.url"):
    # Если URL не установлен извне (например, из нашего теста),
    # конструируем его из настроек приложения.
    if settings.database_url:
        # Alembic для синхронных команд требует синхронный драйвер.
        # Мы заменяем asyncpg на psycopg2 (или просто postgresql).
        sync_url = settings.database_url.replace("postgresql+asyncpg", "postgresql+psycopg2")
        config.set_main_option("sqlalchemy.url", sync_url)


target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Запуск миграций в 'offline' режиме."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Запуск миграций в 'online' режиме. Теперь этот блок полностью синхронный."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()