<template>
  <div id="app-wrapper">
    <!-- Глобальные настройки темы и стиля -->
    <SettingsToggle />
    
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useSettingsStore } from './store/settings'
import SettingsToggle from './core/components/SettingsToggle.vue'

const settings = useSettingsStore()

onMounted(() => {
  settings.applySettings()
})
</script>

<style>
#app-wrapper {
  height: 100%;
  width: 100%;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
