import api from './client';

export const scheduleAPI = {
    // Получить расписание
    getSchedule: (params) =>
        api.get('/schedule', { params }),

    // Импорт Excel файла
    uploadSchedule: (file) => {
        const formData = new FormData();
        formData.append('file', file);
        return api.post('/schedule/import', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
    },
};
