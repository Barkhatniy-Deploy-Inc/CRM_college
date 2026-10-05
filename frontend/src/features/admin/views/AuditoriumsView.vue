<template>
  <div class="admin-page">
    <header class="page-header animate-in">
      <div class="title-section">
        <BaseButton variant="outline" @click="$router.push('/admin')" class="back-btn">
          <AppIcon name="chevron-left" size="18" />
        </BaseButton>
        <h1>Учебные аудитории</h1>
      </div>
      <div class="actions">
        <BaseButton @click="showAddModal = true">
          <AppIcon name="sparkles" size="18" class="btn-icon" />
          Добавить аудиторию
        </BaseButton>
      </div>
    </header>

    <BaseCard class="table-card glass-panel">
      <div v-if="scheduleStore.isLoading" class="loading-overlay">
        <div class="spinner"></div>
      </div>

      <table class="admin-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Название</th>
            <th>Вместимость</th>
            <th>Описание</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="aud in scheduleStore.auditoriums" :key="aud.id">
            <td class="mono">#{{ String(aud.id).padStart(3, '0') }}</td>
            <td class="bold">{{ aud.name }}</td>
            <td>{{ aud.capacity || '—' }} чел.</td>
            <td>{{ aud.description || '—' }}</td>
            <td>
              <button class="icon-btn" title="Редактировать">
                <AppIcon name="settings" size="16" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </BaseCard>

    <!-- Модалка добавления -->
    <BaseModal
      :show="showAddModal"
      title="Новая аудитория"
      @close="showAddModal = false"
      @confirm="handleAdd"
      :loading="isAdding"
    >
      <div class="edit-form">
        <BaseInput label="Номер или название" v-model="newAud.name" placeholder="например, 305" />
        <BaseInput label="Вместимость" type="number" v-model="newAud.capacity" />
        <BaseInput label="Описание" v-model="newAud.description" />
      </div>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useScheduleStore } from '../../../store/schedule'
import BaseCard from '../../../core/components/BaseCard.vue'
import BaseButton from '../../../core/components/BaseButton.vue'
import BaseInput from '../../../core/components/BaseInput.vue'
import BaseModal from '../../../core/components/BaseModal.vue'
import AppIcon from '../../../core/components/AppIcon.vue'
import api from '../../../core/utils/api'

const scheduleStore = useScheduleStore()
const showAddModal = ref(false)
const isAdding = ref(false)

const newAud = reactive({
  name: '',
  capacity: null,
  description: ''
})

const fetchData = () => scheduleStore.fetchAuditoriums()

const handleAdd = async () => {
  if (!newAud.name) return
  isAdding.value = true
  try {
    await api.post('/schedule/auditoriums', newAud)
    await fetchData()
    showAddModal.value = false
    Object.assign(newAud, { name: '', capacity: null, description: '' })
  } catch (e) {
    alert('Ошибка при создании')
  } finally {
    isAdding.value = false
  }
}

onMounted(fetchData)
</script>

<style scoped>
.admin-page {
  max-width: 1200px;
  margin: 0 auto;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}
.title-section {
  display: flex;
  align-items: center;
  gap: 16px;
}
h1 {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 800;
}
.table-card {
  padding: 0;
  overflow: hidden;
  position: relative;
  min-height: 200px;
}
.admin-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}
th {
  padding: 16px 24px;
  background: rgba(255, 255, 255, 0.03);
  font-size: 0.8rem;
  text-transform: uppercase;
  color: var(--text-secondary);
  font-weight: 700;
}
td {
  padding: 16px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  font-size: 0.95rem;
}
.mono {
  font-family: 'JetBrains Mono', monospace;
  opacity: 0.6;
}
.bold {
  font-weight: 700;
  color: var(--primary-color);
}
.icon-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.2s;
}
.icon-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--primary-color);
}
.edit-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}
.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(255, 215, 0, 0.1);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
