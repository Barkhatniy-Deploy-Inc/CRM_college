import { defineStore } from 'pinia'
import api from '../core/utils/api'

export const useScheduleStore = defineStore('schedule', {
  state: () => ({
    lessons: [],
    groups: [],
    auditoriums: [],
    isLoading: false,
    error: null,
    currentFilters: {
      group_id: null,
      date_from: null,
      date_to: null
    }
  }),

  actions: {
    async fetchGroups() {
      try {
        const response = await api.get('/schedule/groups')
        this.groups = response.data
      } catch (err) {
        console.error('Failed to fetch groups', err)
      }
    },

    async fetchAuditoriums() {
      try {
        const response = await api.get('/schedule/auditoriums')
        this.auditoriums = response.data
      } catch (err) {
        console.error('Failed to fetch auditoriums', err)
      }
    },

    async fetchSchedule(filters = {}) {
      this.isLoading = true
      this.error = null
      try {
        const params = { ...this.currentFilters, ...filters }
        const response = await api.get('/schedule/list', { params })
        this.lessons = response.data
        return this.lessons
      } catch (err) {
        this.error = 'Не удалось загрузить расписание'
        console.error(err)
        throw err
      } finally {
        this.isLoading = false
      }
    },

    async fetchUpcoming() {
      // Получаем расписание на сегодня
      const today = new Date().toISOString().split('T')[0]
      return await this.fetchSchedule({ 
        date_from: today, 
        date_to: today 
      })
    }
  }
})
