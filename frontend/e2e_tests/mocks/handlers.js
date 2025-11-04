import UserAccountMockData from './UserAccountsData'
import TransactionMockData from './TransactionData'
import BudgetCategoriesMockData from './BudgetCategoriesData'
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

export async function mockHandlers(req, pathAfterApi) {
  if (pathAfterApi.startsWith('accounts')) {
    return ok(UserAccountMockData)
  }
  if (pathAfterApi.startsWith('transactions')) {
    return ok(TransactionMockData)
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
