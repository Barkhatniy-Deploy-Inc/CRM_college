<template>
  <div :class="{ 'glass-disabled': !settingsStore.glassEnabled }">
    <!-- Для неавторизованных -->
    <router-view v-if="!authStore.isAuthenticated" />
    
    <!-- Для авторизованных (Dashboard и т.д.) -->
    <DefaultLayout v-else>
      <router-view />
    </DefaultLayout>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useSettingsStore } from './store/settings'
import { useAuthStore } from './store/auth'
import DefaultLayout from './core/layouts/DefaultLayout.vue'

const settingsStore = useSettingsStore()
const authStore = useAuthStore()

onMounted(() => {
  settingsStore.initTheme()
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
