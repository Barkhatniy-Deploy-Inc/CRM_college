<template>
  <div class="logs-page">
    <header class="page-header animate-in">
      <div class="title-section">
        <h1>Аудит системы</h1>
        <p class="subtitle">Мониторинг критических действий и безопасности</p>
      </div>
      <div class="header-actions">
        <BaseButton variant="outline" @click="fetchLogs">
          <AppIcon name="activity" size="18" class="btn-icon" />
          Обновить
        </BaseButton>
      </div>
    </header>

    <div class="logs-container glass-panel">
      <!-- Панель фильтров -->
      <aside class="filters-sidebar">
        <h3>Фильтры</h3>
        <div class="filter-group">
          <label>Тип действия</label>
          <select v-model="filters.action" class="styled-select">
            <option value="">Все события</option>
            <option value="security_alert">🚨 Безопасность</option>
            <option value="login">🔑 Вход в систему</option>
            <option value="schedule_edited">🗓️ Расписание</option>
            <option value="user_deleted">❌ Удаление пользователей</option>
          </select>
        </div>
        <div class="filter-group">
          <label>ID пользователя</label>
          <input type="number" v-model="filters.user_id" placeholder="Любой..." class="styled-input" />
        </div>
        <div class="filter-group">
          <label>Период</label>
          <input type="date" v-model="filters.date_from" class="styled-input" />
          <input type="date" v-model="filters.date_to" class="styled-input" />
        </div>
      </aside>

      <!-- Основная лента логов -->
      <main class="logs-feed">
        <div v-if="adminStore.isLoading" class="loading-state">
          <div class="spinner"></div>
          <p>Сканирование архивов...</p>
        </div>

        <div v-else-if="adminStore.auditLogs.length === 0" class="empty-state">
          <AppIcon name="shield" size="48" class="empty-icon" />
          <p>Подозрительная активность не обнаружена</p>
        </div>

        <div v-else class="terminal-logs">
          <div 
            v-for="log in adminStore.auditLogs" 
            :key="log.id" 
            class="log-entry"
            :class="getLogSeverity(log.action)"
            @click="selectedLog = log"
          >
            <span class="log-time">[{{ formatTime(log.created_at) }}]</span>
            <span class="log-badge">{{ formatAction(log.action) }}</span>
            <span class="log-user">User #{{ log.user_id || 'SYSTEM' }}</span>
            <span class="log-ip">{{ log.ip_address || 'local' }}</span>
            <span class="log-message">{{ getShortMessage(log) }}</span>
          </div>
        </div>
      </main>
    </div>

    <!-- Модалка деталей (JSON Inspector) -->
    <BaseModal 
      :show="!!selectedLog" 
      :title="'Детали события #' + selectedLog?.id" 
      @close="selectedLog = null"
    >
      <div class="log-details" v-if="selectedLog">
        <div class="detail-row">
          <strong>Действие:</strong> 
          <span :class="getLogSeverity(selectedLog.action)">{{ selectedLog.action }}</span>
        </div>
        <div class="detail-row">
          <strong>Время:</strong> {{ formatDateTime(selectedLog.created_at) }}
        </div>
        <div class="detail-row">
          <strong>IP / Браузер:</strong> {{ selectedLog.ip_address }} / {{ selectedLog.user_agent }}
        </div>
        <div class="metadata-section">
          <label>Полные данные (JSON):</label>
          <pre class="json-box">{{ formatJSON(selectedLog.details) }}</pre>
        </div>
      </div>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useAdminStore } from '../../../store/admin'
import BaseButton from '../../../core/components/BaseButton.vue'
import BaseModal from '../../../core/components/BaseModal.vue'
import AppIcon from '../../../core/components/AppIcon.vue'

const adminStore = useAdminStore()
const selectedLog = ref(null)

const filters = reactive({
  action: '',
  user_id: '',
  date_from: '',
  date_to: ''
})

const fetchLogs = () => {
  adminStore.fetchAuditLogs({ ...filters })
}

watch(filters, () => fetchLogs())

const getLogSeverity = (action) => {
  const cleanAction = action.replace('AuditAction.', '').toLowerCase()
  if (['security_alert', 'unauthorized_access', 'user_deleted'].includes(cleanAction)) return 'critical'
  if (['schedule_edited', 'role_change', 'password_change'].includes(cleanAction)) return 'warning'
  return 'info'
}

const formatAction = (action) => {
  return action.replace('AuditAction.', '').toUpperCase()
}

const formatTime = (dateStr) => {
  return new Date(dateStr).toLocaleTimeString('ru-RU', { hour12: false })
}

const formatDateTime = (dateStr) => {
  return new Date(dateStr).toLocaleString('ru-RU')
}

const getShortMessage = (log) => {
  try {
    const details = JSON.parse(log.details)
    if (log.action === 'login') return `Вход выполнен`
    if (details?.email) return `Объект: ${details.email}`
    return ''
  } catch (e) { return '' }
}

const formatJSON = (jsonStr) => {
  try {
    return JSON.stringify(JSON.parse(jsonStr), null, 2)
  } catch (e) { return jsonStr }
}

onMounted(() => fetchLogs())
</script>

<style scoped>
.logs-page { max-width: 1400px; margin: 0 auto; height: 100%; display: flex; flex-direction: column; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
h1 { font-size: 2.2rem; font-weight: 800; margin: 0; }
.subtitle { color: var(--text-secondary); }

.logs-container { 
  display: grid; grid-template-columns: 280px 1fr; gap: 1px; 
  background: var(--glass-border); overflow: hidden; height: 70vh;
}

.filters-sidebar { background: var(--bg-color); padding: 24px; display: flex; flex-direction: column; gap: 20px; }
.filters-sidebar h3 { margin: 0 0 16px 0; font-size: 1rem; opacity: 0.6; text-transform: uppercase; }

.filter-group { display: flex; flex-direction: column; gap: 8px; }
.filter-group label { font-size: 0.8rem; font-weight: 700; color: var(--text-secondary); }

.logs-feed { background: #0a0a0c; overflow-y: auto; position: relative; }

.terminal-logs { padding: 16px; font-family: 'JetBrains Mono', 'Fira Code', monospace; font-size: 0.85rem; line-height: 1.6; }

.log-entry { 
  padding: 8px 12px; border-radius: 6px; cursor: pointer; 
  display: flex; gap: 16px; transition: background 0.2s;
  border-left: 3px solid transparent;
}
.log-entry:hover { background: rgba(255, 255, 255, 0.05); }

.log-time { color: #5c6370; }
.log-badge { font-weight: 800; min-width: 140px; }
.log-user { color: var(--primary-color); min-width: 100px; }
.log-ip { color: #61afef; min-width: 120px; }
.log-message { color: var(--text-secondary); flex: 1; }

/* Severities */
.critical { color: #e06c75; border-color: #e06c75; }
.warning { color: #d19a66; border-color: #d19a66; }
.info { color: #98c379; border-color: #98c379; }

.json-box { 
  background: #1e1e1e; padding: 16px; border-radius: 12px; 
  font-family: monospace; font-size: 0.9rem; color: #dcdcdc;
  max-height: 300px; overflow-y: auto; border: 1px solid rgba(255,255,255,0.1);
}

.detail-row { margin-bottom: 12px; font-size: 1rem; }
.detail-row strong { color: var(--text-secondary); margin-right: 8px; }

.loading-state, .empty-state { 
  height: 100%; display: flex; flex-direction: column; 
  align-items: center; justify-content: center; color: var(--text-secondary);
}

.spinner { 
  width: 40px; height: 40px; border: 4px solid rgba(255,215,0,0.1); 
  border-top-color: var(--primary-color); border-radius: 50%; 
  animation: spin 1s linear infinite; margin-bottom: 16px;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
