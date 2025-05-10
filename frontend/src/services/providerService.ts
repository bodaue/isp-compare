import api from './api';
import {Provider} from '../types/provider.types';

export const providerService = {
    async getAllProviders(): Promise<Provider[]> {
        const response = await api.get<Provider[]>('/providers');
        return response.data;
    },

    async getProviderById(providerId: string): Promise<Provider> {
        const response = await api.get<Provider>(`/providers/${providerId}`);
        return response.data;
    }
};