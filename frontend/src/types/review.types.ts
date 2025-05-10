export interface ReviewUser {
    id: string;
    username: string;
    fullname: string;
}

export interface ReviewProvider {
    id: string;
    name: string;
    logo_url: string | null;
    rating: number | null;
}

export interface Review {
    id: string;
    rating: number;
    comment: string;
    created_at: string;
    updated_at: string;
    user: ReviewUser | null;
    provider: ReviewProvider | null;
}

export interface ReviewCreate {
    rating: number;
    comment: string;
}

export interface ReviewUpdate {
    rating?: number;
    comment?: string;
}