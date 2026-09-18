from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import WaitlistEntry, WaitlistState


class WaitlistRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create_entry(
        self, restaurant_id: int, name: str, phone: str, party_size: int
    ) -> WaitlistEntry:
        entry = WaitlistEntry(
            restaurant_id=restaurant_id,
            name=name,
            phone=phone,
            party_size=party_size,
        )
        self._db.add(entry)
        await self._db.commit()
        await self._db.refresh(entry)
        return entry

    async def get_by_token(self, status_token: str) -> WaitlistEntry | None:
        entry: WaitlistEntry | None = await self._db.scalar(
            select(WaitlistEntry).where(WaitlistEntry.status_token == status_token)
        )
        return entry

    async def list_waiting(self, restaurant_id: int) -> list[WaitlistEntry]:
        result = await self._db.scalars(
            select(WaitlistEntry)
            .where(
                WaitlistEntry.restaurant_id == restaurant_id,
                WaitlistEntry.state == WaitlistState.WAITING,
            )
            .order_by(WaitlistEntry.joined_at, WaitlistEntry.id)
        )
        return list(result.all())
