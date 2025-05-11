// frontend/src/components/tariffs/TariffComparison.tsx
import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { tariffService } from '../../services/tariffService';
import { ComparisonResult } from '../../types/comparison.types';
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
                <table className="comparison-table">
                    <thead>
                        <tr>
                            <th className="fixed-column">Характеристика</th>
                            {comparison.items.map(item => (
                                <th key={item.id}>
                                    <div className="tariff-header-cell">
                                        <div className="provider-info">
                                            <div className="provider-name">{item.provider_name}</div>
                                            <a
                                                href={`/tariffs/${item.id}`}
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
                                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
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
                                    <div className="price-cell">
                                        <span className="current-price">
                                            {formatPrice(item.current_price)} ₽
                                        </span>
                                    </div>
                                </td>
                            ))}
                        </tr>

                        {/* Скорость */}
                        <tr>
                            <td className="fixed-column">Скорость</td>
                            {comparison.items.map(item => (
                                <td key={item.id}>
                                    <div className="speed-cell">
                                        <span className="speed-value">
                                            {item.speed} Мбит/с
                                        </span>
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
                                    <div className="features-cell">
                                        {item.features.length > 0 ? (
                                            <ul className="features-list">
                                                {item.features
                                                    .filter(feature => feature !== "Бесплатное подключение")
                                                    .map((feature, index) => (
                                                        <li key={index}>{feature}</li>
                                                    ))}
                                            </ul>
                                        ) : (
                                            <span className="no-features">Нет</span>
                                        )}
                                    </div>
                                </td>
                            ))}
                        </tr>

                        {/* Оценка ценности */}
                        <tr className="metrics-section">
                            <td className="fixed-column">Оценка ценности</td>
                            {comparison.items.map(item => (
                                <td key={item.id}>
                                    <div className="value-cell">
                                        <div className="value-bar">
                                            <div
                                                className="value-fill"
                                                style={{
                                                    width: `${Math.min(100, (1 / parseNumber(item.value_score)) * 100)}%`
                                                }}
                                            ></div>
                                        </div>
                                    </div>
                                </td>
                            ))}
                        </tr>

                        {/* Преимущества */}
                        <tr className="awards-section">
                            <td className="fixed-column">Преимущества</td>
                            {comparison.items.map(item => (
                                <td key={item.id}>
                                    <div className="awards-cell">
                                        {item.is_cheapest && (
                                            <span className="badge badge-price">
                                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                                                </svg>
                                                Самый дешевый
                                            </span>
                                        )}
                                        {item.is_fastest && (
                                            <span className="badge badge-speed">
                                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                    <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
                                                </svg>
                                                Самый быстрый
                                            </span>
                                        )}
                                        {item.is_best_value && (
                                            <span className="badge badge-value">
                                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                    <path d="M9 11l3 3L22 4"/>
                                                    <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
                                                </svg>
                                                Лучшее предложение
                                            </span>
                                        )}
                                        {item.has_most_features && (
                                            <span className="badge badge-features">
                                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                    <path d="M12 2v20m-8-10h16m-4-4l8 8-8 8"/>
                                                </svg>
                                                Больше услуг
                                            </span>
                                        )}
                                        {!item.is_cheapest && !item.is_fastest && !item.is_best_value && !item.has_most_features && (
                                            <span className="no-awards">—</span>
                                        )}
                                    </div>
                                </td>
                            ))}
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
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                    <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                                </svg>
                            </div>
                            <p>{recommendation}</p>
                        </div>
                    ))}
                </div>
            </div>

            <div className="comparison-footer">
                <button
                    onClick={() => navigate('/tariffs')}
                    className="btn btn-primary"
                >
                    Начать новое сравнение
                </button>
            </div>
        </div>
    );
};

export default TariffComparison;