export interface Provider {
    id: string;
    name: string;
    description: string | null;
    website: string | null;
    logo_url: string | null;
    rating: number | null;
}

export interface Tariff {
    id: string;
    provider_id: string;
    name: string;
    description: string | null;
    price: number;
    speed: number;
    connection_type: ConnectionType;
    has_tv: boolean;
    has_phone: boolean;
    additional_services: Record<string, any> | null;
    connection_cost: number;
    contract_period: number | null;
    is_active: boolean;
}

export enum ConnectionType {
    FTTH = 'FTTH',
    ADSL = 'ADSL',
    PON = 'PON',
    ETHERNET = 'ETHERNET',
    WIMAX = 'WIMAX',
    LTE = 'LTE'
}

export interface TariffSearchParams {
    min_price?: number;
    max_price?: number;
    min_speed?: number;
    max_speed?: number;
    connection_type?: ConnectionType;
    has_tv?: boolean;
    has_phone?: boolean;
    limit?: number;
    offset?: number;
}