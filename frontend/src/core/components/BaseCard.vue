<template>
  <div class="glass-panel md-card animate-in">
    <slot></slot>
  </div>
</template>

<style scoped>
.md-card {
  padding: 24px;
  border-radius: 24px;
  box-sizing: border-box;
}

.animate-in {
  animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
