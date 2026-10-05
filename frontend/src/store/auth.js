import { defineStore } from 'pinia'
import api from '../core/utils/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null,
    accessToken: localStorage.getItem('access_token') || null,
    isLoading: false,
    error: null
  }),

  getters: {
    isAuthenticated: state => !!state.accessToken,
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
      // Восстанавливаем профиль, если есть признаки активной сессии.
      if (!this.accessToken && !this.user) return
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
