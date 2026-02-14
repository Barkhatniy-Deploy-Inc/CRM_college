import { defineStore } from 'pinia'
import api from '../core/utils/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isAuthenticated: false,
    loading: false,
    error: null,
    isInitialized: false
  }),
  actions: {
    setUser(user) {
      this.user = user
      this.isAuthenticated = !!user
    },
    async login(email, password) {
      this.loading = true
      this.error = null
      try {
        const response = await api.post('/auth/login', { email, password })
        this.setUser(response.data.user)
        return true
      } catch (err) {
        this.error = err.response?.data?.detail || 'Ошибка при входе в систему'
        return false
      } finally {
        this.loading = false
      }
    },
    async fetchUser() {
      if (this.isInitialized) return
      try {
        const response = await api.get('/auth/me')
        this.setUser(response.data)
      } catch (err) {
        this.clearAuth()
      } finally {
        this.isInitialized = true
      }
    },
    async logout() {
      try {
        await api.post('/auth/logout')
      } finally {
        this.clearAuth()
      }
    },
    clearAuth() {
      this.user = null
      this.isAuthenticated = false
    }
  }
})
