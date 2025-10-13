'use client'

import { useAuth } from '@/components/auth/AuthProvider'
import { useForm } from 'react-hook-form'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Grid3x3 } from 'lucide-react'

export default function LoginPage() {
  const { login } = useAuth()

  const router = useRouter()
  const searchParams = useSearchParams()
  const next = searchParams.get('next') || '/'
  const { register, handleSubmit } = useForm()

  async function onSubmit(val) {
    await login(val.email, val.password)
    router.push(next)
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background px-4">
      <div className="absolute left-8 top-8 flex items-center gap-2">
        <Grid3x3 className="h-7 w-7" />
        <span className="text-xl font-semibold leading-none">FinGuard</span>
      </div>

      <div className="-mt-12 w-full max-w-sm">
        <Card className="w-full shadow-none border-0">
          <CardHeader className="space-y-2 text-center">
            <CardTitle className="text-2xl font-semibold tracking-tight">Welcome back!</CardTitle>
            <p className="text-sm text-muted-foreground">
              Enter your email and password below to login
            </p>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              <div>
                <Input
                  id="email"
                  type="email"
                  placeholder="name@example.com"
                  autoComplete="email"
                  {...register('email', { required: true })}
                />
              </div>

              <div>
                <Input
                  id="password"
                  type="password"
                  placeholder="Password"
                  autoComplete="current-password"
                  {...register('password', { required: true })}
                />
              </div>

              <Button type="submit" className="w-full cursor-pointer">
                Login
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>

      <Link
        href="/register"
        className="absolute right-8 top-8 mt-2 text-sm font-medium hover:underline"
      >
        Register
      </Link>
    </div>
  )
}
