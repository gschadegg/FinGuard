'use client'
import React, { useState, useMemo, useCallback } from 'react'
import { useNotify } from '@/components/notification/NotificationProvider'
import { columns } from '@/components/transaction-table/columns'
import { TransactionDataTable } from '@/components/transaction-table'
import { GET_TRANSACTIONS_BY_ACCOUNT_ID } from '@/lib/api_urls'
import PageLayout from '@/components/layouts/page-layout'
import RollupCardRow from '@/components/rollup-cards'
import useCursor from '@/hooks/useCursor'
import { useParams } from 'next/navigation'
import { useUserContext } from '@/components/user-data'
import { useAuth } from '@/components/auth/AuthProvider'
import { RotateCw } from 'lucide-react'
import { Button } from '@/components/ui/button'

const STALE_DATA = 5 * 60 * 1000

export default function AccountsIDPage() {
  const notify = useNotify()
  const { makeAuthRequest, user } = useAuth()

  const { accounts } = useUserContext()
  const params = useParams()
  const id = params.id

  const [accountID, _setAccountID] = useState(Number(id))
  const [start, _setStart] = useState(null)
  const [end, _setEnd] = useState(null)
  const [selected, _setSelected] = useState(true)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  const fetchTransactions = useCallback(
    async ({ limit, cursor, accountID, start, end, selected = true }) => {
      const params = new URLSearchParams()
      params.set('account_id', String(accountID))
      params.set('limit', String(limit))
      params.set('selected', String(selected))
      if (cursor) params.set('cursor', cursor)

      // date format should be YYYY-MM-DD, save for filtering if added later
      if (start) params.set('start', start)
      if (end) params.set('end', end)

      const userId = user?.id
      const timestampKey = userId ? `last_transaction_fetch_${userId}_${accountID}` : null
      const last = timestampKey ? Number(localStorage.getItem(timestampKey) || 0) : 0
      const shouldRefresh = Date.now() - last > STALE_DATA

      if (shouldRefresh) params.set('refresh', true)

      try {
        const res = await makeAuthRequest(GET_TRANSACTIONS_BY_ACCOUNT_ID(accountID, params))

        if (timestampKey) localStorage.setItem(timestampKey, String(Date.now()))
        return {
          rows: res.items ? res.items : [],
          nextCursor: res.next_cursor ?? null,
          hasMore: res.has_more,
        }
      } catch {
        notify({
          type: 'error',
          title: 'Account Error',
          message: 'Experienced issues fetching transactions, please try again.',
        })
        return {
          rows: [],
          nextCursor: null,
          hasMore: false,
        }
      }
    },
    [makeAuthRequest, user?.id, notify]
  )

  const staticArgs = useMemo(
    () => ({ accountID, start, end, selected, refreshTrigger }),
    [accountID, start, end, selected, refreshTrigger]
  )

  const pager = useCursor(fetchTransactions, 50, staticArgs)

  const handleManualRefresh = useCallback(() => {
    if (!user?.id) return
    localStorage.setItem(`last_transaction_fetch_${user?.id}_${accountID}`, '0')
    setRefreshTrigger((n) => n + 1)
  }, [user?.id, accountID])

  const account = useMemo(
    () => accounts?.find((a) => String(a.id) === String(accountID)),
    [accounts, accountID]
  )

  const pageTitle = account
    ? `${account.institution_name} - ${account.name}`
    : accounts
      ? 'Account not found'
      : 'Loading…'

  return (
    <PageLayout pageTitle={pageTitle}>
      <RollupCardRow />
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-xl text-gray-500 font-semibold tracking-tight mb-4">Transactions</h2>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className="cursor-pointer inline-flex items-center gap-2"
          onClick={handleManualRefresh}
          title="Refresh transactions"
        >
          <RotateCw className="h-4 w-4" aria-hidden="true" />
          Refresh
        </Button>
      </div>
      <TransactionDataTable columns={columns} pager={pager} />
    </PageLayout>
  )
}
