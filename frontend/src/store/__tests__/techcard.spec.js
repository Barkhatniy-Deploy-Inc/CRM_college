import { setActivePinia, createPinia } from 'pinia'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useTechcardStore } from '../techcard'
import api from '../../core/utils/api'

vi.mock('../../core/utils/api', () => ({
  default: {
    get: vi.fn(),
    put: vi.fn(),
    post: vi.fn()
  }
}))

describe('Techcard Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('should fetch techcards list', async () => {
    const store = useTechcardStore()
    const mockData = [{ id: 1, tema: 'Test Card' }]
    api.get.mockResolvedValueOnce({ data: mockData })

    await store.fetchTechcards()

    expect(store.techcards).toEqual(mockData)
    expect(api.get).toHaveBeenCalledWith('/techcards', { params: {} })
  })

  it('should create a card', async () => {
    const store = useTechcardStore()
    const payload = { tema: 'New Card' }
    api.post.mockResolvedValueOnce({ data: { id: 7, ...payload } })

    const result = await store.createCard(payload)

    expect(result.id).toBe(7)
    expect(api.post).toHaveBeenCalledWith('/techcards', payload)
  })

  it('should fetch card by id', async () => {
    const store = useTechcardStore()
    const mockCard = { id: 1, tema: 'Specific Card' }
    api.get.mockResolvedValueOnce({ data: mockCard })

    const result = await store.fetchCardById(1)

    expect(result).toEqual(mockCard)
    expect(store.currentCard).toEqual(mockCard)
    expect(api.get).toHaveBeenCalledWith('/techcards/1')
  })

  it('should save card successfully', async () => {
    const store = useTechcardStore()
    const cardData = { tema: 'Updated' }
    api.put.mockResolvedValueOnce({ data: { id: 1, ...cardData } })

    const result = await store.saveCard(1, cardData)

    expect(result.tema).toBe('Updated')
    expect(api.put).toHaveBeenCalledWith('/techcards/1', cardData)
  })
})
