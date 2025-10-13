// @ts-nocheck
import { test, expect } from '@playwright/test'

import { render, screen } from '@testing-library/react'
import React from 'react'

test.describe('Login', () => {
  test.beforeEach(async ({ page, baseURL }) => {
    await page.goto(new URL('/login', baseURL).toString())

    await page.evaluate(() => {
      localStorage.removeItem('finguard_auth_token')
      localStorage.removeItem('finguard_auth_user')
    })

    await expect(page.getByRole('button', { name: /login/i })).toBeVisible()
  })

  test('handles successful login', async ({ page }) => {
    await page.getByPlaceholder(/name@example.com/i).fill(process.env.E2E_EMAIL || 'a@b.com')
    await page.getByPlaceholder(/Password/i).fill(process.env.E2E_PASSWORD || 'secretpassword')

    const respPromise = page.waitForResponse(
      (r) => r.url().endsWith('/api/auth/login') && r.request().method() === 'POST'
    )

    await page.getByRole('button', { name: /Login/i }).click()
    await expect(page).toHaveURL((url) => url.pathname === '/')
  })

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

  test('handles 500 response, failed Login ', async ({ page, baseURL }) => {
    await page.route('**/api/auth/login', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal Server Error' }),
      })
    })

    await page.getByPlaceholder(/name@example.com/i).fill('a@b.com')
    await page.getByPlaceholder(/Password/i).fill('secretpassword')
    await page.getByRole('button', { name: /login/i }).click()

    await expect(page).toHaveURL((u) => u.pathname === '/login')

    await expect(page.getByText(/Failed Login/i)).toBeVisible()
    await expect(page.getByText(/Unable login at this time/i)).toBeVisible()
  })
})
