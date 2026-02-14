import { defineStore } from 'pinia'

export const useSettingsStore = defineStore('settings', {
  state: () => ({
    theme: localStorage.getItem('theme') || 'light',
    glassEnabled: localStorage.getItem('glassEnabled') !== 'false'
  }),
  actions: {
    toggleTheme() {
      this.theme = this.theme === 'light' ? 'dark' : 'light'
      localStorage.setItem('theme', this.theme)
      this.applySettings()
    },
    toggleGlass() {
      this.glassEnabled = !this.glassEnabled
      localStorage.setItem('glassEnabled', this.glassEnabled)
      this.applySettings()
    },
    applySettings() {
      const html = document.documentElement
      
      // Применяем тему через атрибут (самый надежный способ)
      html.setAttribute('data-theme', this.theme)
      
      // Применяем стиль стекла через класс
      if (this.glassEnabled === false) {
        html.classList.add('glass-disabled')
      } else {
        html.classList.remove('glass-disabled')
      }
    }
  }
})
