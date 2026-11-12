import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import ApiDocsView from '../ApiDocsView.vue'

vi.mock('../../../store/auth', () => ({
  useAuthStore: () => ({ isAuthenticated: false })
}))

const RouterLinkStub = {
  props: ['to'],
  template: '<a :href="to"><slot /></a>'
}

describe('API documentation landing page', () => {
  it('links each service to its gateway Swagger UI and OpenAPI schema', () => {
    const wrapper = mount(ApiDocsView, { global: { stubs: { RouterLink: RouterLinkStub } } })

    expect(wrapper.find('h1').text()).toBe('Документация сервисов')
    for (const prefix of ['auth', 'schedule', 'techcard']) {
      expect(wrapper.find(`a[href="/api/${prefix}/docs"]`).exists()).toBe(true)
      expect(wrapper.find(`a[href="/api/${prefix}/openapi.json"]`).exists()).toBe(true)
    }
  })
})
