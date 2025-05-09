import React, {useEffect, useState} from 'react';
import {Route, Routes, useNavigate} from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import Home from './components/Home';
import Profile from './components/profile/Profile';
import {authService} from './services/authService';

import './App.css';

const ProviderList = () => (
    <div className="page animate-fade-in">
        <h2>Список провайдеров</h2>
        <p>Выберите провайдера для просмотра тарифов</p>
    </div>
);

const TariffComparison = () => (
    <div className="page animate-fade-in">
        <h2>Сравнение тарифов</h2>
        <p>Сравните тарифы разных провайдеров</p>
    </div>
);

const App: React.FC = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(() => {
        return authService.isAuthenticated();
    });
    const [isScrolled, setIsScrolled] = useState(false);
    const navigate = useNavigate();


    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 10);
        };

        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const handleLogout = async () => {
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
        <div className="app">
            <Header
                isLoggedIn={isLoggedIn}
                isScrolled={isScrolled}
                onLogout={handleLogout}
            />

            <main>
                <Routes>
                    <Route path="/" element={<Home isLoggedIn={isLoggedIn}/>}/>
                    <Route path="/providers" element={<ProviderList/>}/>
                    <Route path="/comparison" element={<TariffComparison/>}/>
                    <Route path="/login" element={<Login/>}/>
                    <Route path="/register" element={<Register/>}/>
                    <Route path="/profile" element={<Profile/>}/>
                </Routes>
            </main>

            <Footer/>
        </div>
    );
};

export default App;