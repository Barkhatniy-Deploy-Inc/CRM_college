import api from './client';

export const authAPI = {
    // Авторизация
    login: (email, password) =>
        api.post('/auth/login', { email, password }),

    // Регистрация
    register: (userData) =>
        api.post('/auth/register', userData),

    // Получение профиля
    getProfile: () =>
        api.get('/auth/me'),

    // Выход
    logout: () =>
        api.post('/auth/logout'),
};
