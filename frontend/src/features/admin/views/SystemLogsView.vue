<template>
  <div class="admin-page">
    <header class="page-header">
      <div class="title-section">
        <BaseButton variant="outline" @click="$router.back()" class="back-btn">
          <AppIcon name="chevron-left" size="18" />
        </BaseButton>
        <h1>Системные логи</h1>
      </div>
      <div class="actions">
        <BaseButton @click="fetchData">
          <AppIcon name="activity" size="18" class="btn-icon" />
          Обновить
        </BaseButton>
      </div>
    </header>

    <BaseCard class="table-card glass-panel">
      <div v-if="adminStore.isLoading" class="loading-overlay">
        <div class="spinner"></div>
      </div>

      <table class="admin-table">
        <thead>
          <tr>
            <th>Время</th>
            <th>Действие</th>
            <th>Пользователь</th>
            <th>IP адрес</th>
            <th>Детали</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in adminStore.auditLogs" :key="log.id">
            <td class="date">{{ formatDate(log.created_at) }}</td>
            <td><span class="action-badge">{{ log.action }}</span></td>
            <td>
              <span v-if="log.user_id" class="user-link">ID: {{ log.user_id }}</span>
              <span v-else class="system">Система</span>
            </td>
            <td class="mono">{{ log.ip_address || '—' }}</td>
            <td class="details">{{ formatDetails(log.details) }}</td>
          </tr>
        </tbody>
      </table>

      <div v-if="adminStore.auditLogs.length === 0 && !adminStore.isLoading" class="empty-table">
        Записей в аудите пока нет
      </div>
    </BaseCard>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAdminStore } from '../../../store/admin'
import BaseCard from '../../../core/components/BaseCard.vue'
import BaseButton from '../../../core/components/BaseButton.vue'
import AppIcon from '../../../core/components/AppIcon.vue'

const adminStore = useAdminStore()

const fetchData = () => adminStore.fetchAuditLogs()

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString('ru-RU', { 
    day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', second: '2-digit'
  })
}

const formatDetails = (details) => {
  if (!details) return '—'
  return typeof details === 'object' ? JSON.stringify(details).slice(0, 50) + '...' : details
}

onMounted(fetchData)
</script>

<style scoped>
/* Стили идентичны UsersManagementView для единообразия */
.admin-page { max-width: 1200px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 32px; }
.title-section { display: flex; align-items: center; gap: 16px; }
h1 { margin: 0; font-size: 1.8rem; font-weight: 800; }
.back-btn { padding: 8px; min-height: auto; }
.table-card { padding: 0; overflow: hidden; position: relative; min-height: 400px; }
.admin-table { width: 100%; border-collapse: collapse; text-align: left; }
th { padding: 16px 24px; background: rgba(255, 255, 255, 0.03); font-size: 0.8rem; text-transform: uppercase; color: var(--text-secondary); font-weight: 700; }
td { padding: 14px 24px; border-bottom: 1px solid rgba(255, 255, 255, 0.05); font-size: 0.85rem; }
.mono { font-family: 'JetBrains Mono', monospace; opacity: 0.7; }
.date { white-space: nowrap; color: var(--text-secondary); }
.action-badge { 
  background: rgba(255, 215, 0, 0.1); 
  color: var(--primary-color); 
  padding: 4px 8px; 
  border-radius: 6px; 
  font-size: 0.75rem; 
  font-weight: 700;
}
.details { font-size: 0.8rem; opacity: 0.6; max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.loading-overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.2); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 10; }
.spinner { width: 32px; height: 32px; border: 3px solid rgba(255, 215, 0, 0.1); border-top-color: var(--primary-color); border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.empty-table { text-align: center; padding: 64px; color: var(--text-secondary); }
</style>
