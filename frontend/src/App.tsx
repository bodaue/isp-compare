// frontend/src/App.tsx
import React, {useEffect, useState} from 'react';
import {Link, Route, Routes, useNavigate} from 'react-router-dom';
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import './App.css';

// Placeholder components
const Home = () => <div className="page">Главная страница</div>;
const ProviderList = () => <div className="page">Список провайдеров</div>;
const TariffComparison = () => <div className="page">Сравнение тарифов</div>;
const Profile = () => <div className="page">Профиль пользователя</div>;

const App: React.FC = () => {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        // Проверяем наличие токена при загрузке
        const token = localStorage.getItem('accessToken');
        setIsLoggedIn(!!token);
    }, []);

    const handleLogout = () => {
        // Удаляем токен
        localStorage.removeItem('accessToken');
        setIsLoggedIn(false);
        navigate('/');
    };

    return (
        <div className="app">
            <header className="app-header">
                <h1>ISP Compare</h1>
                <nav>
                    <ul>
                        <li><Link to="/">Главная</Link></li>
                        <li><Link to="/providers">Провайдеры</Link></li>
                        <li><Link to="/comparison">Сравнение</Link></li>
                        {isLoggedIn ? (
                            <>
                                <li><Link to="/profile">Профиль</Link></li>
                                <li>
                                    <button onClick={handleLogout}>Выход</button>
                                </li>
                            </>
                        ) : (
                            <>
                                <li><Link to="/login">Вход</Link></li>
                                <li><Link to="/register">Регистрация</Link></li>
                            </>
                        )}
                    </ul>
                </nav>
            </header>

            <main>
                <Routes>
                    <Route path="/" element={<Home/>}/>
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