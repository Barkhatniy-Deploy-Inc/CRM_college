import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import Schedule from './Schedule';
import TechCard from './TechCard';
import './Dashboard.css';

export default function Dashboard() {
    const { user, logout } = useAuth();
    const [activeTab, setActiveTab] = useState('schedule');

    return (
        <div className="dashboard">
            <header className="header-nav">
                <div className="container header-container">
                    <div className="logo-section">
                        <h2>CRM College</h2>
                    </div>

                    <nav className="main-nav">
                        <button
                            className={`nav-item ${activeTab === 'schedule' ? 'active' : ''}`}
                            onClick={() => setActiveTab('schedule')}
                        >
                            Расписание
                        </button>
                        <button
                            className={`nav-item ${activeTab === 'techcard' ? 'active' : ''}`}
                            onClick={() => setActiveTab('techcard')}
                        >
                            Техкарты
                        </button>
                    </nav>

                    <div className="user-section">
                        <div className="user-info">
                            <span className="user-name">{user?.full_name || user?.email}</span>
                        </div>
                        <button onClick={logout} className="btn btn-glass btn-sm">
                            Выйти
                        </button>
                    </div>
                </div>
            </header>

            <main className="main-content">
                <div className="container">
                    {activeTab === 'schedule' ? <Schedule /> : <TechCard />}
                </div>
            </main>
        </div>
    );
}
