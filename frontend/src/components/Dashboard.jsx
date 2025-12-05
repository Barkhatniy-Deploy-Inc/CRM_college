import React, { useState } from 'react';
import './Dashboard.css';
import ScheduleCalendar from './schedule/ScheduleCalendar';
import ScheduleForm from './schedule/ScheduleForm';

export default function Dashboard({ user, onLogout, apiUrl }) {
  // Стейт модального окна расписания
  const [showScheduleForm, setShowScheduleForm] = useState(false);
  const [editingSchedule, setEditingSchedule] = useState(null);
  const [scheduleRefreshKey, setScheduleRefreshKey] = useState(0);

  // --- HANDLERS ---
  const handleCreateSchedule = (initialDate = null) => {
    if (initialDate) {
      setEditingSchedule({ 
        isNew: true, 
        date_time: `${initialDate}T09:00:00` 
      });
    } else {
      setEditingSchedule(null);
    }
    setShowScheduleForm(true);
  };

  const handleEditSchedule = (entry) => {
    setEditingSchedule(entry);
    setShowScheduleForm(true);
  };

  const handleCloseScheduleForm = () => {
    setShowScheduleForm(false);
    setEditingSchedule(null);
  };

  const handleSaveSchedule = () => {
    setScheduleRefreshKey(prev => prev + 1);
    handleCloseScheduleForm();
  };

  return (
    <div className="dashboard">
      {/* Шапка */}
      <header className="dashboard-header">
        <h1>Умное расписание курсов</h1>
        <div className="user-info">
          <span>{user?.full_name || user?.email}</span>
          <button className="logout-btn" onClick={onLogout}>
            Выйти
          </button>
        </div>
      </header>

      {/* Основной контент - Календарь */}
      <main className="dashboard-content">
        <ScheduleCalendar
          key={scheduleRefreshKey}
          apiUrl={apiUrl}
          onEdit={handleEditSchedule}
          onCreateNew={handleCreateSchedule}
        />
      </main>

      {/* Модальное окно формы расписания */}
      {showScheduleForm && (
        <ScheduleForm
          entry={editingSchedule}
          onClose={handleCloseScheduleForm}
          onSave={handleSaveSchedule}
          apiUrl={apiUrl}
        />
      )}
    </div>
  );
}
