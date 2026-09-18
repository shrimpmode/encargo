from app.models import WaitlistEntry
from app.repositories.waitlist_repository import WaitlistRepository


class WaitlistService:
    def __init__(self, repo: WaitlistRepository) -> None:
        self._repo = repo

    async def join(
        self, restaurant_id: int, name: str, phone: str, party_size: int
    ) -> WaitlistEntry:
        return await self._repo.create_entry(restaurant_id, name, phone, party_size)
