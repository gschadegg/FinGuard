import UserAccountMockData from './UserAccountsData'
import TransactionMockData from './TransactionData'
import BudgetCategoriesMockData from './BudgetCategoriesData'
import DashboardMockData from './DashboardData'
import { NextResponse } from 'next/server'

function makeFakeJwt(email, uid, ttlSec = 3600) {
  const now = Math.floor(Date.now() / 1000)
  const header = { alg: 'HS256', typ: 'JWT' }
  const payload = { sub: email, uid, iat: now, exp: now + ttlSec }
  const b64 = (obj) => Buffer.from(JSON.stringify(obj)).toString('base64url')
  return `${b64(header)}.${b64(payload)}.mock-signature`
}

const ok = (data, init = 200) => NextResponse.json(data, { status: init })
const err = (data, init = 400) => NextResponse.json(data, { status: init })

const isoNow = () => new Date().toISOString()
const clone = (x) => JSON.parse(JSON.stringify(x))
let BudgetStore = clone(BudgetCategoriesMockData)
let TransactionStore = clone(TransactionMockData)

for (const t of TransactionStore.items) {
  if (t.fraud_review_status == null) t.fraud_review_status = 'pending'
  if (t.risk_level == null) t.risk_level = null
}

function findTransactionById(id) {
  id = Number(id)
  return TransactionStore.items.find((txn) => txn.id === id) || null
}

function computeRiskRollupsForUser(userId) {
  const items = TransactionStore.items.filter((txn) => txn.user_id === userId && !txn.removed)
  const pending = items.filter((txn) => (txn.fraud_review_status || 'pending') === 'pending')

  const isHigh = (txn) => txn.is_fraud_suspected === true || txn.risk_level === 'high'
  const isMed = (txn) => txn.is_fraud_suspected === false && txn.risk_level === 'medium'
  const isLow = (txn) => txn.is_fraud_suspected === false && txn.risk_level === 'low'

  const pending_total = pending.length
  const pending_high = pending.filter(isHigh).length
  const pending_medium = pending.filter(isMed).length
  const pending_low = pending.filter(isLow).length

  const byAccount = {}
  for (const txn of pending) {
    const key = txn.account_id
    if (!byAccount[key]) byAccount[key] = { high: 0, medium: 0, low: 0, total: 0 }
    byAccount[key].total += 1
    if (isHigh(txn)) byAccount[key].high += 1
    else if (isMed(txn)) byAccount[key].medium += 1
    else if (isLow(txn)) byAccount[key].low += 1
  }

  return {
    risks: { pending_total, pending_high, pending_medium, pending_low },
    byAccount,
  }
}

export async function mockHandlers(req, pathAfterApi) {
  if (pathAfterApi.startsWith('accounts')) {
    return ok(UserAccountMockData)
  }

  if (pathAfterApi.startsWith('dashboard')) {
    const referer = req.headers.get('referer') || ''
    const refUrl = new URL(referer)

    const delay = Number(refUrl.searchParams.get('__delay') || '0')

    if (delay > 0) {
      await new Promise((r) => setTimeout(r, delay))
    }

    return ok(DashboardMockData)
  }

  if (pathAfterApi.startsWith('transactions')) {
    const url = new URL(req.url)
    const parts = pathAfterApi
      .replace(/^\/+|\/+$/g, '')
      .split('?')[0]
      .split('/')

    if (req.method === 'GET' && parts[0] === 'transactions' && parts[1] === 'rollups') {
      const userId = 1
      return ok(computeRiskRollupsForUser(userId))
    }

    if (req.method === 'PUT' && parts[0] === 'transactions' && parts[2] === 'fraud-review') {
      const id = parts[1]
      const body = await req.json().catch(() => ({}))

      const { status } = body || {}
      const allowed = new Set(['fraud', 'not_fraud', 'ignored', 'pending'])

      if (!allowed.has(status)) {
        return err({ detail: 'Invalid status' }, 400)
      }

      const txn = findTransactionById(id)
      if (!txn) return err({ detail: 'Transaction not found' }, 404)

      txn.fraud_review_status = status

      if (status === 'not_fraud') {
        txn.is_fraud_suspected = false
        if (txn.risk_level === 'high') txn.risk_level = 'low'
      }

      if (status === 'fraud') {
        txn.is_fraud_suspected = true
        txn.risk_level = 'high'
      }

      return ok({ ok: true, transaction_id: id, status })
    }

    if (req.method === 'GET') {
      return ok(TransactionStore)
    }
  }

  if (pathAfterApi.startsWith('budgets')) {
    const p = pathAfterApi.replace(/^\/+|\/+$/g, '').split('?')[0]

    if (req.method === 'GET' && p === 'budgets/categories') {
      return ok(BudgetStore)
    }

    if (req.method === 'POST' && p === 'budgets/categories') {
      const body = await req.json().catch(() => ({}))
      const id = Math.floor(Math.random() * 1e6)
      const item = {
        id,
        name: body.name || 'New Category',
        allotted_amount: String(body.allotted_amount ?? '0'),
        group: body.group || 'Expenses',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }
      return ok(item, 201)
    }

    if (req.method === 'PATCH' || req.method === 'PUT') {
      const body = await req.json().catch(() => ({}))
      const id = Number(p.split('/').pop())
      const updated = {
        id,
        name: body.name || 'Updated Category',
        allotted_amount: String(body.allotted_amount ?? '0'),
        group: body.group || 'Expenses',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }
      return ok(updated)
    }

    if (req.method === 'DELETE') {
      return ok({ ok: true })
    }

    return err({ detail: 'Method not allowed' }, 405)
  }

  // mocking login route
  if (pathAfterApi.startsWith('auth/login')) {
    const body = req.method === 'POST' ? await req.json().catch(() => ({})) : {}
    if (body?.password === 'wrong') {
      return err({ detail: 'Invalid email or password' }, 401)
    }
    const email = body?.email || 'a@b.com'
    const token = makeFakeJwt(email, 1, 3600)
    return ok({
      access_token: token,
      token_type: 'bearer',
      user: { id: 1, email, name: 'Alice' },
    })
  }

  if (pathAfterApi.startsWith('auth/register')) {
    const body = req.method === 'POST' ? await req.json().catch(() => ({})) : {}
    // faking out "email already exists"
    if (
      String(body?.email || '')
        .toLowerCase()
        .includes('exists')
    ) {
      return err({ detail: 'Email already exists' }, 409)
    }

    const email = body?.email || 'new@test.local'
    const token = makeFakeJwt(email, 2, 3600)
    return ok({
      access_token: token,
      token_type: 'bearer',
      user: { id: 2, email, name: body?.name || 'New User' },
    })
  }

  if (pathAfterApi === 'auth/refresh') {
    const token = makeFakeJwt('a@b.com', 1, 3600)
    return ok({
      access_token: token,
      token_type: 'bearer',
      user: { id: 1, email: 'a@b.com', name: 'Alice' },
    })
  }

  return err({ detail: `No mock for /api/${pathAfterApi}` }, 404)
}
