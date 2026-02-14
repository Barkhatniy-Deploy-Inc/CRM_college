<template>
  <div class="settings-panel glass-panel">
    <button @click="settings.toggleTheme" class="icon-btn" :title="settings.theme === 'light' ? 'Темная тема' : 'Светлая тема'">
      {{ settings.theme === 'light' ? '🌙' : '☀️' }}
    </button>
    <button @click="settings.toggleGlass" class="icon-btn" :title="settings.glassEnabled ? 'Выключить стекло' : 'Включить стекло'">
      {{ settings.glassEnabled ? '💎' : '⏹️' }}
    </button>
  </div>
</template>

<script setup>
import { useSettingsStore } from '../../store/settings'

const settings = useSettingsStore()
</script>

<style scoped>
.settings-panel {
  position: fixed;
  top: 20px;
  right: 20px;
  display: flex;
  gap: 8px;
  padding: 6px;
  border-radius: 16px;
  z-index: 9999; /* Максимальный приоритет */
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.icon-btn {
  background: rgba(0, 0, 0, 0.05);
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  transition: all 0.2s ease;
}

.icon-btn:hover {
  background-color: rgba(0,0,0,0.1);
  transform: scale(1.05);
}

.icon-btn:active {
  transform: scale(0.95);
}

/* Стили для темной темы */
:global(.dark-theme) .icon-btn {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}

:global(.dark-theme) .icon-btn:hover {
  background-color: rgba(255, 255, 255, 0.2);
}
</style>
