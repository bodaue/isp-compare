// frontend/src/components/tariffs/TariffCard.tsx
import React from 'react';
import {Provider, Tariff} from '../../types/provider.types';
import './TariffCard.css';

interface TariffCardProps {
    tariff: Tariff;
    provider?: Provider;
    showProvider?: boolean;
}

const TariffCard: React.FC<TariffCardProps> = ({tariff, provider, showProvider = false}) => {
    const getConnectionTypeLabel = (type: string) => {
        const labels: Record<string, string> = {
            FTTH: 'Оптоволокно',
            ADSL: 'ADSL',
            PON: 'PON',
            ETHERNET: 'Ethernet',
            WIMAX: 'WiMAX',
            LTE: 'LTE'
        };
        return labels[type] || type;
    };

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
                    <span className="price-value">{tariff.price}</span>
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

                <div className="tariff-feature">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M2 12a10 10 0 1 0 20 0a10 10 0 1 0 -20 0"></path>
                        <path d="M12 2a14.5 14.5 0 0 0 0 20a14.5 14.5 0 0 0 0 -20"></path>
                        <path d="M2 12h20"></path>
                    </svg>
                    <span>{getConnectionTypeLabel(tariff.connection_type)}</span>
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
                {tariff.connection_cost > 0 && (
                    <div className="tariff-detail">
                        <span>Подключение:</span>
                        <span>{tariff.connection_cost} ₽</span>
                    </div>
                )}
                {tariff.contract_period && (
                    <div className="tariff-detail">
                        <span>Контракт:</span>
                        <span>{tariff.contract_period} мес.</span>
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