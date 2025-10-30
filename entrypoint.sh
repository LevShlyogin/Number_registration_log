#!/bin/sh
set -e

echo "Waiting for PostgreSQL to be ready..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_SERVER" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done
>&2 echo "PostgreSQL is up - proceeding."

# --- Alembic migrations ---
echo "Applying Alembic migrations..."
/app/.venv/bin/alembic upgrade head
echo "Alembic migrations applied."

# --- Start FastAPI ---
echo "Starting Uvicorn server..."
exec /app/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
