// @ts-check
import { defineConfig, devices } from '@playwright/test'
const path = require('path')
import dotenv from 'dotenv'

dotenv.config({ path: path.resolve(process.cwd(), '.env.local') })
/**
 * Read environment variables from file.
 * https://github.com/motdotla/dotenv
 */
// import dotenv from 'dotenv';
// import path from 'path';
// dotenv.config({ path: path.resolve(__dirname, '.env') });

/**
 * @see https://playwright.dev/docs/test-configuration
 */

const USE_MOCKS = process.env.USE_MOCKS === 'true'
const BASE_URL = process.env.BASE_URL || 'http://127.0.0.1:3000'

export default defineConfig({
  testDir: './e2e_tests',
  /* Run tests in files in parallel */
  fullyParallel: true,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : undefined,
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: 'html',
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: BASE_URL,

    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: 'on-first-retry',
  },

  /* Configure projects for major browsers */
  projects: [
    // {
    //   name: 'chromium',
    //   use: { ...devices['Desktop Chrome'] },
    // },

    // {
    //   name: 'firefox',
    //   use: { ...devices['Desktop Firefox'] },
    // },

    // {
    //   name: 'webkit',
    //   use: { ...devices['Desktop Safari'] },
    // },
    {
      name: 'setup',
      testMatch: ['e2e_tests/auth.setup.spec.js'],
    },
    {
      name: 'auth',
      use: { ...devices['Desktop Chrome'], storageState: 'e2e_tests/.auth/storageState.json' },
      testMatch: /.*\.spec\.(js|ts)$/,
      testIgnore: /.*\.auth\.spec\.(js|ts)$/,
      dependencies: ['setup'],
    },
    {
      name: 'anon',
      use: { ...devices['Desktop Chrome'], storageState: { cookies: [], origins: [] } },
      testMatch: /.*\.auth\.spec\.(js|ts)$/,
    },
    /* Test against mobile viewports. */
    // {
    //   name: 'Mobile Chrome',
    //   use: { ...devices['Pixel 5'] },
    // },
    // {
    //   name: 'Mobile Safari',
    //   use: { ...devices['iPhone 12'] },
    // },

    /* Test against branded browsers. */
    // {
    //   name: 'Microsoft Edge',
    //   use: { ...devices['Desktop Edge'], channel: 'msedge' },
    // },
    // {
    //   name: 'Google Chrome',
    //   use: { ...devices['Desktop Chrome'], channel: 'chrome' },
    // },
  ],

  /* Run your local dev server before starting the tests */
  webServer: {
    command: `cross-env NEXT_PUBLIC_USE_MOCKS=${USE_MOCKS ? 'true' : 'false'} USE_MOCKS=${USE_MOCKS ? 'true' : 'false'} next dev -p 3000 -H 127.0.0.1`,
    url: BASE_URL,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    env: {
      ...process.env,
      NEXT_PUBLIC_USE_MOCKS: USE_MOCKS ? 'true' : 'false',
      USE_MOCKS: USE_MOCKS ? 'true' : 'false',
      BASE_URL,
    },
  },
})
