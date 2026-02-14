<template>
  <div class="md-input-container">
    <label v-if="label" class="input-label">{{ label }}</label>
    <input 
      :type="type" 
      :value="modelValue" 
      @input="$emit('update:modelValue', $event.target.value)"
      class="md-input"
      :placeholder="placeholder"
    />
  </div>
</template>

<script setup>
defineProps(['label', 'type', 'modelValue', 'placeholder'])
defineEmits(['update:modelValue'])
</script>

<style scoped>
.md-input-container {
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
  text-align: left;
}

.input-label {
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: 6px;
  color: #555;
  transition: color 0.2s ease;
}

.md-input {
  padding: 12px 16px;
  border-radius: 10px;
  border: 2px solid #eee;
  background: white;
  font-size: 1rem;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  outline: none;
}

.md-input:focus {
  border-color: var(--md-sys-color-primary);
  box-shadow: 0 0 0 4px rgba(255, 215, 0, 0.15);
}

.md-input-container:focus-within .input-label {
  color: #000;
}
</style>
