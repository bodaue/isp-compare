import React, {useState} from 'react';
import {useProviders, useTariffs} from '../../hooks';
import {TariffSearchParams} from '../../types/provider.types';
import TariffCard from './TariffCard';
import styles from './TariffList.module.css';

const TariffList: React.FC = () => {
    const {tariffs, loading, error, searchTariffs, fetchTariffs} = useTariffs();
    const {getProviderById} = useProviders();
    const [filters, setFilters] = useState<TariffSearchParams>({});
    const [showFilters, setShowFilters] = useState(false);

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

    if (loading) {
        return (
            <div className={styles.tariffLoading}>
                <div className={styles.loadingSpinner}></div>
                Загрузка тарифов...
            </div>
        );
    }

    if (error) {
        return (
            <div className={styles.tariffError}>
                <p>{error}</p>
                <button onClick={fetchTariffs} className="btn btn-primary">
                    Повторить попытку
                </button>
            </div>
        );
    }

    return (
        <div className={styles.tariffListContainer}>
            <div className={styles.tariffHeader}>
                <h2>Тарифные планы</h2>
                <p>Найдите подходящий тариф среди всех провайдеров</p>
            </div>

            <div className={styles.tariffControls}>
                <button
                    className={styles.filterToggle}
                    onClick={() => setShowFilters(!showFilters)}
                >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M4 6h16M4 12h10M4 18h4"/>
                    </svg>
                    Фильтры
                </button>
            </div>

            {showFilters && (
                <div className={styles.filterPanel}>
                    <div className={styles.filterGroup}>
                        <label>Цена (₽/мес)</label>
                        <div className={styles.filterRange}>
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

                    <div className={styles.filterGroup}>
                        <label>Скорость (Мбит/с)</label>
                        <div className={styles.filterRange}>
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

                    <div className={styles.filterGroup}>
                        <label>Дополнительные услуги</label>
                        <div className={styles.filterCheckboxes}>
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

                    <div className={styles.filterActions}>
                        <button onClick={applyFilters} className={`${styles.btn} ${styles.btnPrimary}`}>
                            Применить
                        </button>
                        <button onClick={resetFilters} className={`${styles.btn} ${styles.btnSecondary}`}>
                            Сбросить
                        </button>
                    </div>
                </div>
            )}

            <div className={styles.tariffsGrid}>
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
                <div className={styles.noTariffs}>
                    <p>Тарифы не найдены. Попробуйте изменить параметры поиска.</p>
                </div>
            )}
        </div>
    );
};

export default TariffList;