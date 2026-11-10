import { describe, expect, it, beforeEach, afterEach, vi } from 'vitest'
import { createApp, nextTick } from 'vue'
import { usePwa } from '../usePwa'

describe('usePwa', () => {
  let app
  let container
  let state

  beforeEach(() => {
    vi.stubGlobal('navigator', { onLine: true })
    vi.stubGlobal(
      'matchMedia',
      vi.fn(() => ({ matches: false }))
    )
    container = document.createElement('div')
    document.body.appendChild(container)
    app = createApp({
      setup() {
        state = usePwa()
        return () => null
      }
    })
    app.mount(container)
  })

  afterEach(() => {
    app.unmount()
    container.remove()
    vi.unstubAllGlobals()
  })

  it('keeps installation disabled until the browser provides a prompt', () => {
    expect(state.canInstall.value).toBe(false)
    return expect(state.installApp()).resolves.toBe(false)
  })

  it('stores the install prompt and clears it after the user chooses', async () => {
    const prompt = vi.fn().mockResolvedValue(undefined)
    const event = new Event('beforeinstallprompt', { cancelable: true })
    Object.assign(event, {
      preventDefault: vi.fn(),
      prompt,
      userChoice: Promise.resolve({ outcome: 'accepted' })
    })

    window.dispatchEvent(event)
    await nextTick()

    expect(state.canInstall.value).toBe(true)
    await expect(state.installApp()).resolves.toBe(true)
    expect(prompt).toHaveBeenCalledOnce()
    expect(state.canInstall.value).toBe(false)
  })

  it('tracks online state and removes listeners on component teardown', async () => {
    vi.stubGlobal('navigator', { onLine: false })
    window.dispatchEvent(new Event('offline'))
    await nextTick()
    expect(state.isOnline.value).toBe(false)

    vi.stubGlobal('navigator', { onLine: true })
    window.dispatchEvent(new Event('online'))
    await nextTick()
    expect(state.isOnline.value).toBe(true)
  })
})
