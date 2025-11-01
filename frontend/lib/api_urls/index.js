const ROOT = '/api'

export const HOME = ROOT
// export const USERS = `${ROOT}/users`
export const ACCOUNTS = `${ROOT}/accounts`
export const PLAID_BASE = `${ROOT}/plaid`
export const BUDGET_BASE = `${ROOT}/budgets`

export const USER_REGISTER_URL = `${ROOT}/auth/register`
export const USER_LOGIN_URL = `${ROOT}/auth/login`
export const AUTH_TOKEN_REFRESH_URL = `${ROOT}/auth/refresh`

export const CREATE_PLAID_TOKEN_URL = `${PLAID_BASE}/token/create`
export const EXCHANGE_PLAID_TOKEN_URL = `${PLAID_BASE}/token/exchange`

export const GET_ALL_ACCOUNTS = `${ACCOUNTS}`
export const GET_ACCOUNT_BY_ID = (accountId) => `${ACCOUNTS}/${encodeURIComponent(accountId)}`

export const GET_TRANSACTIONS_BY_ACCOUNT_ID = (accountId, params) =>
  withQuery(`${ROOT}/transactions/accounts/${encodeURIComponent(accountId)}`, params)

export const GET_TRANSACTIONS_BY_USER_ID = (params) => withQuery(`${ROOT}/transactions`, params)

export const GET_BUDGET_CATEGORIES = `${BUDGET_BASE}/categories`
export const CREATE_BUDGET_CATEGORY = `${BUDGET_BASE}/categories`

export const UPDATE_BUDGET_CATEGORY = (categoryId) =>
  `${BUDGET_BASE}/categories/${encodeURIComponent(categoryId)}`

export const DELETE_BUDGET_CATEGORY = (categoryId) =>
  `${BUDGET_BASE}/categories/${encodeURIComponent(categoryId)}`

const withQuery = (url, params) => {
  if (!params) return url
  const query = new URLSearchParams(params).toString()
  return query ? `${url}?${query}` : url
}
