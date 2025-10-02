'use client'

import { useEffect, useRef } from 'react'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { X, CheckCircle2, AlertCircle, InfoIcon } from 'lucide-react'
import { useNotifications } from './NotificationProvider'
import { cn } from '@/lib/utils'

export function NotificationCard({ notice, onClose }) {
  const Icon =
    notice.type === 'error' ? AlertCircle : notice.type === 'success' ? CheckCircle2 : InfoIcon
  const variant = notice.type === 'error' ? 'destructive' : 'default'

  const timerRef = useRef(null)

  useEffect(() => {
    timerRef.current = setTimeout(onClose, notice.duration || 4000)
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current)
    }
  }, [notice.duration, onClose])

  const pause = () => {
    if (timerRef.current) {
      clearTimeout(timerRef.current)
      timerRef.current = null
    }
  }

  const resume = () => {
    if (!timerRef.current) {
      timerRef.current = setTimeout(onClose, 1200)
    }
  }

  if (!notice.message && !notice.title) return
  return (
    <div
      onMouseEnter={pause}
      onMouseLeave={resume}
      className="pointer-events-auto animate-in slide-in-from-bottom-5 fade-in-0"
    >
      <Alert variant={variant} className="relative pr-9 shadow-lg border" role="status">
        <Icon
          className={cn(
            'h-4 w-4',
            notice.type === 'success' && '!text-emerald-600 dark:!text-emerald-400'
          )}
        />
        {notice.title ? (
          <AlertTitle
            className={
              notice.type === 'success' ? 'text-emerald-700 dark:text-emerald-300' : undefined
            }
          >
            {notice.title}
          </AlertTitle>
        ) : null}
        <AlertDescription>{notice.message}</AlertDescription>

        <button
          aria-label="Close notification"
          onClick={onClose}
          className="absolute right-2 top-2 inline-flex h-6 w-6 items-center justify-center rounded-md opacity-70 hover:opacity-100"
        >
          <X className="h-4 w-4" />
        </button>
      </Alert>
    </div>
  )
}

export default function NotificationStack() {
  const { notices, remove } = useNotifications()

  return (
    <div className="pointer-events-none fixed bottom-4 right-4 z-50 flex w-96 max-w-[90vw] flex-col gap-3">
      {notices.map((notice) => (
        <NotificationCard key={notice.id} notice={notice} onClose={() => remove(notice.id)} />
      ))}
    </div>
  )
}
