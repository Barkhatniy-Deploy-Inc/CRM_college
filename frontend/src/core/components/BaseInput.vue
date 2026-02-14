<template>
  <div class="input-group">
    <label v-if="label" class="styled-label">{{ label }}</label>
    <div class="input-wrapper">
      <input 
        :type="type" 
        :value="modelValue" 
        @input="$emit('update:modelValue', $event.target.value)"
        class="styled-input"
        :placeholder="placeholder"
      />
      <div class="focus-indicator"></div>
    </div>
  </div>
</template>

<script setup>
defineProps(['label', 'type', 'modelValue', 'placeholder'])
defineEmits(['update:modelValue'])
</script>

<style scoped>
.input-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 24px;
  text-align: left;
}

.styled-label {
  font-family: 'Inter', sans-serif;
  font-size: 0.85rem;
  font-weight: 600;
  color: #4A4A4A;
  margin-bottom: 8px;
  margin-left: 4px;
  letter-spacing: 0.3px;
  text-transform: uppercase;
  opacity: 0.8;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.styled-input {
  width: 100%;
  padding: 14px 18px;
  font-family: 'Inter', sans-serif;
  font-size: 1rem;
  font-weight: 400;
  color: #1C1B1F;
  background: #FFFFFF;
  border: 1.5px solid #F0F0F0;
  border-radius: 14px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  outline: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
}

.styled-input::placeholder {
  color: #A0A0A0;
  font-weight: 400;
  opacity: 0.7;
}

.styled-input:hover {
  border-color: #D0D0D0;
  background: #FAFAFA;
}

.styled-input:focus {
  border-color: transparent;
  background: #FFFFFF;
  box-shadow: 0 8px 20px rgba(255, 215, 0, 0.15);
}

.focus-indicator {
  position: absolute;
  inset: -1.5px;
  border-radius: 14px;
  border: 2px solid var(--md-sys-color-primary);
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease;
  z-index: 1;
}

.styled-input:focus + .focus-indicator {
  opacity: 1;
}
</style>
