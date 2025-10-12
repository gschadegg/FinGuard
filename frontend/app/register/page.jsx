'use client'

import { useAuth } from '@/components/auth/AuthProvider'
import { useForm } from 'react-hook-form'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Grid3x3 } from 'lucide-react'

export default function RegisterPage() {
  const { register: handleRegister } = useAuth()
  const { register, handleSubmit } = useForm()

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background px-4">
      <div className="absolute left-8 top-8 flex items-center gap-2">
        <Grid3x3 className="h-7 w-7" />
        <span className="text-xl font-semibold leading-none">FinGuard</span>
      </div>

      <div className="-mt-12 w-full max-w-sm">
        <Card className="w-full shadow-none border-0">
          <CardHeader className="space-y-1 text-center">
            <CardTitle className="text-2xl font-semibold tracking-tight">
              Create an account
            </CardTitle>
            <p className="text-sm text-muted-foreground">
              Enter your email below to create your account
            </p>
          </CardHeader>

          <CardContent>
            <form
              onSubmit={handleSubmit(async (v) => handleRegister(v.name, v.email, v.password))}
              className="space-y-5"
            >
              <div>
                <Input
                  id="name"
                  placeholder="Full name"
                  autoComplete="name"
                  {...register('name', { required: true })}
                />
              </div>
              <div>
                <Input
                  id="email"
                  placeholder="name@example.com"
                  {...register('email', { required: true })}
                />
              </div>

              <div>
                <Input
                  id="password"
                  type="password"
                  placeholder="Password"
                  {...register('password', { required: true })}
                />
              </div>

              <Button type="submit" className="w-full cursor-pointer">
                Sign up with Email
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>

      <Link
        href="/login"
        className="absolute right-8 top-8 mt-2 text-sm font-medium hover:underline"
      >
        Login
      </Link>
    </div>
  )
}
