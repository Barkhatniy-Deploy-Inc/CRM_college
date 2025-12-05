import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Schedule.css';

export default function ScheduleForm({ lesson, onClose, onSave, apiUrl }) {
  const [formData, setFormData] = useState({
    group_id: lesson?.group_id || '',
    subject_id: lesson?.subject_id || '',
    teacher_id: lesson?.teacher_id || '',
    auditorium_id: lesson?.auditorium_id || '',
    date: lesson?.date || new Date().toISOString().slice(0, 10),
    time_start: lesson?.time_start || '09:00',
    time_end: lesson?.time_end || '10:20',
    lesson_number: lesson?.lesson_number || null,
    subgroup: lesson?.subgroup || null,
    activity_type: lesson?.activity_type || 'lesson',
    comment: lesson?.comment || ''
  });

  const [groups, setGroups] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [teachers, setTeachers] = useState([]);
  const [auditoriums, setAuditoriums] = useState([]);
  const [errors, setErrors] = useState({});

  // Загрузка справочников
  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem('token');
        const headers = { Authorization: `Bearer ${token}` };

        const [groupsRes, subjectsRes, teachersRes, auditoriumsRes] = await Promise.all([
          axios.get(`${apiUrl}/api/schedule/groups`, { headers }),
          axios.get(`${apiUrl}/api/schedule/subjects`, { headers }),
          axios.get(`${apiUrl}/api/schedule/teachers`, { headers }),
          axios.get(`${apiUrl}/api/schedule/auditoriums`, { headers })
        ]);

        setGroups(groupsRes.data);
        setSubjects(subjectsRes.data);
        setTeachers(teachersRes.data);
        setAuditoriums(auditoriumsRes.data.filter(a => a.is_active));
      } catch (error) {
        console.error('Ошибка загрузки справочников:', error);
      }
    };
    fetchData();
  }, [apiUrl]);

  const validate = () => {
    const newErrors = {};
    if (!formData.group_id) newErrors.group_id = 'Выберите группу';
    if (!formData.subject_id) newErrors.subject_id = 'Выберите предмет';
    if (!formData.teacher_id) newErrors.teacher_id = 'Выберите преподавателя';
    if (!formData.time_start) newErrors.time_start = 'Укажите время начала';
    if (!formData.time_end) newErrors.time_end = 'Укажите время окончания';
    
    if (formData.time_start && formData.time_end && formData.time_start >= formData.time_end) {
      newErrors.time_end = 'Время окончания должно быть позже времени начала';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    try {
      const token = localStorage.getItem('token');
      const method = lesson?.id ? 'PUT' : 'POST';
      const url = lesson?.id 
        ? `${apiUrl}/api/schedule/lessons/${lesson.id}` 
        : `${apiUrl}/api/schedule/lessons`;

      const payload = {
        group_id: parseInt(formData.group_id),
        subject_id: parseInt(formData.subject_id),
        teacher_id: parseInt(formData.teacher_id),
        auditorium_id: formData.auditorium_id ? parseInt(formData.auditorium_id) : null,
        date: formData.date,
        time_start: formData.time_start,
        time_end: formData.time_end,
        lesson_number: formData.lesson_number || null,
        subgroup: formData.subgroup || null,
        activity_type: formData.activity_type,
        comment: formData.comment || null
      };

      await axios({
        method,
        url,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        data: payload
      });

      onSave();
    } catch (error) {
      console.error('Ошибка:', error);
      alert(`Ошибка: ${error.response?.data?.detail || 'Не удалось сохранить'}`);
    }
  };

  const handleDelete = async () => {
    if (!lesson?.id) return;
    if (!window.confirm('Удалить занятие?')) return;

    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${apiUrl}/api/schedule/lessons/${lesson.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      onSave();
    } catch (error) {
      console.error('Ошибка удаления:', error);
      alert('Не удалось удалить занятие');
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content schedule-form-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{lesson?.id ? 'Редактирование занятия' : 'Новое занятие'}</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        <form onSubmit={handleSubmit} className="schedule-form">
          {/* Группа */}
          <div className="form-group">
            <label>Группа <span className="required-mark">*</span></label>
            <select 
              value={formData.group_id} 
              onChange={(e) => setFormData({...formData, group_id: e.target.value})}
            >
              <option value="">Выберите группу</option>
              {groups.map(g => (
                <option key={g.id} value={g.id}>{g.name}</option>
              ))}
            </select>
            {errors.group_id && <span className="error-message">{errors.group_id}</span>}
          </div>

          {/* Предмет */}
          <div className="form-group">
            <label>Предмет <span className="required-mark">*</span></label>
            <select 
              value={formData.subject_id} 
              onChange={(e) => setFormData({...formData, subject_id: e.target.value})}
            >
              <option value="">Выберите предмет</option>
              {subjects.map(s => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
            {errors.subject_id && <span className="error-message">{errors.subject_id}</span>}
          </div>

          {/* Преподаватель */}
          <div className="form-group">
            <label>Преподаватель <span className="required-mark">*</span></label>
            <select 
              value={formData.teacher_id} 
              onChange={(e) => setFormData({...formData, teacher_id: e.target.value})}
            >
              <option value="">Выберите преподавателя</option>
              {teachers.map(t => (
                <option key={t.id} value={t.id}>{t.name}</option>
              ))}
            </select>
            {errors.teacher_id && <span className="error-message">{errors.teacher_id}</span>}
          </div>

          {/* Аудитория */}
          <div className="form-group">
            <label>Аудитория</label>
            <select 
              value={formData.auditorium_id || ''} 
              onChange={(e) => setFormData({...formData, auditorium_id: e.target.value})}
            >
              <option value="">Без аудитории</option>
              {auditoriums.map(a => (
                <option key={a.id} value={a.id}>{a.number}</option>
              ))}
            </select>
          </div>

          {/* Дата */}
          <div className="form-group">
            <label>Дата <span className="required-mark">*</span></label>
            <input 
              type="date"
              value={formData.date}
              onChange={(e) => setFormData({...formData, date: e.target.value})}
            />
          </div>

          {/* Время начала */}
          <div className="form-row">
            <div className="form-group">
              <label>Время начала <span className="required-mark">*</span></label>
              <input
                type="time"
                value={formData.time_start}
                onChange={(e) => setFormData({...formData, time_start: e.target.value})}
              />
              {errors.time_start && <span className="error-message">{errors.time_start}</span>}
            </div>

            {/* Время окончания */}
            <div className="form-group">
              <label>Время окончания <span className="required-mark">*</span></label>
              <input
                type="time"
                value={formData.time_end}
                onChange={(e) => setFormData({...formData, time_end: e.target.value})}
              />
              {errors.time_end && <span className="error-message">{errors.time_end}</span>}
            </div>
          </div>

          {/* Номер пары (опционально) */}
          <div className="form-row">
            <div className="form-group">
              <label>Номер пары</label>
              <input
                type="number"
                min="1"
                max="8"
                value={formData.lesson_number || ''}
                onChange={(e) => setFormData({...formData, lesson_number: e.target.value ? parseInt(e.target.value) : null})}
                placeholder="1, 2, 3..."
              />
            </div>

            {/* Подгруппа */}
            <div className="form-group">
              <label>Подгруппа</label>
              <select 
                value={formData.subgroup || ''} 
                onChange={(e) => setFormData({...formData, subgroup: e.target.value || null})}
              >
                <option value="">Вся группа</option>
                <option value="I">I подгруппа</option>
                <option value="II">II подгруппа</option>
              </select>
            </div>
          </div>

          {/* Тип занятия */}
          <div className="form-group">
            <label>Тип занятия</label>
            <select 
              value={formData.activity_type} 
              onChange={(e) => setFormData({...formData, activity_type: e.target.value})}
            >
              <option value="lesson">Урок</option>
              <option value="practice_edu">Учебная практика</option>
              <option value="practice_prod">Производственная практика</option>
            </select>
          </div>

          {/* Примечания */}
          <div className="form-group">
            <label>Примечания</label>
            <textarea
              value={formData.comment || ''}
              onChange={(e) => setFormData({...formData, comment: e.target.value})}
              placeholder="Дополнительная информация (кураторский час, разговор о важном и т.п.)"
              rows="3"
            />
          </div>

          {/* Кнопки */}
          <div className="form-actions">
            {lesson?.id && (
              <button type="button" className="btn-delete" onClick={handleDelete}>
                Удалить
              </button>
            )}
            <button type="button" className="btn-cancel" onClick={onClose}>
              Отмена
            </button>
            <button type="submit" className="btn-save">
              Сохранить
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
