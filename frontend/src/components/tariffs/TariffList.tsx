import React, {useState} from 'react';
import {useProviders, useTariffs} from '../../hooks';
import {TariffSearchParams} from '../../types/provider.types';
import {searchHistoryService} from '../../services/searchHistoryService';
import {useAuth} from '../../contexts/AuthContext';
import TariffCard from './TariffCard';
import './TariffList.css';

const TariffList: React.FC = () => {
    const {tariffs, loading, error, searchTariffs, fetchTariffs} = useTariffs();
    const {getProviderById} = useProviders();
    const {isLoggedIn} = useAuth();
    const [filters, setFilters] = useState<TariffSearchParams>({});
    const [showFilters, setShowFilters] = useState(false);
    const [loadingHistory, setLoadingHistory] = useState(false);

    const handleFilterChange = (name: keyof TariffSearchParams, value: any) => {
        setFilters(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const applyFilters = async () => {
        await searchTariffs(filters);
    };

    const resetFilters = () => {
        setFilters({});
        fetchTariffs();
    };

    const restoreLastSearch = async () => {
        if (!isLoggedIn) return;

        try {
            setLoadingHistory(true);
            const lastSearch = await searchHistoryService.getLatestSearch();

            if (lastSearch?.search_params) {
                setFilters(lastSearch.search_params);
                await searchTariffs(lastSearch.search_params);
            }
        } catch (error) {
            console.error('Error restoring last search:', error);
        } finally {
            setLoadingHistory(false);
        }
    };

    if (loading) {
        return (
            <div className="tariff-loading">
                <div className="loading-spinner"></div>
                Загрузка тарифов...
            </div>
        );
    }

    if (error) {
        return (
            <div className="tariff-error">
                <p>{error}</p>
                <button onClick={fetchTariffs} className="btn btn-primary">
                    Повторить попытку
                </button>
            </div>
        );
    }

    return (
        <div className="tariff-list-container">
            <div className="tariff-header">
                <h2>Тарифные планы</h2>
                <p>Найдите подходящий тариф среди всех провайдеров</p>
            </div>

            <div className="tariff-controls">
                <button
                    className="filter-toggle"
                    onClick={() => setShowFilters(!showFilters)}
                >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M4 6h16M4 12h10M4 18h4"/>
                    </svg>
                    Фильтры
                </button>
            </div>

            {showFilters && (
                <div className="filter-panel">
                    <div className="filter-group">
                        <label>Цена (₽/мес)</label>
                        <div className="filter-range">
                            <input
                                type="number"
                                placeholder="От"
                                value={filters.min_price || ''}
                                onChange={(e) => handleFilterChange('min_price', e.target.value ? Number(e.target.value) : undefined)}
                            />
                            <span>—</span>
                            <input
                                type="number"
                                placeholder="До"
                                value={filters.max_price || ''}
                                onChange={(e) => handleFilterChange('max_price', e.target.value ? Number(e.target.value) : undefined)}
                            />
                        </div>
                    </div>

                    <div className="filter-group">
                        <label>Скорость (Мбит/с)</label>
                        <div className="filter-range">
                            <input
                                type="number"
                                placeholder="От"
                                value={filters.min_speed || ''}
                                onChange={(e) => handleFilterChange('min_speed', e.target.value ? Number(e.target.value) : undefined)}
                            />
                            <span>—</span>
                            <input
                                type="number"
                                placeholder="До"
                                value={filters.max_speed || ''}
                                onChange={(e) => handleFilterChange('max_speed', e.target.value ? Number(e.target.value) : undefined)}
                            />
                        </div>
                    </div>

                    <div className="filter-group">
                        <label>Дополнительные услуги</label>
                        <div className="filter-checkboxes">
                            <label>
                                <input
                                    type="checkbox"
                                    checked={filters.has_tv || false}
                                    onChange={(e) => handleFilterChange('has_tv', e.target.checked || undefined)}
                                />
                                <span>Телевидение</span>
                            </label>
                            <label>
                                <input
                                    type="checkbox"
                                    checked={filters.has_phone || false}
                                    onChange={(e) => handleFilterChange('has_phone', e.target.checked || undefined)}
                                />
                                <span>Телефония</span>
                            </label>
                        </div>
                    </div>

                    <div className="filter-actions">
                        <button onClick={applyFilters} className="btn btn-primary">
                            Применить
                        </button>
                        <button onClick={resetFilters} className="btn btn-secondary">
                            Сбросить
                        </button>
                        {isLoggedIn && (
                            <button
                                onClick={restoreLastSearch}
                                className="btn btn-secondary btn-restore"
                                disabled={loadingHistory}
                            >
                                {loadingHistory ? (
                                    <>
                                        <span className="loading-spinner-small"></span>
                                        <span>Загрузка...</span>
                                    </>
                                ) : (
                                    <>
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                            <path d="M1 4v6h6M23 20v-6h-6"/>
                                            <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"/>
                                        </svg>
                                        <span>Восстановить фильтры</span>
                                    </>
                                )}
                            </button>
                        )}
                    </div>
                </div>
            )}

            <div className="tariffs-grid">
                {tariffs.map((tariff) => (
                    <TariffCard
                        key={tariff.id}
                        tariff={tariff}
                        provider={getProviderById(tariff.provider_id)}
                        showProvider={true}
                    />
                ))}
            </div>

            {tariffs.length === 0 && (
                <div className="no-tariffs">
                    <p>Тарифы не найдены. Попробуйте изменить параметры поиска.</p>
                </div>
            )}
        </div>
    );
};

export default TariffList;