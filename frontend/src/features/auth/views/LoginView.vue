<template>
  <div class="auth-container glass-enabled">
    <BaseCard class="login-card">
      <div class="logo-placeholder">🎓</div>
      <h2 class="auth-title">Вход в систему</h2>
      <p class="auth-subtitle">Сургутский институт экономики, управления и права</p>
      
      <form @submit.prevent="handleLogin">
        <BaseInput 
          label="Электронная почта" 
          type="email" 
          v-model="email" 
          placeholder="example@sielom.ru"
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

        <BaseButton type="submit" :loading="authStore.loading" class="full-width">
          {{ authStore.loading ? 'Загрузка...' : 'Войти' }}
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
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.login-card {
  width: 100%;
  max-width: 420px;
  text-align: center;
  border-top: 4px solid var(--md-sys-color-primary) !important;
}

.logo-placeholder {
  font-size: 3rem;
  margin-bottom: 16px;
}

.auth-title {
  margin: 0 0 8px 0;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.auth-subtitle {
  margin: 0 0 32px 0;
  opacity: 0.6;
  font-size: 0.85rem;
  line-height: 1.4;
}

.full-width {
  width: 100%;
  margin-top: 24px;
  font-weight: 600;
  height: 48px;
}

.error-message {
  color: #b71c1c;
  background: rgba(183, 28, 28, 0.08);
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 0.85rem;
  border: 1px solid rgba(183, 28, 28, 0.2);
}
</style>

