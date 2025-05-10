from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProviderBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = Field(None, max_length=4096)
    website: str | None = Field(None, max_length=2048)
    logo_url: str | None = Field(None, max_length=512)


class ProviderResponse(ProviderBase):
    id: UUID
    rating: float | None = None

    model_config = ConfigDict(from_attributes=True)
