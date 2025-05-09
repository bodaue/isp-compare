import {useEffect, useState} from 'react';
import {tariffService} from '../services/tariffService';
import {Tariff, TariffSearchParams} from '../types/provider.types';

export const useTariffs = () => {
    const [tariffs, setTariffs] = useState<Tariff[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [filters, setFilters] = useState<TariffSearchParams>({});

    const fetchTariffs = async () => {
        try {
            setLoading(true);
            const data = await tariffService.getAllTariffs();
            setTariffs(data);
            setError('');
        } catch (err: any) {
            setError('Ошибка при загрузке тарифов');
        } finally {
            setLoading(false);
        }
    };

    const searchTariffs = async (searchParams: TariffSearchParams) => {
        try {
            setLoading(true);
            const data = await tariffService.searchTariffs(searchParams);
            setTariffs(data);
            setFilters(searchParams);
            setError('');
        } catch (err: any) {
            setError('Ошибка при поиске тарифов');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchTariffs();
    }, []);

    return {
        tariffs,
        loading,
        error,
        filters,
        fetchTariffs,
        searchTariffs,
        setFilters
    };
};