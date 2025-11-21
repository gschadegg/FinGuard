import { DashboardCard } from './DashboardCard'
import { Progress } from '@/components/ui/progress'
import { formatCurrency } from '@/lib/utils'

export function BudgetCard({ budgetTotal = 0, spentTotal = 0 }) {
  const remaining = Math.max(0, (budgetTotal ?? 0) - (spentTotal ?? 0))
  const percent =
    budgetTotal && budgetTotal > 0 ? Math.min(100, (spentTotal / budgetTotal) * 100) : 0

  return (
    <DashboardCard
      title={`${new Date().toLocaleString('default', { month: 'long' }) || 'Current Month'} Budget`}
      data-testid="budget-card"
    >
      <div className="flex flex-col gap-4">
        <div className="flex items-end justify-between">
          <div className="flex flex-col gap-1">
            <span className="text-xs tracking-wide text-muted-foreground">Spent</span>
            <span className="text-2xl font-semibold text-red-500" data-testid="budget-spent">
              {formatCurrency(spentTotal)}
            </span>
          </div>

          <div className="flex flex-col gap-1">
            <span className="text-xs tracking-wide text-muted-foreground">Budget</span>
            <span className="text-2xl font-semibold">{formatCurrency(budgetTotal)}</span>
          </div>

          <div className="flex flex-col gap-1">
            <span className="text-xs tracking-wide text-muted-foreground ">Available</span>
            <span
              className="text-2xl font-semibold text-emerald-500"
              data-testid="budget-available"
            >
              {formatCurrency(remaining)}
            </span>
          </div>
        </div>
        <div className="space-y-1">
          <Progress value={percent} className="h-2 [&>div]:bg-emerald-500" />
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>{percent.toFixed(0)}% of budget used</span>
          </div>
        </div>
      </div>
    </DashboardCard>
  )
}
