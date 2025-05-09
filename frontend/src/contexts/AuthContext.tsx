// src/contexts/AuthContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';

interface AuthContextType {
    isLoggedIn: boolean;
    login: (username: string, password: string) => Promise<void>;
    register: (data: any) => Promise<void>;
    logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [isLoggedIn, setIsLoggedIn] = useState(() => {
        return authService.isAuthenticated();
    });
    const navigate = useNavigate();

    useEffect(() => {
        setIsLoggedIn(authService.isAuthenticated());
    }, []);

    const login = async (username: string, password: string) => {
        try {
            await authService.login({ username, password });
            setIsLoggedIn(true);
            navigate('/');
        } catch (error) {
            throw error;
        }
    };

    const register = async (data: any) => {
        try {
            await authService.register(data);
            setIsLoggedIn(true);
            navigate('/');
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

    return (
        <AuthContext.Provider value={{ isLoggedIn, login, register, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};