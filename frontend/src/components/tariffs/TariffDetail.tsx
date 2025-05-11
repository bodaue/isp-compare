import React, {useEffect, useState} from 'react';
import {Link, useParams} from 'react-router-dom';
import {tariffService} from '../../services/tariffService';
import {providerService} from '../../services/providerService';
import {Provider, Tariff} from '../../types/provider.types';
import Modal from '../common/Modal';
import './TariffDetail.css';

const TariffDetail: React.FC = () => {
    const {id} = useParams<{ id: string }>();
    const [tariff, setTariff] = useState<Tariff | null>(null);
    const [provider, setProvider] = useState<Provider | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [showConnectModal, setShowConnectModal] = useState(false);
    const [copiedPhone, setCopiedPhone] = useState(false);

    useEffect(() => {
        if (id) {
            fetchTariffData();
        }
    }, [id]);

    const fetchTariffData = async () => {
        try {
            const tariffData = await tariffService.getTariffById(id!);
            setTariff(tariffData);

            // Загружаем информацию о провайдере
            const providerData = await providerService.getProviderById(tariffData.provider_id);
            setProvider(providerData);

            setError('');
        } catch (err: any) {
            setError('Ошибка при загрузке данных тарифа');
        } finally {
            setLoading(false);
        }
    };

    const handleConnect = () => {
        setShowConnectModal(true);
    };

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
        setCopiedPhone(true);

        // Сбрасываем состояние через 2 секунды
        setTimeout(() => {
            setCopiedPhone(false);
        }, 2000);
    };

    if (loading) {
        return (
            <div className="tariff-detail-loading">
                <div className="loading-spinner"></div>
                Загрузка информации о тарифе...
            </div>
        );
    }

    if (error || !tariff || !provider) {
        return (
            <div className="tariff-detail-error">
                <p>{error || 'Тариф не найден'}</p>
                <Link to="/tariffs" className="btn btn-primary">
                    Вернуться к списку тарифов
                </Link>
            </div>
        );
    }

    return (
        <div className="tariff-detail-container">
            <div className="breadcrumb">
                <Link to="/providers">Провайдеры</Link>
                <span> / </span>
                <Link to={`/providers/${provider.id}`}>{provider.name}</Link>
                <span> / </span>
                <span>{tariff.name}</span>
            </div>

            <div className="tariff-detail-header">
                <div className="tariff-detail-title">
                    <h1>{tariff.name}</h1>
                    <div className="provider-info">
                        <Link to={`/providers/${provider.id}`} className="provider-link">
                            {provider.logo_url ? (
                                <img src={provider.logo_url} alt={provider.name}/>
                            ) : (
                                <div className="provider-placeholder">
                                    {provider.name.charAt(0)}
                                </div>
                            )}
                            <span>{provider.name}</span>
                        </Link>
                    </div>
                </div>
                <div className="tariff-detail-price">
                    {tariff.promo_price ? (
                        <>
                            <div className="promo-price">
                                <span className="value">{tariff.promo_price}</span>
                                <span className="currency">₽/мес</span>
                            </div>
                            <div className="original-price">
                                <span className="value">{tariff.price}</span>
                                <span className="currency">₽/мес</span>
                            </div>
                            {tariff.promo_period && (
                                <div className="promo-period">
                                    Акция на {tariff.promo_period} мес.
                                </div>
                            )}
                        </>
                    ) : (
                        <div className="price">
                            <span className="value">{tariff.price}</span>
                            <span className="currency">₽/мес</span>
                        </div>
                    )}
                </div>
            </div>

            {tariff.description && (
                <div className="tariff-detail-section">
                    <h2>Описание</h2>
                    <p>{tariff.description}</p>
                </div>
            )}

            <div className="tariff-detail-section">
                <h2>Характеристики</h2>
                <div className="characteristics-grid">
                    <div className="characteristic">
                        <div className="icon">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                 strokeWidth="2">
                                <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"></path>
                            </svg>
                        </div>
                        <div className="info">
                            <h3>Скорость</h3>
                            <p>{tariff.speed} Мбит/с</p>
                        </div>
                    </div>

                    {tariff.has_tv && (
                        <div className="characteristic">
                            <div className="icon">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                     strokeWidth="2">
                                    <rect x="2" y="7" width="20" height="15" rx="2" ry="2"></rect>
                                    <polyline points="17 2 12 7 7 2"></polyline>
                                </svg>
                            </div>
                            <div className="info">
                                <h3>Телевидение</h3>
                                <p>Включено</p>
                            </div>
                        </div>
                    )}

                    {tariff.has_phone && (
                        <div className="characteristic">
                            <div className="icon">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                     strokeWidth="2">
                                    <path
                                        d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
                                </svg>
                            </div>
                            <div className="info">
                                <h3>Телефония</h3>
                                <p>Включено</p>
                            </div>
                        </div>
                    )}

                    <div className="characteristic">
                        <div className="icon">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                 strokeWidth="2">
                                <circle cx="12" cy="12" r="10"></circle>
                                <path d="M12 6v6l4 2"></path>
                            </svg>
                        </div>
                        <div className="info">
                            <h3>Подключение</h3>
                            <p>{tariff.connection_cost > 0 ? `${tariff.connection_cost} ₽` : 'Бесплатно'}</p>
                        </div>
                    </div>
                </div>
            </div>

            <div className="tariff-detail-actions">
                <button className="btn btn-primary" onClick={handleConnect}>
                    Подключить тариф
                </button>
                <Link to={`/providers/${provider.id}`} className="btn btn-secondary">
                    Все тарифы {provider.name}
                </Link>
            </div>

            <Modal
                isOpen={showConnectModal}
                onClose={() => setShowConnectModal(false)}
                title="Подключение тарифа"
            >
                <div className="connect-modal-content">
                    <div className="connect-info">
                        <h3>Как подключить тариф "{tariff.name}"</h3>
                        <p>Для подключения тарифа свяжитесь с провайдером {provider.name} одним из следующих
                            способов:</p>
                    </div>

                    <div className="provider-contacts">
                        <div className="contact-item">
                            <div className="contact-icon">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                     strokeWidth="2">
                                    <path
                                        d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
                                </svg>
                            </div>
                            <div className="contact-info">
                                <h4>Позвоните по телефону</h4>
                                <p>{provider.phone}</p>

                                <button
                                    className={`btn btn-secondary ${copiedPhone ? 'btn-success-subtle' : ''}`}
                                    onClick={() => copyToClipboard(provider.phone)}
                                >
                                    {copiedPhone ? (
                                        <>
                                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                                                 stroke="currentColor" strokeWidth="2">
                                                <path d="M20 6L9 17l-5-5"></path>
                                            </svg>
                                            Скопировано
                                        </>
                                    ) : (
                                        <>
                                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                                                 stroke="currentColor" strokeWidth="2">
                                                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                                                <path
                                                    d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                                            </svg>
                                            Скопировать номер
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>

                        <div className="contact-item">
                            <div className="contact-icon">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                     strokeWidth="2">
                                    <circle cx="12" cy="12" r="10"></circle>
                                    <line x1="2" y1="12" x2="22" y2="12"></line>
                                    <path
                                        d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
                                </svg>
                            </div>
                            <div className="contact-info">
                                {tariff.url ? (
                                    // Если есть ссылка на конкретный тариф
                                    <>
                                        <h4>Перейдите на страницу тарифа</h4>
                                        <p>{new URL(tariff.url).hostname}</p>

                                        <a href={tariff.url}
                                           target="_blank"
                                           rel="noopener noreferrer"
                                           className="btn btn-primary"
                                           style={{width: 'auto', display: 'inline-block'}}>
                                            Открыть страницу тарифа
                                        </a>
                                    </>
                                ) : (
                                    <>
                                        <h4>Перейдите на сайт</h4>
                                        <p>{provider.website}</p>
                                        <a href={provider.website}
                                           target="_blank"
                                           rel="noopener noreferrer"
                                           className="btn btn-primary"
                                           style={{width: 'auto', display: 'inline-block'}}>
                                            Открыть сайт
                                        </a>
                                    </>
                                )}
                            </div>
                        </div>
                    </div>

                    <div className="connect-note">
                        <p>При обращении сообщите, что вас интересует тариф "{tariff.name}"</p>
                    </div>
                </div>
            </Modal>
        </div>
    );
};

export default TariffDetail;