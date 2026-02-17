<template>
  <div class="admin-page">
    <header class="page-header animate-in">
      <div class="title-section">
        <BaseButton variant="outline" @click="$router.back()" class="back-btn">
          <AppIcon name="chevron-left" size="18" />
        </BaseButton>
        <h1>Управление пользователями</h1>
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
            <th>ID</th>
            <th>Пользователь</th>
            <th>Email</th>
            <th>Роль</th>
            <th>Статус</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in adminStore.users" :key="user.id">
            <td class="mono">#{{ String(user.id).padStart(4, '0') }}</td>
            <td>
              <div class="user-cell">
                <div class="avatar">{{ user.full_name[0] }}</div>
                <span class="name">{{ user.full_name }}</span>
              </div>
            </td>
            <td>{{ user.email }}</td>
            <td><span class="role-badge" :class="user.role.toLowerCase()">{{ user.role }}</span></td>
            <td>
              <span class="status-dot" :class="{ active: user.is_active }"></span>
              {{ user.is_active ? 'Активен' : 'Заблокирован' }}
            </td>
            <td>
              <div class="actions-cell">
                <button class="icon-btn" @click="openDetails(user)" title="Просмотр">
                  <AppIcon name="user" size="16" />
                </button>
                <button class="icon-btn" @click="openEdit(user)" title="Редактировать">
                  <AppIcon name="settings" size="16" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </BaseCard>

    <!-- Модалка редактирования (ВОССТАНОВЛЕНА) -->
    <BaseModal 
      :show="!!selectedUser" 
      title="Редактирование пользователя" 
      @close="selectedUser = null"
      @confirm="handleUpdate"
      :loading="isUpdating"
    >
      <div class="edit-form" v-if="selectedUser">
        <BaseInput label="Полное имя" v-model="editForm.full_name" />
        
        <div class="select-group">
          <label class="styled-label">Роль в системе</label>
          <select v-model="editForm.role" class="styled-select glass-panel">
            <option value="student">Студент</option>
            <option value="teacher">Преподаватель</option>
            <option value="moderator">Модератор</option>
            <option value="admin">Администратор</option>
          </select>
        </div>

        <div class="checkbox-group">
          <label class="switch">
            <input type="checkbox" v-model="editForm.is_active">
            <span class="slider"></span>
          </label>
          <span class="label-text">Аккаунт активен</span>
        </div>
      </div>
    </BaseModal>

    <!-- Модалка деталей -->
    <UserDetailModal 
      :show="showDetails" 
      :user="userDetails" 
      :loading="isLoadingDetails"
      @close="showDetails = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useAdminStore } from '../../../store/admin'
import BaseCard from '../../../core/components/BaseCard.vue'
import BaseButton from '../../../core/components/BaseButton.vue'
import BaseInput from '../../../core/components/BaseInput.vue'
import BaseModal from '../../../core/components/BaseModal.vue'
import AppIcon from '../../../core/components/AppIcon.vue'
import UserDetailModal from './UserDetailModal.vue'

const adminStore = useAdminStore()
const selectedUser = ref(null)
const isUpdating = ref(false)

// Состояние для деталей
const showDetails = ref(false)
const userDetails = ref(null)
const isLoadingDetails = ref(false)

const editForm = reactive({
  full_name: '',
  role: '',
  is_active: true
})

const fetchData = () => adminStore.fetchUsers()

const openEdit = (user) => {
  selectedUser.value = user
  editForm.full_name = user.full_name
  editForm.role = user.role.toLowerCase()
  editForm.is_active = user.is_active
}

const openDetails = async (user) => {
  showDetails.value = true
  isLoadingDetails.value = true
  try {
    userDetails.value = await adminStore.fetchUserDetails(user.id)
  } catch (err) {
    alert('Не удалось загрузить детали пользователя')
    showDetails.value = false
  } finally {
    isLoadingDetails.value = false
  }
}

const handleUpdate = async () => {
  isUpdating.value = true
  try {
    await adminStore.updateUser(selectedUser.value.id, { ...editForm })
    selectedUser.value = null
    await fetchData() // Обновляем список для актуализации статусов
  } catch (e) {
    alert('Ошибка при обновлении')
  } finally {
    isUpdating.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.admin-page { max-width: 1200px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 32px; }
.title-section { display: flex; align-items: center; gap: 16px; }
h1 { margin: 0; font-size: 1.8rem; font-weight: 800; }

.table-card { padding: 0; overflow: hidden; position: relative; min-height: 400px; }
.admin-table { width: 100%; border-collapse: collapse; text-align: left; }
th { padding: 16px 24px; background: rgba(255, 255, 255, 0.03); font-size: 0.8rem; text-transform: uppercase; color: var(--text-secondary); font-weight: 700; }
td { padding: 16px 24px; border-bottom: 1px solid rgba(255, 255, 255, 0.05); font-size: 0.9rem; }

.mono { font-family: 'JetBrains Mono', monospace; opacity: 0.6; }
.user-cell { display: flex; align-items: center; gap: 12px; }
.avatar { width: 32px; height: 32px; border-radius: 10px; background: var(--primary-color); color: #1C1B1F; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 0.8rem; }
.name { font-weight: 600; }

.role-badge { padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; }
.role-badge.admin { background: rgba(255, 77, 79, 0.15); color: #ff4d4f; }
.role-badge.student { background: rgba(255, 215, 0, 0.15); color: var(--primary-color); }
.role-badge.teacher { background: rgba(64, 169, 255, 0.15); color: #40a9ff; }

.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #ff4d4f; margin-right: 8px; }
.status-dot.active { background: #52c41a; box-shadow: 0 0 10px rgba(82, 196, 26, 0.4); }

.actions-cell { display: flex; gap: 8px; }
.icon-btn { background: transparent; border: none; color: var(--text-secondary); cursor: pointer; padding: 8px; border-radius: 8px; transition: all 0.2s; }
.icon-btn:hover { background: rgba(255, 255, 255, 0.1); color: var(--primary-color); }

.loading-overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.2); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 10; }
.spinner { width: 32px; height: 32px; border: 3px solid rgba(255, 215, 0, 0.1); border-top-color: var(--primary-color); border-radius: 50%; animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Form styles */
.edit-form { display: flex; flex-direction: column; gap: 20px; }
.select-group { display: flex; flex-direction: column; gap: 8px; }
.styled-label { font-size: 0.85rem; font-weight: 700; text-transform: uppercase; opacity: 0.7; margin-left: 4px; }
.styled-select { width: 100%; padding: 14px 16px; border-radius: 14px; background: var(--input-bg); color: var(--text-primary); border: 1px solid rgba(255, 255, 255, 0.1); font-family: inherit; font-size: 1rem; outline: none; cursor: pointer; }
.checkbox-group { display: flex; align-items: center; gap: 12px; margin-top: 8px; }
.label-text { font-weight: 600; font-size: 0.95rem; }

.switch { position: relative; display: inline-block; width: 48px; height: 24px; }
.switch input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; cursor: pointer; inset: 0; background-color: rgba(255, 255, 255, 0.1); transition: .4s; border-radius: 24px; }
.slider:before { position: absolute; content: ""; height: 18px; width: 18px; left: 3px; bottom: 3px; background-color: white; transition: .4s; border-radius: 50%; }
input:checked + .slider { background-color: var(--primary-color); }
input:checked + .slider:before { transform: translateX(24px); background-color: #1C1B1F; }
</style>
