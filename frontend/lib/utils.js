import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs) {
  return twMerge(clsx(inputs))
}

export function decodeJwt(token) {
  try {
    const [, payload] = token.split('.')
    const json = atob(payload.replace(/-/g, '+').replace(/_/g, '/'))
    return JSON.parse(json)
  } catch {
    return null
  }
}

export function getExp(token) {
  const p = decodeJwt(token)
  return p?.exp ? Number(p.exp) : null // in seconds
}

export function isExpired(token) {
  const exp = getExp(token)
  if (!exp) return false
  return Math.floor(Date.now() / 1000) >= exp
}

export const formatCurrency = (num) =>
  new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(num)
