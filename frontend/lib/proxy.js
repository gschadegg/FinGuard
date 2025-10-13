import { NextResponse } from 'next/server'

const BLOCKED_HEADERS = new Set([
  'connection',
  'keep-alive',
  'proxy-authenticate',
  'proxy-authorization',
  'te',
  'trailer',
  'transfer-encoding',
  'upgrade',
  'host',
  'content-length',
  'accept-encoding',
])

function sanitizeHeaders(headers) {
  const out = new Headers()
  for (const [key, value] of headers.entries()) {
    const k = key.toLowerCase()
    if (BLOCKED_HEADERS.has(k)) continue
    if (k.startsWith('sec-fetch-')) continue
    out.set(key, value)
  }
  return out
}

export async function normalizeToJson(upstream) {
  const status = upstream.status
  const ct = upstream.headers.get('content-type') || ''
  const text = await upstream.text()

  if (!text) return NextResponse.json({ ok: upstream.ok, status, body: null }, { status })
  if (ct.includes('application/json')) {
    try {
      return NextResponse.json(JSON.parse(text), { status })
    } catch {}
  }
  return NextResponse.json({ ok: upstream.ok, status, body: text }, { status })
}

async function readBody(req) {
  if (req.method === 'GET' || req.method === 'HEAD') return undefined
  const ct = (req.headers.get('content-type') || '').toLowerCase()
  if (!ct) return undefined
  if (ct.includes('application/json')) return JSON.stringify(await req.json())
  if (ct.includes('application/x-www-form-urlencoded')) return await req.text()

  return await req.text()
}

export async function proxyJson(req, targetUrl) {
  try {
    const body = await readBody(req)

    const init = {
      method: req.method,
      headers: sanitizeHeaders(req.headers),
      cache: 'no-store',
      redirect: 'manual',
    }
    if (body !== undefined) {
      init.body = body
    }
    const upstream = await fetch(targetUrl, init)

    return normalizeToJson(upstream)
  } catch (err) {
    const name = err?.name || ''
    const status = /timeout/i.test(name) ? 504 : 502
    return NextResponse.json(
      { ok: false, status, error: String(err?.message || err), code: err?.code ?? null },
      { status }
    )
  }
}
