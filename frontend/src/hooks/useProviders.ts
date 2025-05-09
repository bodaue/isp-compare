import {useEffect, useState} from 'react';
import {providerService} from '../services/providerService';
import {Provider} from '../types/provider.types';

export const useProviders = () => {
    const [providers, setProviders] = useState<Provider[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const fetchProviders = async () => {
        try {
            setLoading(true);
            const data = await providerService.getAllProviders();
            setProviders(data);
            setError('');
        } catch (err: any) {
            setError('Ошибка при загрузке провайдеров');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchProviders();
    }, []);

    const getProviderById = (providerId: string) => {
        return providers.find(p => p.id === providerId);
    };

    return {
        providers,
        loading,
        error,
        fetchProviders,
        getProviderById
    };
};