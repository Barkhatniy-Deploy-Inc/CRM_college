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
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useSettingsStore } from './store/settings'
import { useAuthStore } from './store/auth'
import DefaultLayout from './core/layouts/DefaultLayout.vue'
import IdleTimeoutWarning from './core/components/IdleTimeoutWarning.vue'

const settingsStore = useSettingsStore()
const authStore = useAuthStore()

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
</style>
