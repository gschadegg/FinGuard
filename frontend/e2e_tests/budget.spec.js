// @ts-nocheck
import { test, expect } from '@playwright/test'

import { render, screen } from '@testing-library/react'
import React from 'react'

const isCatsUrl = (u) => /\/api\/budgets\/categories(?:[/?]|$)/.test(u)

test.describe('Budget', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('loads budget page', async ({ page, baseURL }) => {
    await page.getByRole('button', { name: 'Toggle Sidebar' }).click()
    await expect(page.getByRole('link', { name: 'Budget' })).toBeVisible()
    await page.getByRole('link', { name: 'Budget' }).click()

    await expect(page.getByRole('heading', { name: 'Budget' })).toBeVisible()
    await expect(page.getByText('Total Budgeted')).toBeVisible()
    await expect(page.getByText('Month')).toBeVisible()
  })

  test('creates category', async ({ page }) => {
    await page.goto('/budget')

    await page.getByRole('button', { name: 'Add Category' }).click()
    const dialog = page.getByRole('dialog')

    await page.getByRole('combobox').click()
    await page.getByRole('option', { name: 'Expenses' }).click()
    await page.getByRole('textbox', { name: 'Category Name' }).fill('Internet')
    await page.getByRole('spinbutton', { name: 'Assigned Amount' }).fill('120')

    await Promise.all([
      page.waitForResponse(
        (res) =>
          isCatsUrl(res.url()) &&
          (res.request().method() === 'POST' || res.request().method() === 'GET') &&
          res.status() >= 200 &&
          res.status() < 300
      ),
      dialog.getByRole('button', { name: 'Save' }).click(),
    ])

    await expect(dialog).toBeHidden()

    const card = page.locator('[data-testid^="category-card-"][data-name="Internet"]').first()
    await expect(card).toBeVisible()
    await expect(card).toContainText('$120')
  })

  test('update category amount', async ({ page }) => {
    await page.goto('/budget')

    await page.getByRole('button', { name: 'Add Category' }).click()
    const dialog = page.getByRole('dialog')

    await page.getByRole('combobox').click()
    await page.getByRole('option', { name: 'Expenses' }).click()
    await page.getByRole('textbox', { name: 'Category Name' }).fill('Internet')
    await page.getByRole('spinbutton', { name: 'Assigned Amount' }).fill('120')

    await Promise.all([
      page.waitForResponse(
        (res) =>
          isCatsUrl(res.url()) &&
          (res.request().method() === 'POST' || res.request().method() === 'GET') &&
          res.status() >= 200 &&
          res.status() < 300
      ),
      dialog.getByRole('button', { name: 'Save' }).click(),
    ])

    const card = page.locator('[data-testid^="category-card-"][data-name="Internet"]').first()
    await expect(card).toBeVisible()

    await card.getByRole('button', { name: /open menu/i }).click()
    await page.getByRole('menuitem', { name: 'Edit' }).click()

    const dialog2 = page.getByRole('dialog')
    const amt = dialog2.getByRole('spinbutton', { name: 'Assigned Amount' })
    await amt.fill('300')

    await Promise.all([
      page.waitForResponse(
        (res) =>
          isCatsUrl(res.url()) &&
          (res.request().method() === 'PATCH' ||
            res.request().method() === 'PUT' ||
            res.request().method() === 'GET') &&
          res.status() >= 200 &&
          res.status() < 300
      ),
      dialog.getByRole('button', { name: 'Save' }).click(),
    ])

    await expect(dialog).toBeHidden()

    await expect(card).toContainText('$300')
    await expect(card).not.toContainText('$120')
  })

  test('delete category removes its card', async ({ page }) => {
    await page.goto('/budget')

    await page.getByRole('button', { name: 'Add Category' }).click()
    const addDialog = page.getByRole('dialog')

    await addDialog.getByRole('combobox').click()

    await page.getByRole('option', { name: 'Expenses' }).click()
    await addDialog.getByRole('textbox', { name: 'Category Name' }).fill('DeleteCategory')
    await addDialog.getByRole('spinbutton', { name: 'Assigned Amount' }).fill('40')

    await Promise.all([
      page.waitForResponse(
        (res) =>
          isCatsUrl(res.url()) &&
          (res.request().method() === 'POST' || res.request().method() === 'GET') &&
          res.status() >= 200 &&
          res.status() < 300
      ),
      addDialog.getByRole('button', { name: 'Save' }).click(),
    ])
    await expect(addDialog).toBeHidden()

    const card = page.locator('[data-testid^="category-card-"][data-name="DeleteCategory"]').first()
    await expect(card).toBeVisible()

    await card.getByRole('button', { name: /open menu/i }).click()
    await page.getByRole('menuitem', { name: /delete/i }).click()

    const deleteDialog = page.getByRole('dialog')
    await Promise.all([
      page.waitForResponse(
        (res) =>
          isCatsUrl(res.url()) &&
          (res.request().method() === 'DELETE' || res.request().method() === 'GET') &&
          res.status() >= 200 &&
          res.status() < 300
      ),
      deleteDialog.getByRole('button', { name: /^delete$/i }).click(),
    ])
    await expect(deleteDialog).toBeHidden()

    await expect(card).toHaveCount(0)
  })
})
