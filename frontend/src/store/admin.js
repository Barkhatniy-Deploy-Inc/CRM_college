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
        this.users = response.data.users
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
        this.auditLogs = response.data.items
        this.totalLogs = response.data.total
      } catch (err) {
        this.error = 'Ошибка при загрузке логов'
        console.error(err)
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
