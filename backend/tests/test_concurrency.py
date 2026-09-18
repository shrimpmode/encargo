import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.repositories.waitlist_repository import WaitlistRepository


async def test_concurrent_call_only_one_succeeds(
    session_factory: async_sessionmaker[AsyncSession], restaurant_id: int
) -> None:
    async with session_factory() as session:
        entry = await WaitlistRepository(session).create_entry(
            restaurant_id, "Carla", "+51900000001", 4
        )

    async def attempt_call() -> bool:
        async with session_factory() as session:
            return await WaitlistRepository(session).call_entry(restaurant_id, entry.id)

    results = await asyncio.gather(attempt_call(), attempt_call())

    assert sorted(results) == [False, True]
