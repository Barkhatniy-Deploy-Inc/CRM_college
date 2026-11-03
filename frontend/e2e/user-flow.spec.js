import { test, expect } from '@playwright/test'

test('registered user can log in and create and reopen a techcard', async ({ page, request }) => {
  const email = `e2e-${Date.now()}-${Math.random().toString(36).slice(2)}@example.com`
  const password = 'e2e-password-123'
  const registration = await request.post('/api/auth/register', {
    data: { email, password, full_name: 'E2E Student' }
  })
  expect(registration.status()).toBe(201)

  await page.goto('/')
  await page.getByPlaceholder('example@sielom.ru').fill(email)
  await page.getByPlaceholder('••••••••').fill(password)
  await page.getByRole('button', { name: 'Войти' }).click()
  await expect(page).toHaveURL(/\/dashboard$/)
  await page.goto('/techcards/new')
  await page.getByPlaceholder('Введите тему полностью...').fill('E2E lesson')
  page.once('dialog', dialog => dialog.accept())
  await page.getByRole('button', { name: 'Сохранить и Экспорт' }).click()
  await expect(page).toHaveURL(/\/techcards\/\d+$/)
  await page.reload()
  await expect(page.getByPlaceholder('Введите тему полностью...')).toHaveValue('E2E lesson')
})
