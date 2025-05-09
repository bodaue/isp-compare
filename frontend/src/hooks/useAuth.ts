import {useEffect, useState} from 'react';
import {useNavigate} from 'react-router-dom';
import {authService} from '../services/authService';

export const useAuth = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(() => {
        return authService.isAuthenticated();
    });
    const navigate = useNavigate();

    useEffect(() => {
        // Проверяем статус аутентификации при монтировании
        setIsLoggedIn(authService.isAuthenticated());
    }, []);

    const login = async (username: string, password: string) => {
        try {
            await authService.login({username, password});
            setIsLoggedIn(true);
            navigate('/');
            window.location.reload();
        } catch (error) {
            throw error;
        }
    };

    const register = async (data: any) => {
        try {
            await authService.register(data);
            setIsLoggedIn(true);
            navigate('/');
            window.location.reload();
        } catch (error) {
            throw error;
        }
    };

    const logout = async () => {
        try {
            await authService.logout();
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            setIsLoggedIn(false);
            navigate('/');
        }
    };

    return {
        isLoggedIn,
        login,
        register,
        logout
    };
};