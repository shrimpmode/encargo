from fastapi import APIRouter

from app.api.deps import DbSession
from app.models import WaitlistEntry
from app.repositories.waitlist_repository import WaitlistRepository
from app.schemas import JoinRequest, JoinResponse, StatusResponse
from app.services.waitlist_service import WaitlistService, WaitlistStatus

router = APIRouter(tags=["guest"])


def get_service(db: DbSession) -> WaitlistService:
    return WaitlistService(WaitlistRepository(db))


@router.post("/restaurants/{restaurant_id}/waitlist", response_model=JoinResponse, status_code=201)
async def join_waitlist(restaurant_id: int, body: JoinRequest, db: DbSession) -> WaitlistEntry:
    return await get_service(db).join(restaurant_id, body.name, body.phone, body.party_size)


@router.get("/waitlist/status/{token}", response_model=StatusResponse)
async def get_status(token: str, db: DbSession) -> WaitlistStatus:
    return await get_service(db).get_status(token)
