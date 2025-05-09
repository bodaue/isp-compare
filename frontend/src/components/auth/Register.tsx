import React, {useState} from 'react';
import {Link} from 'react-router-dom';
import styles from './Auth.module.css';
import {useForm} from '@/hooks';
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
            setErrors({form: err.response?.data?.detail || 'Произошла ошибка при регистрации'});
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.authContainer}>
            <div className={styles.authCard}>
                <h2>Регистрация</h2>

                {errors.form && <div className={styles.errorMessage}>{errors.form}</div>}

                <form onSubmit={handleSubmit}>
                    <div className={styles.formGroup}>
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
                    </div>

                    <div className={styles.formGroup}>
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
                    </div>

                    <div className={styles.formGroup}>
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
                    </div>

                    <div className={styles.formGroup}>
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
                            <div className={`${styles.passwordStrength} ${styles[passwordStrength]}`}></div>
                        )}
                    </div>

                    <div className={styles.formGroup}>
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
                    </div>

                    <button type="submit" className={styles.btnPrimary} disabled={loading}>
                        {loading ? (
                            <>
                                <span className={styles.loadingSpinner}></span>
                                Регистрация...
                            </>
                        ) : (
                            'Зарегистрироваться'
                        )}
                    </button>
                </form>

                <div className={styles.authFooter}>
                    <p>Уже есть аккаунт? <Link to="/login">Войдите</Link></p>
                </div>
            </div>
        </div>
    );
};

export default Register;