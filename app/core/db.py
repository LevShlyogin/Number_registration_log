from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine: AsyncEngine = create_async_engine(settings.database_url, future=True, pool_pre_ping=True)
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False, autocommit=False)

async def lifespan_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session