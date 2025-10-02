'use client'
import * as React from 'react'
import { useNotify } from '@/components/notification/NotificationProvider'
export default function AccountsPage() {
  const notify = useNotify()
  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold tracking-tight">Accounts page</h1>
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
