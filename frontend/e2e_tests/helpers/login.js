import fs from 'fs'
import path from 'path'
import { chromium, request } from '@playwright/test'

const TOKEN_KEY = 'finguard_auth_token'
const USER_KEY = 'finguard_auth_user'

export async function loginViaApiAndLocalStorage(
  page,
  baseURL,
  {
    email = process.env.E2E_EMAIL || 'a@b.com',
    password = process.env.E2E_PASSWORD || 'DevPass1!',
  } = {}
) {
  const res = await page.request.post(`${baseURL}/api/auth/login`, { data: { email, password } })
  if (!res.ok()) throw new Error(`Login failed: ${res.status()} ${await res.text()}`)
  const { access_token, user } = await res.json()
  if (!access_token) throw new Error('No access token')
  await page.goto(baseURL)
  await page.evaluate(
    ([tk, uk, token, usr]) => {
      localStorage.setItem(tk, token)
      localStorage.setItem(uk, JSON.stringify(usr))
    },
    [TOKEN_KEY, USER_KEY, access_token, user]
  )
  await page.reload()
}

export async function loginAndSaveStorageState(
  baseURL,
  outFile,
  {
    email = process.env.E2E_EMAIL || 'a@b.com',
    password = process.env.E2E_PASSWORD || 'DevPass1!',
  } = {}
) {
  const api = await request.newContext()
  const res = await api.post(`${baseURL}/api/auth/login`, { data: { email, password } })

  if (!res.ok()) throw new Error(`Login failed: ${res.status()} ${await res.text()}`)

  const { access_token, user } = await res.json()

  if (!access_token) throw new Error('No access token')

  const browser = await chromium.launch()
  const ctx = await browser.newContext()
  const page = await ctx.newPage()

  await page.goto(baseURL)

  await page.evaluate(
    ([tk, uk, token, usr]) => {
      localStorage.setItem(tk, token)
      localStorage.setItem(uk, JSON.stringify(usr))
    },
    [TOKEN_KEY, USER_KEY, access_token, user]
  )

  fs.mkdirSync(path.dirname(outFile), { recursive: true })
  await ctx.storageState({ path: outFile })

  await browser.close()
  await api.dispose()
  return outFile
}
