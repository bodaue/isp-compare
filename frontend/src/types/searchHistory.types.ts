export interface SearchHistoryResponse {
    id: string;
    user_id: string;
    search_params: {
        min_price?: number;
        max_price?: number;
        min_speed?: number;
        max_speed?: number;
        has_tv?: boolean;
        has_phone?: boolean;
    };
    created_at: string;
}