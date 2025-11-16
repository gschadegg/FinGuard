import { DashboardCard } from './DashboardCard'
import { DollarSign } from 'lucide-react'

const formatCurrency = (n) =>
  new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(n)

export function TotalBalanceCard({ total = '0.00' }) {
  return (
    <DashboardCard title="Total Balance" iconRight={DollarSign}>
      <div className="flex items-center justify-between">
        <div className="text-4xl font-bold">{formatCurrency(total)}</div>
      </div>
    </DashboardCard>
  )
}
