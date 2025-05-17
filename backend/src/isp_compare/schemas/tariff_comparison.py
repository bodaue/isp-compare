from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ComparisonRequest(BaseModel):
    tariff_ids: list[UUID] = Field(..., min_length=2, max_length=5)


class TariffComparisonItem(BaseModel):
    id: UUID
    name: str
    provider_name: str

    current_price: Decimal
    original_price: Decimal
    is_promo: bool
    promo_period: int | None = None

    speed: int
    features: list[str]
    connection_cost: Decimal | None

    price_per_mbps: Decimal
    yearly_cost: Decimal
    value_score: Decimal

    is_cheapest: bool = False
    is_fastest: bool = False
    is_best_value: bool = False
    has_most_features: bool = False

    model_config = ConfigDict(from_attributes=True)


class ComparisonResult(BaseModel):
    items: list[TariffComparisonItem]
    recommendations: list[str]
    summary: str
