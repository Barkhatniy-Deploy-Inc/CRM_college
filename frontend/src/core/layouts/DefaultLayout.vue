<template>
  <div class="app-layout">
    <!-- Sidebar -->
    <aside class="sidebar glass-panel" :class="{ 'collapsed': isCollapsed }">
      <div class="sidebar-header">
        <img src="/sielom/logo-sielom.svg" alt="Logo" class="logo" />
        <span v-if="!isCollapsed" class="app-name">CRM College</span>
      </div>

      <nav class="sidebar-nav">
        <template v-for="item in filteredMenuItems" :key="item.path">
          <router-link :to="item.path" class="nav-item" active-class="active">
            <AppIcon :name="item.icon" class="nav-icon" />
            <span v-if="!isCollapsed" class="label">{{ item.label }}</span>
          </router-link>
        </template>
      </nav>

      <div class="sidebar-footer">
        <button @click="handleLogout" class="nav-item logout-btn">
          <AppIcon name="logout" class="nav-icon" />
          <span v-if="!isCollapsed" class="label">Выйти</span>
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="main-wrapper">
      <header class="top-bar glass-panel">
        <button @click="isCollapsed = !isCollapsed" class="toggle-btn">
          <AppIcon :name="isCollapsed ? 'chevron-right' : 'chevron-left'" />
        </button>
        <div class="user-profile">
          <div class="user-info">
            <span class="name">{{ authStore.user?.full_name }}</span>
            <span class="role badge">{{ authStore.user?.role }}</span>
          </div>
        </div>
      </header>
      
      <div class="content-area">
        <slot></slot>
      </div>
    </main>

    <!-- Глобальные настройки -->
    <SettingsToggle />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '../../store/auth'
import SettingsToggle from '../components/SettingsToggle.vue'
import AppIcon from '../components/AppIcon.vue'

const authStore = useAuthStore()
const isCollapsed = ref(false)

const allMenuItems = [
  { path: '/dashboard', label: 'Главная', icon: 'dashboard', roles: ['admin', 'student', 'teacher'] },
  { path: '/schedule', label: 'Расписание', icon: 'schedule', roles: ['admin', 'student', 'teacher'] },
  { path: '/admin', label: 'Администрирование', icon: 'shield', roles: ['admin'] },
]

const filteredMenuItems = computed(() => {
  const role = authStore.user?.role?.toLowerCase() || 'guest'
  return allMenuItems.filter(item => item.roles.includes(role))
})

const handleLogout = () => {
  authStore.logout()
}
</script>

<style scoped>
.app-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  background: var(--bg-color);
}

.sidebar {
  width: 260px;
  height: calc(100vh - 24px);
  margin: 12px 0 12px 12px;
  display: flex;
  flex-direction: column;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 20px;
  z-index: 100;
  overflow: hidden;
  box-sizing: border-box;
}

.sidebar.collapsed {
  width: 84px;
}

.sidebar-header {
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  min-height: 80px;
}

.logo {
  height: 36px;
  width: 36px;
  min-width: 36px;
}

.app-name {
  font-weight: 800;
  font-size: 1.1rem;
  white-space: nowrap;
  color: var(--text-primary);
  letter-spacing: -0.5px;
}

.sidebar-nav {
  flex: 1;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-radius: 14px;
  text-decoration: none;
  color: var(--text-secondary);
  transition: all 0.2s ease;
  background: transparent;
  border: none;
  width: 100%;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.95rem;
  font-weight: 600;
  box-sizing: border-box;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
}

.nav-item.active {
  background: var(--primary-color);
  color: #1C1B1F;
}

.nav-icon {
  min-width: 24px;
  margin-right: 16px;
  transition: margin 0.4s;
}

.sidebar.collapsed .nav-icon {
  margin-right: 0;
}

.sidebar.collapsed .nav-item {
  justify-content: center;
  padding: 12px;
}

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.logout-btn {
  color: #ff4d4f;
}

.logout-btn:hover {
  background: rgba(255, 77, 79, 0.1);
}

.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0 12px;
}

.top-bar {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  margin: 12px 0;
  border-radius: 16px;
}

.toggle-btn {
  background: rgba(255, 255, 255, 0.05);
  border: none;
  color: var(--text-primary);
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-radius: 10px;
  transition: all 0.2s;
}

.toggle-btn:hover {
  background: var(--primary-color);
  color: #1C1B1F;
}

.user-profile {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.name {
  font-weight: 700;
  font-size: 0.95rem;
}

.role.badge {
  background: rgba(255, 215, 0, 0.1);
  color: var(--primary-color);
  padding: 4px 10px;
  border-radius: 8px;
  font-size: 0.7rem;
  font-weight: 800;
  text-transform: uppercase;
  border: 1px solid rgba(255, 215, 0, 0.2);
}

.content-area {
  flex: 1;
  overflow-y: auto;
  padding: 12px 4px 24px 4px;
}

.content-area::-webkit-scrollbar {
  width: 6px;
}
.content-area::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}
</style>
