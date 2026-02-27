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
        <button @click="openCreate" class="btn-primary create-btn">
          <AppIcon name="plus" size="20" />
          <span>Добавить пользователя</span>
        </button>
        <button @click="fetchData" class="btn-secondary" title="Обновить список">
          <AppIcon name="refresh" size="18" :class="{ 'spin': adminStore.isLoading }" />
        </button>
      </div>
    </header>

    <div class="table-container glass-panel animate-in">
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
            <th class="text-right">Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in adminStore.users" :key="user.id" class="table-row">
            <td class="mono-id">#{{ String(user.id).padStart(4, '0') }}</td>
            <td>
              <div class="user-info-cell">
                <div class="user-avatar">{{ user.full_name[0] }}</div>
                <div class="user-meta">
                  <span class="user-name">{{ user.full_name }}</span>
                  <span class="user-sub">{{ user.role }}</span>
                </div>
              </div>
            </td>
            <td class="email-cell">{{ user.email }}</td>
            <td>
              <span class="badge-role" :class="user.role.toLowerCase()">
                {{ user.role }}
              </span>
            </td>
            <td>
              <div class="status-wrapper" :class="{ 'is-active': user.is_active }">
                <span class="status-dot"></span>
                <span class="status-text">{{ user.is_active ? 'Активен' : 'Заблокирован' }}</span>
              </div>
            </td>
            <td>
              <div class="actions-group justify-end">
                <button class="action-btn view" @click="openDetails(user)" title="Детали профиля">
                  <AppIcon name="eye" size="18" />
                </button>
                <button class="action-btn edit" @click="openEdit(user)" title="Редактировать">
                  <AppIcon name="edit" size="18" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Модалка создания -->
    <BaseModal 
      :show="showCreateModal" 
      title="Новый пользователь" 
      @close="showCreateModal = false"
      @confirm="handleCreate"
      confirm-text="Создать"
      :loading="isCreating"
    >
      <div class="edit-form">
        <BaseInput label="Полное имя" v-model="createForm.full_name" placeholder="Иванов Иван Иванович" />
        <BaseInput label="Email" v-model="createForm.email" placeholder="user@sielom.ru" />
        <BaseInput label="Пароль" v-model="createForm.password" type="password" placeholder="Минимум 8 символов" />
        
        <div class="select-group">
          <label class="styled-label">Роль</label>
          <select v-model="createForm.role" class="styled-select glass-panel">
            <option value="student">Студент</option>
            <option value="teacher">Преподаватель</option>
            <option value="moderator">Модератор</option>
            <option value="admin">Администратор</option>
          </select>
        </div>
      </div>
    </BaseModal>

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
const isCreating = ref(false)
const showCreateModal = ref(false)

// Состояние для деталей
const showDetails = ref(false)
const userDetails = ref(null)
const isLoadingDetails = ref(false)

const editForm = reactive({
  full_name: '',
  role: '',
  is_active: true
})

const createForm = reactive({
  full_name: '',
  email: '',
  password: '',
  role: 'student'
})

const fetchData = () => adminStore.fetchUsers()

const openCreate = () => {
  createForm.full_name = ''
  createForm.email = ''
  createForm.password = ''
  createForm.role = 'student'
  showCreateModal.value = true
}

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

const handleCreate = async () => {
  if (createForm.password.length < 8) return alert('Пароль слишком короткий')
  isCreating.value = true
  try {
    await adminStore.createUser(createForm)
    showCreateModal.value = false
    await fetchData()
  } catch (e) {
    alert('Ошибка при создании пользователя: ' + (e.response?.data?.detail || 'Неизвестная ошибка'))
  } finally {
    isCreating.value = false
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
.admin-page { max-width: 1300px; margin: 0 auto; padding: 20px; }

/* Header & Actions */
.page-header { 
  display: flex; justify-content: space-between; align-items: center; 
  margin-bottom: 40px; 
}
.title-section { display: flex; align-items: center; gap: 20px; }
h1 { margin: 0; font-size: 2.2rem; font-weight: 900; letter-spacing: -0.5px; }

.actions { display: flex; gap: 12px; }

/* Premium Buttons */
.btn-primary {
  background: linear-gradient(135deg, var(--primary-color) 0%, #FFD700 100%);
  color: #1C1B1F; border: none; padding: 12px 24px; border-radius: 14px;
  font-weight: 800; display: flex; align-items: center; gap: 10px;
  cursor: pointer; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 15px rgba(255, 215, 0, 0.2);
}
.btn-primary:hover { 
  transform: translateY(-2px) scale(1.02); 
  box-shadow: 0 8px 25px rgba(255, 215, 0, 0.3);
}
.btn-primary:active { transform: translateY(0); }

.btn-secondary {
  background: rgba(255, 255, 255, 0.05); color: white;
  border: 1px solid rgba(255, 255, 255, 0.1); padding: 12px;
  border-radius: 14px; cursor: pointer; transition: all 0.2s;
}
.btn-secondary:hover { background: rgba(255, 255, 255, 0.1); border-color: var(--primary-color); }

/* Table Styling */
.table-container { 
  position: relative; border-radius: 24px; overflow: hidden; 
  background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05);
}
.admin-table { width: 100%; border-collapse: collapse; }

th { 
  text-align: left; padding: 20px 24px; font-size: 0.75rem; 
  font-weight: 800; text-transform: uppercase; letter-spacing: 1px;
  color: var(--text-secondary); background: rgba(255, 255, 255, 0.03);
}

.table-row { transition: background 0.2s; border-bottom: 1px solid rgba(255, 255, 255, 0.03); }
.table-row:hover { background: rgba(255, 215, 0, 0.03); }

td { padding: 18px 24px; vertical-align: middle; }

.mono-id { font-family: 'JetBrains Mono', monospace; font-weight: 700; opacity: 0.4; font-size: 0.85rem; }

.user-info-cell { display: flex; align-items: center; gap: 16px; }
.user-avatar { 
  width: 40px; height: 40px; border-radius: 12px; 
  background: linear-gradient(135deg, var(--primary-color) 0%, #FFA500 100%);
  color: #1C1B1F; display: flex; align-items: center; justify-content: center;
  font-weight: 900; font-size: 1.1rem;
}
.user-name { display: block; font-weight: 700; font-size: 1rem; }
.user-sub { font-size: 0.7rem; text-transform: uppercase; opacity: 0.5; font-weight: 800; letter-spacing: 0.5px; }

.email-cell { color: var(--text-secondary); font-weight: 500; }

/* Role Badges */
.badge-role {
  padding: 6px 12px; border-radius: 10px; font-size: 0.7rem; 
  font-weight: 800; text-transform: uppercase; display: inline-block;
}
.badge-role.admin { background: rgba(255, 77, 79, 0.1); color: #ff4d4f; border: 1px solid rgba(255, 77, 79, 0.2); }
.badge-role.student { background: rgba(255, 215, 0, 0.1); color: var(--primary-color); border: 1px solid rgba(255, 215, 0, 0.2); }
.badge-role.teacher { background: rgba(64, 169, 255, 0.1); color: #40a9ff; border: 1px solid rgba(64, 169, 255, 0.2); }

/* Status Indicators */
.status-wrapper { display: flex; align-items: center; gap: 8px; font-weight: 700; font-size: 0.85rem; color: #ff4d4f; }
.status-wrapper.is-active { color: #52c41a; }
.status-dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
.status-wrapper.is-active .status-dot { box-shadow: 0 0 10px #52c41a; }

/* Action Buttons */
.actions-group { display: flex; gap: 8px; }
.action-btn {
  width: 38px; height: 38px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);
  background: rgba(255,255,255,0.03); color: var(--text-secondary);
  cursor: pointer; transition: all 0.2s; display: flex; align-items: center; justify-content: center;
}
.action-btn:hover { border-color: var(--primary-color); color: var(--primary-color); background: rgba(255, 215, 0, 0.05); }
.action-btn.edit:hover { border-color: #40a9ff; color: #40a9ff; background: rgba(64, 169, 255, 0.05); }

.justify-end { justify-content: flex-end; }
.text-right { text-align: right; }

.loading-overlay { position: absolute; inset: 0; background: rgba(0,0,0,0.4); backdrop-filter: blur(10px); display: flex; align-items: center; justify-content: center; z-index: 100; }
.spinner { width: 40px; height: 40px; border: 4px solid rgba(255,215,0,0.1); border-top-color: var(--primary-color); border-radius: 50%; animation: spin 1s linear infinite; }
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Form & Inputs */
.edit-form { display: flex; flex-direction: column; gap: 24px; padding: 10px 0; }
.select-group { display: flex; flex-direction: column; gap: 10px; }
.styled-label { font-size: 0.75rem; font-weight: 800; text-transform: uppercase; opacity: 0.6; letter-spacing: 1px; }
.styled-select { 
  width: 100%; padding: 16px; border-radius: 16px; 
  background: rgba(255,255,255,0.03); color: white; border: 1px solid rgba(255,255,255,0.1);
  font-size: 1rem; outline: none; cursor: pointer; appearance: none;
}
.styled-select:focus { border-color: var(--primary-color); background: rgba(255,255,255,0.05); }

.animate-in { animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1); }
@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>
