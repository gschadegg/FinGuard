const ROOT = process.env.NEXT_PUBLIC_API_URL

export const HOME = ROOT
export const USERS = `${ROOT}/users`

export const PLAID_BASE = `${ROOT}/plaid`

export const CREATE_PLAID_TOKEN = `${PLAID_BASE}/token/create`
export const EXCHANGE_PLAID_TOKEN = `${PLAID_BASE}/token/exchange`
