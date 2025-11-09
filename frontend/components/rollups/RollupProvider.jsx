'use client'

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { useAuth } from '@/components/auth/AuthProvider'

import { GET_RISKS_ROLLUP } from '@/lib/api_urls'

const RollupsContext = createContext(null)

export function RollupsProvider({ children, pollInMsecs = 60000 }) {
  const { makeAuthRequest } = useAuth()
  const [risks, setRisks] = useState({
    pending_total: 0,
    pending_high: 0,
    pending_medium: 0,
    pending_low: 0,
  })

  const [byAccount, setByAccount] = useState({})

  const refresh = useCallback(async () => {
    try {
      const res = await makeAuthRequest(GET_RISKS_ROLLUP)
      if (res?.risks) setRisks(res.risks)
      setByAccount(res?.by_account || {})
    } catch {}
  }, [makeAuthRequest])

  useEffect(() => {
    refresh()
    const id = setInterval(refresh, pollInMsecs)
    return () => clearInterval(id)
  }, [refresh, pollInMsecs])

  const value = useMemo(() => ({ risks, byAccount, refresh }), [risks, byAccount, refresh])

  return <RollupsContext.Provider value={value}>{children}</RollupsContext.Provider>
}

export function useRollups() {
  const context = useContext(RollupsContext)
  return context
}
