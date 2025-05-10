from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ComparisonRequest(BaseModel):
    tariff_ids: list[UUID] = Field(..., min_length=2, max_length=5)
    include_provider_info: bool = True


class PriceComparison(BaseModel):
    tariff_id: UUID
    base_price: Decimal
    effective_price: Decimal
    is_promo: bool
    promo_discount: Decimal | None = None
    promo_period: int | None = None
    yearly_cost: Decimal
    monthly_savings: Decimal | None = None  # Экономия относительно самого дорогого


class SpeedComparison(BaseModel):
    tariff_id: UUID
    speed: int
    price_per_mbps: Decimal
    is_fastest: bool
    speed_difference: int  # Разница со средней скоростью


class FeatureComparison(BaseModel):
    tariff_id: UUID
    has_tv: bool
    has_phone: bool
    connection_cost: Decimal
    features_count: int
    unique_features: list[str] = []


class ValueMetrics(BaseModel):
    price_per_mbps: Decimal
    features_per_price: Decimal
    overall_score: Decimal  # Комплексная оценка


class TariffComparisonItem(BaseModel):
    id: UUID
    name: str
    provider_id: UUID
    provider_name: str | None = None

    # Основные параметры
    base_price: Decimal
    effective_price: Decimal
    speed: int
    has_tv: bool
    has_phone: bool
    connection_cost: Decimal

    # Акции
    is_promo: bool
    promo_price: Decimal | None = None
    promo_period: int | None = None

    # Расчетные метрики
    price_per_mbps: Decimal
    yearly_cost: Decimal
    value_score: Decimal

    # Сравнительные метки
    is_cheapest: bool = False
    is_fastest: bool = False
    is_best_value: bool = False
    has_best_features: bool = False

    model_config = ConfigDict(from_attributes=True)


class ComparisonResult(BaseModel):
    tariffs: list[TariffComparisonItem]

    # Статистика по сравнению
    price_range: tuple[Decimal, Decimal]
    speed_range: tuple[int, int]
    average_price: Decimal
    average_speed: int

    # Рекомендации
    best_for_price: UUID
    best_for_speed: UUID
    best_for_value: UUID
    best_for_features: UUID

    # Детальное сравнение
    price_comparison: list[PriceComparison]
    speed_comparison: list[SpeedComparison]
    feature_comparison: list[FeatureComparison]

    # Аналитика
    total_savings_with_promo: Decimal
    average_price_per_mbps: Decimal
    recommendations: list[str]


class ComparisonSummary(BaseModel):
    total_comparisons: int
    tariffs_compared: list[UUID]
    comparison_date: str
    most_popular_choice: UUID | None = None
