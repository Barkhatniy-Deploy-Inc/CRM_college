import { test, expect } from '@playwright/test'

// Дымовой E2E-тест: приложение отвечает и монтирует Vue.
// Требует запущенного стека (`make up`).
test('home page renders', async ({ page }) => {
  const response = await page.goto('/')
  expect(response?.status()).toBeLessThan(400)
  await expect(page.locator('#app')).toBeAttached()
})
