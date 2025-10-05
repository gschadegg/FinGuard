'use client'
import React, { useCallback, useEffect, useState } from 'react'
import { usePlaidLink } from 'react-plaid-link'
import { Button } from '@/components/ui/button'
import { useNotify } from '@/components/notification/NotificationProvider'
import { Plus, Loader2 } from 'lucide-react'
import { EXCHANGE_PLAID_TOKEN_URL, CREATE_PLAID_TOKEN_URL } from '@/lib/api_urls'
import { useUserContext } from '../user-data'

export function CreateLinkAccountButton({}) {
  const notify = useNotify()
  const { userId, refreshAccounts } = useUserContext()
  const [linkToken, setLinkToken] = useState(null)
  const [autoOpen, setAutoOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const { open, ready } = usePlaidLink({
    token: linkToken ?? '',
    onSuccess: async (public_token, metadata) => {
      try {
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

        const res = await fetch(EXCHANGE_PLAID_TOKEN_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            public_token,
            user_id: userId,
            selected_accounts,
            institution,
            unselect_others: false,
          }),
        })

        if (!res.ok)
          notify({
            type: 'error',
            title: 'Link Error',
            message: 'Could not finish linking.',
          })
        const data = await res.json()

        // Instead want to sync connection item transactions?
        // data.connection_item_id  sync by the account

        notify({ type: 'success', title: 'Connected', message: 'New connection created.' })
      } catch (_e) {
        notify({ type: 'error', title: 'Link Error', message: 'Could not finish linking.' })
      } finally {
        setLinkToken(null)
        setAutoOpen(false)
        setIsLoading(false)

        refreshAccounts()
      }
    },
    onExit: () => {
      setLinkToken(null)
      setAutoOpen(false)
      setIsLoading(false)
    },
  })

  const handleClick = useCallback(async () => {
    try {
      setIsLoading(true)
      const res = await fetch(CREATE_PLAID_TOKEN_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, mode: 'create' }),
      })
      if (!res.ok)
        notify({ type: 'error', title: 'Token Error', message: 'Unable to start Plaid Link.' })
      const data = await res.json()
      setLinkToken(data.link_token)
      setAutoOpen(true)
    } catch (_e) {
      notify({ type: 'error', title: 'Token Error', message: 'Unable to start Plaid Link.' })
      setIsLoading(false)
    }
  }, [userId, notify])

  useEffect(() => {
    if (autoOpen && linkToken && ready) open()
  }, [autoOpen, linkToken, ready, open])

  return (
    <Button
      onClick={handleClick}
      disabled={isLoading}
      size="sm"
      variant="secondary"
      className="w-full bg-secondary/90 text-secondary-foreground hover:bg-primary hover:text-primary-foreground border border-border/90"
    >
      {isLoading ? (
        <span className="inline-flex items-center">
          <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
          <span>Linking...</span>
        </span>
      ) : (
        <span className="inline-flex items-center">
          <Plus className="mr-2 size-4" />
          Add Account
        </span>
      )}
    </Button>
  )
}
