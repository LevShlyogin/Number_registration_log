import asyncio
from typing import AsyncGenerator, Generator
from fastapi import Header
from sqlalchemy import select

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from testcontainers.postgres import PostgresContainer
from alembic.config import Config
from alembic import command

from app.core.auth import get_current_user, CurrentUser
from app.core.db import lifespan_session
from app.main import app
from app.models.user import User
from app.models.equipment import Equipment

@pytest.fixture(scope="session", autouse=True)
def test_db_url() -> Generator[str, None, None]:
    with PostgresContainer("postgres:15") as postgres:
        sync_db_url = postgres.get_connection_url()
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", sync_db_url)
        command.upgrade(alembic_cfg, "head")
        yield sync_db_url.replace("postgresql+psycopg2", "postgresql+asyncpg")

@pytest.fixture(scope="session")
def default_admin_headers() -> dict[str, str]:
    return {"X-Test-User": "test_admin"}

@pytest.fixture(scope="session")
def default_user_headers() -> dict[str, str]:
    return {"X-Test-User": "test_user"}

@pytest_asyncio.fixture(scope="session")
async def default_equipment(test_db_url: str) -> Equipment:
    """Создает один объект оборудования напрямую в БД для всей сессии."""
    engine = create_async_engine(test_db_url)
    Session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    
    async with Session() as session:
        async with session.begin():
            eq = Equipment(eq_type="Session-Scoped Switch", factory_no="99999")
            session.add(eq)
            await session.flush()
            equipment_data = {
                "id": eq.id,
                "eq_type": eq.eq_type,
                "factory_no": eq.factory_no
            }

        await session.commit()

    await engine.dispose()
    
    class TempEq:
        def __init__(self, data):
            self.id = data["id"]
            self.eq_type = data["eq_type"]
            self.factory_no = data["factory_no"]

    return TempEq(equipment_data)

@pytest_asyncio.fixture
async def db_session(test_db_url: str) -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(test_db_url)
    TestSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    async with TestSessionLocal() as session:
        await session.begin()
        yield session
        await session.rollback()
    await engine.dispose()

@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_current_user(x_test_user: str | None = Header(default=None, alias="X-Test-User")) -> CurrentUser:
        if not x_test_user:
            username = "test_admin"
            is_admin = True
        else:
            username = x_test_user
            is_admin = "admin" in username
        
        user_in_db = (await db_session.execute(select(User).where(User.username == username))).scalars().first()
        if not user_in_db:
            user_in_db = User(username=username)
            db_session.add(user_in_db)
            await db_session.flush()
        return CurrentUser(id=user_in_db.id, username=username, is_admin=is_admin)

    def override_lifespan_session() -> Generator[AsyncSession, None, None]:
        yield db_session

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[lifespan_session] = override_lifespan_session
    
    base_url = "http://test/api/v1"
    async with AsyncClient(app=app, base_url=base_url) as ac:
        yield ac
        
    app.dependency_overrides.clear()