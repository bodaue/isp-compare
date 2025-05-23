// frontend/src/components/tariffs/TariffComparison.tsx
import React, {useEffect, useState} from 'react';
import {useNavigate, useSearchParams} from 'react-router-dom';
import {tariffService} from '../../services/tariffService';
import {ComparisonResult} from '../../types/comparison.types';
import PageHeader from '../common/PageHeader';
import './TariffComparison.css';

const TariffComparison: React.FC = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const [comparison, setComparison] = useState<ComparisonResult | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const ids = searchParams.get('ids')?.split(',').filter(Boolean) || [];

        if (ids.length < 2 || ids.length > 5) {
            navigate('/tariffs');
            return;
        }

        fetchComparison(ids);
    }, [searchParams, navigate]);

    const fetchComparison = async (ids: string[]) => {
        try {
            setLoading(true);
            const data = await tariffService.compareTariffs(ids);
            setComparison(data);
            setError('');
        } catch (err: any) {
            setError('Ошибка при сравнении тарифов');
        } finally {
            setLoading(false);
        }
    };

    const removeFromComparison = (id: string) => {
        const currentIds = searchParams.get('ids')?.split(',').filter(Boolean) || [];
        const newIds = currentIds.filter(tariffId => tariffId !== id);

        if (newIds.length < 2) {
            navigate('/tariffs');
        } else {
            navigate(`/tariffs/compare?ids=${newIds.join(',')}`);
        }
    };

    const formatPrice = (price: number | string) => {
        const numPrice = typeof price === 'string' ? parseFloat(price) : price;
        return new Intl.NumberFormat('ru-RU').format(numPrice);
    };

    const parseNumber = (value: number | string): number => {
        return typeof value === 'string' ? parseFloat(value) : value;
    };

    const calculateValuePercentage = (valueScore: number | string): number => {
        const score = parseNumber(valueScore);
        // Преобразуем значение value_score в проценты
        // Чем меньше value_score, тем лучше (более высокий процент)
        const percentage = Math.min(100, Math.max(0, (1 / score) * 100));
        return Math.round(percentage);
    };

    if (loading) {
        return (
            <div className="comparison-loading">
                <div className="loading-spinner"></div>
                Загрузка сравнения...
            </div>
        );
    }

    if (error || !comparison) {
        return (
            <div className="comparison-error">
                <p>{error || 'Не удалось загрузить сравнение'}</p>
                <button onClick={() => navigate('/tariffs')} className="btn btn-primary">
                    Вернуться к тарифам
                </button>
            </div>
        );
    }

    // Устанавливаем переменную CSS для количества столбцов
    const tableStyle = {
        '--columns-count': comparison.items.length
    } as React.CSSProperties;

    return (
        <div className="comparison-container">
            <PageHeader
                title="Сравнение тарифов"
                subtitle={comparison.summary}
            />

            <div className="comparison-actions">
                <button
                    onClick={() => navigate('/tariffs')}
                    className="btn btn-secondary"
                >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M19 12H5M12 19l-7-7 7-7"/>
                    </svg>
                    Изменить выбор
                </button>
            </div>

            <div className="comparison-table-wrapper">
                <table className="comparison-table" style={tableStyle}>
                    <thead>
                    <tr>
                        <th className="fixed-column">Характеристика</th>
                        {comparison.items.map(item => (
                            <th key={item.id}>
                                <div className="tariff-header-cell">
                                    <div className="provider-info">
                                        <div className="provider-name">{item.provider_name}</div>
                                        <a href={`/tariffs/${item.id}`}
                                           target="_blank"
                                           rel="noopener noreferrer"
                                           className="tariff-name-link"
                                           title="Открыть тариф в новой вкладке"
                                        >
                                            {item.name}
                                        </a>
                                    </div>
                                    <button
                                        className="remove-btn"
                                        onClick={() => removeFromComparison(item.id)}
                                        title="Удалить из сравнения"
                                    >
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                                             stroke="currentColor" strokeWidth="2">
                                            <path d="M18 6L6 18M6 6l12 12"/>
                                        </svg>
                                    </button>
                                </div>
                            </th>
                        ))}
                    </tr>
                    </thead>
                    <tbody>
                    {/* Цена */}
                    <tr>
                        <td className="fixed-column">Цена</td>
                        {comparison.items.map(item => (
                            <td key={item.id}>
                                <div className={`price-cell ${item.is_cheapest ? 'best-value' : ''}`}>
                                    <span className="current-price">
                                        {formatPrice(item.current_price)} ₽
                                    </span>
                                    {item.is_cheapest && (
                                        <span className="best-indicator" title="Самый дешевый">
                                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                <path d="M20 6L9 17l-5-5"/>
                                            </svg>
                                        </span>
                                    )}
                                </div>
                            </td>
                        ))}
                    </tr>

                    {/* Скорость */}
                    <tr>
                        <td className="fixed-column">Скорость</td>
                        {comparison.items.map(item => (
                            <td key={item.id}>
                                <div className={`speed-cell ${item.is_fastest ? 'best-value' : ''}`}>
                                    <span className="speed-value">
                                        {item.speed} Мбит/с
                                    </span>
                                    {item.is_fastest && (
                                        <span className="best-indicator" title="Самый быстрый">
                                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
                                            </svg>
                                        </span>
                                    )}
                                </div>
                            </td>
                        ))}
                    </tr>

                    {/* Цена за Мбит/с */}
                    <tr className="metrics-section">
                        <td className="fixed-column">Цена за Мбит/с</td>
                        {comparison.items.map(item => (
                            <td key={item.id}>
                                <div className="metric-cell">
                                    <span className="metric-value">
                                        {parseNumber(item.price_per_mbps).toFixed(2)} ₽
                                    </span>
                                </div>
                            </td>
                        ))}
                    </tr>

                    {/* Годовая стоимость */}
                    <tr className="metrics-section">
                        <td className="fixed-column">Годовая стоимость</td>
                        {comparison.items.map(item => (
                            <td key={item.id}>
                                <div className="metric-cell">
                                    <span className="metric-value">
                                        {formatPrice(item.yearly_cost)} ₽
                                    </span>
                                </div>
                            </td>
                        ))}
                    </tr>

                    {/* Дополнительные услуги */}
                    <tr>
                        <td className="fixed-column">Дополнительные услуги</td>
                        {comparison.items.map(item => (
                            <td key={item.id}>
                                <div className={`features-cell ${item.has_most_features ? 'best-value' : ''}`}>
                                    {item.features.length > 0 ? (
                                        <>
                                            <ul className="features-list">
                                                {item.features
                                                    .filter(feature => feature !== "Бесплатное подключение")
                                                    .map((feature, index) => (
                                                        <li key={index}>{feature}</li>
                                                    ))}
                                            </ul>
                                            {item.has_most_features && (
                                                <span className="best-indicator" title="Больше всего услуг">
                                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                                                    </svg>
                                                </span>
                                            )}
                                        </>
                                    ) : (
                                        <span className="no-features">—</span>
                                    )}
                                </div>
                            </td>
                        ))}
                    </tr>

                    {/* Оценка ценности */}
                    <tr className="metrics-section">
                        <td className="fixed-column">Оценка ценности</td>
                        {comparison.items.map(item => {
                            const percentage = calculateValuePercentage(item.value_score);
                            return (
                                <td key={item.id}>
                                    <div className={`value-cell ${item.is_best_value ? 'best-value' : ''}`}>
                                        <div className="value-info">
                                            <span className="value-percentage">{percentage}%</span>
                                            {item.is_best_value && (
                                                <span className="best-indicator" title="Лучшее предложение">
                                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                        <path d="M9 11l3 3L22 4"/>
                                                        <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
                                                    </svg>
                                                </span>
                                            )}
                                        </div>
                                        <div className="value-bar-container">
                                            <div className="value-bar">
                                                <div
                                                    className="value-fill"
                                                    style={{
                                                        width: `${percentage}%`
                                                    }}
                                                ></div>
                                            </div>
                                        </div>
                                    </div>
                                </td>
                            );
                        })}
                    </tr>
                    </tbody>
                </table>
            </div>

            <div className="recommendations-section">
                <h3>Рекомендации</h3>
                <div className="recommendations-grid">
                    {comparison.recommendations.map((recommendation, index) => (
                        <div key={index} className="recommendation-card">
                            <div className="recommendation-icon">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                     strokeWidth="2">
                                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                                </svg>
                            </div>
                            <p>{recommendation}</p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default TariffComparison;