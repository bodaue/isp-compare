from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TariffBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = Field(None, max_length=4096)
    price: Decimal = Field(..., ge=0, decimal_places=2)
    speed: int = Field(..., gt=0)
    has_tv: bool = False
    has_phone: bool = False
    connection_cost: Decimal | None = Field(None, ge=0, decimal_places=2)
    promo_price: Decimal | None = Field(None, ge=0, decimal_places=2)
    promo_period: int | None = Field(None, ge=0)
    is_active: bool = True
    url: str | None = Field(None, max_length=512)  # НОВОЕ ПОЛЕ


class TariffCreate(TariffBase):
    pass


class TariffUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = Field(None, max_length=4096)
    price: Decimal | None = Field(None, ge=0, decimal_places=2)
    speed: int | None = Field(None, gt=0)
    has_tv: bool | None = None
    has_phone: bool | None = None
    connection_cost: Decimal | None = Field(None, ge=0, decimal_places=2)
    promo_price: Decimal | None = Field(None, ge=0, decimal_places=2)
    promo_period: int | None = Field(None, ge=0)
    is_active: bool | None = None


class TariffResponse(TariffBase):
    id: UUID
    provider_id: UUID

    model_config = ConfigDict(from_attributes=True)


class TariffSearchParams(BaseModel):
    min_price: Decimal | None = Field(None, ge=0)
    max_price: Decimal | None = Field(None, ge=0)
    min_speed: int | None = Field(None, ge=0)
    max_speed: int | None = Field(None, ge=0)
    has_tv: bool | None = None
    has_phone: bool | None = None
    limit: int = 50
    offset: int = 0
