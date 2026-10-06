import { defineStore } from 'pinia'
import api from '../core/utils/api'

const getStoredUser = () => {
  try {
    const rawUser = localStorage.getItem('user')
    return rawUser ? JSON.parse(rawUser) : null
  } catch {
    localStorage.removeItem('user')
    return null
  }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: getStoredUser(),
    accessToken: localStorage.getItem('access_token') || null,
    isLoading: false,
    error: null
  }),

  getters: {
    // Источник истины — профиль, подтверждённый /auth/me и httpOnly cookie.
    // accessToken остаётся временно для совместимости с Bearer endpoint'ами.
    isAuthenticated: state => !!state.user,
    userRole: state => state.user?.role || 'guest'
  },

  actions: {
    async login(email, password) {
      this.isLoading = true
      this.error = null
      try {
        const response = await api.post('/auth/login', { email, password })
        const { access_token, user } = response.data

        this.accessToken = access_token
        this.user = user

        localStorage.setItem('access_token', access_token)
        localStorage.setItem('user', JSON.stringify(user))

        return true
      } catch (err) {
        this.error = err.response?.data?.detail || 'Ошибка входа'
        throw err
      } finally {
        this.isLoading = false
      }
    },

    async fetchMe() {
      const response = await api.get('/auth/me')
      this.user = response.data
      localStorage.setItem('user', JSON.stringify(this.user))
      return this.user
    },

    async bootstrap() {
      // Всегда проверяем cookie-сессию: localStorage может быть очищен,
      // тогда /auth/me + refresh-интерцептор восстановят профиль.
      try {
        await this.fetchMe()
      } catch {
        // 401 обрабатывается интерцептором (refresh или разлогин).
      }
    },

    async logout() {
      try {
        await api.post('/auth/logout')
      } catch (e) {
        console.error('Logout error', e)
      } finally {
        this.user = null
        this.accessToken = null
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
        window.location.href = '/'
      }
    }
  }
})
