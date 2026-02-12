import { useState, useEffect } from 'react';
import { techcardAPI } from '../api/techcard';
import './TechCard.css';

export default function TechCardPage() {
    const [techcards, setTechcards] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadTechCards();
    }, []);

    const loadTechCards = async () => {
        try {
            const response = await techcardAPI.getTechCards();
            setTechcards(response.data);
        } catch (error) {
            console.error('Ошибка загрузки техкарт:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleGenerate = async (id) => {
        try {
            const response = await techcardAPI.generateDocument(id);

            // Скачивание файла
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `techcard_${id}.docx`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            alert('Ошибка генерации документа');
        }
    };

    if (loading) {
        return (
            <div className="techcard-page">
                <div className="loading">Загрузка...</div>
            </div>
        );
    }

    return (
        <div className="techcard-page fade-in">
            <header className="page-header">
                <h1>Технологические карты</h1>
                <p className="text-muted">Управление техкартами занятий</p>
            </header>

            <div className="techcard-grid">
                {techcards.length === 0 ? (
                    <div className="card empty-state">
                        <p className="text-muted">Техкарты не найдены</p>
                    </div>
                ) : (
                    techcards.map((card) => (
                        <div key={card.id} className="card techcard-item">
                            <h3>{card.title || `Техкарта #${card.id}`}</h3>
                            <p className="text-muted">{card.description || 'Описание отсутствует'}</p>

                            <div className="techcard-meta">
                                <span className="meta-item">📅 {new Date(card.created_at).toLocaleDateString('ru-RU')}</span>
                            </div>

                            <button
                                className="btn btn-primary btn-full"
                                onClick={() => handleGenerate(card.id)}
                            >
                                📄 Скачать DOCX
                            </button>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
