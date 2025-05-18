import React, {useState} from 'react';
import {useNavigate} from 'react-router-dom';
import {useProviders, useTariffs, useToast} from '../../hooks';
import {TariffSearchParams} from '../../types/provider.types';
import {searchHistoryService} from '../../services/searchHistoryService';
import {useAuth} from '../../contexts/AuthContext';
import TariffCard from './TariffCard';
import TariffSort, {SortConfig} from './TariffSort';
import PageHeader from '../common/PageHeader';
import Toast from '../common/Toast';
import './TariffList.css';

const TariffList: React.FC = () => {
    const navigate = useNavigate();
    const {tariffs, loading, error, searchTariffs, fetchTariffs} = useTariffs();
    const {getProviderById} = useProviders();
    const {isLoggedIn} = useAuth();
    const {toasts, showToast, removeToast} = useToast();
    const [filters, setFilters] = useState<TariffSearchParams>({});
    const [showFilters, setShowFilters] = useState(false);
    const [loadingHistory, setLoadingHistory] = useState(false);

    const [compareMode, setCompareMode] = useState(false);
    const [selectedTariffs, setSelectedTariffs] = useState<string[]>([]);

    // Добавляем состояние для сортировки
    const [sortConfig, setSortConfig] = useState<SortConfig>({
        field: 'price',
        direction: 'asc'
    });

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
            } else {
                showToast('Нет сохраненных фильтров для восстановления', 'info', 2000);
            }
        } catch (error) {
            console.error('Error restoring last search:', error);
            showToast('Ошибка при восстановлении фильтров', 'error', 2000);
        } finally {
            setLoadingHistory(false);
        }
    };

    // Применяем сортировку к списку тарифов
    const sortedTariffs = React.useMemo(() => {
        // Если список пустой или все еще загружается, возвращаем исходный список
        if (!tariffs.length || loading) return tariffs;

        const sorted = [...tariffs];
        const {field, direction} = sortConfig;

        return sorted.sort((a, b) => {
            let comparison = 0;

            if (field === 'price') {
                const aPrice = a.promo_price ?? a.price;
                const bPrice = b.promo_price ?? b.price;
                comparison = aPrice - bPrice;
            } else if (field === 'speed') {
                comparison = a.speed - b.speed;
            } else if (field === 'name') {
                comparison = a.name.localeCompare(b.name);
            }

            return direction === 'asc' ? comparison : -comparison;
        });
    }, [tariffs, sortConfig, loading]);

    const toggleCompareMode = () => {
        if (compareMode) {
            setSelectedTariffs([]);
        }
        setCompareMode(!compareMode);
    };

    const handleTariffSelect = (tariffId: string) => {
        setSelectedTariffs(prev => {
            if (prev.includes(tariffId)) {
                return prev.filter(id => id !== tariffId);
            }
            if (prev.length < 5) {
                return [...prev, tariffId];
            }
            return prev;
        });
    };

    const startComparison = () => {
        if (selectedTariffs.length >= 2) {
            navigate(`/tariffs/compare?ids=${selectedTariffs.join(',')}`);
        }
    };

    // Обработчик изменения сортировки
    const handleSortChange = (newConfig: SortConfig) => {
        setSortConfig(newConfig);
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
            <PageHeader
                title="Тарифные планы"
                subtitle="Найдите подходящий тариф среди всех провайдеров"
            />

            <div className="tariff-controls">
                <button
                    className={`compare-toggle ${compareMode ? 'active' : ''}`}
                    onClick={toggleCompareMode}
                >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M3 3v18h18"></path>
                        <path d="M9.5 17V9"></path>
                        <path d="M13 17V5"></path>
                        <path d="M17 17V11"></path>
                    </svg>
                    {compareMode ? 'Отменить сравнение' : 'Сравнить тарифы'}
                </button>
                <button
                    className="filter-toggle"
                    onClick={() => setShowFilters(!showFilters)}
                >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M4 6h16M4 12h10M4 18h4"/>
                    </svg>
                    Фильтры
                </button>

                {/* Добавляем компонент сортировки */}
                <TariffSort
                    currentSort={sortConfig}
                    onChange={handleSortChange}
                />
            </div>

            {compareMode && (
                <div className="compare-panel">
                    <div className="compare-info">
                        <span>Выбрано {selectedTariffs.length} из 5 тарифов</span>
                        {selectedTariffs.length >= 2 && selectedTariffs.length <= 5 && (
                            <button
                                className="btn btn-primary btn-sm"
                                onClick={startComparison}
                            >
                                Сравнить выбранные ({selectedTariffs.length})
                            </button>
                        )}
                    </div>
                    {selectedTariffs.length < 2 && (
                        <p className="compare-hint">Выберите минимум 2 тарифа для сравнения</p>
                    )}
                </div>
            )}

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
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                                             stroke="currentColor" strokeWidth="2">
                                            <path d="M1 4v6h6M23 20v-6h-6"/>
                                            <path
                                                d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"/>
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
                {sortedTariffs.map((tariff) => (
                    <TariffCard
                        key={tariff.id}
                        tariff={tariff}
                        provider={getProviderById(tariff.provider_id)}
                        showProvider={true}
                        selectable={compareMode}
                        selected={selectedTariffs.includes(tariff.id)}
                        onSelect={() => handleTariffSelect(tariff.id)}
                    />
                ))}
            </div>

            {sortedTariffs.length === 0 && (
                <div className="no-tariffs">
                    <p>Тарифы не найдены. Попробуйте изменить параметры поиска.</p>
                </div>
            )}

            {toasts.map(toast => (
                <Toast
                    key={toast.id}
                    message={toast.message}
                    type={toast.type}
                    duration={toast.duration}
                    onClose={() => removeToast(toast.id)}
                />
            ))}
        </div>
    );
};

export default TariffList;