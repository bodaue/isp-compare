import api from './api';
import {APIResponse, PasswordChangeRequest, ProfileUpdateRequest, UserProfile} from '../types/api.types';

export const userService = {
    async getProfile(): Promise<UserProfile> {
        const response = await api.get<UserProfile>('/users/me');
        return response.data;
    },

    async updateProfile(data: ProfileUpdateRequest): Promise<UserProfile> {
        const response = await api.patch<UserProfile>('/users/profile', data);
        return response.data;
    },

    async changePassword(data: PasswordChangeRequest): Promise<APIResponse> {
        const response = await api.post<APIResponse>('/users/change-password', data);
        return response.data;
    }
};