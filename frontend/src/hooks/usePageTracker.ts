// frontend/src/hooks/usePageTracker.ts
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useClickTracking } from '../contexts/ClickTrackingContext';

export const usePageTracker = () => {
    const location = useLocation();
    const { trackPageVisit } = useClickTracking();

    useEffect(() => {
        // Трекаем посещение страницы при изменении location
        trackPageVisit(location.pathname);
    }, [location.pathname, trackPageVisit]);
};