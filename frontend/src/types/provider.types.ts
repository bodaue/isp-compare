export interface Provider {
    id: string;
    name: string;
    description: string | null;
    website: string
    logo_url: string | null;
    rating: number | null;
    phone: string;
}

export interface Tariff {
    id: string;
    provider_id: string;
    name: string;
    description: string | null;
    price: number;
    speed: number;
    has_tv: boolean;
    has_phone: boolean;
    connection_cost: number;
    promo_price: number | null;
    promo_period: number | null;
    is_active: boolean;
    url: string | null;
}

export interface TariffSearchParams {
    min_price?: number;
    max_price?: number;
    min_speed?: number;
    max_speed?: number;
    has_tv?: boolean;
    has_phone?: boolean;
    limit?: number;
    offset?: number;
}