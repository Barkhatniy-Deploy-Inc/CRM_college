<template>
  <div class="glass-panel md-card animate-in">
    <slot></slot>
  </div>
</template>

<style scoped>
.md-card {
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
  transition: box-shadow 0.3s ease;
}

.animate-in {
  animation: slideUp 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.md-card:hover {
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}
</style>
