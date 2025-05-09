import React from 'react';
import { Link } from 'react-router-dom';
import { useProviders } from '../../hooks';
import './ProviderList.css';

const ProviderList: React.FC = () => {
    const { providers, loading, error, fetchProviders } = useProviders();

    if (loading) {
        return (
            <div className="provider-loading">
                <div className="loading-spinner"></div>
                Загрузка провайдеров...
            </div>
        );
    }

    if (error) {
        return (
            <div className="provider-error">
                <p>{error}</p>
                <button onClick={fetchProviders} className="btn btn-primary">
                    Повторить попытку
                </button>
            </div>
        );
    }

    return (
        <div className="provider-list-container">
            <div className="provider-header">
                <h2>Интернет-провайдеры</h2>
                <p>Выберите провайдера для просмотра тарифов и отзывов</p>
            </div>

            <div className="providers-grid">
                {providers.map((provider) => (
                    <Link to={`/providers/${provider.id}`} key={provider.id} className="provider-card">
                        <div className="provider-logo">
                            {provider.logo_url ? (
                                <img src={provider.logo_url} alt={provider.name} />
                            ) : (
                                <div className="provider-placeholder">
                                    {provider.name.charAt(0)}
                                </div>
                            )}
                        </div>
                        <div className="provider-info">
                            <h3>{provider.name}</h3>
                            {provider.description && (
                                <p className="provider-description">{provider.description}</p>
                            )}
                            {provider.rating !== null && (
                                <div className="provider-rating">
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
                        </div>
                        <div className="provider-arrow">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M9 18l6-6-6-6" />
                            </svg>
                        </div>
                    </Link>
                ))}
            </div>

            {providers.length === 0 && (
                <div className="no-providers">
                    <p>Провайдеры не найдены</p>
                </div>
            )}
        </div>
    );
};

export default ProviderList;