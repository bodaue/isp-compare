from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ComparisonRequest(BaseModel):
    tariff_ids: list[UUID] = Field(..., min_length=2, max_length=5)


class TariffComparisonItem(BaseModel):
    """Элемент сравнения тарифа с минимально необходимой информацией"""

    id: UUID
    name: str
    provider_name: str

    # Цены
    current_price: Decimal  # Актуальная цена (с учетом акции)
    original_price: Decimal  # Оригинальная цена
    is_promo: bool
    promo_period: int | None = None

    # Характеристики
    speed: int
    features: list[str]  # ["ТВ", "Телефон", "Бесплатное подключение"]
    connection_cost: Decimal | None

    # Расчетные метрики
    price_per_mbps: Decimal
    yearly_cost: Decimal
    value_score: Decimal

    # Сравнительные метки
    is_cheapest: bool = False
    is_fastest: bool = False
    is_best_value: bool = False
    has_most_features: bool = False

    model_config = ConfigDict(from_attributes=True)


class ComparisonResult(BaseModel):
    """Результат сравнения тарифов"""

    items: list[TariffComparisonItem]
    recommendations: list[str]
    summary: str  # Краткое резюме сравнения
