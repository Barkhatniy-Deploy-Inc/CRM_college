import { createApp } from 'vue'
import './core/styles/main.css'
import App from './App.vue'
import router from './router'
import pinia from './store'
import { useAuthStore } from './store/auth'

const app = createApp(App)
app.use(pinia)

async function bootstrap() {
  // Восстанавливаем cookie-сессию до установки router: навигационные гарды
  // получают актуального пользователя и не редиректят валидную сессию на '/'.
  await useAuthStore(pinia).bootstrap()
  app.use(router)
  await router.isReady()
  app.mount('#app')
}

bootstrap()
