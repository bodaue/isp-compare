// frontend/src/contexts/ClickTrackingContext.tsx
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

interface ClickData {
    timestamp: number;
    elementType: string;
    elementText?: string;
    page: string;
    clickNumber: number;
}

interface UserSession {
    sessionId: string;
    startTime: number;
    endTime?: number;
    totalClicks: number;
    clickPath: ClickData[];
    goalReached: boolean;
    userPath: string[]; // страницы, которые посетил пользователь
}

interface ClickTrackingContextType {
    currentSession: UserSession | null;
    trackClick: (elementType: string, elementText?: string) => void;
    trackPageVisit: (page: string) => void;
    trackGoalReached: () => void;
    resetSession: () => void;
    getSessionStats: () => {
        totalClicks: number;
        sessionDuration: number;
        pagesVisited: number;
        goalReached: boolean;
    };
}

const ClickTrackingContext = createContext<ClickTrackingContextType | undefined>(undefined);

export const ClickTrackingProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [currentSession, setCurrentSession] = useState<UserSession | null>(null);

    // Инициализация сессии при первом заходе
    useEffect(() => {
        const existingSession = localStorage.getItem('clickTrackingSession');

        if (existingSession) {
            try {
                const session = JSON.parse(existingSession);
                // Проверяем, не истекла ли сессия (более 30 минут)
                const now = Date.now();
                if (now - session.startTime < 30 * 60 * 1000 && !session.goalReached) {
                    setCurrentSession(session);
                    return;
                }
            } catch (error) {
                console.error('Error parsing session data:', error);
            }
        }

        // Создаем новую сессию
        const newSession: UserSession = {
            sessionId: generateSessionId(),
            startTime: Date.now(),
            totalClicks: 0,
            clickPath: [],
            goalReached: false,
            userPath: []
        };

        setCurrentSession(newSession);
        localStorage.setItem('clickTrackingSession', JSON.stringify(newSession));
    }, []);

    // Сохранение сессии при изменениях
    useEffect(() => {
        if (currentSession) {
            localStorage.setItem('clickTrackingSession', JSON.stringify(currentSession));
        }
    }, [currentSession]);

    const generateSessionId = (): string => {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    };

    const trackClick = useCallback((elementType: string, elementText?: string) => {
        if (!currentSession || currentSession.goalReached) return;

        const clickData: ClickData = {
            timestamp: Date.now(),
            elementType,
            elementText,
            page: window.location.pathname,
            clickNumber: currentSession.totalClicks + 1
        };

        setCurrentSession(prev => {
            if (!prev) return prev;

            const updatedSession = {
                ...prev,
                totalClicks: prev.totalClicks + 1,
                clickPath: [...prev.clickPath, clickData]
            };

            console.log(`[Click Tracking] Click #${updatedSession.totalClicks}: ${elementType} on ${clickData.page}`, clickData);

            return updatedSession;
        });
    }, [currentSession]);

    const trackPageVisit = useCallback((page: string) => {
        if (!currentSession || currentSession.goalReached) return;

        setCurrentSession(prev => {
            if (!prev) return prev;

            // Добавляем страницу только если она отличается от последней
            const lastPage = prev.userPath[prev.userPath.length - 1];
            if (lastPage === page) return prev;

            console.log(`[Click Tracking] Page visit: ${page}`);

            return {
                ...prev,
                userPath: [...prev.userPath, page]
            };
        });
    }, [currentSession]);

    const trackGoalReached = useCallback(() => {
        if (!currentSession || currentSession.goalReached) return;

        setCurrentSession(prev => {
            if (!prev) return prev;

            const completedSession = {
                ...prev,
                endTime: Date.now(),
                goalReached: true
            };

            console.log('[Click Tracking] Goal reached!', {
                totalClicks: completedSession.totalClicks,
                duration: completedSession.endTime! - completedSession.startTime,
                path: completedSession.userPath
            });

            // Отправляем данные на сервер
            sendSessionData(completedSession);

            return completedSession;
        });
    }, [currentSession]);

    const resetSession = useCallback(() => {
        localStorage.removeItem('clickTrackingSession');

        const newSession: UserSession = {
            sessionId: generateSessionId(),
            startTime: Date.now(),
            totalClicks: 0,
            clickPath: [],
            goalReached: false,
            userPath: []
        };

        setCurrentSession(newSession);
        console.log('[Click Tracking] Session reset');
    }, []);

    const getSessionStats = useCallback(() => {
        if (!currentSession) {
            return {
                totalClicks: 0,
                sessionDuration: 0,
                pagesVisited: 0,
                goalReached: false
            };
        }

        const endTime = currentSession.endTime || Date.now();

        return {
            totalClicks: currentSession.totalClicks,
            sessionDuration: endTime - currentSession.startTime,
            pagesVisited: currentSession.userPath.length,
            goalReached: currentSession.goalReached
        };
    }, [currentSession]);

    const sendSessionData = async (session: UserSession) => {
        try {
            // Отправляем данные на сервер для аналитики
            await fetch('/api/analytics/user-session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    sessionId: session.sessionId,
                    startTime: session.startTime,
                    endTime: session.endTime,
                    totalClicks: session.totalClicks,
                    clickPath: session.clickPath,
                    userPath: session.userPath,
                    goalReached: session.goalReached,
                    sessionDuration: session.endTime! - session.startTime
                })
            });
        } catch (error) {
            console.error('Failed to send session data:', error);
        }
    };

    return (
        <ClickTrackingContext.Provider
            value={{
                currentSession,
                trackClick,
                trackPageVisit,
                trackGoalReached,
                resetSession,
                getSessionStats
            }}
        >
            {children}
        </ClickTrackingContext.Provider>
    );
};

export const useClickTracking = () => {
    const context = useContext(ClickTrackingContext);
    if (context === undefined) {
        throw new Error('useClickTracking must be used within a ClickTrackingProvider');
    }
    return context;
};