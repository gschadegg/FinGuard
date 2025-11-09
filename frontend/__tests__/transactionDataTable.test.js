import React from 'react'
import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { TestProviders } from './utils/renderProviders'
import { TransactionDataTable } from './../components/transaction-table'
import { columns } from './../components/transaction-table/columns'

// mocking pager object
function makePager(overrides = {}) {
  return {
    pageIndex: 0,
    pageSize: 50,
    rows: [],
    isLoading: false,
    error: null,
    hasMore: false,
    pageCount: 1,
    setPageIndex: jest.fn(),
    setPageSize: jest.fn(),
    ...overrides,
  }
}

function renderWithProviders(ui) {
  return render(ui, { wrapper: ({ children }) => <TestProviders>{children}</TestProviders> })
}

jest.mock('./../components/auth/AuthProvider', () => ({
  useAuth: () => ({
    makeAuthRequest: jest.fn().mockResolvedValue({
      ok: true,
      categories: [],
      total_budgeted: 0,
    }),
  }),
}))

jest.mock('./../components/rollups/RollupProvider', () => {
  return {
    RollupsProvider: ({ children }) => children,
    useRollups: () => ({
      risks: {
        pending_total: 0,
        pending_high: 0,
        pending_medium: 0,
        pending_low: 0,
      },
      byAccount: {},
      refresh: jest.fn(),
    }),
  }
})

//TC-TABLE-DISPLAY-001: BASE scenario, table renders rows with data
test('Table renders with data rows', () => {
  const rows = [
    {
      id: 'a1',
      merchant_name: 'Coffee Shop',
      name: 'Coffee',
      date: '2025-08-01',
      category: 'unassigned',
      category_id: null,
      amount: -3.5,
      pending: 0,
      is_fraud_suspected: false,
      fraud_score: null,
    },
    {
      id: 'a2',
      merchant_name: 'Market',
      name: 'Groceries',
      date: '2025-08-02',
      category: 'groceries',
      category_id: 2,
      amount: -45.23,
      pending: 0,
      is_fraud_suspected: false,
      fraud_score: null,
    },
  ]
  const pager = makePager({ rows, isLoading: false, hasMore: true, pageCount: 2 })
  renderWithProviders(<TransactionDataTable columns={columns} pager={pager} />)

  expect(screen.getByText('Payee')).toBeInTheDocument()
  expect(screen.getByText('Name')).toBeInTheDocument()
  expect(screen.getByText('Date')).toBeInTheDocument()
  expect(screen.getByText('Amount')).toBeInTheDocument()

  expect(screen.getByText('Coffee Shop')).toBeInTheDocument()
  expect(screen.getByText('Coffee')).toBeInTheDocument()
  expect(screen.getByText('08/01/2025')).toBeInTheDocument()
})

//TC-TABLE-DISPLAY-002: skeleton is rendered while loading
test('Skeleton shows while loading', () => {
  const pager = makePager({ isLoading: true })
  renderWithProviders(<TransactionDataTable columns={columns} pager={pager} />)

  expect(screen.getByTestId('table-skeleton')).toBeInTheDocument()
  expect(screen.queryByText(/No results\./i)).not.toBeInTheDocument()
})

//TC-TABLE-DISPLAY-003: When no data, 'No Results' message Renders
test('Empty state when no data', () => {
  const pager = makePager({ rows: [], isLoading: false })
  renderWithProviders(<TransactionDataTable columns={columns} pager={pager} />)

  expect(screen.getByText(/No results\./i)).toBeInTheDocument()
})

//TC-TABLE-DISPLAY-004: Clicking Next in pagination calls to set page index to ++1
test("Change page index on 'Next' click", async () => {
  const user = userEvent.setup()
  const pager = makePager({ rows: [{ id: 'id1', name: 'Row' }], hasMore: true, pageCount: 2 })
  renderWithProviders(<TransactionDataTable columns={columns} pager={pager} />)

  const nextBtn =
    screen.queryByRole('button', { name: /go to next page/i }) ||
    screen.getByRole('button', { name: /next/i })

  expect(nextBtn).toBeEnabled()
  await user.click(nextBtn)

  expect(pager.setPageIndex).toHaveBeenCalledWith(1)
})
