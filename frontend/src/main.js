import { createApp } from 'vue'
import './core/styles/main.css'
import App from './App.vue'
import router from './router'
import pinia from './store'
import { useAuthStore } from './store/auth'

const app = createApp(App)
app.use(pinia)
app.use(router)

// Восстанавливаем сессию до монтирования, чтобы гарды маршрутизатора
// видели актуального пользователя.
useAuthStore(pinia).bootstrap()

app.mount('#app')
