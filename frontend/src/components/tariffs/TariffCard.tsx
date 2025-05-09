import React from 'react';
import {Provider, Tariff} from '@/types/provider.types.ts';
import styles from './TariffCard.module.css';

interface TariffCardProps {
    tariff: Tariff;
    provider?: Provider;
    showProvider?: boolean;
}

const TariffCard: React.FC<TariffCardProps> = ({tariff, provider, showProvider = false}) => {
    return (
        <div className={styles.tariffCard}>
            {showProvider && provider && (
                <div className={styles.tariffProvider}>
                    {provider.logo_url ? (
                        <img src={provider.logo_url} alt={provider.name}/>
                    ) : (
                        <div className={styles.providerMiniPlaceholder}>
                            {provider.name.charAt(0)}
                        </div>
                    )}
                    <span>{provider.name}</span>
                </div>
            )}

            <div className={styles.tariffHeader}>
                <h3>{tariff.name}</h3>
                <div className={styles.tariffPrice}>
                    {tariff.promo_price ? (
                        <>
                            <span className={styles.pricePromo}>{tariff.promo_price}</span>
                            <span className={styles.priceOriginal}>{tariff.price}</span>
                        </>
                    ) : (
                        <span className={styles.priceValue}>{tariff.price}</span>
                    )}
                    <span className={styles.priceCurrency}>₽/мес</span>
                </div>
            </div>

            {tariff.description && (
                <p className={styles.tariffDescription}>{tariff.description}</p>
            )}

            <div className={styles.tariffFeatures}>
                <div className={styles.tariffFeature}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"></path>
                    </svg>
                    <span>{tariff.speed} Мбит/с</span>
                </div>

                {(tariff.has_tv || tariff.has_phone) && (
                    <div className={styles.tariffFeature}>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                             strokeWidth="2">
                            <rect x="2" y="7" width="20" height="15" rx="2" ry="2"></rect>
                            <polyline points="17 2 12 7 7 2"></polyline>
                        </svg>
                        <span>
                            {[
                                tariff.has_tv && 'ТВ',
                                tariff.has_phone && 'Телефония'
                            ].filter(Boolean).join(' + ')}
                        </span>
                    </div>
                )}
            </div>

            <div className={styles.tariffFooter}>
                {tariff.promo_period && (
                    <div className={styles.tariffDetail}>
                        <span>Акция:</span>
                        <span>{tariff.promo_period} мес.</span>
                    </div>
                )}
                {tariff.connection_cost > 0 && (
                    <div className={styles.tariffDetail}>
                        <span>Подключение:</span>
                        <span>{tariff.connection_cost} ₽</span>
                    </div>
                )}
            </div>

            <button className={styles.tariffButton}>
                Подробнее
            </button>
        </div>
    );
};

export default TariffCard;