<template>
  <button class="md-button" :class="[variant]">
    <slot></slot>
  </button>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'primary'
  }
})
</script>

<style scoped>
.md-button {
  padding: 10px 24px;
  border-radius: 20px;
  border: none;
  cursor: pointer;
  font-weight: 500;
  transition: opacity 0.2s;
}
.primary {
  background-color: var(--md-sys-color-primary);
  color: var(--md-sys-color-on-primary);
}
</style>
