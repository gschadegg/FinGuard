import { NextResponse } from 'next/server'

export async function normalizeToJson(upstream) {
  const text = await upstream.text()
  const ct = upstream.headers.get('content-type') || ''

  if (!text) {
    return NextResponse.json(
      { ok: upstream.ok, status: upstream.status, body: null },
      { status: upstream.status }
    )
  }

  if (ct.includes('application/json')) {
    try {
      return NextResponse.json(JSON.parse(text), { status: upstream.status })
    } catch {
      // need to handle or have it pass through to wrapper?
    }
  }

  return NextResponse.json(
    { ok: upstream.ok, status: upstream.status, body: text },
    { status: upstream.status }
  )
}

export async function fetchAndNormalize(url, init = {}) {
  const upstream = await fetch(url, { cache: 'no-store', ...init })
  return normalizeToJson(upstream)
}
