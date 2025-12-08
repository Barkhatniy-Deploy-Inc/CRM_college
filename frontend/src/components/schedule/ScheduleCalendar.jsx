import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Schedule.css';

const WEEKDAYS = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'];

export default function ScheduleCalendar({ apiUrl, onEdit, onCreateNew }) {
  const [weekStart, setWeekStart] = useState(getMonday(new Date()));
  const [lessons, setLessons] = useState([]);
  const [groups, setGroups] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState(1);
  const [selectedDay, setSelectedDay] = useState(0); // 0-5 (пн-сб)
  const [loading, setLoading] = useState(false);

  function getMonday(date) {
    const d = new Date(date);
    const day = d.getDay();
    const diff = d.getDate() - day + (day === 0 ? -6 : 1);
    return new Date(d.setDate(diff));
  }

  // Загрузка групп
  useEffect(() => {
    const fetchGroups = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(`${apiUrl}/api/schedule/groups`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setGroups(response.data.filter(g => g.course === selectedCourse));
      } catch (error) {
        console.error('Ошибка загрузки групп:', error);
      }
    };
    fetchGroups();
  }, [apiUrl, selectedCourse]);

  // Загрузка занятий
  useEffect(() => {
    if (groups.length === 0) return;

    const fetchLessons = async () => {
      setLoading(true);
      try {
        const token = localStorage.getItem('token');
        const targetDate = new Date(weekStart.getTime() + selectedDay * 24 * 60 * 60 * 1000);
        const dateStr = targetDate.toISOString().slice(0, 10);

        const response = await axios.get(`${apiUrl}/schedule/lessons`, {
          headers: { Authorization: `Bearer ${token}` },
          params: {
            date: dateStr,
            group_ids: groups.map(g => g.id).join(',')
          }
        });
        setLessons(response.data);
      } catch (error) {
        console.error('Ошибка загрузки занятий:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchLessons();
  }, [apiUrl, weekStart, selectedDay, groups]);

  const prevWeek = () => setWeekStart(new Date(weekStart.getTime() - 7 * 24 * 60 * 60 * 1000));
  const nextWeek = () => setWeekStart(new Date(weekStart.getTime() + 7 * 24 * 60 * 60 * 1000));
  const goToday = () => setWeekStart(getMonday(new Date()));

  // Группировка по времени
  const timeSlots = [...new Set(lessons.map(l => `${l.time_start}-${l.time_end}`))].sort();

  // Получить занятие для конкретной группы и времени
  const getLessonForGroupAndTime = (groupId, timeSlot) => {
    return lessons.find(l => 
      l.group_id === groupId && 
      `${l.time_start}-${l.time_end}` === timeSlot
    );
  };

  const formatWeekRange = () => {
    const endDate = new Date(weekStart.getTime() + 5 * 24 * 60 * 60 * 1000);
    return `${weekStart.toLocaleDateString('ru-RU')} - ${endDate.toLocaleDateString('ru-RU')}`;
  };

  const currentDate = new Date(weekStart.getTime() + selectedDay * 24 * 60 * 60 * 1000);

  // Создание нового занятия
  const handleCreateLesson = () => {
    onCreateNew({
      date: currentDate.toISOString().slice(0, 10),
      time_start: '09:00',
      time_end: '10:20',
      group_id: groups.length > 0 ? groups[0].id : null
    });
  };

  return (
    <div className="schedule-calendar">
      {/* Панель управления */}
      <div className="schedule-controls">
        <div className="week-navigation">
          <button onClick={prevWeek} className="nav-btn">◀ Предыдущая неделя</button>
          <button onClick={goToday} className="today-btn">Текущая неделя</button>
          <button onClick={nextWeek} className="nav-btn">Следующая неделя ▶</button>
        </div>

        <div className="week-info">
          <h2>{formatWeekRange()}</h2>
        </div>

        <div className="controls-right">
          <div className="course-selector">
            <label>Курс:</label>
            <select 
              value={selectedCourse} 
              onChange={(e) => setSelectedCourse(Number(e.target.value))}
            >
              {[1, 2, 3, 4].map(course => (
                <option key={course} value={course}>{course} курс</option>
              ))}
            </select>
          </div>

          <button className="btn-create-lesson" onClick={handleCreateLesson}>
            + Создать занятие
          </button>
        </div>
      </div>

      {/* Навигация по дням недели */}
      <div className="weekday-tabs">
        {WEEKDAYS.map((day, idx) => (
          <button
            key={idx}
            className={`weekday-tab ${selectedDay === idx ? 'active' : ''}`}
            onClick={() => setSelectedDay(idx)}
          >
            {day}
            <span className="tab-date">
              {new Date(weekStart.getTime() + idx * 24 * 60 * 60 * 1000)
                .toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' })}
            </span>
          </button>
        ))}
      </div>

      {/* Таблица расписания */}
      {loading ? (
        <div className="loading">Загрузка...</div>
      ) : (
        <div className="schedule-table-wrapper">
          <table className="schedule-table">
            <thead>
              <tr>
                <th className="time-column">Время</th>
                {groups.map(group => (
                  <th key={group.id} className="group-column">{group.name}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {timeSlots.length > 0 ? (
                timeSlots.map((timeSlot, idx) => (
                  <tr key={idx}>
                    <td className="time-cell">{timeSlot}</td>
                    {groups.map(group => {
                      const lesson = getLessonForGroupAndTime(group.id, timeSlot);
                      return (
                        <td
                          key={group.id}
                          className={`lesson-cell ${lesson ? 'has-lesson' : 'empty-cell'}`}
                          onClick={() => {
                            if (lesson) {
                              onEdit(lesson);
                            } else {
                              const [startTime, endTime] = timeSlot.split('-');
                              onCreateNew({
                                date: currentDate.toISOString().slice(0, 10),
                                time_start: startTime,
                                time_end: endTime,
                                group_id: group.id
                              });
                            }
                          }}
                        >
                          {lesson ? (
                            <div className="lesson-content">
                              <div className="lesson-subject">{lesson.subject_name}</div>
                              <div className="lesson-teacher">{lesson.teacher_name}</div>
                              {lesson.auditorium_number && (
                                <div className="lesson-room">ауд. {lesson.auditorium_number}</div>
                              )}
                            </div>
                          ) : (
                            <div className="empty-slot">+</div>
                          )}
                        </td>
                      );
                    })}
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={groups.length + 1} className="no-lessons">
                    Занятий нет. Нажмите кнопку "Создать занятие" чтобы добавить первое.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}