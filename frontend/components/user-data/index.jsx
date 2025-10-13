'use client'

import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { GET_ALL_ACCOUNTS } from '@/lib/api_urls'
import { useAuth } from '@/components/auth/AuthProvider'

const UserContext = createContext(null)

export const UserProvider = ({ children }) => {
  const { user, makeAuthRequest } = useAuth()
  const [accounts, setAccounts] = useState(null)
  const [_isLoading, _setIsLoading] = useState(false)

  const getAccounts = useCallback(async () => {
    if (!user?.id) return
    _setIsLoading(true)

    try {
      const params = new URLSearchParams({ user_id: String(user.id) })
      const data = await makeAuthRequest(`${GET_ALL_ACCOUNTS}?${params}`)
      setAccounts(data)
    } catch {
      notify({
        type: 'error',
        title: 'Account Error',
        message: 'Experienced issues fetching your accounts, please refresh the page to try again.',
      })
      setAccounts([])
    } finally {
      _setIsLoading(false)
    }
  }, [user?.id, makeAuthRequest])

  useEffect(() => {
    getAccounts()
  }, [getAccounts])

  return (
    <UserContext.Provider
      value={{ user: user, userId: user?.id, accounts, _isLoading, refreshAccounts: getAccounts }}
    >
      {children}
    </UserContext.Provider>
  )
}

export const useUserContext = () => {
  const context = useContext(UserContext)

  return context
}
