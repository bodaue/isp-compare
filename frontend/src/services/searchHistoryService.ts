import api from './api';
import {SearchHistoryResponse} from '../types/searchHistory.types';

export const searchHistoryService = {
    async getLatestSearch(): Promise<SearchHistoryResponse | null> {
        const response = await api.get<SearchHistoryResponse | null>('/search-history/latest');
        return response.data;
    }
};