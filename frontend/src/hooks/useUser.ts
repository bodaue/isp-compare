import {useEffect, useState} from 'react';
import {userService} from '../services/userService';
import {UserProfile} from '../types/api.types';

export const useUser = () => {
    const [userData, setUserData] = useState<UserProfile | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const fetchUserData = async () => {
        try {
            setLoading(true);
            const data = await userService.getProfile();
            setUserData(data);
            setError('');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Ошибка при загрузке профиля');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUserData();
    }, []);

    const updateProfile = async (data: any) => {
        try {
            const updatedProfile = await userService.updateProfile(data);
            setUserData(updatedProfile);
            return updatedProfile;
        } catch (error) {
            throw error;
        }
    };

    const changePassword = async (data: any) => {
        return userService.changePassword(data);
    };

    return {
        userData,
        loading,
        error,
        fetchUserData,
        updateProfile,
        changePassword
    };
};