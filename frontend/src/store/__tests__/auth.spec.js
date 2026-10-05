import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useAuthStore } from '../auth'
import api from '../../core/utils/api'

// Mock api
vi.mock('../../core/utils/api', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn()
  }
}))

// Mock localStorage
const localStorageMock = (() => {
  let store = {}
  return {
    getItem: vi.fn(key => store[key] || null),
    setItem: vi.fn((key, value) => {
      store[key] = value.toString()
    }),
    removeItem: vi.fn(key => {
      delete store[key]
    }),
    clear: vi.fn(() => {
      store = {}
    })
  }
})()

vi.stubGlobal('localStorage', localStorageMock)

// Mock window.location
const locationMock = { href: '' }
vi.stubGlobal('location', locationMock)

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorageMock.clear()
    vi.clearAllMocks()
  })

  it('should have initial state', () => {
    const store = useAuthStore()
    expect(store.user).toBeNull()
    expect(store.accessToken).toBeNull()
    expect(store.isAuthenticated).toBe(false)
  })

  it('should login successfully', async () => {
    const store = useAuthStore()
    const mockUser = { id: 1, full_name: 'Test' }
    const mockToken = 'fake-token'

    api.post.mockResolvedValueOnce({
      data: { access_token: mockToken, user: mockUser }
    })

    const result = await store.login('test@test.com', 'pass')

    expect(result).toBe(true)
    expect(store.user).toEqual(mockUser)
    expect(store.accessToken).toBe(mockToken)
    expect(store.isAuthenticated).toBe(true)
    expect(localStorageMock.setItem).toHaveBeenCalledWith('access_token', mockToken)
  })

  it('should handle login error', async () => {
    const store = useAuthStore()
    api.post.mockRejectedValueOnce({
      response: { data: { detail: 'Invalid credentials' } }
    })

    await expect(store.login('test@test.com', 'wrong')).rejects.toThrow()

    expect(store.isAuthenticated).toBe(false)
    expect(store.error).toBe('Invalid credentials')
  })

  it('should logout and clear data', async () => {
    const store = useAuthStore()
    store.user = { id: 1 }
    store.accessToken = 'token'

    api.post.mockResolvedValueOnce({})

    await store.logout()

    expect(store.user).toBeNull()
    expect(store.accessToken).toBeNull()
    expect(store.isAuthenticated).toBe(false)
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('user')
  })

  it('should fetch current user profile', async () => {
    const store = useAuthStore()
    const mockUser = { id: 5, full_name: 'Me' }
    api.get.mockResolvedValueOnce({ data: mockUser })

    const result = await store.fetchMe()

    expect(result).toEqual(mockUser)
    expect(store.user).toEqual(mockUser)
    expect(api.get).toHaveBeenCalledWith('/auth/me')
  })

  it('should skip bootstrap without session', async () => {
    const store = useAuthStore()

    await store.bootstrap()

    expect(api.get).not.toHaveBeenCalled()
  })
})
