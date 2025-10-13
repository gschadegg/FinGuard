'use client'

import { useState } from 'react'
import { useAuth } from '@/components/auth/AuthProvider'
import { useForm, useWatch } from 'react-hook-form'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Grid3x3, CheckCircle2, XCircle } from 'lucide-react'

const MIN_LEN = 12
const hasUpper = (s) => /[A-Z]/.test(s)
const hasSpecial = (s) => /[^A-Za-z0-9]/.test(s)
const noWhitespace = (s) => !/\s/.test(s)

function PolicyItem({ passes, label }) {
  const Icon = passes ? CheckCircle2 : XCircle
  return (
    <div className="flex items-center gap-2 text-sm">
      <Icon
        className={`h-4 w-4 ${passes ? 'text-emerald-600' : 'text-rose-600'}`}
        aria-hidden="true"
      />
      <span className={passes ? 'text-emerald-700' : 'text-rose-700'}>{label}</span>
    </div>
  )
}

const getHint = (lenPass, upperPass, specialPass, spacePass) => {
  if (!lenPass) return `Needs at least ${MIN_LEN} characters.`
  if (!upperPass) return 'Needs at least 1 uppercase letter.'
  if (!specialPass) return 'Needs at least 1 special character.'
  if (!spacePass) return 'Must not contain whitespace.'
  return null
}

export default function RegisterPage() {
  const { register: handleRegister } = useAuth()

  const {
    register,
    handleSubmit,
    control,
    setError,
    clearErrors,
    formState: { errors, isSubmitting },
  } = useForm({ defaultValues: { name: '', email: '', password: '' } })

  const [showPolicy, setShowPolicy] = useState(false)

  const password = useWatch({ control, name: 'password', defaultValue: '' })
  const nonEmpty = password.length > 0

  const lenPass = (password || '').length >= MIN_LEN
  const upperPass = nonEmpty && hasUpper(password || '')
  const specialPass = nonEmpty && hasSpecial(password || '')
  const spacePass = nonEmpty && noWhitespace(password)

  const liveHint = getHint(lenPass, upperPass, specialPass, spacePass)

  async function onSubmit(v) {
    const res = await handleRegister(v.name, v.email, v.password)
    if (res !== 'Invalid Password') {
      setShowPolicy(false)
      clearErrors('password')
    } else {
      setShowPolicy(true)
      setError('password', { type: 'server', message: liveHint || 'Invalid password.' })
    }
  }

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
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
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
                  {...register('password', {
                    required: true,
                    onChange: () => {
                      if (errors.password) clearErrors('password')
                    },
                  })}
                />
              </div>
              {showPolicy && (
                <div className="rounded-md border bg-muted/30 px-3 py-2">
                  <div className="grid gap-1.5">
                    <PolicyItem passes={lenPass} label={`At least ${MIN_LEN} characters`} />
                    <PolicyItem passes={upperPass} label="At least 1 uppercase letter (A–Z)" />
                    <PolicyItem passes={specialPass} label="At least 1 special character (!@#$…)" />
                    <PolicyItem passes={spacePass} label="No whitespace" />
                  </div>
                </div>
              )}

              {showPolicy && liveHint && <p className="text-sm text-rose-600">{liveHint}</p>}
              <Button type="submit" className="w-full cursor-pointer" disabled={isSubmitting}>
                {isSubmitting ? 'Registering…' : 'Sign up with Email'}
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
