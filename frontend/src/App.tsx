import React, { useState } from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import './App.css';

// Placeholder components - you'll implement these later
const Home = () => <div className="page">Главная страница</div>;
const ProviderList = () => <div className="page">Список провайдеров</div>;
const TariffComparison = () => <div className="page">Сравнение тарифов</div>;
const Login = () => <div className="page">Вход в систему</div>;
const Register = () => <div className="page">Регистрация</div>;
const Profile = () => <div className="page">Профиль пользователя</div>;

const App: React.FC = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  
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
                <li><button onClick={() => setIsLoggedIn(false)}>Выход</button></li>
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
          <Route path="/" element={<Home />} />
          <Route path="/providers" element={<ProviderList />} />
          <Route path="/comparison" element={<TariffComparison />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/profile" element={<Profile />} />
        </Routes>
      </main>
      
      <footer>
        <p>© 2025 ISP Compare | Керимов Тимур Илгарович | ВКР ПРИН-467</p>
      </footer>
    </div>
  );
};

export default App;