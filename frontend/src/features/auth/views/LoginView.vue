<template>
  <div class="auth-container glass-enabled">
    <BaseCard class="login-card">
      <h2 class="auth-title">Вход в CRM</h2>
      <p class="auth-subtitle">Информационная система колледжа</p>
      
      <form @submit.prevent="handleLogin">
        <BaseInput 
          label="Email" 
          type="email" 
          v-model="email" 
          placeholder="example@college.ru"
        />
        <BaseInput 
          label="Пароль" 
          type="password" 
          v-model="password" 
          placeholder="••••••••"
        />
        
        <div v-if="authStore.error" class="error-message">
          {{ authStore.error }}
        </div>

        <BaseButton type="submit" :disabled="authStore.loading" class="full-width">
          {{ authStore.loading ? 'Вход...' : 'Войти' }}
        </BaseButton>
      </form>
    </BaseCard>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../../../store/auth'
import BaseCard from '../../../core/components/BaseCard.vue'
import BaseInput from '../../../core/components/BaseInput.vue'
import BaseButton from '../../../core/components/BaseButton.vue'

const authStore = useAuthStore()
const email = ref('')
const password = ref('')

const handleLogin = async () => {
  if (!email.value || !password.value) return
  await authStore.login(email.value, password.value)
}
</script>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #004A99 0%, #002d66 100%);
}

.login-card {
  width: 100%;
  max-width: 400px;
  text-align: center;
}

.auth-title {
  margin: 0 0 8px 0;
  color: var(--md-sys-color-on-surface);
}

.auth-subtitle {
  margin: 0 0 24px 0;
  opacity: 0.7;
  font-size: 0.9rem;
}

.full-width {
  width: 100%;
  margin-top: 16px;
}

.error-message {
  color: #d32f2f;
  background: rgba(211, 47, 47, 0.1);
  padding: 8px;
  border-radius: 4px;
  margin-bottom: 16px;
  font-size: 0.85rem;
}
</style>
