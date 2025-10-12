'use client'
import { useEffect } from 'react'
import { usePathname, useRouter } from 'next/navigation'

import { useAuth } from '@/components/auth/AuthProvider'
import { SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar'
import { AppSidebar } from '@/components/app-sidebar'
import NotificationStack from '@/components/notification'
import RenewSessionDialog from '@/components/RenewSessionDialog'
import { RequireAuth } from '@/components/auth/RequireAuth'

export default function MainNavLayout({ defaultOpen, children }) {
  const { token, isLoading, showSessionPrompt } = useAuth()

  const router = useRouter()
  const pathname = usePathname()

  const isPublicRoute =
    pathname === '/login' ||
    pathname === '/register' ||
    pathname?.startsWith('/login/') ||
    pathname?.startsWith('/register/')

  useEffect(() => {
    if (!isLoading) {
      if (!token && !isPublicRoute) {
        const next = encodeURIComponent(pathname || '/')
        router.replace(`/login?next=${next}`)
      }
    }
  }, [token, isPublicRoute, pathname, router, isLoading])

  if (isLoading) return null
  if (!token && !isPublicRoute) return null

  // login/register pages
  if (!token && isPublicRoute) {
    return (
      <>
        {children}
        <NotificationStack />
      </>
    )
  }

  return (
    <RequireAuth>
      {() => (
        <SidebarProvider defaultOpen={defaultOpen}>
          <AppSidebar />
          <SidebarTrigger className="p-3 ml-2 mt-6" />
          {children}
          <NotificationStack />
          {showSessionPrompt && <RenewSessionDialog />}
        </SidebarProvider>
      )}
    </RequireAuth>
  )
}
