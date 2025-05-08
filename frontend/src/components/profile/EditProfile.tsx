
import React, {useState} from 'react';
import axios from 'axios';

interface EditProfileProps {
    userData: {
        fullname: string;
        username: string;
    };
    onUpdate: () => void;
}

const EditProfile: React.FC<EditProfileProps> = ({userData, onUpdate}) => {
    const [formData, setFormData] = useState({
        fullname: userData.fullname,
        username: userData.username
    });
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState('');
    const [error, setError] = useState('');

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
        setError('');
        setSuccess('');
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setSuccess('');

        try {
            const token = localStorage.getItem('accessToken');
            await axios.patch('/api/users/profile', formData, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            setSuccess('Профиль успешно обновлен');
            onUpdate();
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Ошибка при обновлении профиля');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="edit-profile">
            {success && <div className="success-message">{success}</div>}
            {error && <div className="error-message">{error}</div>}

            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="fullname">Полное имя</label>
                    <input
                        type="text"
                        id="fullname"
                        name="fullname"
                        value={formData.fullname}
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
                        value={formData.username}
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