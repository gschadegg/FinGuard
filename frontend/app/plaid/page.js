'use client'
import { useState, useEffect, useCallback } from 'react'
import { usePlaidLink } from 'react-plaid-link'
import { EXCHANGE_PLAID_TOKEN_URL, CREATE_PLAID_TOKEN_URL } from '@/lib/API_URLS/PROXY'
export default function PlaidTest() {
  const [linkToken, setLinkToken] = useState(null)

  useEffect(() => {
    ;(async () => {
      const r = await fetch(CREATE_PLAID_TOKEN_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: '1' }),
      })
      const data = await r.json()
      // data.link_token will be the link-sandbox- token, needs to be exchanged for creating access tokens
      setLinkToken(data.link_token)
    })()
  }, [])

  const onSuccess = useCallback(async (public_token, metadata) => {
    const selected_accounts = (metadata?.accounts ?? []).map((a) => ({
      id: a.id, // plaid account_id
      name: a.name,
      mask: a.mask,
    }))

    await fetch(EXCHANGE_PLAID_TOKEN_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        public_token,
        selected_accounts,
      }),
    })
    alert('Exchanged access_token created')
  }, [])

  const { open, ready } = usePlaidLink({
    token: linkToken ?? '',
    onSuccess,
    onExit: (err) => err && console.error(err),
  })

  return (
    <button disabled={!ready || !linkToken} onClick={() => open()}>
      Connect bank
    </button>
  )
}
