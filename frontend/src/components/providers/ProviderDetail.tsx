import React, {useEffect, useState} from 'react';
import {Link, useParams} from 'react-router-dom';
import {providerService} from '../../services/providerService';
import {tariffService} from '../../services/tariffService';
import {Provider, Tariff} from '../../types/provider.types';
import TariffCard from '../tariffs/TariffCard';
import ReviewList from '../reviews/ReviewList';
import './ProviderDetail.css';

const ProviderDetail: React.FC = () => {
    const {id} = useParams<{ id: string }>();
    const [provider, setProvider] = useState<Provider | null>(null);
    const [tariffs, setTariffs] = useState<Tariff[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [activeTab, setActiveTab] = useState('tariffs');

    useEffect(() => {
        if (id) {
            fetchProviderData();
        }
    }, [id]);

    const fetchProviderData = async () => {
        try {
            setLoading(true);
            const [providerData, tariffsData] = await Promise.all([
                providerService.getProviderById(id!),
                tariffService.getProviderTariffs(id!)
            ]);
            setProvider(providerData);
            setTariffs(tariffsData);
            setError('');
        } catch (err: any) {
            setError('Ошибка при загрузке данных провайдера');
        } finally {
            setLoading(false);
        }
    };

    // Новая функция для обновления данных провайдера
    const refreshProviderData = async () => {
        try {
            if (id) {
                const providerData = await providerService.getProviderById(id);
                setProvider(providerData);
            }
        } catch (err) {
            console.error("Error refreshing provider data:", err);
        }
    };

    if (loading) {
        return (
            <div className="provider-detail-loading">
                <div className="loading-spinner"></div>
                Загрузка информации о провайдере...
            </div>
        );
    }

    if (error || !provider) {
        return (
            <div className="provider-detail-error">
                <p>{error || 'Провайдер не найден'}</p>
                <Link to="/providers" className="btn btn-primary">
                    Вернуться к списку провайдеров
                </Link>
            </div>
        );
    }

    return (
        <div className="provider-detail-container">
            <div className="breadcrumb">
                <Link to="/providers">Провайдеры</Link>
                <span> / </span>
                <span>{provider.name}</span>
            </div>

            <div className="provider-detail-header">
                <div className="provider-detail-logo">
                    {provider.logo_url ? (
                        <img src={provider.logo_url} alt={provider.name}/>
                    ) : (
                        <div className="provider-detail-placeholder">
                            {provider.name.charAt(0)}
                        </div>
                    )}
                </div>
                <div className="provider-detail-info">
                    <h1>{provider.name}</h1>
                    {provider.description && (
                        <p className="provider-detail-description">{provider.description}</p>
                    )}
                    {provider.rating !== null && (
                        <div className="provider-detail-rating">
                            <div className="rating-stars">
                                {[...Array(5)].map((_, index) => (
                                    <span
                                        key={index}
                                        className={`star ${index < Math.round(provider.rating!) ? 'filled' : ''}`}
                                    >
                                        ★
                                    </span>
                                ))}
                            </div>
                            <span className="rating-value">{provider.rating.toFixed(1)}</span>
                        </div>
                    )}
                    {provider.website && (

                        <a href={provider.website}
                           target="_blank"
                           rel="noopener noreferrer"
                           className="provider-website"
                        >
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                 strokeWidth="2">
                                <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
                                <path d="M2 17l10 5 10-5"></path>
                                <path d="M2 12l10 5 10-5"></path>
                            </svg>
                            Официальный сайт
                        </a>
                    )}
                </div>
            </div>

            <div className="provider-tabs">
                <button
                    className={`tab-button ${activeTab === 'tariffs' ? 'active' : ''}`}
                    onClick={() => setActiveTab('tariffs')}
                >
                    Тарифы ({tariffs.length})
                </button>
                <button
                    className={`tab-button ${activeTab === 'reviews' ? 'active' : ''}`}
                    onClick={() => setActiveTab('reviews')}
                >
                    Отзывы ({provider.reviews_count})
                </button>
            </div>

            {activeTab === 'tariffs' && (
                <div className="provider-tariffs">
                    <h2>Тарифные планы</h2>
                    {tariffs.length > 0 ? (
                        <div className="tariffs-grid">
                            {tariffs.map((tariff) => (
                                <TariffCard key={tariff.id} tariff={tariff} provider={provider}/>
                            ))}
                        </div>
                    ) : (
                        <div className="no-tariffs">
                            <p>Тарифы не найдены</p>
                        </div>
                    )}
                </div>
            )}

            {activeTab === 'reviews' && (
                <ReviewList
                    providerId={provider.id}
                    onReviewChange={refreshProviderData}
                />
            )}
        </div>
    );
};

export default ProviderDetail;