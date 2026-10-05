<template>
  <BaseModal
    :show="show"
    :title="'Профиль: ' + user?.full_name"
    @close="$emit('close')"
    confirm-text="Закрыть"
    @confirm="$emit('close')"
    hide-cancel
    hide-close-icon
  >
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
          <span class="role-badge">{{ user.role?.toUpperCase() }}</span>
        </div>
        <div class="info-row">
          <span class="label">Статус:</span>
          <span
            class="status-indicator"
            :style="{ color: user.is_active !== false ? '#52c41a' : '#ff4d4f' }"
          >
            {{ user.is_active !== false ? 'Активен' : 'Заблокирован' }}
          </span>
        </div>
        <div class="info-row">
          <span class="label">Пароль:</span>
          <span class="value password-info">
            {{
              user.password_updated_at
                ? 'Обновлен ' + formatDate(user.password_updated_at)
                : 'С момента создания'
            }}
          </span>
        </div>
      </section>

      <!-- Управление паролем -->
      <section class="tech-section password-section glass-panel">
        <header class="section-title">
          <AppIcon name="lock" size="16" />
          Управление безопасностью
        </header>

        <div v-if="newPassword" class="generated-password animate-in">
          <span class="password-label">НОВЫЙ ПАРОЛЬ:</span>
          <div class="password-box">
            <span class="password-text">{{ newPassword }}</span>
            <button class="copy-btn" @click="copyPassword" title="Копировать">
              <AppIcon name="copy" size="14" />
            </button>
          </div>
          <p class="warning-text">Обязательно сохраните его сейчас!</p>
        </div>

        <div v-else class="password-actions">
          <div class="manual-reset" v-if="isEditingPassword">
            <input
              type="text"
              v-model="manualPassword"
              placeholder="Минимум 8 символов"
              class="password-input glass-panel"
            />
            <div class="edit-btns">
              <button
                class="small-btn save"
                @click="handleManualReset"
                :disabled="manualPassword.length < 8"
              >
                Сохранить
              </button>
              <button class="small-btn cancel" @click="isEditingPassword = false">Отмена</button>
            </div>
          </div>

          <div v-else class="action-grid">
            <button class="action-card reset" @click="generateAndReset">
              <AppIcon name="refresh" size="20" />
              <span>Сбросить и показать</span>
            </button>
            <button class="action-card edit" @click="isEditingPassword = true">
              <AppIcon name="edit" size="20" />
              <span>Установить свой</span>
            </button>
          </div>
        </div>
      </section>

      <!-- Технические данные -->
      <section class="tech-section glass-panel">
        <header class="section-title">
          <AppIcon name="settings" size="16" />
          Последняя активность
        </header>

        <div class="tech-grid" v-if="user.last_ip || user.last_user_agent">
          <div class="tech-item">
            <AppIcon :name="getDeviceIcon(user.device_type)" size="32" class="device-icon" />
            <div class="tech-info">
              <span class="tech-label">Устройство</span>
              <span class="tech-value">{{
                user.device_type ? user.device_type.toUpperCase() : 'DESKTOP'
              }}</span>
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

        <div v-else class="empty-tech">Нет данных о входах</div>
      </section>

      <div class="timestamps">Создан: {{ formatDate(user.created_at) }}</div>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useAdminStore } from '../../../store/admin'
import BaseModal from '../../../core/components/BaseModal.vue'
import AppIcon from '../../../core/components/AppIcon.vue'

const props = defineProps({
  show: Boolean,
  user: Object,
  loading: Boolean
})

const adminStore = useAdminStore()
const emit = defineEmits(['close'])

const newPassword = ref('')
const isEditingPassword = ref(false)
const manualPassword = ref('')

// Сброс состояния при закрытии/открытии
watch(
  () => props.show,
  val => {
    if (!val) {
      newPassword.value = ''
      isEditingPassword.value = false
      manualPassword.value = ''
    }
  }
)

const generatePassword = () => {
  const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*'
  return Array.from({ length: 12 }, () => chars[Math.floor(Math.random() * chars.length)]).join('')
}

const generateAndReset = async () => {
  const pwd = generatePassword()
  try {
    await adminStore.resetUserPassword(props.user.id, pwd)
    newPassword.value = pwd
  } catch (err) {
    alert('Ошибка при сбросе пароля')
  }
}

const handleManualReset = async () => {
  try {
    await adminStore.resetUserPassword(props.user.id, manualPassword.value)
    newPassword.value = manualPassword.value
    isEditingPassword.value = false
  } catch (err) {
    alert('Ошибка при смене пароля')
  }
}

const copyPassword = () => {
  navigator.clipboard.writeText(newPassword.value)
  alert('Пароль скопирован!')
}

const getDeviceIcon = type => {
  if (type === 'mobile') return 'smartphone'
  if (type === 'tablet') return 'tablet'
  return 'monitor'
}

const formatBrowser = ua => {
  if (!ua) return 'Неизвестно'
  if (ua.includes('Chrome')) return 'Google Chrome'
  if (ua.includes('Firefox')) return 'Mozilla Firefox'
  if (ua.includes('Safari') && !ua.includes('Chrome')) return 'Apple Safari'
  if (ua.includes('Edge')) return 'Microsoft Edge'
  return 'Другой'
}

const formatDate = dateStr => {
  if (!dateStr) return '—'
  const date = new Date(dateStr)
  return isNaN(date.getTime()) ? '—' : date.toLocaleString('ru-RU')
}
</script>

<style scoped>
.user-details {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.detail-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.label {
  color: var(--text-secondary);
  font-size: 0.9rem;
}
.value {
  font-weight: 700;
}
.password-info {
  font-size: 0.85rem;
  opacity: 0.8;
}

.role-badge {
  background: rgba(255, 215, 0, 0.1);
  color: var(--primary-color);
  padding: 4px 12px;
  border-radius: 8px;
  font-weight: 800;
  font-size: 0.8rem;
}

.status-indicator {
  font-weight: 700;
  font-size: 0.9rem;
}
.status-indicator.active {
  color: #52c41a;
}
.status-indicator:not(.active) {
  color: #ff4d4f;
}

.tech-section {
  padding: 20px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.02);
}
.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  font-weight: 800;
  text-transform: uppercase;
  margin-bottom: 20px;
  opacity: 0.6;
}

.tech-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
.tech-item {
  display: flex;
  align-items: center;
  gap: 12px;
}
.tech-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.tech-label {
  font-size: 0.75rem;
  opacity: 0.5;
  font-weight: 700;
}
.tech-value {
  font-weight: 600;
  font-size: 0.95rem;
}
.mono {
  font-family: monospace;
}
.truncate {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.device-icon {
  color: var(--primary-color);
  opacity: 0.8;
}

.password-section {
  border: 1px solid rgba(255, 215, 0, 0.1);
}
.action-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.action-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 16px;
  border-radius: 16px;
  border: none;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.03);
  color: var(--text-primary);
  transition: all 0.2s;
  font-size: 0.8rem;
  font-weight: 700;
}
.action-card:hover {
  background: rgba(255, 215, 0, 0.1);
  transform: translateY(-2px);
}
.action-card span {
  opacity: 0.8;
}

.generated-password {
  text-align: center;
  padding: 10px 0;
}
.password-label {
  font-size: 0.7rem;
  font-weight: 800;
  opacity: 0.5;
  letter-spacing: 1px;
}
.password-box {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin: 12px 0;
  background: rgba(0, 0, 0, 0.2);
  padding: 12px 20px;
  border-radius: 12px;
}
.password-text {
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.2rem;
  color: var(--primary-color);
  font-weight: 800;
}
.copy-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  opacity: 0.6;
}
.copy-btn:hover {
  opacity: 1;
  color: var(--primary-color);
}
.warning-text {
  font-size: 0.75rem;
  color: #ff4d4f;
  font-weight: 700;
}

.manual-reset {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.password-input {
  width: 100%;
  padding: 12px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(0, 0, 0, 0.2);
  color: white;
  outline: none;
  font-family: monospace;
}
.edit-btns {
  display: flex;
  gap: 8px;
}
.small-btn {
  flex: 1;
  padding: 10px;
  border-radius: 10px;
  border: none;
  font-weight: 700;
  cursor: pointer;
  font-size: 0.8rem;
}
.small-btn.save {
  background: var(--primary-color);
  color: #1c1b1f;
}
.small-btn.save:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}
.small-btn.cancel {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-secondary);
}

.timestamps {
  font-size: 0.75rem;
  opacity: 0.4;
  text-align: center;
  margin-top: 12px;
}

.loading-state {
  text-align: center;
  padding: 40px;
}
.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(255, 215, 0, 0.1);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
