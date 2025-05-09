// frontend/src/components/auth/Register.tsx
import React, {useState} from 'react';
import {Link} from 'react-router-dom';
import './Auth.css';
import {useForm} from '../../hooks';
import {useAuth} from '../../contexts/AuthContext';

const Register: React.FC = () => {
    const {register} = useAuth();
    const {
        values,
        errors,
        loading,
        handleChange,
        setErrors,
        setLoading
    } = useForm({
        fullname: '',
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
    });

    const [passwordStrength, setPasswordStrength] = useState('');

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

    const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        handleChange(e);
        if (e.target.name === 'password') {
            checkPasswordStrength(e.target.value);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setErrors({});

        if (values.password !== values.confirmPassword) {
            setErrors({form: 'Пароли не совпадают'});
            return;
        }

        if (values.password.length < 8) {
            setErrors({form: 'Пароль должен содержать минимум 8 символов'});
            return;
        }

        if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(values.password)) {
            setErrors({form: 'Пароль должен содержать заглавные и строчные буквы, а также цифры'});
            return;
        }

        setLoading(true);

        try {
            await register({
                fullname: values.fullname,
                username: values.username,
                email: values.email,
                password: values.password
            });
        } catch (err: any) {
            if (err.response?.status === 422 && err.response?.data?.detail) {
                const newErrors: Record<string, string> = {};

                if (Array.isArray(err.response.data.detail)) {
                    err.response.data.detail.forEach((error: any) => {
                        const field = error.loc[error.loc.length - 1];

                        // Маппинг сообщений об ошибках на русский язык
                        let message = error.msg;
                        if (message.includes('Password must contain at least one uppercase letter')) {
                            message = 'Пароль должен содержать хотя бы одну заглавную букву';
                        } else if (message.includes('Password must contain at least one lowercase letter')) {
                            message = 'Пароль должен содержать хотя бы одну строчную букву';
                        } else if (message.includes('Password must contain at least one digit')) {
                            message = 'Пароль должен содержать хотя бы одну цифру';
                        } else if (message.includes('field required')) {
                            message = 'Это поле обязательно';
                        } else if (message.includes('value is not a valid email address')) {
                            message = 'Некорректный email адрес';
                        } else if (message.includes('ensure this value has at least')) {
                            const match = message.match(/at least (\d+) characters/);
                            if (match) {
                                message = `Минимальная длина: ${match[1]} символов`;
                            }
                        } else if (message.includes('ensure this value has at most')) {
                            const match = message.match(/at most (\d+) characters/);
                            if (match) {
                                message = `Максимальная длина: ${match[1]} символов`;
                            }
                        }

                        newErrors[field] = message;
                    });

                    setErrors(newErrors);
                } else {
                    setErrors({form: err.response.data.detail});
                }
            } else {
                setErrors({form: err.response?.data?.detail || 'Произошла ошибка при регистрации'});
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <h2>Регистрация</h2>

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
                            required
                            disabled={loading}
                            placeholder="Введите ваше полное имя"
                        />
                        {errors.fullname && <div className="error-message">{errors.fullname}</div>}
                    </div>

                    <div className="form-group">
                        <label htmlFor="username">Имя пользователя</label>
                        <input
                            type="text"
                            id="username"
                            name="username"
                            value={values.username}
                            onChange={handleChange}
                            required
                            minLength={4}
                            disabled={loading}
                            placeholder="Минимум 4 символа"
                            autoComplete="username"
                        />
                        {errors.username && <div className="error-message">{errors.username}</div>}
                    </div>

                    <div className="form-group">
                        <label htmlFor="email">Email</label>
                        <input
                            type="email"
                            id="email"
                            name="email"
                            value={values.email}
                            onChange={handleChange}
                            required
                            disabled={loading}
                            placeholder="example@email.com"
                            autoComplete="email"
                        />
                        {errors.email && <div className="error-message">{errors.email}</div>}
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Пароль</label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            value={values.password}
                            onChange={handlePasswordChange}
                            required
                            minLength={8}
                            disabled={loading}
                            placeholder="Минимум 8 символов"
                            autoComplete="new-password"
                        />
                        {values.password && (
                            <div className={`password-strength ${passwordStrength}`}></div>
                        )}
                        {errors.password && <div className="error-message">{errors.password}</div>}
                    </div>

                    <div className="form-group">
                        <label htmlFor="confirmPassword">Подтвердите пароль</label>
                        <input
                            type="password"
                            id="confirmPassword"
                            name="confirmPassword"
                            value={values.confirmPassword}
                            onChange={handleChange}
                            required
                            disabled={loading}
                            placeholder="Повторите пароль"
                            autoComplete="new-password"
                        />
                        {errors.confirmPassword && <div className="error-message">{errors.confirmPassword}</div>}
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