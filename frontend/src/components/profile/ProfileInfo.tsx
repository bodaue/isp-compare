import React from 'react';
import styles from './Profile.module.css';

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
        <div className={styles.profileInfo}>
            <div className={styles.infoCard}>
                <div className={styles.infoItem}>
                    <label>Полное имя:</label>
                    <span>{userData.fullname}</span>
                </div>
                <div className={styles.infoItem}>
                    <label>Имя пользователя:</label>
                    <span>{userData.username}</span>
                </div>
                <div className={styles.infoItem}>
                    <label>Email:</label>
                    <span>{userData.email}</span>
                </div>
                <div className={styles.infoItem}>
                    <label>ID пользователя:</label>
                    <span>{userData.id}</span>
                </div>
            </div>
        </div>
    );
};

export default ProfileInfo;