import { test, expect } from '@playwright/test'

const usingMocks = () => process.env.USE_MOCKS === 'true'
const goto = (page, baseURL, path) => page.goto(new URL(path, baseURL).toString())

async function fillRegisterForm(page, { name, email, password }) {
  await page.getByPlaceholder('Full name').fill(name)
  await page.getByPlaceholder('name@example.com').fill(email)
  await page.getByPlaceholder('Password').fill(password)
}

test.describe('Register', () => {
  test.beforeEach(async ({ page, baseURL }) => {
    await goto(page, baseURL, '/register')
    await page.evaluate(() => {
      localStorage.removeItem('finguard_auth_token')
      localStorage.removeItem('finguard_auth_user')
    })

    await expect(page.getByText('Create an account')).toBeVisible()
    await expect(page.getByRole('button', { name: 'Sign up with Email' })).toBeVisible()
  })

  test('handles successful registration', async ({ page }) => {
    const unique = Date.now()
    const email = usingMocks() ? 'new@test.local' : `new${unique}@test.local`

    const respPromise = page.waitForResponse(
      (r) => r.url().endsWith('/api/auth/register') && r.request().method() === 'POST'
    )
    await fillRegisterForm(page, { name: 'New User', email, password: 'secretpassword' })
    await page.getByRole('button', { name: 'Sign up with Email' }).click()
    const resp = await respPromise
    expect(resp.status()).toBeLessThan(400)

    // redirected to dashboard
    await expect(page).toHaveURL((u) => u.pathname === '/')
    await expect(page.getByText(/FINGUARD Dashboard/i)).toBeVisible()
  })

  test('handles when account with "Email already exists”', async ({ page }) => {
    if (!usingMocks()) {
      await page.route('**/api/auth/register', (route) =>
        route.fulfill({
          status: 409,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Email already exists' }),
        })
      )
    }

    const respPromise = page.waitForResponse(
      (r) => r.url().endsWith('/api/auth/register') && r.request().method() === 'POST'
    )
    await fillRegisterForm(page, {
      name: 'Existing User',
      email: 'alreadyexists@test.local',
      password: 'secretpassword',
    })

    await page.getByRole('button', { name: 'Sign up with Email' }).click()
    const resp = await respPromise
    expect([400, 409]).toContain(resp.status())

    await expect(page).toHaveURL((u) => u.pathname === '/register')

    await expect(page.getByText(/unable to create account/i)).toBeVisible()
    await expect(page.getByText(/already exists|use another/i)).toBeVisible()
  })

  test('handles when password is less then 8 chars long', async ({ page, baseURL }) => {
    await page.route('**/api/auth/register', (route) =>
      route.fulfill({
        status: 422,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: [
            {
              loc: ['body', 'password'],
              msg: 'String should have at least 8 characters',
              type: 'string_too_short',
            },
          ],
        }),
      })
    )

    await page.goto(new URL('/register', baseURL).toString())
    await page.getByPlaceholder('Full name').fill('Weak Pwd')
    await page.getByPlaceholder('name@example.com').fill('weak@test.local')
    await page.getByPlaceholder('Password').fill('short')
    await page.getByRole('button', { name: 'Sign up with Email' }).click()

    await expect(page).toHaveURL((u) => u.pathname === '/register')
    await expect(page.getByText(/invalid password/i)).toBeVisible()
    await expect(page.getByText(/at least 8 characters/i)).toBeVisible()
  })
})
