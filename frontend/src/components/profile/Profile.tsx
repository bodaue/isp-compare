// frontend/src/components/profile/Profile.tsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import ProfileInfo from './ProfileInfo';
import EditProfile from './EditProfile';
import ChangePassword from './ChangePassword';
import './Profile.css';

const Profile: React.FC = () => {
    const [activeTab, setActiveTab] = useState('info');
    const [userData, setUserData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem('accessToken');
        if (!token) {
            navigate('/login');
            return;
        }

        fetchUserData();
    }, [navigate]);

    const fetchUserData = async () => {
        try {
            const token = localStorage.getItem('accessToken');
            const response = await axios.get('/api/users/me', {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            setUserData(response.data);
            setError('');
        } catch (err: any) {
            if (err.response?.status === 401) {
                localStorage.removeItem('accessToken');
                navigate('/login');
            } else {
                setError('Ошибка при загрузке профиля');
            }
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="profile-loading">
                <div className="loading-spinner"></div>
                Загрузка профиля...
            </div>
        );
    }

    if (error) {
        return (
            <div className="profile-error">
                <p>{error}</p>
                <button onClick={fetchUserData} className="btn btn-primary">
                    Повторить попытку
                </button>
            </div>
        );
    }

    return (
        <div className="profile-container">
            <div className="profile-header">
                <h2>Личный кабинет</h2>
            </div>

            <div className="profile-nav">
                <button
                    className={`nav-button ${activeTab === 'info' ? 'active' : ''}`}
                    onClick={() => setActiveTab('info')}
                >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0 -18 0"></path>
                        <path d="M12 10m-3 0a3 3 0 1 0 6 0a3 3 0 1 0 -6 0"></path>
                        <path d="M6.168 18.849a4 4 0 0 1 3.832 -2.849h4a4 4 0 0 1 3.834 2.855"></path>
                    </svg>
                    Профиль
                </button>
                <button
                    className={`nav-button ${activeTab === 'edit' ? 'active' : ''}`}
                    onClick={() => setActiveTab('edit')}
                >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path>
                    </svg>
                    Редактировать
                </button>
                <button
                    className={`nav-button ${activeTab === 'password' ? 'active' : ''}`}
                    onClick={() => setActiveTab('password')}
                >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <rect x="3" y="11" width="18" height="10" rx="2" ry="2"></rect>
                        <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                    </svg>
                    Сменить пароль
                </button>
            </div>

            <div className="profile-content">
                {activeTab === 'info' && (
                    <ProfileInfo userData={userData} />
                )}
                {activeTab === 'edit' && (
                    <EditProfile userData={userData} onUpdate={fetchUserData} />
                )}
                {activeTab === 'password' && (
                    <ChangePassword />
                )}
            </div>
        </div>
    );
};

export default Profile;