import { computed, onMounted, onUnmounted, shallowRef } from 'vue'

/** @typedef {Event & { prompt: () => Promise<void>, userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }> }} InstallPromptEvent */

export function usePwa() {
  const canInstall = shallowRef(false)
  const isInstalled = shallowRef(false)
  const isOnline = shallowRef(typeof navigator === 'undefined' ? true : navigator.onLine)
  /** @type {import('vue').ShallowRef<InstallPromptEvent | null>} */
  const deferredPrompt = shallowRef(null)

  const installLabel = computed(() => (canInstall.value ? 'Установить приложение' : ''))

  const handleBeforeInstallPrompt = event => {
    event.preventDefault()
    deferredPrompt.value = event
    canInstall.value = true
  }

  const handleInstalled = () => {
    isInstalled.value = true
    canInstall.value = false
    deferredPrompt.value = null
  }

  const handleNetworkChange = () => {
    isOnline.value = navigator.onLine
  }

  onMounted(() => {
    isInstalled.value = window.matchMedia('(display-mode: standalone)').matches
    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
    window.addEventListener('appinstalled', handleInstalled)
    window.addEventListener('online', handleNetworkChange)
    window.addEventListener('offline', handleNetworkChange)
  })

  onUnmounted(() => {
    window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
    window.removeEventListener('appinstalled', handleInstalled)
    window.removeEventListener('online', handleNetworkChange)
    window.removeEventListener('offline', handleNetworkChange)
  })

  const installApp = async () => {
    const prompt = deferredPrompt.value
    if (!prompt) return false

    try {
      await prompt.prompt()
      const { outcome } = await prompt.userChoice
      return outcome === 'accepted'
    } catch {
      return false
    } finally {
      deferredPrompt.value = null
      canInstall.value = false
    }
  }

  return { canInstall, isInstalled, isOnline, installLabel, installApp }
}
