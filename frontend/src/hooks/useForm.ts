import { useState } from 'react';

export const useForm = <T>(initialValues: T) => {
    const [values, setValues] = useState<T>(initialValues);
    const [errors, setErrors] = useState<Record<string, string>>({});
    const [loading, setLoading] = useState(false);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
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

    const reset = () => {
        setValues(initialValues);
        setErrors({});
        setLoading(false);
    };

    return {
        values,
        errors,
        loading,
        handleChange,
        setValues,
        setErrors,
        setLoading,
        reset
    };
};