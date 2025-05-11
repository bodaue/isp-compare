export interface TariffComparisonItem {
    id: string;
    name: string;
    provider_name: string;

    // Цены
    current_price: number;
    original_price: number;
    is_promo: boolean;
    promo_period: number | null;

    // Характеристики
    speed: number;
    features: string[];
    connection_cost: number | null;

    // Расчетные метрики
    price_per_mbps: number;
    yearly_cost: number;
    value_score: number;

    // Сравнительные метки
    is_cheapest: boolean;
    is_fastest: boolean;
    is_best_value: boolean;
    has_most_features: boolean;
}

export interface ComparisonResult {
    items: TariffComparisonItem[];
    recommendations: string[];
    summary: string;
}

export interface ComparisonRequest {
    tariff_ids: string[];
}