'use client'

import { useState, useEffect } from 'react'
import { TotalBalanceCard } from '@/components/dashboard-widgets/TotalBalanceCard'
import { HighRiskCard } from '@/components/dashboard-widgets/HighRiskCard'
import { AccountsCard } from '@/components/dashboard-widgets/AccountsCard'
import { DashboardSkeleton } from '@/components/dashboard-widgets/skeleton'
import { BudgetCard } from '@/components/dashboard-widgets/BudgetCard'
import { SpendingCategoriesCard } from '@/components/dashboard-widgets/SpendingCategoriesCard'

import { GET_DASHBOARD_DATA } from '@/lib/api_urls'
import { useAuth } from '@/components/auth/AuthProvider'
import { useNotify } from '@/components/notification/NotificationProvider'
import PageLayout from '@/components/layouts/page-layout'
import { useRouter } from 'next/navigation'
import { useUserContext } from '@/components/user-data'

export default function Home() {
  const router = useRouter()
  const { makeAuthRequest } = useAuth()
  const { setAccountsTotal } = useUserContext()
  const notify = useNotify()
  const [data, setData] = useState(null)

  const handleClickViewTransactions = () => {
    router.push('/accounts?high_risk_only=true')
  }

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const res = await makeAuthRequest(GET_DASHBOARD_DATA)
        if (res) {
          setData(res)
          setAccountsTotal(res?.totals ?? '0.00')
        }
      } catch {
        notify({
          type: 'error',
          title: 'Dashboard Error',
          message: 'Experienced issues fetching dashboard data, please try again.',
        })
      }
    }
    fetchDashboardData()
  }, [notify, makeAuthRequest, setData, setAccountsTotal])

  if (!data) {
    return <DashboardSkeleton />
  }

  return (
    <PageLayout
      pageTitle="Dashboard"
      subTitle={data?.period?.label || ''}
      data-testid="dashboard-page"
    >
      <div className="space-y-8 w-full">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <TotalBalanceCard total={data?.totals} />
            <HighRiskCard
              count={data?.risk_data?.risks?.pending_high}
              onViewTransactions={handleClickViewTransactions}
            />
            <BudgetCard budgetTotal={data?.budget?.budget} spentTotal={data?.budget?.spent} />
          </div>
          <SpendingCategoriesCard
            spendingCategories={data?.spending_categories}
            period={data?.period?.label}
          />
        </div>
        <AccountsCard accounts={data?.accounts} />
      </div>
    </PageLayout>
  )
}
