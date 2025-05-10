import React, {useState} from 'react';
import {userService} from '../../services/userService';
import {UserProfile} from '../../types/api.types';

interface EditProfileProps {
    userData: UserProfile;
    onUpdate: (updatedProfile: UserProfile) => void;
}

const EditProfile: React.FC<EditProfileProps> = ({userData, onUpdate}) => {
    const [values, setValues] = useState({
        fullname: userData.fullname,
        username: userData.username
    });
    const [errors, setErrors] = useState<Record<string, string>>({});
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState('');

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const {name, value} = e.target;
        setValues(prev => ({
            ...prev,
            [name]: value
        }));
        // Очищаем ошибку при изменении поля
        if (errors[name]) {
            setErrors(prev => ({
                ...prev,
                [name]: ''
            }));
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setErrors({});
        setSuccess('');

        try {
            const updatedProfile = await userService.updateProfile(values);
            setSuccess('Профиль успешно обновлен');

            // Обновляем данные в родительском компоненте после задержки
            setTimeout(() => {
                onUpdate(updatedProfile);
            }, 1500);
        } catch (err: any) {
            setErrors({form: err.response?.data?.detail || 'Ошибка при обновлении профиля'});
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="edit-profile">
            {success && <div className="success-message">{success}</div>}
            {errors.form && <div className="error-message">{errors.form}</div>}

            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="fullname">Полное имя</label>
                    <input
                        type="text"
                        id="fullname"
                        name="fullname"
                        value={values.fullname}
                        onChange={handleChange}
                        disabled={loading}
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="username">Имя пользователя</label>
                    <input
                        type="text"
                        id="username"
                        name="username"
                        value={values.username}
                        onChange={handleChange}
                        disabled={loading}
                        minLength={4}
                    />
                </div>

                <button type="submit" className="btn btn-primary" disabled={loading}>
                    {loading ? 'Сохранение...' : 'Сохранить изменения'}
                </button>
            </form>
        </div>
    );
};

export default EditProfile;