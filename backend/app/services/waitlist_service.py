from dataclasses import dataclass

from app.models import WaitlistEntry, WaitlistState
from app.repositories.waitlist_repository import WaitlistRepository


class WaitlistEntryNotFoundError(Exception):
    def __init__(self, token: str) -> None:
        self.token = token


class WaitlistCallConflictError(Exception):
    def __init__(self, restaurant_id: int, entry_id: int) -> None:
        self.restaurant_id = restaurant_id
        self.entry_id = entry_id


@dataclass
class WaitlistStatus:
    state: WaitlistState
    position: int | None


class WaitlistService:
    def __init__(self, repo: WaitlistRepository) -> None:
        self._repo = repo

    async def join(
        self, restaurant_id: int, name: str, phone: str, party_size: int
    ) -> WaitlistEntry:
        return await self._repo.create_entry(restaurant_id, name, phone, party_size)

    async def get_status(self, token: str) -> WaitlistStatus:
        entry = await self._repo.get_by_token(token)
        if entry is None:
            raise WaitlistEntryNotFoundError(token)

        if entry.state != WaitlistState.WAITING:
            return WaitlistStatus(state=entry.state, position=None)

        waiting = await self._repo.list_waiting(entry.restaurant_id)
        position = next(i + 1 for i, e in enumerate(waiting) if e.id == entry.id)
        return WaitlistStatus(state=entry.state, position=position)

    async def list_waiting(self, restaurant_id: int) -> list[WaitlistEntry]:
        return await self._repo.list_waiting(restaurant_id)

    async def call(self, restaurant_id: int, entry_id: int) -> None:
        updated = await self._repo.call_entry(restaurant_id, entry_id)
        if not updated:
            raise WaitlistCallConflictError(restaurant_id, entry_id)
