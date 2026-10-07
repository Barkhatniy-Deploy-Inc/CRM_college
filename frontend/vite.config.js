import { defineConfig, configDefaults } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

// Проксируем API на отдельные сервисы по внешним портам из docker-compose.yml.
// Это позволяет разрабатывать фронтенд локально без Docker и nginx.
// В production фронтенд собирается в статику и отдаётся через nginx,
// поэтому dev-proxy на продакшен не влияет.
const proxy = {
  '/api/auth': 'http://localhost:8002',
  '/api/users': 'http://localhost:8002',
  '/api/schedule': 'http://localhost:8000',
  '/api/relations': 'http://localhost:8000',
  '/api/techcards': 'http://localhost:8001',
  '/api/techcard': 'http://localhost:8001'
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    // ngrok-free.app/ngrok.app нужны при демонстрации локального dev-сервера.
    // Для собственного домена можно задать VITE_ALLOWED_HOST.
    allowedHosts: [
      '.ngrok-free.app',
      '.ngrok.app',
      ...(process.env.VITE_ALLOWED_HOST ? [process.env.VITE_ALLOWED_HOST] : [])
    ],
    proxy
  },
  test: {
    globals: true,
    environment: 'jsdom',
    exclude: [...configDefaults.exclude, 'e2e/**']
  }
})
