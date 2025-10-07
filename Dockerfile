FROM python:3.13-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app

# Копируем файлы зависимостей
COPY ./pyproject.toml ./uv.lock* /app/

RUN uv venv && uv pip install --upgrade pip && uv sync --no-dev

COPY ./app /app/app

# Копируем 'alembic.ini' и папку 'alembic/' в рабочую директорию '/app'
COPY ./alembic.ini /app/alembic.ini
COPY ./alembic /app/alembic

# Копируем скрипт запуска
COPY ./entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]