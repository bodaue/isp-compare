import React from 'react';
import {Link} from 'react-router-dom';
import {useProviders} from '../../hooks';
import styles from './ProviderList.module.css';

const ProviderList: React.FC = () => {
    const {providers, loading, error, fetchProviders} = useProviders();

    if (loading) {
        return (
            <div className={styles.providerLoading}>
                <div className={styles.loadingSpinner}></div>
                Загрузка провайдеров...
            </div>
        );
    }

    if (error) {
        return (
            <div className={styles.providerError}>
                <p>{error}</p>
                <button onClick={fetchProviders} className="btn btn-primary">
                    Повторить попытку
                </button>
            </div>
        );
    }

    return (
        <div className={styles.providerListContainer}>
            <div className={styles.providerHeader}>
                <h2>Интернет-провайдеры</h2>
                <p>Выберите провайдера для просмотра тарифов и отзывов</p>
            </div>

            <div className={styles.providersGrid}>
                {providers.map((provider) => (
                    <Link to={`/providers/${provider.id}`} key={provider.id} className={styles.providerCard}>
                        <div className={styles.providerLogo}>
                            {provider.logo_url ? (
                                <img src={provider.logo_url} alt={provider.name}/>
                            ) : (
                                <div className={styles.providerPlaceholder}>
                                    {provider.name.charAt(0)}
                                </div>
                            )}
                        </div>
                        <div className={styles.providerInfo}>
                            <h3>{provider.name}</h3>
                            {provider.description && (
                                <p className={styles.providerDescription}>{provider.description}</p>
                            )}
                            {provider.rating !== null && (
                                <div className={styles.providerRating}>
                                    <div className={styles.ratingStars}>
                                        {[...Array(5)].map((_, index) => (
                                            <span
                                                key={index}
                                                className={`${styles.star} ${index < Math.round(provider.rating!) ? styles.filled : ''}`}
                                            >
                                                ★
                                            </span>
                                        ))}
                                    </div>
                                    <span className={styles.ratingValue}>{provider.rating.toFixed(1)}</span>
                                </div>
                            )}
                        </div>
                        <div className={styles.providerArrow}>
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                 strokeWidth="2">
                                <path d="M9 18l6-6-6-6"/>
                            </svg>
                        </div>
                    </Link>
                ))}
            </div>

            {providers.length === 0 && (
                <div className={styles.noProviders}>
                    <p>Провайдеры не найдены</p>
                </div>
            )}
        </div>
    );
};

export default ProviderList;