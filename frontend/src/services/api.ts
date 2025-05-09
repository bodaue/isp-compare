import axios, {AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig} from 'axios';

// Создаем базовый instance
export const api = axios.create({
    baseURL: '/api',
    withCredentials: true, // Важно для отправки cookies
});

// Интерцептор для добавления access token к запросам
api.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        const token = localStorage.getItem('accessToken');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Флаг для предотвращения множественных рефреш запросов
let isRefreshing = false;
let failedQueue: Array<{
    resolve: (value: unknown) => void;
    reject: (reason?: unknown) => void;
}> = [];

const processQueue = (error: any, token: string | null = null) => {
    failedQueue.forEach((prom) => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token);
        }
    });

    failedQueue = [];
};

// Интерцептор для обработки ответов и обновления токенов
api.interceptors.response.use(
    (response: AxiosResponse) => {
        return response;
    },
    async (error) => {
        const originalRequest: AxiosRequestConfig & { _retry?: boolean } = error.config;

        // Если ошибка 401 и мы еще не пытались обновить токен
        if (error.response?.status === 401 && !originalRequest._retry) {
            if (isRefreshing) {
                // Если уже идет процесс обновления, добавляем запрос в очередь
                return new Promise((resolve, reject) => {
                    failedQueue.push({resolve, reject});
                }).then((token) => {
                    originalRequest.headers = originalRequest.headers || {};
                    originalRequest.headers.Authorization = `Bearer ${token}`;
                    return api(originalRequest);
                }).catch((err) => {
                    return Promise.reject(err);
                });
            }

            originalRequest._retry = true;
            isRefreshing = true;

            try {
                // Пытаемся обновить токен
                const response = await axios.post('/api/auth/refresh', {}, {
                    withCredentials: true // Важно для отправки refresh token из cookies
                });

                const {access_token} = response.data;
                localStorage.setItem('accessToken', access_token);

                // Обновляем заголовок для оригинального запроса
                originalRequest.headers = originalRequest.headers || {};
                originalRequest.headers.Authorization = `Bearer ${access_token}`;

                processQueue(null, access_token);

                return api(originalRequest);
            } catch (refreshError) {
                processQueue(refreshError, null);

                // Если не удалось обновить токен, перенаправляем на логин
                localStorage.removeItem('accessToken');
                window.location.href = '/login';

                return Promise.reject(refreshError);
            } finally {
                isRefreshing = false;
            }
        }

        return Promise.reject(error);
    }
);

export default api;