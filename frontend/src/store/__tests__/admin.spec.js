import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useAdminStore } from '../admin'
import api from '../../core/utils/api'

vi.mock('../../core/utils/api', () => ({
  default: {
    get: vi.fn(),
    put: vi.fn()
  }
}))

describe('Admin Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('should fetch users list', async () => {
    const store = useAdminStore()
    const mockData = { users: [{ id: 1, full_name: 'Admin' }], total: 1 }
    api.get.mockResolvedValueOnce({ data: mockData })

    await store.fetchUsers()
    
    expect(store.users).toHaveLength(1)
    expect(store.totalUsers).toBe(1)
    expect(api.get).toHaveBeenCalledWith('/users', expect.any(Object))
  })

  it('should fetch audit logs', async () => {
    const store = useAdminStore()
    const mockData = { items: [{ id: 1, action: 'LOGIN' }], total: 1 }
    api.get.mockResolvedValueOnce({ data: mockData })

    await store.fetchAuditLogs()
    
    expect(store.auditLogs).toHaveLength(1)
    expect(api.get).toHaveBeenCalledWith('/users/audit-log/all', expect.any(Object))
  })

  it('should update user successfully', async () => {
    const store = useAdminStore()
    api.put.mockResolvedValueOnce({})
    api.get.mockResolvedValueOnce({ data: { users: [], total: 0 } }) // fetchUsers reload

    const result = await store.updateUser(1, { role: 'admin' })
    
    expect(result).toBe(true)
    expect(api.put).toHaveBeenCalledWith('/users/1', { role: 'admin' })
  })
})
