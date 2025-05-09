import React, {useState} from 'react';
import { userService } from '../../services/userService';

const ChangePassword: React.FC = () => {
    const [formData, setFormData] = useState({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
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
        setError('');
        setSuccess('');

        if (formData.newPassword !== formData.confirmPassword) {
            setError('Новые пароли не совпадают');
            return;
        }

        if (formData.newPassword.length < 8) {
            setError('Пароль должен содержать минимум 8 символов');
            return;
        }

        if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.newPassword)) {
            setError('Пароль должен содержать заглавные и строчные буквы, а также цифры');
            return;
        }

        setLoading(true);

        try {
            await userService.changePassword({
                current_password: formData.currentPassword,
                new_password: formData.newPassword
            });
            setSuccess('Пароль успешно изменен');
            setFormData({
                currentPassword: '',
                newPassword: '',
                confirmPassword: ''
            });
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Ошибка при смене пароля');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="change-password">
            {success && <div className="success-message">{success}</div>}
            {error && <div className="error-message">{error}</div>}

            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="currentPassword">Текущий пароль</label>
                    <input
                        type="password"
                        id="currentPassword"
                        name="currentPassword"
                        value={formData.currentPassword}
                        onChange={handleChange}
                        required
                        disabled={loading}
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="newPassword">Новый пароль</label>
                    <input
                        type="password"
                        id="newPassword"
                        name="newPassword"
                        value={formData.newPassword}
                        onChange={handleChange}
                        required
                        minLength={8}
                        disabled={loading}
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="confirmPassword">Подтвердите новый пароль</label>
                    <input
                        type="password"
                        id="confirmPassword"
                        name="confirmPassword"
                        value={formData.confirmPassword}
                        onChange={handleChange}
                        required
                        disabled={loading}
                    />
                </div>

                <button type="submit" className="btn btn-primary" disabled={loading}>
                    {loading ? 'Изменение...' : 'Изменить пароль'}
                </button>
            </form>
        </div>
    );
};

export default ChangePassword;