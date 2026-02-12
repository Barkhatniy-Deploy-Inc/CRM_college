import api from './client';

export const techcardAPI = {
    // Получить список техкарт
    getTechCards: () =>
        api.get('/techcard'),

    // Создать техкарту
    createTechCard: (data) =>
        api.post('/techcard', data),

    // Получить техкарту по ID
    getTechCard: (id) =>
        api.get(`/techcard/${id}`),

    // Сгенерировать DOCX
    generateDocument: (id) =>
        api.get(`/techcard/${id}/generate`, {
            responseType: 'blob'
        }),
};
