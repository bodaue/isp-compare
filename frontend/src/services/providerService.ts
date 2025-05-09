import api from './api';
import { Provider } from '../types/provider.types';

export const providerService = {
    async getAllProviders(limit: number = 100, offset: number = 0): Promise<Provider[]> {
        const response = await api.get<Provider[]>('/providers', {
            params: { limit, offset }
        });
        return response.data;
    },

    async getProviderById(providerId: string): Promise<Provider> {
        const response = await api.get<Provider>(`/providers/${providerId}`);
        return response.data;
    }
};