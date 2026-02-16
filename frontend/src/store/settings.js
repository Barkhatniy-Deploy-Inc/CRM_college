import { defineStore } from 'pinia'

export const useSettingsStore = defineStore('settings', {
  state: () => ({
    theme: localStorage.getItem('theme') || 'light',
    glassEnabled: JSON.parse(localStorage.getItem('glass_enabled') ?? 'true')
  }),

  actions: {
    initTheme() {
      // Применяем тему к тегу html при загрузке
      document.documentElement.setAttribute('data-theme', this.theme)
      if (this.theme === 'dark') {
        document.documentElement.classList.add('dark-theme')
      } else {
        document.documentElement.classList.remove('dark-theme')
      }
    },

    toggleTheme() {
      this.theme = this.theme === 'light' ? 'dark' : 'light'
      localStorage.setItem('theme', this.theme)
      this.initTheme()
    },

    toggleGlass() {
      this.glassEnabled = !this.glassEnabled
      localStorage.setItem('glass_enabled', JSON.stringify(this.glassEnabled))
    }
  }
})
