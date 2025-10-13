import { useEffect, useRef } from 'react'
import { getExp } from '@/lib/utils'

export function useSessionTimers(token, { leadSeconds = 120, onPrompt, onExpire }) {
  const promptRef = useRef(null)
  const expireRef = useRef(null)

  useEffect(() => {
    if (promptRef.current) {
      clearTimeout(promptRef.current)
      promptRef.current = null
    }
    if (expireRef.current) {
      clearTimeout(expireRef.current)
      expireRef.current = null
    }

    if (!token) return
    const exp = getExp(token)
    if (!exp) return

    const now = Date.now()
    const expMs = exp * 1000
    const promptAt = expMs - leadSeconds * 1000

    const promptDelay = Math.max(0, promptAt - now)
    const expireDelay = Math.max(0, expMs - now)

    promptRef.current = setTimeout(() => onPrompt?.(), promptDelay)
    expireRef.current = setTimeout(() => onExpire?.(), expireDelay)

    return () => {
      if (promptRef.current) clearTimeout(promptRef.current)
      if (expireRef.current) clearTimeout(expireRef.current)
    }

    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, leadSeconds])
}
