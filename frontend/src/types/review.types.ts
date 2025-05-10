export interface ReviewUser {
    id: string;
    username: string;
    fullname: string;
}

export interface Review {
    id: string;
    rating: number;
    comment: string;
    created_at: string;
    updated_at: string;
    user: ReviewUser | null;
}

export interface ReviewCreate {
    rating: number;
    comment: string;
}

export interface ReviewUpdate {
    rating?: number;
    comment?: string;
}