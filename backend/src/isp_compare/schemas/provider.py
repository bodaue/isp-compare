from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_serializer


class ProviderBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = None
    website: HttpUrl | None = None
    logo_url: str | None = Field(None, max_length=512)

    @field_serializer("website")
    def serialize_website(self, website: HttpUrl | None) -> str | None:
        if website is not None:
            return str(website)
        return None


class ProviderCreate(ProviderBase):
    pass


class ProviderUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = None
    website: HttpUrl | None = None
    logo_url: str | None = Field(None, max_length=512)

    @field_serializer("website")
    def serialize_website(self, website: HttpUrl | None) -> str | None:
        if website is not None:
            return str(website)
        return None


class ProviderResponse(ProviderBase):
    id: UUID
    rating: float | None = None

    model_config = ConfigDict(from_attributes=True)
