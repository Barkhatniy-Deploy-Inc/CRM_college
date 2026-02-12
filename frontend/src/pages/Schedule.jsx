import { useState } from 'react';
import { scheduleAPI } from '../api/schedule';
import './Schedule.css';

export default function SchedulePage() {
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [message, setMessage] = useState('');

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            setFile(selectedFile);
            setMessage('');
        }
    };

    const handleUpload = async () => {
        if (!file) {
            setMessage('Выберите файл Excel');
            return;
        }

        setUploading(true);
        setMessage('');

        try {
            await scheduleAPI.uploadSchedule(file);
            setMessage('✅ Расписание успешно загружено');
            setFile(null);
        } catch (error) {
            setMessage('❌ Ошибка загрузки: ' + (error.response?.data?.message || error.message));
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="schedule-page fade-in">
            <header className="page-header">
                <h1>Расписание занятий</h1>
                <p className="text-muted">Загрузка и управление расписанием колледжа</p>
            </header>

            <div className="card upload-card">
                <h3>Импорт расписания</h3>
                <p className="text-muted">Загрузите Excel файл с расписанием</p>

                <div className="upload-area">
                    <input
                        type="file"
                        id="file-input"
                        accept=".xlsx,.xls"
                        onChange={handleFileChange}
                        className="file-input"
                    />
                    <label htmlFor="file-input" className="file-label">
                        <div className="file-icon">📁</div>
                        <div>
                            {file ? file.name : 'Выберите файл Excel'}
                        </div>
                    </label>
                </div>

                {message && (
                    <div className={`message ${message.startsWith('✅') ? 'success' : 'error'}`}>
                        {message}
                    </div>
                )}

                <button
                    className="btn btn-primary"
                    onClick={handleUpload}
                    disabled={!file || uploading}
                >
                    {uploading ? 'Загрузка...' : 'Загрузить расписание'}
                </button>
            </div>

            <div className="card info-card">
                <h3>📊 Информация</h3>
                <ul className="info-list">
                    <li>Поддерживаемые форматы: .xlsx, .xls</li>
                    <li>Максимальный размер файла: 10 МБ</li>
                    <li>После загрузки расписание будет обработано автоматически</li>
                </ul>
            </div>
        </div>
    );
}
