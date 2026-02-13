import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isAuthenticated: false,
    loading: false,
    error: null
  }),
  actions: {
    setUser(user) {
      this.user = user
      this.isAuthenticated = !!user
    },
    clearAuth() {
      this.user = null
      this.isAuthenticated = false
    }
  }
})
