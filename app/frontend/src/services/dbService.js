import api from './dbApi.js';

export const dbService = {
  
  getFlightCount: () => 
    api.get('/flight_count').then(r => r.data),
  
  uploadFile: async (formData, onProgress) => {
    try {
      const response = await api.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const progress = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            onProgress(progress);
          }
        },
        timeout: 300000, // 5 минут таймаут для больших файлов
      });
      
      return response.data;
    } catch (error) {
      if (error.response) {
        // Сервер ответил с ошибкой
        throw new Error(error.response.data.detail || 'Upload failed');
      } else if (error.request) {
        // Запрос был сделан, но ответ не получен
        throw new Error('No response from server');
      } else {
        // Что-то пошло не так при настройке запроса
        throw new Error('Upload request configuration error');
      }
    }
  }
};