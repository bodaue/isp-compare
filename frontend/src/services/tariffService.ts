import api from './api';
import {Tariff, TariffSearchParams} from '../types/provider.types';
import {ComparisonRequest, ComparisonResult} from '../types/comparison.types';

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
    },

    async compareTariffs(tariffIds: string[]): Promise<ComparisonResult> {
        const request: ComparisonRequest = {tariff_ids: tariffIds};
        const response = await api.post<ComparisonResult>('/tariffs/comparison', request);
        return response.data;
    }
};