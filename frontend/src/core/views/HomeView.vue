<template>
  <div class="home-container">
    <BaseCard class="login-card animate-in">
      <div class="floating-logo">
        <img src="/sielom/logo-sielom.svg" alt="Логотип СИЭУиП" class="main-logo" />
      </div>

      <h2 class="auth-title">Вход в систему</h2>
      <p class="auth-subtitle">Личный кабинет CRM College</p>

      <form @submit.prevent="handleLogin" class="form-section">
        <BaseInput
          label="Электронная почта"
          v-model="email"
          placeholder="example@sielom.ru"
          required
        />
        <BaseInput
          label="Пароль"
          type="password"
          v-model="password"
          placeholder="••••••••"
          required
        />

        <transition name="fade">
          <div v-if="authStore.error" class="error-message">
            {{ authStore.error }}
          </div>
        </transition>

        <BaseButton type="submit" class="full-width" :loading="authStore.isLoading">
          Войти
        </BaseButton>
      </form>

      <div class="footer-logo">
        <img src="/sielom/ten-years-logo.svg" alt="10 лет" class="anniversary-logo" />
      </div>
    </BaseCard>

    <!-- Переключатель настроек для страницы логина -->
    <SettingsToggle />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../store/auth'
import BaseCard from '../components/BaseCard.vue'
import BaseInput from '../components/BaseInput.vue'
import BaseButton from '../components/BaseButton.vue'
import SettingsToggle from '../components/SettingsToggle.vue'

const authStore = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')

const handleLogin = async () => {
  try {
    await authStore.login(email.value, password.value)
    router.push('/dashboard')
  } catch (e) {
    console.error('Login failed', e)
  }
}
</script>

<style scoped>
.home-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-color);
  overflow: hidden;
}

.login-card {
  position: relative;
  width: 100%;
  max-width: 400px;
  text-align: center;
  padding: 40px;
  border-radius: 28px;
}

.floating-logo {
  margin-bottom: 24px;
}

.main-logo {
  height: 70px;
  width: auto;
}

.auth-title {
  margin: 0;
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.5px;
}

.auth-subtitle {
  margin-top: 4px;
  font-size: 0.9rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.form-section {
  width: 100%;
  margin-top: 32px;
}

.full-width {
  width: 100%;
  margin-top: 8px;
}

.error-message {
  color: #ff4d4f;
  background: rgba(255, 77, 79, 0.1);
  padding: 12px;
  border-radius: 12px;
  margin-bottom: 16px;
  font-size: 0.85rem;
  font-weight: 600;
  border: 1px solid rgba(255, 77, 79, 0.2);
}

.footer-logo {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  opacity: 0.6;
}

.anniversary-logo {
  height: 36px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
