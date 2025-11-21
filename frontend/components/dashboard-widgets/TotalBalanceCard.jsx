import { DashboardCard } from './DashboardCard'
import { DollarSign } from 'lucide-react'
import { formatCurrency } from '@/lib/utils'

export function TotalBalanceCard({ total = '0.00' }) {
  return (
    <DashboardCard title="Total Balance" iconRight={DollarSign} data-testid="total-balance-card">
      <div className="flex items-center justify-between">
        <div className="text-4xl font-bold" data-testid="total-balance-amount">
          {formatCurrency(total)}
        </div>
      </div>
    </DashboardCard>
  )
}
