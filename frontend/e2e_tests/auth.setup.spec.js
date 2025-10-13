import path from 'path'
import { test } from '@playwright/test'
import { loginAndSaveStorageState } from './helpers/login.js'

test('create storageState', async ({ baseURL }) => {
  const out = path.join(process.cwd(), 'e2e_tests/.auth/storageState.json')
  await loginAndSaveStorageState(baseURL, out)
})
