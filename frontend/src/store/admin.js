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
        // Принудительно приводим к Boolean для корректного отображения статусов
        this.users = response.data.users.map(u => ({
          ...u,
          is_active: Boolean(u.is_active)
        }))
        this.totalUsers = response.data.total
      } catch (err) {
        this.error = 'Ошибка при загрузке пользователей'
        console.error(err)
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
          userData.is_active = Boolean(userData.is_active)
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

    async updateUser(userId, data) {
      try {
        await api.put(`/users/${userId}`, data)
        await this.fetchUsers() // Обновляем список
        return true
      } catch (err) {
        console.error('Failed to update user', err)
        throw err
      }
    }
  }
})
