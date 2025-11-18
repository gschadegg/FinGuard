// @ts-nocheck
import { test, expect } from '@playwright/test'

import { render, screen } from '@testing-library/react'
import React from 'react'

test.beforeEach(async ({ page }) => {
  await page.goto('/')
})

test('loads dashboard  already authenticated', async ({ page, baseURL }) => {
  const debug = await page.evaluate(() => ({
    href: location.href,
    token: localStorage.getItem('finguard_auth_token'),
    user: localStorage.getItem('finguard_auth_user'),
  }))
  // console.log('DEBUG storage:', debug)

  await expect(page.getByText(/Dashboard/i)).toBeVisible()
})

test('renders accounts and at least 5 table items', async ({ page }) => {
  // await page.getByRole('heading', { name: 'Home' }).click()
  // await expect(page.getByRole('heading', { name: 'Home' })).toBeVisible()
  await page.getByRole('button', { name: 'Toggle Sidebar' }).click()
  await expect(page.getByRole('link', { name: 'All Accounts' })).toBeVisible()
  await page.getByRole('link', { name: 'All Accounts' }).click()

  await expect(page.getByRole('cell', { name: 'Payee' })).toBeVisible()
  const tableRows = page.locator('table tbody tr')
  const rowCount = await tableRows.count()
  await expect(rowCount).toBeGreaterThanOrEqual(5)
})
