// frontend/src/components/profile/SearchHistory.tsx
import React, {useEffect, useState} from 'react';
import axios from 'axios';

interface SearchHistoryItem {
    id: string;
    search_params: any;
    created_at: string;
}

const SearchHistory: React.FC = () => {
    const [history, setHistory] = useState<SearchHistoryItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchSearchHistory();
    }, []);

    const fetchSearchHistory = async () => {
        try {
            const token = localStorage.getItem('accessToken');
            const response = await axios.get('/api/search-history', {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            setHistory(response.data);
            setError('');
        } catch (err: any) {
            setError('Ошибка при загрузке истории поиска');
        } finally {
            setLoading(false);
        }
    };

    const deleteHistoryItem = async (id: string) => {
        try {
            const token = localStorage.getItem('accessToken');
            await axios.delete(`/api/search-history/${id}`, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            setHistory(history.filter(item => item.id !== id));
        } catch (err) {
            console.error('Ошибка при удалении:', err);
        }
    };

    const clearHistory = async () => {
        if (!window.confirm('Вы уверены, что хотите очистить всю историю поиска?')) {
            return;
        }

        try {
            const token = localStorage.getItem('accessToken');
            await axios.delete('/api/search-history', {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            setHistory([]);
        } catch (err) {
            console.error('Ошибка при очистке истории:', err);
        }
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleString('ru-RU');
    };

    const formatSearchParams = (params: any) => {
        const parts = [];
        if (params.min_price || params.max_price) {
            parts.push(`Цена: ${params.min_price || '?'} - ${params.max_price || '?'} ₽`);
        }
        if (params.min_speed || params.max_speed) {
            parts.push(`Скорость: ${params.min_speed || '?'} - ${params.max_speed || '?'} Мбит/с`);
        }
        if (params.connection_type) {
            parts.push(`Тип: ${params.connection_type}`);
        }
        if (params.has_tv) {
            parts.push('ТВ включено');
        }
        if (params.has_phone) {
            parts.push('Телефон включен');
        }
        return parts.join(' | ');
    };

    if (loading) {
        return <div className="loading">Загрузка истории...</div>;
    }

    if (error) {
        return <div className="error-message">{error}</div>;
    }

    return (
        <div className="search-history">
            <div className="history-header">
                <h3>История поиска</h3>
                {history.length > 0 && (
                    <button onClick={clearHistory} className="btn btn-secondary">
                        Очистить историю
                    </button>
                )}
            </div>

            {history.length === 0 ? (
                <p className="empty-history">История поиска пуста</p>
            ) : (
                <div className="history-list">
                    {history.map(item => (
                        <div key={item.id} className="history-item">
                            <div className="history-content">
                                <p className="history-params">
                                    {formatSearchParams(item.search_params)}
                                </p>
                                <p className="history-date">
                                    {formatDate(item.created_at)}
                                </p>
                            </div>
                            <button
                                onClick={() => deleteHistoryItem(item.id)}
                                className="delete-button"
                                title="Удалить"
                            >
                                ×
                            </button>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default SearchHistory;