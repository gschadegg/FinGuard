import { NextResponse } from 'next/server'

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
  const ct = req.headers.get('content-type') || ''
  if (ct.includes('application/json')) return JSON.stringify(await req.json())
  if (ct.includes('application/x-www-form-urlencoded')) return await req.text()
  return req.body
}

export async function proxyJson(req, targetUrl) {
  const upstream = await fetch(targetUrl, {
    method: req.method,
    headers: req.headers,
    body: await readBody(req),
    cache: 'no-store',
    redirect: 'manual',
  })
  return normalizeToJson(upstream)
}
