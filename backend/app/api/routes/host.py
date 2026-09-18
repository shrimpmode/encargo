from fastapi import APIRouter

from app.api.deps import DbSession
from app.models import WaitlistEntry
from app.repositories.waitlist_repository import WaitlistRepository
from app.schemas import WaitlistEntryResponse
from app.services.waitlist_service import WaitlistService

router = APIRouter(prefix="/restaurants", tags=["host"])


def get_service(db: DbSession) -> WaitlistService:
    return WaitlistService(WaitlistRepository(db))


@router.get("/{restaurant_id}/waitlist", response_model=list[WaitlistEntryResponse])
async def list_waitlist(restaurant_id: int, db: DbSession) -> list[WaitlistEntry]:
    return await get_service(db).list_waiting(restaurant_id)


@router.post("/{restaurant_id}/waitlist/{entry_id}/call", status_code=200)
async def call_entry(restaurant_id: int, entry_id: int, db: DbSession) -> dict[str, str]:
    await get_service(db).call(restaurant_id, entry_id)
    return {"status": "called"}
