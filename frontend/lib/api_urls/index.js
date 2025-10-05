const ROOT = '/api'

export const HOME = ROOT
export const USERS = `${ROOT}/users`
export const ACCOUNTS = `${ROOT}/accounts`
export const PLAID_BASE = `${ROOT}/plaid`

export const CREATE_PLAID_TOKEN_URL = `${PLAID_BASE}/token/create`
export const EXCHANGE_PLAID_TOKEN_URL = `${PLAID_BASE}/token/exchange`

export const GET_ALL_ACCOUNTS = `${ACCOUNTS}`
export const GET_ACCOUNT_BY_ID = (accountId) => `${ACCOUNTS}/${encodeURIComponent(accountId)}`

export const GET_TRANSACTIONS_BY_ACCOUNT_ID = (accountId, params) =>
  withQuery(`${ROOT}/transactions/accounts/${encodeURIComponent(accountId)}`, params)

export const GET_TRANSACTIONS_BY_USER_ID = (params) => withQuery(`${ROOT}/transactions`, params)

const withQuery = (url, params) => {
  if (!params) return url
  const query = new URLSearchParams(params).toString()
  return query ? `${url}?${query}` : url
}
