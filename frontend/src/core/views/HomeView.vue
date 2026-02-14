<template>
  <div class="home-container glass-enabled">
    <BaseCard class="welcome-card">
      <h1 class="title">Добро пожаловать в личный кабинет</h1>
      <p class="subtitle">Информационная система управления учебным процессом</p>
      
      <div class="user-info" v-if="authStore.user">
        <div class="info-row">
          <span class="label">Пользователь</span>
          <span class="value">{{ authStore.user.full_name }}</span>
        </div>
        <div class="info-row">
          <span class="label">Email</span>
          <span class="value">{{ authStore.user.email }}</span>
        </div>
        <div class="info-row">
          <span class="label">Роль</span>
          <span class="role-badge">{{ authStore.user.role }}</span>
        </div>
      </div>

      <div class="actions">
        <BaseButton @click="handleLogout" variant="outline">Выйти из системы</BaseButton>
      </div>
    </BaseCard>
  </div>
</template>

<script setup>
import { useAuthStore } from '../../store/auth'
import { useRouter } from 'vue-router'
import BaseCard from '../components/BaseCard.vue'
import BaseButton from '../components/BaseButton.vue'

const authStore = useAuthStore()
const router = useRouter()

const handleLogout = async () => {
  await authStore.logout()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.welcome-card {
  width: 100%;
  max-width: 550px;
  text-align: center;
  border-left: 6px solid var(--md-sys-color-primary) !important;
}

.title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 8px;
}

.subtitle {
  opacity: 0.5;
  font-size: 0.9rem;
  margin-bottom: 32px;
}

.user-info {
  text-align: left;
  background: white;
  padding: 24px;
  border-radius: 12px;
  margin-bottom: 32px;
  border: 1px solid #eee;
}

.info-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f5f5f5;
}

.info-row:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.label {
  color: #666;
  font-size: 0.85rem;
}

.value {
  font-weight: 600;
}

.role-badge {
  background: var(--md-sys-color-primary);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
}

.actions {
  display: flex;
  justify-content: center;
}
</style>

