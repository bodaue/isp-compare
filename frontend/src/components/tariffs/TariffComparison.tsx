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
                                        <div className="provider-name">{item.provider_name}</div>
                                        <div className="tariff-name">{item.name}</div>
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
                        <tr>
                            <td className="fixed-column">Цена</td>
                            {comparison.items.map(item => (
                                <td key={item.id}>
                                    <div className="price-cell">
                                        <span className={`current-price ${item.is_promo ? 'promo' : ''}`}>
                                            {formatPrice(item.current_price)} ₽
                                        </span>
                                        {item.is_promo && (
                                            <span className="original-price">
                                                {formatPrice(item.original_price)} ₽
                                            </span>
                                        )}
                                        {item.is_cheapest && (
                                            <span className="badge badge-success">Самый дешевый</span>
                                        )}
                                    </div>
                                </td>
                            ))}
                        </tr>
                        <tr>
                            <td className="fixed-column">Скорость</td>
                            {comparison.items.map(item => (
                                <td key={item.id}>
                                    <div className="speed-cell">
                                        <span>{item.speed} Мбит/с</span>
                                        {item.is_fastest && (
                                            <span className="badge badge-success">Самый быстрый</span>
                                        )}
                                    </div>
                                </td>
                            ))}
                        </tr>
                        <tr>
                            <td className="fixed-column">Дополнительные услуги</td>
                            {comparison.items.map(item => (
                                <td key={item.id}>
                                    <div className="features-cell">
                                        {item.features.length > 0 ? (
                                            <ul className="features-list">
                                                {item.features.map((feature, index) => (
                                                    <li key={index}>{feature}</li>
                                                ))}
                                            </ul>
                                        ) : (
                                            <span className="no-features">—</span>
                                        )}
                                        {item.has_most_features && (
                                            <span className="badge badge-info">Больше всего услуг</span>
                                        )}
                                    </div>
                                </td>
                            ))}
                        </tr>
                        <tr>
                            <td className="fixed-column">Стоимость подключения</td>
                            {comparison.items.map(item => (
                                <td key={item.id}>
                                    {item.connection_cost !== null ? (
                                        parseNumber(item.connection_cost) === 0 ? (
                                            <span className="free-connection">Бесплатно</span>
                                        ) : (
                                            `${formatPrice(item.connection_cost)} ₽`
                                        )
                                    ) : (
                                        '—'
                                    )}
                                </td>
                            ))}
                        </tr>
                        <tr>
                            <td className="fixed-column">Цена за Мбит/с</td>
                            {comparison.items.map(item => (
                                <td key={item.id}>
                                    {parseNumber(item.price_per_mbps).toFixed(2)} ₽
                                </td>
                            ))}
                        </tr>
                        <tr>
                            <td className="fixed-column">Годовая стоимость</td>
                            {comparison.items.map(item => (
                                <td key={item.id}>
                                    {formatPrice(item.yearly_cost)} ₽
                                </td>
                            ))}
                        </tr>
                        <tr>
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
                                        {item.is_best_value && (
                                            <span className="badge badge-success">Лучшее предложение</span>
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