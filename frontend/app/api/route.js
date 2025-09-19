// app/api/route.ts
import { fetchAndNormalize } from '@/lib/proxy'
import { HOME } from '@/lib/api_urls'

export async function GET() {
  return fetchAndNormalize(`${HOME}/`)
}
