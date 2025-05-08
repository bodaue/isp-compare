// Modern App.tsx with clickable logo and fixed navigation
import React, {useEffect, useState} from 'react';
import {Link, Route, Routes, useLocation, useNavigate} from 'react-router-dom';
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import Home from './components/Home';
import Profile from './components/profile/Profile';

import './App.css';
// Placeholder components with modern styling
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
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [isScrolled, setIsScrolled] = useState(false);
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        // Проверяем наличие токена при загрузке
        const token = localStorage.getItem('accessToken');
        setIsLoggedIn(!!token);
    }, []);

    useEffect(() => {
        // Handle scroll effect for header
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 10);
        };

        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const handleLogout = () => {
        // Удаляем токен
        localStorage.removeItem('accessToken');
        setIsLoggedIn(false);
        navigate('/');
    };

    return (
        <div className="app">
            <header className={`app-header ${isScrolled ? 'scrolled' : ''}`}>
                <div className="header-container">
                    <h1>
                        <Link to="/">ISP Compare</Link>
                    </h1>
                    <nav>
                        <ul>
                            <li>
                                <Link to="/providers" className={location.pathname === '/providers' ? 'active' : ''}>
                                    Провайдеры
                                </Link>
                            </li>
                            <li>
                                <Link to="/comparison" className={location.pathname === '/comparison' ? 'active' : ''}>
                                    Сравнение
                                </Link>
                            </li>
                            {isLoggedIn ? (
                                <>
                                    <li>
                                        <Link to="/profile"
                                              className={location.pathname === '/profile' ? 'active' : ''}>
                                            Профиль
                                        </Link>
                                    </li>
                                    <li>
                                        <button onClick={handleLogout}>Выход</button>
                                    </li>
                                </>
                            ) : (
                                <>
                                    <li>
                                        <Link to="/login" className={location.pathname === '/login' ? 'active' : ''}>
                                            Вход
                                        </Link>
                                    </li>
                                    <li>
                                        <Link to="/register"
                                              className={location.pathname === '/register' ? 'active' : ''}>
                                            Регистрация
                                        </Link>
                                    </li>
                                </>
                            )}
                        </ul>
                    </nav>
                </div>
            </header>

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

            <footer>
                <p>© 2025 ISP Compare | Керимов Тимур Илгарович | ВКР ПРИН-467</p>
            </footer>
        </div>
    );
};

export default App;