<template>
  <div class="admin-container">
    <header class="admin-header animate-in">
      <h1>Панель управления</h1>
      <p class="subtitle">Управление учебным процессом, пользователями и мониторинг</p>
    </header>

    <div class="admin-grid">
      <!-- Управление пользователями -->
      <BaseCard class="admin-card">
        <div class="card-icon"><AppIcon name="users" size="32" /></div>
        <h3>Пользователи</h3>
        <p>Управление учетными записями, ролями и активностью</p>
        <router-link to="/admin/users" class="full-width">
          <BaseButton variant="outline" class="action-btn">Управлять</BaseButton>
        </router-link>
      </BaseCard>

      <!-- Управление группами -->
      <BaseCard class="admin-card">
        <div class="card-icon"><AppIcon name="dashboard" size="32" /></div>
        <h3>Группы</h3>
        <p>Создание и редактирование учебных групп и потоков</p>
        <router-link to="/admin/groups" class="full-width">
          <BaseButton variant="outline" class="action-btn">Управлять</BaseButton>
        </router-link>
      </BaseCard>

      <!-- Управление аудиториями -->
      <BaseCard class="admin-card">
        <div class="card-icon"><AppIcon name="location" size="32" /></div>
        <h3>Аудитории</h3>
        <p>Управление учебными кабинетами и их вместимостью</p>
        <router-link to="/admin/auditoriums" class="full-width">
          <BaseButton variant="outline" class="action-btn">Управлять</BaseButton>
        </router-link>
      </BaseCard>

      <!-- Системные логи -->
      <BaseCard class="admin-card">
        <div class="card-icon"><AppIcon name="activity" size="32" /></div>
        <h3>Системные логи</h3>
        <p>Просмотр истории действий и мониторинг событий</p>
        <router-link to="/admin/logs" class="full-width">
          <BaseButton variant="outline" class="action-btn">Просмотреть</BaseButton>
        </router-link>
      </BaseCard>
    </div>
  </div>
</template>

<script setup>
import BaseCard from '../../../core/components/BaseCard.vue'
import BaseButton from '../../../core/components/BaseButton.vue'
import AppIcon from '../../../core/components/AppIcon.vue'
</script>

<style scoped>
.admin-container {
  max-width: 1200px;
  margin: 0 auto;
}
.admin-header {
  margin-bottom: 40px;
}
h1 {
  font-size: 2rem;
  font-weight: 800;
  margin: 0;
}
.subtitle {
  color: var(--text-secondary);
  margin-top: 8px;
}
.admin-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}
.admin-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 32px;
  transition: transform 0.3s ease;
}
.admin-card:hover {
  transform: translateY(-5px);
}
.card-icon {
  width: 64px;
  height: 64px;
  border-radius: 20px;
  background: rgba(255, 215, 0, 0.1);
  color: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}
h3 {
  margin: 0 0 12px 0;
  font-size: 1.25rem;
}
p {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 24px;
  line-height: 1.5;
  height: 3em;
  display: flex;
  align-items: center;
  justify-content: center;
}
.full-width {
  width: 100%;
  text-decoration: none;
}
.action-btn {
  width: 100%;
}
</style>
