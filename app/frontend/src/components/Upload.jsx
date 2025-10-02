import { useAuth } from '../context/AuthContext.jsx';
import React, { useEffect, useState, useCallback } from "react";
import { dbService } from '../services/dbService.js';

const Upload = () => {
    const { user } = useAuth();
    const [flight_count, setFlightCount] = useState(-1);
    const [uLoading, setULoading] = useState(false);
    const [uError, setUError] = useState(null);
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);

    const loadCount = useCallback(async () => {
        try {
            setULoading(true); 
            setUError(null);
            const data = await dbService.getFlightCount();
            console.log(data);
            setFlightCount(data.flight_count);
        } catch (e) {
            setUError(e?.response?.data?.detail || "Не удалось загрузить данные");
        } finally {
            setULoading(false);
        }
    }, []);

    const handleFileChange = (event) => {
        const selectedFile = event.target.files[0];
        if (selectedFile) {
            // Проверяем тип файла (опционально)
            const allowedTypes = ['.xlsx'];
            const fileExtension = selectedFile.name.toLowerCase().split('.').pop();
            
            if (!allowedTypes.some(type => selectedFile.name.toLowerCase().endsWith(type))) {
                setUError('Неподдерживаемый формат файла. Разрешены: ' + allowedTypes.join(', '));
                return;
            }
            
            setFile(selectedFile);
            setUError(null);
        }
    };

    const handleUpload = async () => {
        if (!file) {
            setUError('Пожалуйста, выберите файл для загрузки');
            return;
        }

        try {
            setUploading(true);
            setUploadProgress(0);
            setUError(null);

            // Создаем FormData для отправки файла
            const formData = new FormData();
            formData.append('file', file);
            formData.append('user_id', user?.id || 'unknown');

            // Отправляем файл на сервер
            const response = await dbService.uploadFile(formData, (progressEvent) => {
                const progress = Math.round(
                    (progressEvent.loaded * 100) / progressEvent.total
                );
                setUploadProgress(progress);
            });

            console.log('Файл успешно загружен:', response);
            
            // Обновляем счетчик полетов после успешной загрузки
            await loadCount();
            
            // Сбрасываем состояние
            setFile(null);
            setUploadProgress(0);
            
            // Очищаем input file
            const fileInput = document.getElementById('file-upload');
            if (fileInput) fileInput.value = '';

        } catch (error) {
            console.error('Ошибка загрузки файла:', error);
            setUError(error?.response?.data?.detail || 'Ошибка при загрузке файла');
        } finally {
            setUploading(false);
        }
    };

    const handleDragOver = (event) => {
        event.preventDefault();
    };

    const handleDrop = (event) => {
        event.preventDefault();
        const droppedFile = event.dataTransfer.files[0];
        if (droppedFile) {
            setFile(droppedFile);
            setUError(null);
        }
    };

    useEffect(() => {
        loadCount();
    }, [loadCount]);

    return (
        <div className="upload-container">
            <h2>Загрузка данных</h2>
            
            <div className="upload-stats">
                <div className="stat-item">
                    <span className="stat-label">Количество полетов в базе:</span>
                    <span className="stat-value">{flight_count}</span>
                </div>
            </div>

            <div 
                className="upload-area"
                onDragOver={handleDragOver}
                onDrop={handleDrop}
            >
                <div className="upload-content">
                    <input
                        id="file-upload"
                        type="file"
                        onChange={handleFileChange}
                        accept=".xlsx"
                        style={{ display: 'none' }}
                    />
                    
                    <label htmlFor="file-upload" className="file-input-label">
                        Выберите файл
                    </label>
                    
                    <p className="upload-hint">
                        или перетащите файл сюда
                    </p>
                    
                    <div className="file-info">
                        {file && (
                            <div className="selected-file">
                                <span className="file-name">{file.name}</span>
                                <span className="file-size">
                                    ({(file.size / 1024 / 1024).toFixed(2)} MB)
                                </span>
                                <button 
                                    className="remove-file"
                                    onClick={() => setFile(null)}
                                >
                                    ×
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {uploading && (
                <div className="upload-progress">
                    <div className="progress-bar">
                        <div 
                            className="progress-fill"
                            style={{ width: `${uploadProgress}%` }}
                        ></div>
                    </div>
                    <span className="progress-text">{uploadProgress}%</span>
                </div>
            )}

            <button 
                className="upload-btn"
                onClick={handleUpload}
                disabled={!file || uploading}
            >
                {uploading ? 'Загрузка...' : 'Загрузить файл'}
            </button>

            {uError && (
                <div className="error-message">
                    {uError}
                </div>
            )}

            <div className="upload-info">
                <h4>Поддерживаемый формат: excel</h4>
                
            </div>
        </div>
    );
};

export default Upload;