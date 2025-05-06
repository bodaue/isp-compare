from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from isp_compare.models.tariff import ConnectionType


class TariffBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = Field(None, max_length=4096)
    price: Decimal = Field(..., ge=0, decimal_places=2)
    speed: int = Field(..., gt=0)
    connection_type: ConnectionType
    has_tv: bool = False
    has_phone: bool = False
    additional_services: dict | None = None
    connection_cost: Decimal = Field(0, ge=0, decimal_places=2)
    contract_period: int | None = Field(None, ge=0)
    is_active: bool = True


class TariffCreate(TariffBase):
    pass


class TariffUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = Field(None, max_length=4096)
    price: Decimal | None = Field(None, ge=0, decimal_places=2)
    speed: int | None = Field(None, gt=0)
    connection_type: ConnectionType | None = None
    has_tv: bool | None = None
    has_phone: bool | None = None
    additional_services: dict | None = None
    connection_cost: Decimal | None = Field(None, ge=0, decimal_places=2)
    contract_period: int | None = Field(None, ge=0)
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
    connection_type: ConnectionType | None = None
    has_tv: bool | None = None
    has_phone: bool | None = None
    limit: int = 50
    offset: int = 0
