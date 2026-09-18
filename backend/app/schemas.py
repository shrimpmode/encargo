from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import WaitlistState


class JoinRequest(BaseModel):
    name: str = Field(min_length=1)
    phone: str = Field(min_length=1)
    party_size: int = Field(gt=0)


class JoinResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status_token: str


class StatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    state: WaitlistState
    position: int | None


class WaitlistEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    party_size: int
    joined_at: datetime
