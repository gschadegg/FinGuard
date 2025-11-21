// export const runtime = 'nodejs' // required if you proxy to http://localhost:8000
import { proxyJson } from '@/lib/proxy'
import { mockHandlers } from '@/e2e_tests/mocks/handlers'

const API_BASE = process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
const PROXY_API_PREFIX = '/api'

function buildTarget(req) {
  const { pathname, search } = req.nextUrl

  const rest = pathname.startsWith(PROXY_API_PREFIX)
    ? pathname.slice(PROXY_API_PREFIX.length).replace(/^\/+/, '')
    : pathname.replace(/^\/+/, '')

  const pathPart = rest ? `/${rest}` : ''
  return `${API_BASE}${pathPart}${search}`
}

async function handle(req) {
  const url = new URL(req.url)
  const pathAfterApi = url.pathname.replace(/^\/api\/?/, '')

  if (process.env.NEXT_PUBLIC_USE_MOCKS === 'true' || process.env.USE_MOCKS === 'true') {
    return await mockHandlers(req, pathAfterApi)
  }

  const target = buildTarget(req)
  return proxyJson(req, target)
}

export {
  handle as GET,
  handle as POST,
  handle as PUT,
  handle as PATCH,
  handle as DELETE,
  handle as OPTIONS,
}
