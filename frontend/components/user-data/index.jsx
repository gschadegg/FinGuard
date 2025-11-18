'use client'

import { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { GET_ALL_ACCOUNTS } from '@/lib/api_urls'
import { useAuth } from '@/components/auth/AuthProvider'
import { useNotify } from '../notification/NotificationProvider'

const UserContext = createContext(null)

export const UserProvider = ({ children }) => {
  const notify = useNotify()
  const { user, makeAuthRequest } = useAuth()
  const [accounts, setAccounts] = useState(null)
  const [accountsTotal, setAccountsTotal] = useState(null)
  const [_isLoading, _setIsLoading] = useState(false)

  const getAccounts = useCallback(async () => {
    if (!user?.id) return
    _setIsLoading(true)

    try {
      const data = await makeAuthRequest(`${GET_ALL_ACCOUNTS}`)
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
  }, [user?.id, makeAuthRequest, notify])

  useEffect(() => {
    getAccounts()
  }, [getAccounts])

  return (
    <UserContext.Provider
      value={{
        user: user,
        userId: user?.id,
        accounts,
        _isLoading,
        accountsTotal,
        setAccountsTotal,
        refreshAccounts: getAccounts,
      }}
    >
      {children}
    </UserContext.Provider>
  )
}

export const useUserContext = () => {
  const context = useContext(UserContext)

  return context
}
