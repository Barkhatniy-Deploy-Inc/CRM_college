import { defineStore } from 'pinia'
import api from '../core/utils/api'

export const useAdminStore = defineStore('admin', {
  state: () => ({
    users: [],
    totalUsers: 0,
    auditLogs: [],
    totalLogs: 0,
    isLoading: false,
    error: null,
    pagination: {
      page: 1,
      limit: 20
    }
  }),

  actions: {
    async fetchUsers(params = {}) {
      this.isLoading = true
      try {
        const response = await api.get('/users', {
          params: { ...this.pagination, ...params }
        })

        console.log('DEBUG: fetchUsers response.data:', response.data)

        // Обработка разных форматов ответа
        let usersData = []
        if (Array.isArray(response.data)) {
          usersData = response.data
        } else if (response.data && Array.isArray(response.data.users)) {
          usersData = response.data.users
        } else {
          console.warn('DEBUG: usersData is not an array, check response structure')
        }

        this.users = usersData.map(u => ({
          ...u,
          is_active: u.is_active !== false
        }))

        this.totalUsers = response.data.total || usersData.length
      } catch (err) {
        this.error = 'Ошибка при загрузке пользователей'
        console.error('Fetch users error:', err)
      } finally {
        this.isLoading = false
      }
    },

    async fetchAuditLogs(params = {}) {
      this.isLoading = true
      try {
        const response = await api.get('/users/audit-log/all', {
          params: { page: 1, limit: 50, ...params }
        })
        this.auditLogs = response.data.logs
        this.totalLogs = response.data.total
      } catch (err) {
        this.error = 'Ошибка при загрузке логов'
        console.error(err)
      } finally {
        this.isLoading = false
      }
    },

    async fetchUserDetails(userId) {
      this.isLoading = true
      try {
        const response = await api.get(`/users/${userId}`)
        const userData = response.data
        console.log('DEBUG: Store received user details:', userData)
        if (userData) {
          userData.is_active = userData.is_active !== false
          console.log('DEBUG: casted is_active to:', userData.is_active)
        }
        return userData
      } catch (err) {
        console.error('Failed to fetch user details', err)
        throw err
      } finally {
        this.isLoading = false
      }
    },

    async createUser(userData) {
      try {
        await api.post('/auth/register', userData)
        return true
      } catch (err) {
        console.error('Failed to create user', err)
        throw err
      }
    },

    async updateUser(userId, data) {
      try {
        await api.put(`/users/${userId}`, data)
        await this.fetchUsers() // Обновляем список
        return true
      } catch (err) {
        console.error('Failed to update user', err)
        throw err
      }
    },

    async resetUserPassword(userId, newPassword) {
      try {
        await api.put(`/users/${userId}/password`, { new_password: newPassword })
        return true
      } catch (err) {
        console.error('Failed to reset password', err)
        throw err
      }
    }
  }
})
