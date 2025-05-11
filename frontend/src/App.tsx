import React, {useEffect, useState} from 'react';
import {Route, Routes} from 'react-router-dom';
import Header from './components/layout/Header';
import Footer from './components/layout/Footer';
import Home from './components/pages/Home';
import {Login, Register} from './components/auth';
import Profile from './components/profile/Profile';
import ProviderList from './components/providers/ProviderList';
import ProviderDetail from './components/providers/ProviderDetail';
import TariffList from './components/tariffs/TariffList';
import TariffDetail from './components/tariffs/TariffDetail';
import {useAuth} from './contexts/AuthContext';
import './App.css';

const App: React.FC = () => {
    const {isLoggedIn, logout} = useAuth();
    const [isScrolled, setIsScrolled] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 10);
        };

        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    return (
        <div className="app">
            <Header
                isLoggedIn={isLoggedIn}
                isScrolled={isScrolled}
                onLogout={logout}
            />

            <main>
                <Routes>
                    <Route path="/" element={<Home isLoggedIn={isLoggedIn}/>}/>
                    <Route path="/providers" element={<ProviderList/>}/>
                    <Route path="/providers/:id" element={<ProviderDetail/>}/>
                    <Route path="/tariffs" element={<TariffList/>}/>
                    <Route path="/tariffs/:id" element={<TariffDetail/>}/>
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