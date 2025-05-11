import React from 'react';
import { Link } from 'react-router-dom';
import './NotFound.css';

const NotFound: React.FC = () => {
    return (
        <div className="not-found-container">
            <div className="not-found-content">
                <div className="not-found-illustration">
                    <div className="error-code">404</div>
                    <div className="floating-element element-1"></div>
                    <div className="floating-element element-2"></div>
                    <div className="floating-element element-3"></div>
                </div>

                <h1 className="not-found-title">Страница не найдена</h1>
                <p className="not-found-description">
                    К сожалению, запрашиваемая страница не существует или была перемещена.
                    Возможно, вы перешли по неверной ссылке или страница была удалена.
                </p>

                <div className="not-found-actions">
                    <Link to="/" className="btn btn-primary">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                            <polyline points="9 22 9 12 15 12 15 22"></polyline>
                        </svg>
                        На главную
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default NotFound;