'use client'
import { useState, useEffect, useCallback } from 'react'
import { usePlaidLink } from 'react-plaid-link'
import { EXCHANGE_PLAID_TOKEN_URL, CREATE_PLAID_TOKEN_URL } from '@/lib/api_urls'
import { Button } from '@/components/ui/button'
import { useNotify } from '@/components/notification/NotificationProvider'

export default function PlaidTest() {
  const notify = useNotify()
  const [linkToken, setLinkToken] = useState(null)
  const [plaidItemId, setPlaidItemId] = useState(
    () => localStorage.getItem('plaid_item_id') || null
  )
  const [unselectOthers, setUnselectOthers] = useState(false)
  const userId = 1

  const requestLinkToken = useCallback(async (mode = 'create', itemId = null) => {
    const body =
      mode === 'update'
        ? { user_id: userId, mode: 'update', plaid_item_id: itemId }
        : { user_id: userId, mode: 'create' }

    const r = await fetch(CREATE_PLAID_TOKEN_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    const data = await r.json()
    setLinkToken(data.link_token)
  }, [])

  useEffect(() => {
    requestLinkToken('create', null)
  }, [requestLinkToken])

  const onSuccess = useCallback(
    async (public_token, metadata) => {
      const institution = metadata.institution
        ? { id: metadata.institution.institution_id, name: metadata.institution.name }
        : null

      const selected_accounts = (metadata?.accounts ?? []).map((a) => ({
        id: a.id,
        name: a.name,
        mask: a.mask,
        type: a.type,
        subtype: a.subtype,
      }))

      const r = await fetch(EXCHANGE_PLAID_TOKEN_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          public_token,
          user_id: userId,
          selected_accounts,
          institution,
          unselect_others: unselectOthers,
        }),
      })
      const data = await r.json()

      if (data?.plaid_item_id) {
        setPlaidItemId(data.plaid_item_id)
        localStorage.setItem('plaid_item_id', data.plaid_item_id)
      }

      alert(`${data?.mode === 'updated' ? 'Reconnected/updated' : 'Created'} OK`)
      setLinkToken(null)
    },
    [unselectOthers]
  )

  const { open, ready } = usePlaidLink({
    token: linkToken ?? '',
    onSuccess,
    onExit: (err) => {
      if (err) console.error(err)
      setLinkToken(null)
    },
  })

  return (
    <div style={{ display: 'grid', gap: 12 }}>
      <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
        <Button onClick={() => requestLinkToken('create', null)}>New connection (create)</Button>

        <Button
          onClick={() => requestLinkToken('update', plaidItemId)}
          disabled={!plaidItemId}
          title={!plaidItemId ? 'Connect once first to get a plaid_item_id' : ''}
        >
          Reconnect / add accounts (update)
        </Button>

        <label style={{ marginLeft: 12 }}>
          <input
            type="checkbox"
            checked={unselectOthers}
            onChange={(e) => setUnselectOthers(e.target.checked)}
          />{' '}
          unselect others
        </label>
      </div>

      <Button disabled={!ready || !linkToken} onClick={() => open()}>
        Open Plaid Link
      </Button>

      {plaidItemId && (
        <small>
          Saved plaid_item_id: <code>{plaidItemId}</code>
        </small>
      )}

      <p className="text-muted-foreground">This is /accounts/all-transactions.</p>
      <button
        className="px-3 py-2 rounded bg-primary text-primary-foreground"
        onClick={() => notify({ type: 'success', title: 'Saved', message: 'Account linked.' })}
      >
        Success
      </button>

      <button
        className="px-3 py-2 rounded bg-destructive text-destructive-foreground"
        onClick={() => notify({ type: 'error', title: 'Error', message: 'Something went wrong.' })}
      >
        Error
      </button>

      <button
        className="px-3 py-2 rounded bg-secondary text-secondary-foreground"
        onClick={() =>
          notify({ type: 'info', title: 'Information', message: 'Some general info.' })
        }
      >
        Info
      </button>
      <button
        className="px-3 py-2 rounded bg-secondary text-secondary-foreground"
        onClick={() => notify({ type: 'info', title: null, message: null })}
      >
        test
      </button>
    </div>
  )
}
