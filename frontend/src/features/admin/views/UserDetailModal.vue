<template>
  <BaseModal :show="show" :title="'Профиль: ' + user?.full_name" @close="$emit('close')" confirm-text="Закрыть" @confirm="$emit('close')">
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Загрузка данных...</p>
    </div>

    <div v-else-if="user" class="user-details">
      <!-- Основная инфа -->
      <section class="detail-section">
        <div class="info-row">
          <span class="label">Email:</span>
          <span class="value">{{ user.email }}</span>
        </div>
        <div class="info-row">
          <span class="label">Роль:</span>
          <span class="role-badge">{{ user.role }}</span>
        </div>
        <div class="info-row">
          <span class="label">Статус:</span>
          <span class="status-indicator" :style="{ color: user.is_active ? '#52c41a' : '#ff4d4f' }">
            {{ user.is_active ? 'Активен' : 'Заблокирован' }}
          </span>
        </div>
      </section>

      <!-- Технические данные -->
      <section class="tech-section glass-panel">
        <header class="section-title">
          <AppIcon name="settings" size="16" />
          Последняя активность
        </header>
        
        <div class="tech-grid" v-if="user.last_login">
          <div class="tech-item">
            <AppIcon :name="getDeviceIcon(user.device_type)" size="32" class="device-icon" />
            <div class="tech-info">
              <span class="tech-label">Устройство</span>
              <span class="tech-value">{{ user.device_type || 'Desktop' }}</span>
            </div>
          </div>

          <div class="tech-item">
            <div class="tech-info">
              <span class="tech-label">Браузер</span>
              <span class="tech-value truncate" :title="user.last_user_agent">
                {{ formatBrowser(user.last_user_agent) }}
              </span>
            </div>
          </div>

          <div class="tech-item">
            <div class="tech-info">
              <span class="tech-label">IP Адрес</span>
              <span class="tech-value mono">{{ user.last_ip || '—' }}</span>
            </div>
          </div>
        </div>
        
        <div v-else class="empty-tech">
          Нет данных о входах
        </div>
      </section>

      <div class="timestamps">
        Создан: {{ formatDate(user.created_at) }}
      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, watch } from 'vue'
import BaseModal from '../../../core/components/BaseModal.vue'
import AppIcon from '../../../core/components/AppIcon.vue'

const props = defineProps({
  show: Boolean,
  user: Object,
  loading: Boolean
})

watch(() => props.user, (newVal) => {
  if (newVal) {
    console.log('DEBUG: User details received:', {
      email: newVal.email,
      is_active: newVal.is_active,
      type: typeof newVal.is_active
    })
  }
})

defineEmits(['close'])

const getDeviceIcon = (type) => {
  if (type === 'mobile') return 'smartphone'
  if (type === 'tablet') return 'tablet'
  return 'monitor'
}

const formatBrowser = (ua) => {
  if (!ua) return 'Неизвестно'
  if (ua.includes('Chrome')) return 'Google Chrome'
  if (ua.includes('Firefox')) return 'Mozilla Firefox'
  if (ua.includes('Safari') && !ua.includes('Chrome')) return 'Apple Safari'
  if (ua.includes('Edge')) return 'Microsoft Edge'
  return 'Другой'
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString('ru-RU')
}
</script>

<style scoped>
.user-details { display: flex; flex-direction: column; gap: 24px; }

.detail-section { display: flex; flex-direction: column; gap: 12px; }
.info-row { display: flex; justify-content: space-between; align-items: center; }
.label { color: var(--text-secondary); font-size: 0.9rem; }
.value { font-weight: 700; }

.role-badge { 
  background: rgba(255, 215, 0, 0.1); color: var(--primary-color);
  padding: 4px 12px; border-radius: 8px; font-weight: 800; font-size: 0.8rem;
}

.status-indicator { font-weight: 700; font-size: 0.9rem; }
.status-indicator.active { color: #52c41a; }
.status-indicator:not(.active) { color: #ff4d4f; }

.tech-section { padding: 20px; border-radius: 20px; background: rgba(255,255,255,0.02); }
.section-title { 
  display: flex; align-items: center; gap: 8px; 
  font-size: 0.85rem; font-weight: 800; text-transform: uppercase;
  margin-bottom: 20px; opacity: 0.6;
}

.tech-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.tech-item { display: flex; align-items: center; gap: 12px; }
.tech-info { display: flex; flex-direction: column; gap: 2px; }
.tech-label { font-size: 0.75rem; opacity: 0.5; font-weight: 700; }
.tech-value { font-weight: 600; font-size: 0.95rem; }
.mono { font-family: monospace; }
.truncate { max-width: 150px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.device-icon { color: var(--primary-color); opacity: 0.8; }

.timestamps { font-size: 0.75rem; opacity: 0.4; text-align: center; margin-top: 12px; }

.loading-state { text-align: center; padding: 40px; }
.spinner { 
  width: 32px; height: 32px; border: 3px solid rgba(255,215,0,0.1); 
  border-top-color: var(--primary-color); border-radius: 50%; 
  animation: spin 1s linear infinite; margin: 0 auto 16px;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
