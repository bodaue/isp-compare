import React from 'react';
import {Link} from 'react-router-dom';
import './Home.css';

interface HomeProps {
    isLoggedIn: boolean;
}

const Home: React.FC<HomeProps> = ({isLoggedIn}) => {
    return (
        <div className="home-page">
            {}
            <section className="hero-section">
                <div className="hero-content">
                    <h1 className="hero-title">
                        Найдите идеального <span className="gradient-text">интернет-провайдера</span>
                    </h1>
                    <p className="hero-subtitle">
                        Сравните тарифы, скорость и качество услуг интернет-провайдеров в Волгограде
                    </p>
                    <div className="hero-buttons">
                        <Link to="/providers" className="btn btn-primary" data-track-click="cta-primary">
                            Начать поиск
                        </Link>
                        <Link to="/tariffs" className="btn btn-secondary" data-track-click="cta-secondary">
                            Сравнить тарифы
                        </Link>
                    </div>
                </div>
                <div className="hero-image">
                    <div className="hero-illustration">
                        <div className="floating-element element-1"></div>
                        <div className="floating-element element-2"></div>
                        <div className="floating-element element-3"></div>
                    </div>
                </div>
            </section>

            {}
            <section className="features-section">
                <h2 className="section-title">Почему выбирают нас</h2>
                <div className="features-grid">
                    <div className="feature-card">
                        <div className="feature-icon">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                 strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M20 6L9 17l-5-5"></path>
                            </svg>
                        </div>
                        <h3>Актуальные данные</h3>
                        <p>Постоянно обновляемая информация о тарифах и услугах провайдеров</p>
                    </div>
                    <div className="feature-card">
                        <div className="feature-icon">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                 strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"></path>
                            </svg>
                        </div>
                        <h3>Быстрое сравнение</h3>
                        <p>Сравнивайте до 5 тарифов одновременно по ключевым параметрам</p>
                    </div>
                    <div className="feature-card">
                        <div className="feature-icon">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                 strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path
                                    d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path>
                            </svg>
                        </div>
                        <h3>Отзывы пользователей</h3>
                        <p>Реальные отзывы от пользователей услуг различных провайдеров</p>
                    </div>
                    <div className="feature-card">
                        <div className="feature-icon">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                 strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                                <line x1="9" y1="9" x2="15" y2="15"></line>
                                <line x1="15" y1="9" x2="9" y2="15"></line>
                            </svg>
                        </div>
                        <h3>Без рекламы</h3>
                        <p>Независимый сервис без скрытой рекламы и предвзятости</p>
                    </div>
                </div>
            </section>

            {}
            {!isLoggedIn && (
                <section className="cta-section">
                    <div className="cta-content">
                        <h2>Готовы найти лучший интернет?</h2>
                        <p>Присоединяйтесь к пользователям, которые уже нашли идеального провайдера</p>
                        <Link to="/register" className="btn btn-primary" data-track-click="cta-register">
                            Создать аккаунт
                        </Link>
                    </div>
                </section>
            )}
        </div>
    );
};

export default Home;