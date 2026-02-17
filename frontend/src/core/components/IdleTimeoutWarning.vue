<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="show" class="idle-overlay">
        <div class="idle-modal glass-panel animate-in">
          <div class="icon-warning">
            <AppIcon name="clock" size="48" />
          </div>
          <h2>Сессия истекает</h2>
          <p>Вы долго не проявляли активность. В целях безопасности система скоро выполнит автоматический выход.</p>
          
          <div class="actions">
            <BaseButton @click="reloadPage" variant="primary" size="lg">
              <AppIcon name="activity" size="18" class="btn-icon" />
              Продолжить работу
            </BaseButton>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import AppIcon from './AppIcon.vue'
import BaseButton from './BaseButton.vue'

defineProps({
  show: Boolean
})

const reloadPage = () => {
  window.location.reload()
}
</script>

<style scoped>
.idle-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 99999; /* Поверх всего */
}

.idle-modal {
  max-width: 450px;
  padding: 40px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  border-color: rgba(255, 215, 0, 0.2);
}

.icon-warning {
  color: var(--primary-color);
  background: rgba(255, 215, 0, 0.1);
  padding: 20px;
  border-radius: 50%;
  margin-bottom: 10px;
}

h2 { margin: 0; font-size: 1.8rem; font-weight: 800; }
p { color: var(--text-secondary); line-height: 1.6; font-size: 1.1rem; }

.actions { margin-top: 10px; width: 100%; }
.btn-icon { margin-right: 8px; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.5s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
