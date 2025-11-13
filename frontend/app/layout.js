import { ThemeProvider } from '@/components/mode-toggle/theme-provider'
import { Geist, Geist_Mono } from 'next/font/google'

import './globals.css'
import { NotificationProvider } from '@/components/notification/NotificationProvider'

import { UserProvider } from '@/components/user-data'
import { AuthProvider } from '@/components/auth/AuthProvider'
import { RollupsProvider } from '@/components/rollups/RollupProvider'
import { cookies } from 'next/headers'

import MainNavLayout from '@/components/layouts/MainNav-Layout'
const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
})

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
})

export const metadata = {
  title: 'FinGuard',
  description: 'Financial management system',
}

export default async function RootLayout({ children }) {
  const cookieStore = await cookies()
  const defaultOpen = cookieStore.get('sidebar_state')?.value === 'true'
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <NotificationProvider>
            <AuthProvider>
              <RollupsProvider>
                <UserProvider>
                  <MainNavLayout defaultOpen={defaultOpen}>{children}</MainNavLayout>
                </UserProvider>
              </RollupsProvider>
            </AuthProvider>
          </NotificationProvider>
        </ThemeProvider>
        <div />
      </body>
    </html>
  )
}
