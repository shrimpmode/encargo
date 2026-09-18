from fastapi import APIRouter

from app.api.deps import DbSession
from app.models import WaitlistEntry
from app.repositories.waitlist_repository import WaitlistRepository
from app.schemas import JoinRequest, JoinResponse
from app.services.waitlist_service import WaitlistService

router = APIRouter(prefix="/restaurants", tags=["guest"])


def get_service(db: DbSession) -> WaitlistService:
    return WaitlistService(WaitlistRepository(db))


@router.post("/{restaurant_id}/waitlist", response_model=JoinResponse, status_code=201)
async def join_waitlist(restaurant_id: int, body: JoinRequest, db: DbSession) -> WaitlistEntry:
    return await get_service(db).join(restaurant_id, body.name, body.phone, body.party_size)
