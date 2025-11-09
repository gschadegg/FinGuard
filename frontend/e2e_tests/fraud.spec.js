// @ts-nocheck
import { test, expect } from '@playwright/test'

import { render, screen } from '@testing-library/react'
import React from 'react'

const goto = (page, baseURL, path) => page.goto(new URL(path, baseURL).toString())
const isFraudReview = (url) => /\/api\/transactions\/\d+\/fraud-review$/.test(url)

test.describe('Fraud Review & Alerts', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  // TC-FLOW-FRAUD-001
  test('high risk transaction notification', async ({ page }) => {
    await page.goto('/accounts')

    const table = page.getByRole('table')
    await expect(table).toBeVisible()

    const highRow = page.locator('tr[data-risk-level="high"]').first()
    await expect(highRow).toBeVisible()

    await expect(page.getByText('potential high-risk transactions need review')).toBeVisible()
    const rollup = await page
      .locator('div')
      .filter({ hasText: /^Potential High Risks$/ })
      .first()

    await expect(page.getByRole('main').getByText('2', { exact: true })).toBeVisible()
  })

  // TC-FLOW-FRAUD-002
  test('high risk transaction review', async ({ page }) => {
    await page.goto('/accounts')

    const table = page.getByRole('table')
    await expect(table).toBeVisible()

    const highRow = page.locator('tr[data-risk-level="high"]').first()
    await expect(highRow).toBeVisible()

    await highRow.getByRole('button', { name: /open menu/i }).click()
    await page.getByRole('menuitem', { name: 'Risk Review' }).click()

    const dialog = page.getByRole('dialog', { name: 'Risk Review' })
    await expect(dialog).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Risk Review' })).toBeVisible()
    await page.getByRole('button', { name: 'Mark as Safe' }).click()

    await Promise.all([
      page.waitForResponse(
        (res) =>
          isFraudReview(res.url()) &&
          res.request().method() === 'PUT' &&
          res.status() >= 200 &&
          res.status() < 300
      ),
      dialog.getByRole('button', { name: /save/i }).click(),
    ])

    await expect(dialog).toBeHidden()

    await expect(page.getByText('Risk Review Saved')).toBeVisible()
    await expect(page.getByText('Transaction has been marked')).toBeVisible()

    await expect(highRow.getByTestId('risk-badge')).toHaveText(/Reviewed/i)
  })

  // TC-FLOW-FRAUD-003
  test('transaction re-review ', async ({ page }) => {
    await page.goto('/accounts')

    const table = page.getByRole('table')
    await expect(table).toBeVisible()

    const reviewedRow = page
      .getByTestId('transaction-row')
      .filter({ has: page.getByTestId('risk-badge').getByText(/Reviewed/i) })
      .first()

    await expect(reviewedRow.getByTestId('risk-badge')).toHaveText(/Reviewed/i)

    await reviewedRow.getByRole('button', { name: /open menu/i }).click()
    await page.getByRole('menuitem', { name: 'Risk Review' }).click()

    const dialog = page.getByRole('dialog', { name: 'Risk Review' })
    await expect(dialog).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Risk Review' })).toBeVisible()
    await page.getByRole('button', { name: 'Mark as Fraudulent' }).click()

    await Promise.all([
      page.waitForResponse(
        (res) =>
          isFraudReview(res.url()) &&
          res.request().method() === 'PUT' &&
          res.status() >= 200 &&
          res.status() < 300
      ),
      dialog.getByRole('button', { name: /save/i }).click(),
    ])

    await expect(dialog).toBeHidden()

    await expect(page.getByText('Risk Review Saved')).toBeVisible()
    await expect(page.getByText('Transaction has been marked')).toBeVisible()

    const badge = reviewedRow.getByTestId('risk-badge')
    await expect(badge).toHaveText(/Reviewed/i)
    await expect(badge).toHaveClass(/text-red-600/)
  })
})
