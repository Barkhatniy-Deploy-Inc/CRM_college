<template>
  <div class="md-input-container">
    <label v-if="label">{{ label }}</label>
    <input 
      :type="type" 
      :value="modelValue" 
      @input="$emit('update:modelValue', $event.target.value)"
      class="md-input"
    />
  </div>
</template>

<script setup>
defineProps(['label', 'type', 'modelValue'])
defineEmits(['update:modelValue'])
</script>

<style scoped>
.md-input-container {
  display: flex;
  flex-direction: column;
  margin-bottom: 16px;
}
.md-input {
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #ddd;
  background: white;
}
</style>
