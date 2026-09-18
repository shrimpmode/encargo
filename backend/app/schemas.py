from pydantic import BaseModel, ConfigDict, Field


class JoinRequest(BaseModel):
    name: str = Field(min_length=1)
    phone: str = Field(min_length=1)
    party_size: int = Field(gt=0)


class JoinResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status_token: str
