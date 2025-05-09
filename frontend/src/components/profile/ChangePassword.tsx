import React from 'react';
import {useForm, useUser} from '../../hooks';

const ChangePassword: React.FC = () => {
    const {changePassword} = useUser();
    const {
        values,
        errors,
        loading,
        handleChange,
        setErrors,
        setLoading,
        reset
    } = useForm({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
    });

    const [success, setSuccess] = React.useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setErrors({});
        setSuccess('');

        if (values.newPassword !== values.confirmPassword) {
            setErrors({form: 'Новые пароли не совпадают'});
            return;
        }

        if (values.newPassword.length < 8) {
            setErrors({form: 'Пароль должен содержать минимум 8 символов'});
            return;
        }

        if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(values.newPassword)) {
            setErrors({form: 'Пароль должен содержать заглавные и строчные буквы, а также цифры'});
            return;
        }

        setLoading(true);

        try {
            await changePassword({
                current_password: values.currentPassword,
                new_password: values.newPassword
            });
            setSuccess('Пароль успешно изменен');
            reset();
        } catch (err: any) {
            setErrors({form: err.response?.data?.detail || 'Ошибка при смене пароля'});
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="change-password">
            {success && <div className="success-message">{success}</div>}
            {errors.form && <div className="error-message">{errors.form}</div>}

            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="currentPassword">Текущий пароль</label>
                    <input
                        type="password"
                        id="currentPassword"
                        name="currentPassword"
                        value={values.currentPassword}
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
                        value={values.newPassword}
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
                        value={values.confirmPassword}
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