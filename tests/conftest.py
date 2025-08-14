import asyncio
import os
import pytest
from httpx import AsyncClient

from app.main import app
from app.core.db import SessionLocal, engine
from alembic.config import Config
from alembic import command


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    # запустить миграции на тестовой БД
    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")
    yield
    command.downgrade(cfg, "base")


@pytest.fixture
async def client():
    headers = {"X-User": "test_user"}
    async with AsyncClient(app=app, base_url="http://test", headers=headers) as c:
        yield c