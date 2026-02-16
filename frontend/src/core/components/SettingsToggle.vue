<template>
  <div class="global-settings">
    <div class="settings-fab" @click="isExpanded = !isExpanded" :class="{ 'active': isExpanded }">
      <div class="options-panel glass-panel" v-if="isExpanded">
        <button @click.stop="settingsStore.toggleTheme" class="option-btn">
          <AppIcon :name="settingsStore.theme === 'light' ? 'moon' : 'sun'" size="18" class="icon" />
          <span class="label">Тема</span>
        </button>
        <button @click.stop="settingsStore.toggleGlass" class="option-btn">
          <AppIcon name="sparkles" size="18" class="icon" />
          <span class="label">Эффекты</span>
        </button>
      </div>
      <div class="fab-trigger">
        <AppIcon name="settings" size="24" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useSettingsStore } from '../../store/settings'
import AppIcon from './AppIcon.vue'

const settingsStore = useSettingsStore()
const isExpanded = ref(false)
</script>

<style scoped>
.global-settings {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 9999;
}

.settings-fab {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.fab-trigger {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  background: var(--primary-color);
  color: #1C1B1F;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(255, 215, 0, 0.3);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.fab-trigger:hover {
  transform: scale(1.1) rotate(30deg);
}

.options-panel {
  position: absolute;
  bottom: calc(100% + 12px);
  right: 0;
  padding: 8px;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 140px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.option-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  border-radius: 10px;
  background: transparent;
  border: none;
  color: var(--text-primary);
  cursor: pointer;
  transition: background 0.2s;
  font-family: inherit;
  font-weight: 600;
  font-size: 0.9rem;
}

.option-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.icon {
  opacity: 0.8;
}
</style>
