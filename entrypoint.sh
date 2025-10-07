#!/bin/sh

set -e

. /app/.venv/bin/activate

echo "Waiting for PostgreSQL to be ready..."
until PGPASSWORD=$POSTGRESS_PASSWORD psql -h "$POSTGRES_SERVER" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done
>&2 echo "PostgreSQL is up - proceeding."


# --- Применение миграций Alembic ---
echo "Applying Alembic migrations..."
alembic upgrade head
echo "Alembic migrations applied."


# --- Запуск FastAPI приложения ---
echo "Starting Uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload