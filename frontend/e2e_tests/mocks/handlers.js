import UserAccountMockData from './/UserAccountsData'
import TransactionMockData from './TransactionData'
import { NextResponse } from 'next/server'

export const mockHandlers = (pathAfterApi) => {
  if (pathAfterApi.startsWith('accounts')) {
    return NextResponse.json(UserAccountMockData, { status: 200 })
  }
  if (pathAfterApi.startsWith('transactions')) {
    return NextResponse.json(TransactionMockData, { status: 200 })
  }
}
