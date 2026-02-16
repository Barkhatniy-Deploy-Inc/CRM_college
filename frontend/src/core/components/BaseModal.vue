<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="show" class="modal-backdrop" @click.self="$emit('close')">
        <div class="modal-container glass-panel animate-modal">
          <header class="modal-header">
            <h3>{{ title }}</h3>
            <button class="close-btn" @click="$emit('close')">
              <AppIcon name="chevron-right" style="transform: rotate(45deg) scale(1.5)" />
            </button>
          </header>
          
          <div class="modal-body">
            <slot></slot>
          </div>

          <footer class="modal-footer">
            <slot name="footer">
              <BaseButton variant="outline" @click="$emit('close')">Отмена</BaseButton>
              <BaseButton :loading="loading" @click="$emit('confirm')">{{ confirmText }}</BaseButton>
            </slot>
          </footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import BaseButton from './BaseButton.vue'
import AppIcon from './AppIcon.vue'

defineProps({
  show: Boolean,
  title: String,
  confirmText: { type: String, default: 'Сохранить' },
  loading: Boolean
})

defineEmits(['close', 'confirm'])
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}

.modal-container {
  width: 100%;
  max-width: 500px;
  background: var(--card-bg);
  border-radius: 28px;
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  box-shadow: 0 20px 50px rgba(0,0,0,0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 800;
}

.close-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}

.modal-body {
  font-size: 1rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* Animations */
.modal-enter-active, .modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from, .modal-leave-to {
  opacity: 0;
}

.animate-modal {
  animation: slideIn 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideIn {
  from { transform: scale(0.9) translateY(20px); opacity: 0; }
  to { transform: scale(1) translateY(0); opacity: 1; }
}
</style>
