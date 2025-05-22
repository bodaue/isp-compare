// frontend/src/hooks/useClickTracker.ts
import { useEffect } from 'react';
import { useClickTracking } from '../contexts/ClickTrackingContext';

export const useClickTracker = () => {
    const { trackClick } = useClickTracking();

    useEffect(() => {
        const handleClick = (event: MouseEvent) => {
            const target = event.target as HTMLElement;

            // Находим ближайший элемент с data-track-click атрибутом
            const trackableElement = target.closest('[data-track-click]') as HTMLElement;

            if (!trackableElement) return;

            const elementType = trackableElement.getAttribute('data-track-click') || 'unknown';
            const elementText = getElementText(trackableElement);

            // Исключаем некоторые типы кликов, которые не должны считаться
            if (shouldIgnoreClick(trackableElement, elementType)) return;

            trackClick(elementType, elementText);
        };

        // Используем event delegation для отслеживания всех кликов
        document.addEventListener('click', handleClick, true);

        return () => {
            document.removeEventListener('click', handleClick, true);
        };
    }, [trackClick]);

    const getElementText = (element: HTMLElement): string => {
        // Для кнопок и ссылок берем текстовое содержимое
        if (element.tagName === 'BUTTON' || element.tagName === 'A') {
            return element.textContent?.trim() || '';
        }

        // Для карточек ищем заголовок
        if (element.classList.contains('tariff-card') || element.classList.contains('provider-card')) {
            const title = element.querySelector('h3, h2, .tariff-name, .provider-name');
            return title?.textContent?.trim() || 'Card';
        }

        // Для других элементов
        const title = element.getAttribute('title') || element.getAttribute('aria-label');
        if (title) return title;

        return element.textContent?.trim().substring(0, 50) || 'Unknown';
    };

    const shouldIgnoreClick = (element: HTMLElement, elementType: string): boolean => {
        // Игнорируем клики по логотипу (возврат на главную)
        if (elementType === 'logo') return true;

        // Игнорируем клики по элементам footer
        if (element.closest('.footer')) return true;

        // Игнорируем клики по элементам внутри модальных окон (кроме основных действий)
        if (element.closest('.modal-overlay') && !element.closest('.modal-content [data-track-click]')) {
            return true;
        }

        // Игнорируем клики по disabled элементам
        if (element.hasAttribute('disabled')) return true;

        return false;
    };
};