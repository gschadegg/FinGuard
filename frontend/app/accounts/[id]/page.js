'use client'
import * as React from 'react'
import PageLayout from '@/components/layouts/page-layout'

export default function AccountsIDPage() {
  return (
    <PageLayout pageTitle="Account Name">
      <div className="p-6">
        <h1 className="text-2xl font-semibold tracking-tight">Accounts ID</h1>
        <p className="text-muted-foreground">This is /accounts/all-transactions.</p>
      </div>
    </PageLayout>
  )
}
