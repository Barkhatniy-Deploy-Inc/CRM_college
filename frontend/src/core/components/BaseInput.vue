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
  width: 100%;
}

.styled-label {
  font-family: 'Inter', sans-serif;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 10px;
  margin-left: 4px;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  opacity: 0.9;
}

.input-wrapper {
  position: relative;
  width: 100%;
}

.styled-input {
  width: 100%;
  padding: 14px 20px;
  font-family: inherit;
  font-size: 1rem;
  color: var(--text-primary);
  background-color: var(--input-bg);
  border: none;
  border-radius: 14px;
  
  /* Более яркая базовая тень */
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  outline: none;
  box-sizing: border-box;
}

.styled-input::placeholder {
  color: var(--text-secondary);
  opacity: 0.6;
}

.styled-input:hover {
  background-color: var(--card-bg);
  /* Насыщенная желтая тень */
  box-shadow: 0 8px 20px rgba(255, 215, 0, 0.3);
}

.styled-input:focus {
  background-color: var(--card-bg);
  /* Очень яркая и широкая тень при фокусе */
  box-shadow: 0 10px 30px rgba(255, 215, 0, 0.45);
  transform: translateY(-1px);
}

/* Темная тема - более агрессивные тени для контраста */
:global(html[data-theme="dark"]) .styled-input {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}

:global(html[data-theme="dark"]) .styled-input:hover {
  box-shadow: 0 8px 25px rgba(255, 215, 0, 0.25);
}

:global(html[data-theme="dark"]) .styled-input:focus {
  box-shadow: 0 12px 35px rgba(255, 215, 0, 0.35);
}
</style>
