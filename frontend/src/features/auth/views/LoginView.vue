<template>
  <div class="auth-container">
    <BaseCard class="login-card">
      <div class="logo-container">
        <img src="/sielom/logo-sielom.svg" alt="Логотип СИЭУиП" class="main-logo" />
      </div>
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
          Войти
        </BaseButton>
      </form>

      <div class="footer-logo">
        <img src="/sielom/ten-years-logo.svg" alt="10 лет" class="anniversary-logo" />
      </div>
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
  if (!email.value || !password.value) {
    alert('Пожалуйста, заполните все поля')
    return
  }
  const success = await authStore.login(email.value, password.value)
  if (success) {
    window.location.href = '/'
  }
}
</script>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 420px;
  text-align: center;
  border-top: 4px solid #FFD700 !important;
}

.logo-container {
  margin-bottom: 20px;
}

.main-logo {
  height: 80px;
  width: auto;
}

.auth-title {
  margin: 0 0 8px 0;
  font-weight: 700;
  color: #1c1b1f;
}

.auth-subtitle {
  margin: 0 0 32px 0;
  opacity: 0.6;
  font-size: 0.85rem;
  color: #1c1b1f;
  line-height: 1.4;
}

.full-width {
  width: 100%;
  margin-top: 24px;
}

.error-message {
  color: #b71c1c;
  background: rgba(183, 28, 28, 0.08);
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 0.85rem;
}

.footer-logo {
  margin-top: 30px;
  opacity: 0.5;
}

.anniversary-logo {
  height: 40px;
}
</style>
