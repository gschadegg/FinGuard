import React from 'react'
import { NotificationProvider } from './../../components/notification/NotificationProvider'

export function TestProviders({ children }) {
  return <NotificationProvider>{children}</NotificationProvider>
}
