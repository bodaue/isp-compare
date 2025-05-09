import React from 'react';
import {useForm, useUser} from '../../hooks';

interface EditProfileProps {
    userData: {
        fullname: string;
        username: string;
    };
    onUpdate: () => void;
}

const EditProfile: React.FC<EditProfileProps> = ({userData, onUpdate}) => {
    const {updateProfile} = useUser();
    const {
        values,
        errors,
        loading,
        handleChange,
        setErrors,
        setLoading
    } = useForm({
        fullname: userData.fullname,
        username: userData.username
    });

    const [success, setSuccess] = React.useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setErrors({});
        setSuccess('');

        try {
            await updateProfile(values);
            setSuccess('Профиль успешно обновлен');
            onUpdate();
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