import { test, expect } from '@playwright/test'

const usingMocks = () => process.env.USE_MOCKS === 'true'
const goto = (page, baseURL, path) => page.goto(new URL(path, baseURL).toString())

async function fillRegisterForm(page, { name, email, password }) {
  await page.getByPlaceholder('Full name').fill(name)
  await page.getByPlaceholder('name@example.com').fill(email)
  await page.getByPlaceholder('Password').fill(password)
}

function getAlert(page) {
  return page.getByRole('status')
}

test.describe('Register', () => {
  test.beforeEach(async ({ page, baseURL, context }) => {
    // await page.addInitScript(() => {
    //   localStorage.clear()
    //   sessionStorage.clear()
    // })

    await context.addInitScript(() => {
      window.localStorage.removeItem('finguard_auth_token')
      window.localStorage.removeItem('finguard_auth_user')
    })

    await goto(page, baseURL, '/register')

    await page.waitForLoadState('domcontentloaded')

    await expect(page.getByText('Create an account')).toBeVisible()
    await expect(page.getByRole('button', { name: 'Sign up with Email' })).toBeVisible()
  })

  // TC-FLOW-REGISTER-001
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
    await page.waitForLoadState('domcontentloaded')

    // redirected to dashboard
    await expect(page).toHaveURL((u) => u.pathname === '/')

    // await page.waitForLoadState('domcontentloaded')
    await expect(page.getByText(/FINGUARD Dashboard/i)).toBeVisible()
  })

  // TC-FLOW-REGISTER-002
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

  // TC-FLOW-REGISTER-003
  test('handles when password is less then 12 chars long', async ({ page, baseURL }) => {
    await page.route(
      '**/api/auth/register',
      (route) =>
        route.fulfill({
          status: 422,
          contentType: 'application/json',
          body: JSON.stringify({
            detail: [
              {
                loc: ['body', 'password'],
                msg: 'String should have at least 12 characters',
                type: 'string_too_short',
              },
            ],
          }),
        }),
      { times: 1 }
    )

    await page.goto(new URL('/register', baseURL).toString())
    await page.getByPlaceholder('Full name').fill('Short Pwd')
    await page.getByPlaceholder('name@example.com').fill('Short@test.local')

    // password is less then 12 chars
    await page.getByPlaceholder('Password').fill('short')

    const respPromise = page.waitForResponse(
      (r) => r.url().endsWith('/api/auth/register') && r.request().method() === 'POST'
    )
    await page.getByRole('button', { name: 'Sign up with Email' }).click()

    await respPromise
    await expect(page).toHaveURL((u) => u.pathname === '/register')

    const alert = getAlert(page)
    await expect(alert).toBeVisible()
    await expect(alert).toContainText(/Invalid Password/i)
    await expect(alert).toContainText(/at least 12 characters/i)
  })

  // TC-FLOW-REGISTER-004
  test('handles when password is missing an uppercase letter', async ({ page, baseURL }) => {
    await page.route(
      '**/api/auth/register',
      (route) =>
        route.fulfill({
          status: 422,
          contentType: 'application/json',
          body: JSON.stringify({
            detail: [
              {
                loc: ['body', 'password'],
                msg: 'Password must include at least one uppercase and one special character.',
                type: 'value_error',
              },
            ],
          }),
        }),
      { times: 1 }
    )

    await page.goto(new URL('/register', baseURL).toString())
    await page.getByPlaceholder('Full name').fill('No Uppercase Char')
    await page.getByPlaceholder('name@example.com').fill('no-uppercase@test.local')

    // has 12 chars length, and has a special char but no uppercase
    await page.getByPlaceholder('Password').fill('lowercase_only!')
    const respPromise = page.waitForResponse(
      (r) => r.url().endsWith('/api/auth/register') && r.request().method() === 'POST'
    )
    await page.getByRole('button', { name: 'Sign up with Email' }).click()
    await respPromise

    await expect(page).toHaveURL((u) => u.pathname === '/register')
    const alert = getAlert(page)
    await expect(alert).toBeVisible()
    await expect(alert).toContainText(/Invalid Password/i)
    await expect(alert).toContainText(/at least 1 uppercase/i)
  })

  // TC-FLOW-REGISTER-005
  test('handles when password is missing a special character', async ({ page, baseURL }) => {
    await page.route(
      '**/api/auth/register',
      (route) =>
        route.fulfill({
          status: 422,
          contentType: 'application/json',
          body: JSON.stringify({
            detail: [
              {
                loc: ['body', 'password'],
                msg: 'Password must include at least one uppercase and one special character.',
                type: 'value_error',
              },
            ],
          }),
        }),
      { times: 1 }
    )

    await page.goto(new URL('/register', baseURL).toString())
    await page.getByPlaceholder('Full name').fill('No Special')
    await page.getByPlaceholder('name@example.com').fill('nospecial@test.local')

    // has 12 chars length, has uppercase, but no special char
    await page.getByPlaceholder('Password').fill('PasswordHasUpper1')

    const respPromise = page.waitForResponse(
      (r) => r.url().endsWith('/api/auth/register') && r.request().method() === 'POST'
    )
    await page.getByRole('button', { name: 'Sign up with Email' }).click()
    await respPromise

    await expect(page).toHaveURL((u) => u.pathname === '/register')

    const alert = getAlert(page)
    await expect(alert).toBeVisible()
    await expect(alert).toContainText(/Invalid Password/i)
    await expect(alert).toContainText(/at least 1 uppercase letter and 1 special character/i)
  })
})
