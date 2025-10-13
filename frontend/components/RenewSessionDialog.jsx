'use client'

import { useAuth } from '@/components/auth/AuthProvider'
import { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'

export default function SessionRenewalDialog() {
  const { showSessionPrompt, setShowSessionPrompt, refreshToken, logout } = useAuth()
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState(null)

  const onStay = async () => {
    setBusy(true)
    setErr(null)
    try {
      await refreshToken()
    } catch (_e) {
      setErr('Could not refresh session')
    } finally {
      setBusy(false)
    }
  }

  return (
    <Dialog open={showSessionPrompt} onOpenChange={(o) => setShowSessionPrompt(o)}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Session expiring soon</DialogTitle>
          <DialogDescription>
            Your session will expire in 2 minutes. Stay logged in?
          </DialogDescription>
        </DialogHeader>
        {err && <p className="text-sm text-destructive">{err}</p>}
        <div className="mt-4 flex gap-2 justify-end">
          <Button variant="secondary" onClick={logout} disabled={busy}>
            Log out
          </Button>
          <Button onClick={onStay} disabled={busy}>
            {busy ? 'Refreshing…' : 'Stay logged in'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
