// frontend/src/hooks/useToast.ts
import { useState, useCallback } from 'react';

export interface ToastItem {
    id: string;
    message: string;
    type?: 'info' | 'success' | 'warning' | 'error';
    duration?: number;
}

export const useToast = () => {
    const [toasts, setToasts] = useState<ToastItem[]>([]);

    const showToast = useCallback((
        message: string,
        type: 'info' | 'success' | 'warning' | 'error' = 'info',
        duration = 2000  // Уменьшено с 3000 до 2000
    ) => {
        const id = Date.now().toString();
        const newToast: ToastItem = {
            id,
            message,
            type,
            duration,
        };

        // Заменяем все существующие toasts новым
        setToasts([newToast]);
    }, []);

    const removeToast = useCallback((id: string) => {
        setToasts(prev => prev.filter(toast => toast.id !== id));
    }, []);

    return {
        toasts,
        showToast,
        removeToast,
    };
};