from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(..., min_length=3, max_length=1000)


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(BaseModel):
    rating: int | None = Field(None, ge=1, le=5)
    comment: str | None = Field(None, min_length=10, max_length=1000)


class ReviewUserInfo(BaseModel):
    id: UUID
    username: str
    fullname: str

    model_config = ConfigDict(from_attributes=True)


class ReviewProviderInfo(BaseModel):
    id: UUID
    name: str
    logo_url: str | None = None
    rating: float | None = None

    model_config = ConfigDict(from_attributes=True)


class ReviewResponse(ReviewBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    user: ReviewUserInfo | None = None
    provider: ReviewProviderInfo | None = None

    model_config = ConfigDict(from_attributes=True)
