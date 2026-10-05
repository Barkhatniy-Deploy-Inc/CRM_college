<template>
  <div class="techcard-page">
    <header class="page-header animate-in">
      <div class="title-section">
        <h1>Технологические карты</h1>
        <p class="subtitle">Управление планами занятий и экспорт в Word</p>
      </div>
      <div class="actions">
        <BaseButton @click="createNewCard">
          <AppIcon name="sparkles" size="18" class="btn-icon" />
          Создать новую карту
        </BaseButton>
      </div>
    </header>

    <BaseCard class="table-card glass-panel">
      <div v-if="techcardStore.isLoading" class="loading-overlay">
        <div class="spinner"></div>
      </div>

      <table class="admin-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Тема занятия</th>
            <th>Группа</th>
            <th>Преподаватель</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="card in techcardStore.techcards" :key="card.id">
            <td class="mono">#{{ String(card.id).padStart(4, '0') }}</td>
            <td class="bold">{{ card.tema || 'Без темы' }}</td>
            <td>{{ card.group_id || '—' }}</td>
            <td>
              <span class="teacher-name">{{ card.teacher_id || '—' }}</span>
            </td>
            <td class="actions-cell">
              <button
                class="icon-btn edit"
                @click="$router.push(`/techcards/${card.id}`)"
                title="Редактировать"
              >
                <AppIcon name="settings" size="16" />
              </button>
              <button
                class="icon-btn download"
                @click="techcardStore.downloadCard(card.id)"
                title="Скачать .docx"
              >
                <AppIcon name="schedule" size="16" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div
        v-if="techcardStore.techcards.length === 0 && !techcardStore.isLoading"
        class="empty-state"
      >
        <AppIcon name="calendar-off" size="48" class="empty-icon" />
        <p>У вас пока нет созданных технологических карт</p>
        <BaseButton variant="outline" @click="createNewCard">Создать первую карту</BaseButton>
      </div>
    </BaseCard>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTechcardStore } from '../../../store/techcard'
import BaseCard from '../../../core/components/BaseCard.vue'
import BaseButton from '../../../core/components/BaseButton.vue'
import AppIcon from '../../../core/components/AppIcon.vue'

const techcardStore = useTechcardStore()
const router = useRouter()

const createNewCard = () => {
  router.push('/techcards/new')
}

onMounted(() => {
  techcardStore.fetchTechcards()
})
</script>

<style scoped>
.techcard-page {
  max-width: 1200px;
  margin: 0 auto;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}
h1 {
  font-size: 2rem;
  font-weight: 800;
  margin: 0;
}
.subtitle {
  color: var(--text-secondary);
  margin-top: 4px;
}

.table-card {
  padding: 0;
  overflow: hidden;
  position: relative;
  min-height: 300px;
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
  color: var(--text-primary);
}
.teacher-name {
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.actions-cell {
  display: flex;
  gap: 8px;
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
.icon-btn.download:hover {
  color: #52c41a;
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

.empty-state {
  text-align: center;
  padding: 64px;
  color: var(--text-secondary);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}
.empty-icon {
  opacity: 0.2;
}
</style>
