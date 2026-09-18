from collections.abc import AsyncIterator
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.db import Base
from app.models import Restaurant


@pytest_asyncio.fixture
async def engine(tmp_path: Path) -> AsyncIterator[AsyncEngine]:
    db_path = tmp_path / "test.db"
    eng = create_async_engine(f"sqlite+aiosqlite:///{db_path}")
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest.fixture
def session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest_asyncio.fixture
async def restaurant_id(session_factory: async_sessionmaker[AsyncSession]) -> int:
    async with session_factory() as session:
        restaurant = Restaurant(name="Test Restaurant")
        session.add(restaurant)
        await session.commit()
        await session.refresh(restaurant)
        return restaurant.id


@pytest_asyncio.fixture
async def other_restaurant_id(session_factory: async_sessionmaker[AsyncSession]) -> int:
    async with session_factory() as session:
        restaurant = Restaurant(name="Other Restaurant")
        session.add(restaurant)
        await session.commit()
        await session.refresh(restaurant)
        return restaurant.id
