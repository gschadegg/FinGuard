// @ts-nocheck
import { test, expect } from '@playwright/test'

import { render, screen } from '@testing-library/react'
import React from 'react'

const goto = (page, baseURL, path) => page.goto(new URL(path, baseURL).toString())

test.describe('Login', () => {
  test.describe.configure({ mode: 'default' })
  test.beforeEach(async ({ page, baseURL, context }) => {
    // await page.addInitScript(() => {
    //   localStorage.clear()
    //   sessionStorage.clear()
    // })

    await context.addInitScript(() => {
      window.localStorage.removeItem('finguard_auth_token')
      window.localStorage.removeItem('finguard_auth_user')
    })
    // await page.context().clearCookies()

    await goto(page, baseURL, '/login')

    await page.waitForLoadState('domcontentloaded')
    await expect(page.getByRole('button', { name: /login/i })).toBeVisible()
  })

  //TC-FLOW-LOGIN-001
  test('handles successful login', async ({ page }) => {
    await page.getByPlaceholder(/name@example.com/i).fill(process.env.E2E_EMAIL || 'a@b.com')
    await page.getByPlaceholder(/Password/i).fill(process.env.E2E_PASSWORD || 'secretpassword')

    const respPromise = page.waitForResponse(
      (r) => r.url().endsWith('/api/auth/login') && r.request().method() === 'POST'
    )

    await page.getByRole('button', { name: /Login/i }).click()

    await respPromise
    await page.waitForURL('/')

    await expect(page).toHaveURL((url) => url.pathname === '/')
    await expect(page.getByTestId('dashboard-skeleton')).toBeVisible()
  })

  //TC-FLOW-LOGIN-002
  test('handles bad credentials', async ({ page, baseURL }) => {
    await page.getByPlaceholder(/name@example.com/i).fill('a@b.com')
    await page.getByPlaceholder(/Password/i).fill('wrong')

    const respPromise = page.waitForResponse(
      (r) => r.url().endsWith('/api/auth/login') && r.request().method() === 'POST'
    )
    await page.getByRole('button', { name: /login/i }).click()
    const resp = await respPromise
    expect(resp.status()).toBe(401)

    await expect(page).toHaveURL((u) => u.pathname === '/login')
    await expect(page.getByText(/Invalid Credentials/i)).toBeVisible()
    await expect(page.getByText(/Failed login, invalid email or password/i)).toBeVisible()
  })

  //TC-FLOW-LOGIN-003
  test('handles 500 response, failed Login ', async ({ page, baseURL }) => {
    await page.route(
      '**/api/auth/login',
      (route) =>
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Internal Server Error' }),
        }),
      { times: 1 }
    )

    await page.getByPlaceholder(/name@example.com/i).fill('a@b.com')
    await page.getByPlaceholder(/Password/i).fill('secretpassword')
    await page.getByRole('button', { name: /login/i }).click()

    await expect(page).toHaveURL((u) => u.pathname === '/login')

    await expect(page.getByText(/Failed Login/i)).toBeVisible()
    await expect(page.getByText(/Unable login at this time/i)).toBeVisible()
  })
})
