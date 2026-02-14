<template>
  <button class="md-button" :class="[variant, { 'is-loading': loading }]" :disabled="loading">
    <span v-if="loading" class="spinner"></span>
    <span :class="{ 'text-transparent': loading }">
      <slot></slot>
    </span>
  </button>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'primary'
  },
  loading: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.md-button {
  position: relative;
  padding: 12px 28px;
  border-radius: 12px;
  border: 2px solid transparent;
  cursor: pointer;
  font-weight: 600;
  font-family: inherit;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  min-height: 48px;
}

.primary {
  background-color: var(--primary-color);
  color: #1C1B1F;
  box-shadow: 0 4px 12px rgba(255, 215, 0, 0.2);
}

.primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4);
}

.outline {
  background-color: transparent;
  border-color: #ddd;
  color: var(--text-primary);
}

.md-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  position: absolute;
  width: 20px;
  height: 20px;
  border: 3px solid rgba(0,0,0,0.1);
  border-top-color: #1C1B1F;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.text-transparent {
  color: transparent;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
