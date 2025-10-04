'use client'
import React, { useEffect, useState, useMemo, useCallback } from 'react'
import { useNotify } from '@/components/notification/NotificationProvider'
import { columns } from '@/components/transaction-table/columns'
import { TransactionDataTable } from '@/components/transaction-table'
import { GET_TRANSACTIONS_BY_USER_ID } from '@/lib/api_urls'
import PageLayout from '@/components/layouts/page-layout'
import RollupCardRow from '@/components/rollup-cards'
import useCursor from '@/hooks/useCursor'

export default function AccountsPage() {
  const notify = useNotify()
  const [userId, setUserId] = useState(1)
  const [start, setStart] = useState(null)
  const [end, setEnd] = useState(null)
  const [selected, setSelected] = useState(true)
  const [refresh, setRefresh] = useState(false)

  //   useEffect(() => {
  //     const ac = new AbortController()

  //     async function load() {
  //       try {
  //         const res = await fetch(GET_TRANSACTIONS_BY_USER_ID({ user_id: 1 }), { signal: ac.signal })
  //         if (!res.ok)
  //           notify({
  //             type: 'error',
  //             title: 'Error',
  //             message: 'Unable to fetch updated transaction data.',
  //           })
  //         const body = await res.json()
  //         const data = body.items

  //         setRows(Array.isArray(data) ? data : [])
  //       } catch (e) {
  //         if (e.name !== 'AbortError') notify({ type: 'error', title: e.name, message: e.message })
  //       }
  //     }

  //     load()
  //     return () => ac.abort()
  //   }, [])
  const fetchTransactions = useCallback(
    async ({ limit, cursor, userId = 1, start, end, selected = true, refresh = false }) => {
      const params = new URLSearchParams()
      params.set('user_id', String(userId))
      params.set('limit', String(limit))
      params.set('selected', String(selected))
      if (cursor) params.set('cursor', cursor)

      // date format should be YYYY-MM-DD, save for filtering if added later
      if (start) params.set('start', start)
      if (end) params.set('end', end)
      if (refresh) params.set('refresh', refresh)

      const res = await fetch(GET_TRANSACTIONS_BY_USER_ID(params))
      if (!res.ok)
        notify({
          type: 'error',
          title: 'Error',
          message: 'Unable to fetch transaction data.',
        })
      const data = await res.json() // return structure should be { items, next_cursor, has_more }

      return {
        rows: data.items ? data.items : [],
        nextCursor: data.next_cursor ?? null,
        hasMore: data.has_more,
      }
    },
    [notify]
  )

  const staticArgs = useMemo(
    () => ({ userId, start, end, selected, refresh }),
    [userId, start, end, selected, refresh]
  )

  const pager = useCursor(fetchTransactions, 50, staticArgs)

  return (
    <PageLayout pageTitle="All Accounts">
      <RollupCardRow />
      <h2 className="text-xl text-gray-500 font-semibold tracking-tight mb-4">Transactions</h2>
      <TransactionDataTable columns={columns} pager={pager} />
    </PageLayout>
  )
}
