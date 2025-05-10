# backend/src/isp_compare/schemas/comparison.py

from typing import Any
from uuid import UUID

from pydantic import BaseModel

from isp_compare.schemas.provider import ProviderResponse
from isp_compare.schemas.tariff import TariffResponse


class TariffComparisonItem(BaseModel):
    tariff: TariffResponse
    provider: ProviderResponse
    characteristics: dict[str, Any]
    advantages: list[str]
    disadvantages: list[str]


class TariffComparisonResponse(BaseModel):
    tariffs: list[TariffComparisonItem]
    comparison_matrix: dict[str, list[Any]]
    best_by_price: UUID | None
    best_by_speed: UUID | None
    best_overall: UUID | None
    summary: str


class TariffComparisonRequest(BaseModel):
    tariff_ids: list[UUID]
