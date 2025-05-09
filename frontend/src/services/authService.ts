import api from './api';
import {APIResponse, LoginRequest, RegisterRequest, TokenResponse} from '../types/api.types';

export const authService = {
    async login(data: LoginRequest): Promise<TokenResponse> {
        const response = await api.post<TokenResponse>('/auth/login', data);
        localStorage.setItem('accessToken', response.data.access_token);
        return response.data;
    },

    async register(data: RegisterRequest): Promise<TokenResponse> {
        const response = await api.post<TokenResponse>('/auth/register', data);
        localStorage.setItem('accessToken', response.data.access_token);
        return response.data;
    },

    async logout(): Promise<APIResponse> {
        try {
            const response = await api.post<APIResponse>('/auth/logout');
            return response.data;
        } finally {
            localStorage.removeItem('accessToken');
        }
    },

    async refreshToken(): Promise<TokenResponse> {
        const response = await api.post<TokenResponse>('/auth/refresh');
        localStorage.setItem('accessToken', response.data.access_token);
        return response.data;
    },

    isAuthenticated(): boolean {
        return !!localStorage.getItem('accessToken');
    }
};