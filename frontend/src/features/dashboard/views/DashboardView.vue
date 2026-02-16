<template>
  <div class="dashboard-container">
    <header class="dashboard-header animate-in">
      <div class="welcome-section">
        <h1>{{ greeting }}, {{ authStore.user?.full_name?.split(' ')[0] || 'Студент' }}!</h1>
        <p class="subtitle">Удачного учебного дня. Вот что вас ждет сегодня.</p>
      </div>
    </header>

    <div class="dashboard-grid">
      <!-- Ближайшие занятия -->
      <BaseCard class="grid-item schedule-widget">
        <div class="widget-header">
          <div class="title-with-icon">
            <AppIcon name="schedule" class="header-icon" />
            <h3>Ближайшие занятия</h3>
          </div>
          <router-link to="/schedule" class="view-all">Смотреть всё</router-link>
        </div>
        
        <div class="schedule-content">
          <div v-if="scheduleStore.isLoading" class="skeleton-list">
            <div v-for="i in 2" :key="i" class="skeleton-item"></div>
          </div>
          
          <div v-else-if="upcomingLessons.length > 0" class="lesson-list">
             <div v-for="lesson in upcomingLessons" :key="lesson.id" class="mini-lesson-card glass-panel">
                <div class="time-box">
                  <span class="start">{{ lesson.start_time.split('T')[1]?.slice(0, 5) || '08:30' }}</span>
                  <AppIcon name="clock" size="14" class="time-icon" />
                </div>
                <div class="lesson-info">
                  <span class="subject">{{ lesson.title }}</span>
                  <div class="meta">
                    <span class="meta-item"><AppIcon name="location" size="12" /> {{ lesson.auditorium_id || '201' }}</span>
                    <span class="meta-item"><AppIcon name="user" size="12" /> {{ lesson.instructor }}</span>
                  </div>
                </div>
             </div>
          </div>

          <div v-else class="empty-state">
            <AppIcon name="coffee" size="48" class="empty-icon" />
            <p>На сегодня занятий больше нет.<br>Отличное время для отдыха!</p>
          </div>
        </div>
      </BaseCard>

      <!-- Статус пользователя -->
      <BaseCard class="grid-item info-card">
        <div class="widget-header">
          <div class="title-with-icon">
            <AppIcon name="user" class="header-icon" />
            <h3>Ваш профиль</h3>
          </div>
        </div>
        <div class="status-info">
          <div class="status-item">
            <span class="label">Роль:</span>
            <span class="value badge">{{ authStore.user?.role }}</span>
          </div>
          <div class="status-item">
            <span class="label">Группа:</span>
            <span class="value">{{ authStore.user?.group || 'ИСП-21' }}</span>
          </div>
          <div class="status-item">
            <span class="label">ID:</span>
            <span class="value mono">#{{ String(authStore.user?.id || '0').padStart(4, '0') }}</span>
          </div>
        </div>
      </BaseCard>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../../../store/auth'
import { useScheduleStore } from '../../../store/schedule'
import BaseCard from '../../../core/components/BaseCard.vue'
import AppIcon from '../../../core/components/AppIcon.vue'

const authStore = useAuthStore()
const scheduleStore = useScheduleStore()

const upcomingLessons = computed(() => {
  return scheduleStore.lessons.slice(0, 3)
})

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return 'Доброй ночи'
  if (hour < 12) return 'Доброе утро'
  if (hour < 18) return 'Добрый день'
  return 'Добрый вечер'
})

onMounted(async () => {
  try {
    await scheduleStore.fetchUpcoming()
  } catch (e) {
    console.error('Failed to load dashboard data', e)
  }
})
</script>

<style scoped>
.dashboard-container {
  padding: 8px;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 32px;
  margin-top: 12px;
}

h1 {
  font-size: 2.2rem;
  font-weight: 800;
  margin: 0;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.subtitle {
  font-size: 1.05rem;
  color: var(--text-secondary);
  margin-top: 8px;
  opacity: 0.8;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1.6fr 1fr;
  gap: 24px;
}

.widget-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.title-with-icon {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  color: var(--primary-color);
}

h3 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 700;
}

.view-all {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 700;
  font-size: 0.85rem;
  padding: 6px 12px;
  border-radius: 8px;
  background: rgba(255, 215, 0, 0.1);
  transition: all 0.2s ease;
}

.view-all:hover {
  background: var(--primary-color);
  color: #1C1B1F;
}

.mini-lesson-card {
  display: flex;
  gap: 20px;
  padding: 16px;
  border-radius: 16px;
  margin-bottom: 12px;
  background: rgba(255, 255, 255, 0.03);
  transition: transform 0.2s ease;
}

.mini-lesson-card:hover {
  transform: scale(1.01);
}

.time-box {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-width: 60px;
  padding-right: 20px;
  border-right: 2px solid var(--primary-color);
  gap: 4px;
}

.time-box .start {
  font-weight: 800;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.time-icon {
  opacity: 0.5;
  color: var(--text-secondary);
}

.lesson-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.subject {
  font-weight: 700;
  font-size: 1.05rem;
}

.meta {
  display: flex;
  gap: 16px;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.empty-state {
  text-align: center;
  padding: 48px 0;
  color: var(--text-secondary);
}

.empty-icon {
  margin: 0 auto 16px;
  opacity: 0.5;
  color: var(--primary-color);
}

.status-info {
  margin-top: 8px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.status-item:last-child {
  border-bottom: none;
}

.label {
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
}

.value {
  font-weight: 700;
  color: var(--text-primary);
  font-size: 0.95rem;
}

.value.badge {
  background: var(--primary-color);
  color: #1C1B1F;
  padding: 2px 10px;
  border-radius: 6px;
  font-size: 0.75rem;
  text-transform: uppercase;
}

.value.mono {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  opacity: 0.7;
}

/* Skeleton loader */
.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.skeleton-item {
  height: 80px;
  background: linear-gradient(90deg, rgba(255,255,255,0.05) 25%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0.05) 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 12px;
}

@keyframes loading {
  from { background-position: 200% 0; }
  to { background-position: -200% 0; }
}

@media (max-width: 900px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}
</style>
