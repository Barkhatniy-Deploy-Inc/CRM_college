<template>
  <div class="home-container">
    <BaseCard class="login-card">
      <div class="floating-logo">
        <img src="/sielom/logo-sielom.svg" alt="Логотип СИЭУиП" class="main-logo" />
      </div>
      
      <h2 class="auth-title">Вход в систему</h2>
      
      <div class="form-section">
        <BaseInput 
          label="Электронная почта" 
          v-model="email" 
          placeholder="example@sielom.ru"
        />
        <BaseInput 
          label="Пароль" 
          type="password" 
          v-model="password" 
          placeholder="••••••••"
        />
        
        <BaseButton class="full-width">
          Войти
        </BaseButton>
      </div>

      <div class="footer-logo">
        <img src="/sielom/ten-years-logo.svg" alt="10 лет" class="anniversary-logo" />
      </div>
    </BaseCard>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../../store/auth'
import BaseCard from '../components/BaseCard.vue'
import BaseInput from '../components/BaseInput.vue'
import BaseButton from '../components/BaseButton.vue'

const authStore = useAuthStore()
const email = ref('')
const password = ref('')
</script>

<style scoped>
.home-container {
  height: 100%;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-card {
  position: relative;
  width: 100%;
  max-width: 440px;
  text-align: center;
  padding: 40px 40px 24px 40px; 
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.12);
  border-top: 6px solid var(--primary-color) !important;
}

.floating-logo {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  bottom: calc(100% + 40px);
  width: auto;
}

.main-logo {
  height: 90px;
  width: auto;
}

.auth-title {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.5px;
}

.form-section {
  width: 100%;
  margin-top: 40px;
}

.full-width {
  width: 100%;
  margin-top: 8px;
}

.footer-logo {
  margin-top: 32px;
  padding-top: 20px;
  border-top: 1px solid var(--input-border);
  opacity: 0.7;
}

.anniversary-logo {
  height: 40px;
}
</style>
