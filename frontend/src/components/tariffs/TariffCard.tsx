import React from 'react';
import {Provider, Tariff} from '../../types/provider.types';
import './TariffCard.css';

interface TariffCardProps {
    tariff: Tariff;
    provider?: Provider;
    showProvider?: boolean;
}

const TariffCard: React.FC<TariffCardProps> = ({tariff, provider, showProvider = false}) => {
    return (
        <div className="tariff-card">
            {showProvider && provider && (
                <div className="tariff-provider">
                    {provider.logo_url ? (
                        <img src={provider.logo_url} alt={provider.name}/>
                    ) : (
                        <div className="provider-mini-placeholder">
                            {provider.name.charAt(0)}
                        </div>
                    )}
                    <span>{provider.name}</span>
                </div>
            )}

            <div className="tariff-header">
                <h3>{tariff.name}</h3>
                <div className="tariff-price">
                    {tariff.promo_price ? (
                        <>
                            <span className="price-promo">{tariff.promo_price}</span>
                            <span className="price-original">{tariff.price}</span>
                        </>
                    ) : (
                        <span className="price-value">{tariff.price}</span>
                    )}
                    <span className="price-currency">₽/мес</span>
                </div>
            </div>

            {tariff.description && (
                <p className="tariff-description">{tariff.description}</p>
            )}

            <div className="tariff-features">
                <div className="tariff-feature">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"></path>
                    </svg>
                    <span>{tariff.speed} Мбит/с</span>
                </div>

                {(tariff.has_tv || tariff.has_phone) && (
                    <div className="tariff-feature">
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

            <div className="tariff-footer">
                {tariff.promo_period && (
                    <div className="tariff-detail">
                        <span>Акция:</span>
                        <span>{tariff.promo_period} мес.</span>
                    </div>
                )}
                {tariff.connection_cost > 0 && (
                    <div className="tariff-detail">
                        <span>Подключение:</span>
                        <span>{tariff.connection_cost} ₽</span>
                    </div>
                )}
            </div>

            <button className="tariff-button">
                Подробнее
            </button>
        </div>
    );
};

export default TariffCard;