// frontend/src/hooks/useSearchHistory.ts
import { useEffect, useState } from 'react';
import { searchHistoryService } from '../services/searchHistoryService';
import { SearchHistoryResponse } from '../types/searchHistory.types';

export const useSearchHistory = () => {
    const [searchHistory, setSearchHistory] = useState<SearchHistoryResponse[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const fetchSearchHistory = async () => {
        try {
            setLoading(true);
            const data = await searchHistoryService.getSearchHistory(10, 0);
            setSearchHistory(data);
            setError('');
        } catch (err: any) {
            setError('Ошибка при загрузке истории поиска');
        } finally {
            setLoading(false);
        }
    };

    const deleteSearchItem = async (id: string) => {
        try {
            await searchHistoryService.deleteSearchHistory(id);
            setSearchHistory(prev => prev.filter(item => item.id !== id));
        } catch (err: any) {
            setError('Ошибка при удалении записи');
        }
    };

    const clearHistory = async () => {
        try {
            await searchHistoryService.clearSearchHistory();
            setSearchHistory([]);
        } catch (err: any) {
            setError('Ошибка при очистке истории');
        }
    };

    useEffect(() => {
        fetchSearchHistory();
    }, []);

    return {
        searchHistory,
        loading,
        error,
        fetchSearchHistory,
        deleteSearchItem,
        clearHistory
    };
};