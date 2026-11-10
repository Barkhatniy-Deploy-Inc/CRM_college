<template>
  <div :class="{ 'glass-disabled': !settingsStore.glassEnabled }">
    <!-- Для неавторизованных -->
    <router-view v-if="!authStore.isAuthenticated" />

    <!-- Для авторизованных (Dashboard и т.д.) -->
    <DefaultLayout v-else>
      <router-view />
    </DefaultLayout>

    <!-- Уведомление о неактивности -->
    <IdleTimeoutWarning :show="isIdle" />
    <div v-if="!isOnline" class="offline-banner" role="status" aria-live="polite">
      Нет подключения к сети. Данные могут быть устаревшими.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useSettingsStore } from './store/settings'
import { useAuthStore } from './store/auth'
import DefaultLayout from './core/layouts/DefaultLayout.vue'
import IdleTimeoutWarning from './core/components/IdleTimeoutWarning.vue'
import { usePwa } from './composables/usePwa'

const settingsStore = useSettingsStore()
const authStore = useAuthStore()
const { isOnline } = usePwa()

// Логика неактивности
const isIdle = ref(false)
let idleTimer = null
let logoutTimer = null

const IDLE_THRESHOLD = 15 * 60 * 1000 // 15 минут до предупреждения
const LOGOUT_THRESHOLD = 20 * 60 * 1000 // 20 минут до автовыхода

const resetTimers = () => {
  if (!authStore.isAuthenticated) {
    isIdle.value = false
    return
  }

  isIdle.value = false
  clearTimeout(idleTimer)
  clearTimeout(logoutTimer)

  idleTimer = setTimeout(() => {
    isIdle.value = true
  }, IDLE_THRESHOLD)

  logoutTimer = setTimeout(() => {
    authStore.logout()
  }, LOGOUT_THRESHOLD)
}

onMounted(() => {
  settingsStore.initTheme()

  // Отслеживаем активность
  const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart']
  events.forEach(event => {
    window.addEventListener(event, resetTimers)
  })

  if (authStore.isAuthenticated) {
    resetTimers()
  }
})

onUnmounted(() => {
  const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart']
  events.forEach(event => {
    window.removeEventListener(event, resetTimers)
  })
  clearTimeout(idleTimer)
  clearTimeout(logoutTimer)
})
</script>

<style>
/* Глобальные переходы между страницами */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.offline-banner {
  position: fixed;
  z-index: 20000;
  top: max(12px, env(safe-area-inset-top));
  left: 50%;
  width: max-content;
  max-width: calc(100vw - 32px);
  padding: 12px 16px;
  transform: translateX(-50%);
  border: 1px solid rgba(220, 120, 20, 0.32);
  border-radius: 14px;
  background: var(--card-bg);
  color: var(--text-primary);
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.18);
  font-size: 0.85rem;
  text-align: center;
}
</style>
