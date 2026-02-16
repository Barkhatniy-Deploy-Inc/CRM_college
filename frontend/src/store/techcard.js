import { defineStore } from 'pinia'
import api from '../core/utils/api'

export const useTechcardStore = defineStore('techcard', {
  state: () => ({
    techcards: [],
    currentCard: null,
    isLoading: false,
    error: null,
    pagination: {
      page: 1,
      limit: 20
    }
  }),

  actions: {
    async fetchTechcards(params = {}) {
      this.isLoading = true
      try {
        // Эндпоинт в Techcard Service: GET /api/techcard/techcards (через Nginx)
        const response = await api.get('/techcard/techcards', { params })
        this.techcards = response.data
      } catch (err) {
        this.error = 'Не удалось загрузить технологические карты'
        console.error(err)
      } finally {
        this.isLoading = false
      }
    },

    async fetchCardById(id) {
      this.isLoading = true
      try {
        const response = await api.get(`/techcard/techcards/${id}`)
        this.currentCard = response.data
        return this.currentCard
      } catch (err) {
        this.error = 'Карта не найдена'
        throw err
      } finally {
        this.isLoading = false
      }
    },

    async saveCard(id, data) {
      this.isLoading = true
      try {
        const response = await api.put(`/techcard/techcards/${id}`, data)
        return response.data
      } catch (err) {
        this.error = 'Ошибка при сохранении'
        throw err
      } finally {
        this.isLoading = false
      }
    },

    async downloadCard(id) {
      try {
        const response = await api.get(`/techcard/techcards/download/${id}`, {
          responseType: 'blob'
        })
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `techcard_${id}.docx`)
        document.body.appendChild(link)
        link.click()
        link.remove()
      } catch (err) {
        console.error('Download failed', err)
        alert('Не удалось скачать файл')
      }
    }
  }
})
