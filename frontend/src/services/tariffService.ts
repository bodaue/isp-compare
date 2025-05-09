import api from './api';
import {Tariff, TariffSearchParams} from '../types/provider.types';

export const tariffService = {
    async getAllTariffs(limit: number = 100, offset: number = 0): Promise<Tariff[]> {
        const response = await api.get<Tariff[]>('/tariffs', {
            params: {limit, offset}
        });
        return response.data;
    },

    async getProviderTariffs(providerId: string, limit: number = 100, offset: number = 0): Promise<Tariff[]> {
        const response = await api.get<Tariff[]>(`/providers/${providerId}/tariffs`, {
            params: {limit, offset}
        });
        return response.data;
    },

    async searchTariffs(params: TariffSearchParams): Promise<Tariff[]> {
        const response = await api.get<Tariff[]>('/tariffs/search', {
            params
        });
        return response.data;
    },

    async getTariffById(tariffId: string): Promise<Tariff> {
        const response = await api.get<Tariff>(`/tariffs/${tariffId}`);
        return response.data;
    }
};