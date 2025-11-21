import { DashboardCard } from './DashboardCard'
import { AlertTriangle } from 'lucide-react'
import { Button } from '@/components/ui/button'

export function HighRiskCard({ count, onViewTransactions }) {
  const topRightComponent = (
    <span
      className="inline-flex items-center justify-center rounded-full px-2.5 py-.5 text-lg font-bold text-red-700 bg-red-500/15"
      data-testid="high-risk-count"
    >
      {count}
    </span>
  )
  return (
    <DashboardCard
      title="High Risks to Review"
      iconTitle={AlertTriangle}
      TopRightComponent={topRightComponent}
      data-testid="high-risk-card"
    >
      <div className="flex items-center justify-between gap-4 mt-2">
        <Button size="sm" className="cursor-pointer" variant="outline" onClick={onViewTransactions}>
          View Transactions
        </Button>
      </div>
    </DashboardCard>
  )
}
