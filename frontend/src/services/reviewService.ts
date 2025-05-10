import api from './api';
import {Review, ReviewCreate, ReviewUpdate} from '../types/review.types';

export const reviewService = {
    async createReview(providerId: string, data: ReviewCreate): Promise<Review> {
        const response = await api.post<Review>(`/providers/${providerId}/reviews`, data);
        return response.data;
    },

    async getProviderReviews(providerId: string, limit: number = 10, offset: number = 0): Promise<Review[]> {
        const response = await api.get<Review[]>(`/providers/${providerId}/reviews`, {
            params: {limit, offset}
        });
        return response.data;
    },

    async getReview(reviewId: string): Promise<Review> {
        const response = await api.get<Review>(`/reviews/${reviewId}`);
        return response.data;
    },

    async updateReview(reviewId: string, data: ReviewUpdate): Promise<Review> {
        const response = await api.patch<Review>(`/reviews/${reviewId}`, data);
        return response.data;
    },

    async deleteReview(reviewId: string): Promise<void> {
        await api.delete(`/reviews/${reviewId}`);
    }
};