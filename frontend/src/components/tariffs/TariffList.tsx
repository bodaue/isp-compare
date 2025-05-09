import React, {useEffect, useState} from 'react';
import {tariffService} from '../../services/tariffService';
import {providerService} from '../../services/providerService';
import {Provider, Tariff, TariffSearchParams} from '../../types/provider.types';
import TariffCard from './TariffCard';
import './TariffList.css';

const TariffList: React.FC = () => {
    const [tariffs, setTariffs] = useState<Tariff[]>([]);
    const [providers, setProviders] = useState<Provider[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [filters, setFilters] = useState<TariffSearchParams>({});
    const [showFilters, setShowFilters] = useState(false);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [tariffsData, providersData] = await Promise.all([
                tariffService.getAllTariffs(),
                providerService.getAllProviders()
            ]);
            setTariffs(tariffsData);
            setProviders(providersData);
            setError('');
        } catch (err: any) {
            setError('Ошибка при загрузке данных');
        } finally {
            setLoading(false);
        }
    };

    const handleFilterChange = (name: keyof TariffSearchParams, value: any) => {
        setFilters(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const applyFilters = async () => {
        setLoading(true);
        try {
            const filteredTariffs = await tariffService.searchTariffs(filters);
            setTariffs(filteredTariffs);
            setError('');
        } catch (err: any) {
            setError('Ошибка при применении фильтров');
        } finally {
            setLoading(false);
        }
    };

    const resetFilters = () => {
        setFilters({});
        fetchData();
    };

    const getProviderById = (providerId: string) => {
        return providers.find(p => p.id === providerId);
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
                <button onClick={fetchData} className="btn btn-primary">
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