'use client'

import { useEffect, useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { ShieldCheck, ShieldAlert } from 'lucide-react'
import clsx from 'clsx'

export default function RiskReviewModal({
  open,
  onOpenChange,
  riskLevel = null,
  institution = null,
  defaultAction = 'not_fraud',
  onSubmit,
}) {
  const [status, setStatus] = useState(defaultAction)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (open) {
      setStatus(defaultAction)
      setSaving(false)
    }
  }, [open, defaultAction])

  const riskWord = riskLevel || 'unknown'
  const isFraudStatus = status === 'fraud'

  async function handleSave(e) {
    e.preventDefault()
    setSaving(true)
    try {
      if (onSubmit) await onSubmit(status)
      onOpenChange(false)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[520px]">
        <DialogHeader>
          <DialogTitle>Risk Review</DialogTitle>
          <DialogDescription>
            {riskLevel ? (
              <>
                This transaction has been marked as a <b className="capitalize">{riskWord}</b>{' '}
                fraudulent risk. If this transaction is unfamiliar, you should review it&apos;s
                legitimacy with{' '}
                {institution ? (
                  <b className="capitalize">{institution}</b>
                ) : (
                  ' the financial institution'
                )}
                .
              </>
            ) : (
              <>This transaction&apos;s risk is still processing. </>
            )}
            {institution ? (
              <>
                You may want to verify with{' '}
                {institution ? <b>{institution}</b> : ' the financial institution'}.
              </>
            ) : null}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSave} className="space-y-4">
          <div
            role="button"
            onClick={() => setStatus('not_fraud')}
            className={clsx(
              'flex items-center gap-3 rounded-xl border p-3 cursor-pointer mt-2',
              status === 'not_fraud' ? 'border-primary ring-1 ring-primary/30' : 'border-gray-300'
            )}
          >
            <ShieldCheck className="h-5 w-5" />
            <div>
              <div className="font-medium">Mark as Safe</div>
              <div className="text-sm text-muted-foreground">Transaction is not fraudulent</div>
            </div>
          </div>

          <div
            role="button"
            onClick={() => setStatus('fraud')}
            className={clsx(
              'flex items-center gap-3 rounded-xl border p-3 cursor-pointer',
              isFraudStatus ? 'border-primary ring-1 ring-primary/30' : 'border-gray-300'
            )}
          >
            <ShieldAlert className="h-5 w-5" />
            <div>
              <div className="font-medium">Mark as Fraudulent</div>
              <div className="text-sm text-muted-foreground">
                Transaction should be reviewed by financial institution
              </div>
            </div>
          </div>

          <DialogFooter className="gap-2 mt-8">
            <Button
              type="button"
              variant="secondary"
              className="cursor-pointer"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={saving} className="cursor-pointer">
              {saving ? 'Saving…' : 'Save'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
