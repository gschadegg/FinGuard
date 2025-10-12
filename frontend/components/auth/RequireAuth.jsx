'use client'

import { useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'

import { useAuth } from '@/components/auth/AuthProvider'
import { Skeleton } from '@/components/ui/skeleton'

export function RequireAuth({ children }) {
  const { token, isLoading } = useAuth()
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    if (isLoading) return
    if (!token) {
      const next = encodeURIComponent(pathname || '/')
      router.replace(`/login?next=${next}`)
    }
  }, [isLoading, token, pathname, router])

  if (isLoading) {
    return <Skeleton className="h-8 w-48" />
  }
  if (!token) return null

  return typeof children === 'function' ? children() : children
}
