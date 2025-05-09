// frontend/src/components/tariffs/SearchHistory.tsx
import React from 'react';
import {SearchHistoryResponse} from '../../types/searchHistory.types';
import {TariffSearchParams} from '../../types/provider.types';
import './SearchHistory.css';

interface SearchHistoryProps {
    searchHistory: SearchHistoryResponse[];
    onSelectSearch: (params: TariffSearchParams) => void;
    onDeleteItem: (id: string) => void;
    onClearHistory: () => void;
}

const SearchHistory: React.FC<SearchHistoryProps> = ({
                                                         searchHistory,
                                                         onSelectSearch,
                                                         onDeleteItem,
                                                         onClearHistory
                                                     }) => {
    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('ru-RU', {
            day: 'numeric',
            month: 'short',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const getSearchDescription = (params: TariffSearchParams) => {
        const parts = [];

        if (params.min_price || params.max_price) {
            const price = [];
            if (params.min_price) price.push(`от ${params.min_price}`);
            if (params.max_price) price.push(`до ${params.max_price}`);
            parts.push(`💰 ${price.join(' ')} ₽`);
        }

        if (params.min_speed || params.max_speed) {
            const speed = [];
            if (params.min_speed) speed.push(`от ${params.min_speed}`);
            if (params.max_speed) speed.push(`до ${params.max_speed}`);
            parts.push(`⚡ ${speed.join(' ')} Мбит/с`);
        }

        if (params.has_tv) parts.push('📺 ТВ');
        if (params.has_phone) parts.push('📞 Телефон');

        return parts.length > 0 ? parts.join(' • ') : 'Все тарифы';
    };

    if (searchHistory.length === 0) {
        return (
            <div className="search-history-empty">
                <p>История поиска пуста</p>
            </div>
        );
    }

    return (
        <div className="search-history">
            <div className="search-history-header">
                <h3>Недавние поиски</h3>
                <button
                    className="clear-history-btn"
                    onClick={onClearHistory}
                    title="Очистить историю"
                >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path
                            d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2m3 0v12a2 2 0 01-2 2H7a2 2 0 01-2-2V6h14M10 11v6M14 11v6"/>
                    </svg>
                </button>
            </div>

            <div className="search-history-list">
                {searchHistory.map((item) => (
                    <div key={item.id} className="search-history-item">
                        <div
                            className="search-history-content"
                            onClick={() => onSelectSearch(item.search_params)}
                        >
                            <div className="search-description">
                                {getSearchDescription(item.search_params)}
                            </div>
                            <div className="search-date">
                                {formatDate(item.created_at)}
                            </div>
                        </div>
                        <button
                            className="delete-search-btn"
                            onClick={(e) => {
                                e.stopPropagation();
                                onDeleteItem(item.id);
                            }}
                            title="Удалить"
                        >
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                 strokeWidth="2">
                                <path d="M18 6L6 18M6 6l12 12"/>
                            </svg>
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default SearchHistory;