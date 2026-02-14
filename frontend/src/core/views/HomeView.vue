<template>
  <div class="page-container">
    
    <!-- Карточка - теперь это единственный центр -->
    <BaseCard class="login-card">
      
      <!-- Логотип вынесен из потока, чтобы не смещать центр карточки -->
      <div class="floating-logo">
        <img src="/sielom/logo-sielom.svg" alt="Логотип СИЭУиП" class="main-logo" />
      </div>
      
      <h2 class="auth-title">Вход в систему</h2>
      <p class="auth-subtitle">Сургутский институт экономики, управления и права</p>
      
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
.page-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  align-items: center; /* Карточка строго по центру вертикали */
  justify-content: center; /* Карточка строго по центру горизонтали */
  background: #f8f9fa;
  overflow: hidden;
  box-sizing: border-box;
}

.login-card {
  position: relative; /* Для позиционирования логотипа */
  width: 100%;
  max-width: 440px;
  text-align: center;
  background: white;
  padding: 40px 40px 32px 40px; 
  border-radius: 24px;
  box-shadow: 0 12px 40px rgba(0,0,0,0.06);
  border-top: 6px solid #FFD700 !important;
}

.floating-logo {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  bottom: calc(100% + 40px); /* Ровно 40px над верхним краем карточки */
  width: auto;
  display: flex;
  justify-content: center;
}

.main-logo {
  height: 90px;
  width: auto;
  display: block;
}

.auth-title {
  margin: 0;
  font-size: 1.7rem;
  font-weight: 800;
  color: #1a1a1a;
  letter-spacing: -0.5px;
}

.auth-subtitle {
  margin: 12px 0 32px 0;
  color: #666;
  font-size: 0.85rem;
  line-height: 1.4;
}

.form-section {
  width: 100%;
}

.full-width {
  width: 100%;
  margin-top: 8px;
}

.footer-logo {
  margin-top: 32px;
  padding-top: 20px;
  border-top: 1px solid #f5f5f5;
  opacity: 0.4;
}

.anniversary-logo {
  height: 40px;
}
</style>
