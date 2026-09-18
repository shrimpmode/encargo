from sqlalchemy.ext.asyncio import AsyncSession

from app.models import WaitlistEntry


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
