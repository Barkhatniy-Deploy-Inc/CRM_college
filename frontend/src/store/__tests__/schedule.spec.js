import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useScheduleStore } from '../schedule'
import api from '../../core/utils/api'

vi.mock('../../core/utils/api', () => ({
  default: {
    get: vi.fn()
  }
}))

describe('Schedule Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('should fetch groups', async () => {
    const store = useScheduleStore()
    const mockGroups = [{ id: 1, name: 'ИСП-21' }]
    api.get.mockResolvedValueOnce({ data: mockGroups })

    await store.fetchGroups()
    
    expect(store.groups).toEqual(mockGroups)
    expect(api.get).toHaveBeenCalledWith('/schedule/groups')
  })

  it('should fetch schedule with filters', async () => {
    const store = useScheduleStore()
    const mockLessons = [{ id: 1, title: 'Math' }]
    api.get.mockResolvedValueOnce({ data: mockLessons })

    const filters = { group_id: 1 }
    await store.fetchSchedule(filters)
    
    expect(store.lessons).toEqual(mockLessons)
    expect(api.get).toHaveBeenCalledWith('/schedule/list', expect.objectContaining({
      params: expect.objectContaining(filters)
    }))
  })

  it('should handle fetch error', async () => {
    const store = useScheduleStore()
    api.get.mockRejectedValueOnce(new Error('Network error'))

    try {
      await store.fetchSchedule()
    } catch (e) {
      // Expected
    }
    
    expect(store.error).toBe('Не удалось загрузить расписание')
    expect(store.isLoading).toBe(false)
  })
})
