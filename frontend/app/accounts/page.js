'use client'
import React, { useState, useMemo, useCallback } from 'react'
import { useNotify } from '@/components/notification/NotificationProvider'
import { columns } from '@/components/transaction-table/columns'
import { TransactionDataTable } from '@/components/transaction-table'
import { GET_TRANSACTIONS_BY_USER_ID } from '@/lib/api_urls'
import PageLayout from '@/components/layouts/page-layout'
import RollupCardRow from '@/components/rollup-cards'
import { useAuth } from '@/components/auth/AuthProvider'
import useCursor from '@/hooks/useCursor'
import { RotateCw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { DollarSign, ShieldAlert, Loader } from 'lucide-react'

const STALE_DATA = 5 * 60 * 1000

export default function AccountsPage() {
  const notify = useNotify()
  const { user, makeAuthRequest, isLoading } = useAuth()
  const userId = user?.id

  const [start, _setStart] = useState(null)
  const [end, _setEnd] = useState(null)
  const [selected, _setSelected] = useState(true)
  const [refreshTrigger, setRefreshTrigger] = useState(0)

  const fetchTransactions = useCallback(
    async ({ limit, cursor, userId, start, end, selected = true }) => {
      if (!userId) return { rows: [], nextCursor: null, hasMore: false }

      const params = new URLSearchParams()
      params.set('limit', String(limit))
      params.set('selected', String(selected))
      if (cursor) params.set('cursor', cursor)

      // date format should be YYYY-MM-DD, save for filtering if added later
      if (start) params.set('start', start)
      if (end) params.set('end', end)

      const timestampKey = userId ? `last_transaction_fetch_${userId}` : null
      const last = timestampKey ? Number(localStorage.getItem(timestampKey) || 0) : 0
      const shouldRefresh = Date.now() - last > STALE_DATA

      if (shouldRefresh) params.set('refresh', true)
      try {
        const res = await makeAuthRequest(GET_TRANSACTIONS_BY_USER_ID(params))
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
    [makeAuthRequest, notify]
  )

  const staticArgs = useMemo(
    () => ({ userId, start, end, selected, refreshTrigger }),
    [userId, start, end, selected, refreshTrigger]
  )

  const cardData = useMemo(() => {
    return [
      {
        title: 'Total Balance',
        detail: '$1,250.00',
        icon: DollarSign,
      },
      {
        title: 'Pending Transations',
        detail: '-$1,250.00',
        icon: Loader,
      },
      {
        title: 'Potential Risks',
        detail: '6',
        icon: ShieldAlert,
      },
    ]
  }, [])

  const pager = useCursor(fetchTransactions, 50, staticArgs)

  const handleManualRefresh = useCallback(() => {
    if (!userId) return
    localStorage.setItem(`last_transaction_fetch_${userId}`, '0')
    setRefreshTrigger((n) => n + 1)
  }, [userId])

  if (isLoading) return null

  return (
    <PageLayout pageTitle="All Accounts">
      <RollupCardRow cardData={cardData} />
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
