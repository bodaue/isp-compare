// Modern Register.tsx with improved design
import React, {useState} from 'react';
import {Link, useNavigate} from 'react-router-dom';
import axios from 'axios';
import './Auth.css';

const Register: React.FC = () => {
    const [formData, setFormData] = useState({
        fullname: '',
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [passwordStrength, setPasswordStrength] = useState('');
    const navigate = useNavigate();

    const checkPasswordStrength = (password: string) => {
        if (password.length < 8) {
            setPasswordStrength('');
            return;
        }

        let strength = 0;
        if (/[a-z]/.test(password)) strength++;
        if (/[A-Z]/.test(password)) strength++;
        if (/\d/.test(password)) strength++;
        if (/[@$!%*?&]/.test(password)) strength++;

        if (strength < 2) setPasswordStrength('weak');
        else if (strength < 3) setPasswordStrength('medium');
        else setPasswordStrength('strong');
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData({
            ...formData,
            [name]: value
        });

        if (name === 'password') {
            checkPasswordStrength(value);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        // Проверка паролей
        if (formData.password !== formData.confirmPassword) {
            setError('Пароли не совпадают');
            return;
        }

        // Проверка сложности пароля
        if (formData.password.length < 8) {
            setError('Пароль должен содержать минимум 8 символов');
            return;
        }

        if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
            setError('Пароль должен содержать заглавные и строчные буквы, а также цифры');
            return;
        }

        setLoading(true);

        try {
            const response = await axios.post('/api/auth/register', {
                fullname: formData.fullname,
                username: formData.username,
                email: formData.email,
                password: formData.password
            });

            localStorage.setItem('accessToken', response.data.access_token);
            navigate('/');
            window.location.reload();
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Произошла ошибка при регистрации');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <h2>Регистрация</h2>

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
                            required
                            disabled={loading}
                            placeholder="Введите ваше полное имя"
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
                            required
                            minLength={4}
                            disabled={loading}
                            placeholder="Минимум 4 символа"
                            autoComplete="username"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="email">Email</label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            required
                            disabled={loading}
                            placeholder="example@email.com"
                            autoComplete="email"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Пароль</label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            required
                            minLength={8}
                            disabled={loading}
                            placeholder="Минимум 8 символов"
                            autoComplete="new-password"
                        />
                        {formData.password && (
                            <div className={`password-strength ${passwordStrength}`}></div>
                        )}
                    </div>

                    <div className="form-group">
                        <label htmlFor="confirmPassword">Подтвердите пароль</label>
                        <input
                            type="password"
                            id="confirmPassword"
                            name="confirmPassword"
                            value={formData.confirmPassword}
                            onChange={handleChange}
                            required
                            disabled={loading}
                            placeholder="Повторите пароль"
                            autoComplete="new-password"
                        />
                    </div>

                    <button type="submit" className="btn btn-primary" disabled={loading}>
                        {loading ? (
                            <>
                                <span className="loading-spinner"></span>
                                Регистрация...
                            </>
                        ) : (
                            'Зарегистрироваться'
                        )}
                    </button>
                </form>

                <div className="auth-footer">
                    <p>Уже есть аккаунт? <Link to="/login">Войдите</Link></p>
                </div>
            </div>
        </div>
    );
};

export default Register;