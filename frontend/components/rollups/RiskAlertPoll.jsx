'use client'

import { useRollups } from './RollupProvider'
import { ShieldAlert } from 'lucide-react'

export default function HeaderRiskAlert() {
  const { risks } = useRollups()

  if (!risks?.pending_high) return null

  return (
    <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-50">
      <div className="inline-flex items-center gap-2 rounded-md border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700 shadow-md">
        <ShieldAlert className="h-4 w-4 shrink-0" />
        <span>
          {risks.pending_high} potential high-risk{' '}
          {risks.pending_high === 1 ? ' transaction ' : ' transactions '} need review
        </span>
      </div>
    </div>
  )
}
