import React, {useState} from 'react';
import {Link} from 'react-router-dom';
import './Auth.css';
import {useAuth, useForm} from '../../hooks';

const Login: React.FC = () => {
    const {login} = useAuth();
    const {
        values,
        errors,
        loading,
        handleChange,
        setErrors,
        setLoading
    } = useForm({username: '', password: ''});

    const [attemptsRemaining, setAttemptsRemaining] = useState<number | null>(null);
    const [retryAfter, setRetryAfter] = useState<number | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setErrors({});
        setLoading(true);
        setRetryAfter(null);
        setAttemptsRemaining(null);

        try {
            await login(values.username, values.password);
        } catch (err: any) {
            const errorMessage = err.response?.data?.detail || 'Произошла ошибка при входе';
            setErrors({form: errorMessage});

            // Проверяем заголовки rate limiting
            if (err.response?.headers) {
                const headers = err.response.headers;

                if (headers['retry-after']) {
                    setRetryAfter(parseInt(headers['retry-after']));
                }

                if (headers['x-ratelimit-remaining']) {
                    setAttemptsRemaining(parseInt(headers['x-ratelimit-remaining']));
                }
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <h2>Вход в систему</h2>

                {errors.form && (
                    <div className="error-message">
                        {errors.form.split('\n').map((line, index) => (
                            <div key={index}>{line}</div>
                        ))}
                        {attemptsRemaining !== null && attemptsRemaining > 0 && (
                            <div className="attempts-info">
                                Осталось попыток: {attemptsRemaining}
                            </div>
                        )}
                        {retryAfter && (
                            <div className="retry-info">
                                Попробуйте снова через {Math.ceil(retryAfter / 60)} минут
                            </div>
                        )}
                    </div>
                )}

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="username">Имя пользователя</label>
                        <input
                            type="text"
                            id="username"
                            name="username"
                            value={values.username}
                            onChange={handleChange}
                            required
                            disabled={loading}
                            placeholder="Введите имя пользователя"
                            autoComplete="username"
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Пароль</label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            value={values.password}
                            onChange={handleChange}
                            required
                            disabled={loading}
                            placeholder="Введите пароль"
                            autoComplete="current-password"
                        />
                    </div>

                    <button
                        type="submit"
                        className="btn btn-primary"
                        disabled={loading}
                    >
                        {loading ? (
                            <>
                                <span className="loading-spinner"></span>
                                Вход...
                            </>
                        ) : (
                            'Войти'
                        )}
                    </button>
                </form>

                <div className="auth-footer">
                    <p>Нет аккаунта? <Link to="/register">Зарегистрируйтесь</Link></p>
                </div>
            </div>
        </div>
    );
};

export default Login;