// @ts-nocheck
import { test, expect } from '@playwright/test'

import { render, screen } from '@testing-library/react'
import React from 'react'

test.beforeEach(async ({ page }) => {
  await page.goto('/')
})
// test.beforeEach(async ({ page }) => {
//   await page.route('**/api/accounts*', (route) =>
//     route.fulfill({
//       status: 200,
//       contentType: 'application/json',
//       body: JSON.stringify('test results'),
//     })
//   )
// })
test('renders accounts on home test', async ({ page }) => {
  await page.getByRole('button', { name: 'Get Users Accounts' }).click()
  await expect(page.getByText('[ { "id": 2, "item_id": 9, "')).toBeVisible()
})

test('renders accounts and at least 5 table items', async ({ page }) => {
  await page.getByRole('heading', { name: 'Home' }).click()
  await expect(page.getByRole('heading', { name: 'Home' })).toBeVisible()
  await page.getByRole('button', { name: 'Toggle Sidebar' }).click()
  await expect(page.getByRole('link', { name: 'All Accounts' })).toBeVisible()
  await page.getByRole('link', { name: 'All Accounts' }).click()

  await expect(page.getByRole('cell', { name: 'Payee' })).toBeVisible()
  const tableRows = page.locator('table tbody tr')
  const rowCount = await tableRows.count()
  await expect(rowCount).toBeGreaterThanOrEqual(5)
})

// test('happy path works with mocks or live', async ({ page }) => {
//   await expect(page.getByRole('heading', { name: /accounts/i })).toBeVisible()
//   await expect(page.getByRole('list')).toBeVisible()
// })

// test('has title', async ({ page }) => {
//   await page.goto('https://playwright.dev/')

//   // Expect a title "to contain" a substring.
//   await expect(page).toHaveTitle(/Playwright/)
// })

// test('get started link', async ({ page }) => {
//   await page.goto('https://playwright.dev/')

//   // Click the get started link.
//   await page.getByRole('link', { name: 'Get started' }).click()

//   // Expects page to have a heading with the name of Installation.
//   await expect(page.getByRole('heading', { name: 'Installation' })).toBeVisible()
// })
