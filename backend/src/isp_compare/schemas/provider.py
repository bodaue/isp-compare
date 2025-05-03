from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ProviderBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = None
    website: HttpUrl | None = None
    logo_url: str | None = Field(None, max_length=512)


class ProviderCreate(ProviderBase):
    pass


class ProviderUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = None
    website: HttpUrl | None = None
    logo_url: str | None = Field(None, max_length=512)


class ProviderResponse(ProviderBase):
    id: UUID
    rating: float | None = None

    model_config = ConfigDict(from_attributes=True)
