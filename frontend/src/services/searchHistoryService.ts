import api from './api';
import {SearchHistoryResponse} from '../types/searchHistory.types';

export const searchHistoryService = {
    async getSearchHistory(limit: number = 10, offset: number = 0): Promise<SearchHistoryResponse[]> {
        const response = await api.get<SearchHistoryResponse[]>('/search-history', {
            params: {limit, offset}
        });
        return response.data;
    },

    async deleteSearchHistory(searchHistoryId: string): Promise<void> {
        await api.delete(`/search-history/${searchHistoryId}`);
    },

    async clearSearchHistory(): Promise<void> {
        await api.delete('/search-history');
    }
};