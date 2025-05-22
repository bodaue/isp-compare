// frontend/src/components/debug/AnalyticsDebugPanel.tsx
import React, { useState, useEffect } from 'react';
import { useClickTracking } from '../../contexts/ClickTrackingContext';
import './AnalyticsDebugPanel.css';

const AnalyticsDebugPanel: React.FC = () => {
    const { currentSession, getSessionStats, resetSession } = useClickTracking();
    const [isVisible, setIsVisible] = useState(false);
    const [stats, setStats] = useState(getSessionStats());

    useEffect(() => {
        const interval = setInterval(() => {
            setStats(getSessionStats());
        }, 1000);

        return () => clearInterval(interval);
    }, [getSessionStats]);

    const formatDuration = (ms: number) => {
        const seconds = Math.floor(ms / 1000);
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    };

    const exportSessionData = () => {
        if (!currentSession) return;

        const dataStr = JSON.stringify(currentSession, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `session-${currentSession.sessionId}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    };

    if (!isVisible) {
        return (
            <button
                className="analytics-toggle"
                onClick={() => setIsVisible(true)}
                title="Показать аналитику кликов"
            >
                📊
            </button>
        );
    }

    return (
        <div className="analytics-debug-panel">
            <div className="panel-header">
                <h3>📊 Аналитика кликов</h3>
                <button
                    className="close-btn"
                    onClick={() => setIsVisible(false)}
                    title="Скрыть панель"
                >
                    ✕
                </button>
            </div>

            <div className="panel-content">
                <div className="stats-grid">
                    <div className="stat-item">
                        <div className="stat-label">Всего кликов</div>
                        <div className="stat-value clicks">{stats.totalClicks}</div>
                    </div>

                    <div className="stat-item">
                        <div className="stat-label">Время на сайте</div>
                        <div className="stat-value">{formatDuration(stats.sessionDuration)}</div>
                    </div>

                    <div className="stat-item">
                        <div className="stat-label">Страниц посещено</div>
                        <div className="stat-value">{stats.pagesVisited}</div>
                    </div>

                    <div className="stat-item">
                        <div className="stat-label">Цель достигнута</div>
                        <div className={`stat-value ${stats.goalReached ? 'goal-reached' : 'goal-not-reached'}`}>
                            {stats.goalReached ? '✅ Да' : '❌ Нет'}
                        </div>
                    </div>
                </div>

                {currentSession && currentSession.clickPath.length > 0 && (
                    <div className="click-history">
                        <h4>История кликов:</h4>
                        <div className="click-list">
                            {currentSession.clickPath.slice(-5).map((click, index) => (
                                <div key={index} className="click-item">
                                    <span className="click-number">#{click.clickNumber}</span>
                                    <span className="click-type">{click.elementType}</span>
                                    {click.elementText && (
                                        <span className="click-text">"{click.elementText}"</span>
                                    )}
                                    <span className="click-page">{click.page}</span>
                                </div>
                            ))}
                            {currentSession.clickPath.length > 5 && (
                                <div className="click-item more">
                                    ... и еще {currentSession.clickPath.length - 5} кликов
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {currentSession && currentSession.userPath.length > 0 && (
                    <div className="user-path">
                        <h4>Путь пользователя:</h4>
                        <div className="path-list">
                            {currentSession.userPath.map((page, index) => (
                                <React.Fragment key={index}>
                                    <span className="path-item">{page}</span>
                                    {index < currentSession.userPath.length - 1 && (
                                        <span className="path-arrow">→</span>
                                    )}
                                </React.Fragment>
                            ))}
                        </div>
                    </div>
                )}

                <div className="panel-actions">
                    <button
                        className="btn btn-secondary btn-sm"
                        onClick={exportSessionData}
                        disabled={!currentSession}
                    >
                        📄 Экспорт данных
                    </button>
                    <button
                        className="btn btn-warning btn-sm"
                        onClick={resetSession}
                    >
                        🔄 Сбросить сессию
                    </button>
                </div>
            </div>
        </div>
    );
};

export default AnalyticsDebugPanel;