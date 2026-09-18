from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.models import WaitlistState
from app.repositories.waitlist_repository import WaitlistRepository


async def test_call_transitions_waiting_to_called(
    session_factory: async_sessionmaker[AsyncSession], restaurant_id: int
) -> None:
    async with session_factory() as session:
        entry = await WaitlistRepository(session).create_entry(
            restaurant_id, "Carla", "+51900000001", 4
        )

    async with session_factory() as session:
        updated = await WaitlistRepository(session).call_entry(restaurant_id, entry.id)
        assert updated is True

    async with session_factory() as session:
        fetched = await WaitlistRepository(session).get_by_token(entry.status_token)
        assert fetched is not None
        assert fetched.state == WaitlistState.CALLED
        assert fetched.called_at is not None


async def test_call_ignores_entry_from_a_different_restaurant(
    session_factory: async_sessionmaker[AsyncSession],
    restaurant_id: int,
    other_restaurant_id: int,
) -> None:
    async with session_factory() as session:
        entry = await WaitlistRepository(session).create_entry(
            restaurant_id, "Carla", "+51900000001", 4
        )

    async with session_factory() as session:
        updated = await WaitlistRepository(session).call_entry(other_restaurant_id, entry.id)
        assert updated is False

    async with session_factory() as session:
        fetched = await WaitlistRepository(session).get_by_token(entry.status_token)
        assert fetched is not None
        assert fetched.state == WaitlistState.WAITING
