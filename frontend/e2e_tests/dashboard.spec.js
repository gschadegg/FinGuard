import { test, expect } from '@playwright/test'

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  // TC-FLOW-DASH-001 Base scenario, dashboard loads with widgets
  test('dashboard loads and renders widgets', async ({ page }) => {
    await expect(page.getByTestId('dashboard-page')).toBeVisible()
    await expect(page.getByTestId('dashboard-page').getByText('Dashboard')).toBeVisible()

    await expect(page.getByTestId('total-balance-amount')).toHaveText('$1,490')

    await expect(page.getByTestId('high-risk-count')).toHaveText('6')

    await expect(page.getByTestId('budget-spent')).toHaveText('$304')
    await expect(page.getByTestId('budget-available')).toHaveText('$326')

    await expect(page.getByTestId('spending-categories-card')).toBeVisible()
    await expect(page.getByTestId('accounts-card')).toBeVisible()
  })

  // TC-FLOW-DASH-002  skeleton loads when waiting for data
  test('skeleton is shown while dashboard data is loading', async ({ page }) => {
    await page.goto('/?__delay=2000')

    await expect(page.getByTestId('dashboard-skeleton')).toBeVisible()

    await expect(page.getByTestId('dashboard-page')).toBeVisible()
    await expect(page.getByTestId('dashboard-skeleton')).toHaveCount(0)
  })

  // TC-FLOW-DASH-003 'view transaction' button nav to correct page
  test('view transactions btn navigates with high_risk_only=true', async ({ page }) => {
    await page.getByRole('button', { name: /View Transactions/i }).click()

    await expect(page).toHaveURL(/\/accounts\?high_risk_only=true/)
  })

  // TC-FLOW-DASH-004  high risk widget shows count
  test('high risk count is rendered with count', async ({ page }) => {
    await expect(page.getByTestId('high-risk-count')).toHaveText('6')
  })

  // TC-FLOW-DASH-005 budget widget shows values and percentage
  test('budget widget shows correct values and percentage spent', async ({ page }) => {
    await expect(page.getByTestId('budget-spent')).toHaveText('$304')
    await expect(page.getByTestId('budget-available')).toHaveText('$326')

    await expect(page.getByText(/48% of budget used/i)).toBeVisible()
  })

  // TC-FLOW-DASH-006 spending categories lists
  test('spending categories list rows with percentages and values', async ({ page }) => {
    const card = page.getByTestId('spending-categories-card')
    await expect(card).toBeVisible()

    await expect(card.getByText('Rent')).toBeVisible()
    await expect(card.getByText('$202')).toBeVisible()
    await expect(card.getByText(/66%/)).toBeVisible()

    await expect(card.getByText('Going Out')).toBeVisible()
    await expect(card.getByText('$25')).toBeVisible()
    await expect(card.getByText(/8%/)).toBeVisible()

    await expect(card.getByText('Internet')).toBeVisible()
    await expect(card.getByText('Other')).toBeVisible()
  })

  // TC-FLOW-DASH-007 account widget displays list of account cards
  test('account widget list accounts owned', async ({ page }) => {
    const rows = page.getByTestId('account-row')
    await expect(rows).toHaveCount(9)

    const first = rows.first()
    await expect(first).toContainText('Bank of America')
    await expect(first).toContainText('Plaid Checking')
    await expect(first).toContainText('••••0000')
    await expect(first).toContainText('$110')
    await expect(first).toContainText('$100')
  })
})
