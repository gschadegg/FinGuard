'use client'

import { createContext, useContext, useEffect, useMemo, useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { USER_REGISTER_URL, USER_LOGIN_URL, AUTH_TOKEN_REFRESH_URL } from '@/lib/api_urls'

import { isExpired } from '@/lib/utils'
import { useSessionTimers } from '@/hooks/useSessionTimers'
import { useNotify } from '@/components/notification/NotificationProvider'

const AuthContext = createContext(null)

const LOCAL_STORAGE_TOKEN_KEY = 'finguard_auth_token'
const LOCAL_STORAGE_USER = 'finguard_auth_user'

async function MakeRequest(input, init) {
  const res = await fetch(input, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...(init?.headers || {}) },
  })
  if (!res.ok) {
    const resJson = await res.json()
    const data = {
      ok: res.ok,
      status: res.status,
      url: res.url,
      statusText: res.statusText,
      ...resJson,
    }
    return data
  }
  return res.json()
}

export function AuthProvider({ children }) {
  const router = useRouter()
  const notify = useNotify()

  const [token, setToken] = useState(null)
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  // shown 2 minutes before token expires
  const [showSessionPrompt, setShowSessionPrompt] = useState(false)

  // get user and tokens from local
  useEffect(() => {
    const token =
      typeof window !== 'undefined' ? localStorage.getItem(LOCAL_STORAGE_TOKEN_KEY) : null
    let user = null
    if (typeof window !== 'undefined') {
      try {
        const raw = localStorage.getItem(LOCAL_STORAGE_USER)
        user = raw ? JSON.parse(raw) : null
      } catch {}
    }

    if (token && !isExpired(token)) {
      setToken(token)
      setUser(user)
    } else {
      localStorage.removeItem(LOCAL_STORAGE_TOKEN_KEY)
      localStorage.removeItem(LOCAL_STORAGE_USER)
    }
    setIsLoading(false)
  }, [])

  useEffect(() => {
    const onStorage = (e) => {
      if (e.key !== LOCAL_STORAGE_TOKEN_KEY && e.key !== LOCAL_STORAGE_USER) return
      const token = localStorage.getItem(LOCAL_STORAGE_TOKEN_KEY)
      let user = null
      try {
        const raw = localStorage.getItem(LOCAL_STORAGE_USER)
        user = raw ? JSON.parse(raw) : null
      } catch {}
      if (token && !isExpired(token)) {
        setToken(token)
        setUser(user)
      } else {
        setToken(null)
        setUser(null)
      }
    }
    window.addEventListener('storage', onStorage)
    return () => window.removeEventListener('storage', onStorage)
  }, [])

  useSessionTimers(token, {
    leadSeconds: 120,
    onPrompt: () => setShowSessionPrompt(true),
    onExpire: () => logout(),
  })

  const logout = useCallback(() => {
    setUser(null)
    setToken(null)
    setShowSessionPrompt(false)
    localStorage.removeItem(LOCAL_STORAGE_TOKEN_KEY)
    localStorage.removeItem(LOCAL_STORAGE_USER)
    router.replace('/login')
  }, [router])

  // make request with access token in header
  const makeAuthRequest = useCallback(
    async (input, init) => {
      const headers = { 'Content-Type': 'application/json', ...(init?.headers || {}) }
      if (token) headers.Authorization = `Bearer ${token}`
      const res = await fetch(input, { ...init, headers })

      if (res.status === 401) {
        logout()
        notify({
          type: 'error',
          title: 'Not Authorized',
          message: 'You are not authorized to make this request, you are being logged out.',
        })
        throw new Error('Unauthorized')
      }
      if (!res.ok) {
        const resJson = await res.json()
        const data = {
          ok: res.ok,
          status: res.status,
          url: res.url,
          statusText: res.statusText,
          ...resJson,
        }
        return data
      }
      return res.json()
    },
    [token, logout, notify]
  )

  // app Login
  const login = useCallback(
    async (email, password, next = '/') => {
      const data = await MakeRequest(USER_LOGIN_URL, {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })

      if (data?.detail && data.detail === 'Invalid email or password') {
        notify({
          type: 'error',
          title: 'Invalid Credentials',
          message: 'Failed login, invalid email or password.',
        })
      } else if (!data?.access_token) {
        notify({
          type: 'error',
          title: 'Failed Login',
          message: 'Unable login at this time',
        })

        throw new Error('No access token from login')
      }
      if (isExpired(data.access_token)) throw new Error('Received expired token')

      setToken(data.access_token)
      localStorage.setItem(LOCAL_STORAGE_TOKEN_KEY, data.access_token)

      const user = data.user
      setUser(user)
      if (user) localStorage.setItem(LOCAL_STORAGE_USER, JSON.stringify(user))

      setShowSessionPrompt(false)
      router.replace(next)
    },
    [router, notify]
  )

  // app register
  const register = useCallback(
    async (name, email, password, next = '/') => {
      const data = await MakeRequest(USER_REGISTER_URL, {
        method: 'POST',
        body: JSON.stringify({ name, email, password }),
      })

      if (data?.detail && data.detail === 'Email already exists') {
        notify({
          type: 'error',
          title: 'Unable to Create Account',
          message: 'An account with that email already exists, please use another.',
        })
      } else if (data?.detail && Array.isArray(data?.detail)) {
        const check = data?.detail[0] || null
        if (check) {
          if (check?.loc.find((str) => str === 'password') && check?.type === 'string_too_short') {
            notify({
              type: 'error',
              title: 'Invalid Password',
              message: 'Password should have at least 8 characters.',
            })
          }
        }
      } else if (!data?.access_token) throw new Error('No access token from register')
      else if (isExpired(data.access_token)) throw new Error('Received expired token')
      else {
        setToken(data.access_token)
        localStorage.setItem(LOCAL_STORAGE_TOKEN_KEY, data.access_token)

        const user = data.user
        setUser(user)
        if (user) localStorage.setItem(LOCAL_STORAGE_USER, JSON.stringify(user))

        setShowSessionPrompt(false)
        router.replace(next)
      }
    },
    [router, notify]
  )

  const refreshToken = useCallback(async () => {
    const auth = token || localStorage.getItem(LOCAL_STORAGE_TOKEN_KEY)
    if (!auth) throw new Error('No token to refresh')

    const res = await fetch(AUTH_TOKEN_REFRESH_URL, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    })

    if (!res.ok) {
      const text = await res.text().catch(() => '')
      throw new Error(text || `HTTP ${res.status}`)
    }
    const data = await res.json()
    const newToken = data?.access_token
    if (!newToken) throw new Error('No access token from refresh')
    if (isExpired(newToken)) throw new Error('Received expired token')

    setToken(newToken)
    localStorage.setItem(LOCAL_STORAGE_TOKEN_KEY, newToken)

    if (data.user) {
      setUser(data.user)
      localStorage.setItem(LOCAL_STORAGE_USER, JSON.stringify(data.user))
    }

    setShowSessionPrompt(false)
    return newToken
  }, [token])

  const value = useMemo(
    () => ({
      user,
      token,
      isLoading,
      makeAuthRequest,
      login,
      register,
      logout,
      showSessionPrompt,
      setShowSessionPrompt,
      refreshToken,
    }),
    [
      user,
      token,
      isLoading,
      makeAuthRequest,
      login,
      register,
      logout,
      showSessionPrompt,
      refreshToken,
    ]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  return context
}
