import React, {useEffect, useState} from 'react';
import {useNavigate} from 'react-router-dom';
import ProfileInfo from './ProfileInfo';
import EditProfile from './EditProfile';
import ChangePassword from './ChangePassword';
import PageHeader from '../common/PageHeader';
import './Profile.css';
import {useUser} from '../../hooks';
import {useAuth} from '../../contexts/AuthContext';
import {UserProfile} from '../../types/api.types';

const Profile: React.FC = () => {
    const [activeTab, setActiveTab] = useState('info');
    const {userData, setUserData, loading, error, fetchUserData} = useUser();
    const {isLoggedIn} = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        if (!isLoggedIn) {
            navigate('/login');
        }
    }, [isLoggedIn, navigate]);

    const handleProfileUpdate = (updatedProfile: UserProfile) => {
        setUserData(updatedProfile);
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

    if (!userData) {
        return null;
    }

    return (
        <div className="profile-container">
            <PageHeader title="Личный кабинет" />

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
                    <ProfileInfo userData={userData}/>
                )}
                {activeTab === 'edit' && (
                    <EditProfile userData={userData} onUpdate={handleProfileUpdate}/>
                )}
                {activeTab === 'password' && (
                    <ChangePassword/>
                )}
            </div>
        </div>
    );
};

export default Profile;