import React, {useEffect, useState} from 'react';
import {Link, useParams} from 'react-router-dom';
import {providerService} from '../../services/providerService';
import {tariffService} from '../../services/tariffService';
import {Provider, Tariff} from '../../types/provider.types';
import TariffCard from '../tariffs/TariffCard';
import styles from './ProviderDetail.module.css';

const ProviderDetail: React.FC = () => {
    const {id} = useParams<{ id: string }>();
    const [provider, setProvider] = useState<Provider | null>(null);
    const [tariffs, setTariffs] = useState<Tariff[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        if (id) {
            fetchProviderData();
        }
    }, [id]);

    const fetchProviderData = async () => {
        try {
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

    if (loading) {
        return (
            <div className={styles.providerDetailLoading}>
                <div className={styles.loadingSpinner}></div>
                Загрузка информации о провайдере...
            </div>
        );
    }

    if (error || !provider) {
        return (
            <div className={styles.providerDetailError}>
                <p>{error || 'Провайдер не найден'}</p>
                <Link to="/providers" className="btn btn-primary">
                    Вернуться к списку провайдеров
                </Link>
            </div>
        );
    }

    return (
        <div className={styles.providerDetailContainer}>
            <div className={styles.breadcrumb}>
                <Link to="/providers">Провайдеры</Link>
                <span> / </span>
                <span>{provider.name}</span>
            </div>

            <div className={styles.providerDetailHeader}>
                <div className={styles.providerDetailLogo}>
                    {provider.logo_url ? (
                        <img src={provider.logo_url} alt={provider.name}/>
                    ) : (
                        <div className={styles.providerDetailPlaceholder}>
                            {provider.name.charAt(0)}
                        </div>
                    )}
                </div>
                <div className={styles.providerDetailInfo}>
                    <h1>{provider.name}</h1>
                    {provider.description && (
                        <p className={styles.providerDetailDescription}>{provider.description}</p>
                    )}
                    {provider.rating !== null && (
                        <div className={styles.providerDetailRating}>
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
                    {provider.website && (

                            href={provider.website}
                            target="_blank"
                            rel="noopener noreferrer"
                            className={styles.providerWebsite}
                        >
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
                                <path d="M2 17l10 5 10-5"></path>
                                <path d="M2 12l10 5 10-5"></path>
                            </svg>
                            Официальный сайт
                        </a>
                    )}
                </div>
            </div>

            <div className={styles.providerTabs}>
                <button className={`${styles.tabButton} ${styles.active}`}>
                    Тарифы ({tariffs.length})
                </button>
                <button className={styles.tabButton}>
                    Отзывы
                </button>
            </div>

            <div className={styles.providerTariffs}>
                <h2>Тарифные планы</h2>
                {tariffs.length > 0 ? (
                    <div className={styles.tariffsGrid}>
                        {tariffs.map((tariff) => (
                            <TariffCard key={tariff.id} tariff={tariff} provider={provider}/>
                        ))}
                    </div>
                ) : (
                    <div className={styles.noTariffs}>
                        <p>Тарифы не найдены</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ProviderDetail;