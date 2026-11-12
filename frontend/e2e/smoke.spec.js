import { test, expect } from '@playwright/test'

// Дымовой E2E-тест: приложение отвечает и монтирует Vue.
// Требует запущенного стека (`make up`).
test('home page renders', async ({ page }) => {
  const response = await page.goto('/')
  expect(response?.status()).toBeLessThan(400)
  await expect(page.locator('#app')).toBeAttached()
})

test('documentation is reachable without signing in', async ({ page, request }) => {
  const response = await page.goto('/docs')
  expect(response?.status()).toBeLessThan(400)
  await expect(page.getByRole('heading', { name: 'Документация сервисов' })).toBeVisible()

  for (const service of ['auth', 'schedule', 'techcard']) {
    await expect(page.locator(`a[href="/api/${service}/docs"]`)).toBeVisible()
    const schema = await request.get(`/api/${service}/openapi.json`)
    expect(schema.status()).toBe(200)
    expect((await schema.json()).openapi).toBeTruthy()
  }
})
