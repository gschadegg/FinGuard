'use client'

import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { GET_ALL_ACCOUNTS } from '@/lib/api_urls'

const UserContext = createContext(null)

export const UserProvider = ({ children }) => {
  const [userId, _setUserId] = useState(1)
  const [accounts, setAccounts] = useState(null)
  const [_isLoading, _setIsLoading] = useState(false)

  const getAccounts = useCallback(async () => {
    const params = {
      user_id: userId,
    }
    const queryParams = new URLSearchParams(params)
    try {
      const r = await fetch(`${GET_ALL_ACCOUNTS}?${queryParams.toString()}`, {
        method: 'GET',
        cache: 'no-store',
        headers: { 'Content-Type': 'application/json' },
      })
      const json = await r.json()

      setAccounts(json)
    } catch {
      setAccounts([])
    }
  }, [userId])

  const refreshAccounts = () => {
    getAccounts()
  }
  useEffect(() => {
    getAccounts()
  }, [userId, getAccounts])

  return (
    <UserContext.Provider value={{ userId, accounts, refreshAccounts }}>
      {children}
    </UserContext.Provider>
  )
}

export const useUserContext = () => {
  const context = useContext(UserContext)

  return context
}
