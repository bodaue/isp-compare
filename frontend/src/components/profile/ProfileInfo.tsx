
import React from 'react';

interface ProfileInfoProps {
    userData: {
        id: string;
        fullname: string;
        username: string;
        email: string;
    };
}

const ProfileInfo: React.FC<ProfileInfoProps> = ({userData}) => {
    return (
        <div className="profile-info">
            <div className="info-card">
                <div className="info-item">
                    <label>Полное имя:</label>
                    <span>{userData.fullname}</span>
                </div>
                <div className="info-item">
                    <label>Имя пользователя:</label>
                    <span>{userData.username}</span>
                </div>
                <div className="info-item">
                    <label>Email:</label>
                    <span>{userData.email}</span>
                </div>
                <div className="info-item">
                    <label>ID пользователя:</label>
                    <span>{userData.id}</span>
                </div>
            </div>
        </div>
    );
};

export default ProfileInfo;