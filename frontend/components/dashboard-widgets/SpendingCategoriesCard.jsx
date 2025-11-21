'use client'

import { DashboardCard } from './DashboardCard'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import { formatCurrency } from '@/lib/utils'

const COLOR_CLASSES = [
  'bg-teal-600',
  'bg-orange-400',
  'bg-slate-900',
  'bg-yellow-300',
  'bg-amber-300',
]

const COLOR_HEX = ['#1CA197', '#E67853', '#1F3443', '#E8C66A', '#F4B976']

export function SpendingCategoriesCard({
  period = 'Current Month',
  title = 'Top Spending Categories',
  spendingCategories = [],
}) {
  const { rows, totalAmount } = Top4SpentCategories(spendingCategories)

  const chartData = rows.map((row, index) => ({
    name: row.name,
    value: row.amount,
    color: COLOR_HEX[index < COLOR_HEX.length ? index : COLOR_HEX.length - 1],
  }))

  return (
    <DashboardCard title={title} data-testid="spending-categories-card">
      <div className="flex flex-col gap-1">
        <p className="text-xs text-muted-foreground">{`${period}`}</p>

        <div className="flex items-center justify-center gap-2">
          <div className="h-40 w-40">
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  data={chartData}
                  dataKey="value"
                  nameKey="name"
                  innerRadius="70%"
                  outerRadius="100%"
                  paddingAngle={2}
                >
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${entry.name}-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value, _name, props) => [formatCurrency(value), props.payload.name]}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="h-px bg-border my-2 w-full" />
        <div className="flex items-center gap-4">
          <div className="flex-1 space-y-2">
            {rows.map((row, index) => {
              const percent = totalAmount > 0 ? (row.amount / totalAmount) * 100 : 0

              const colorClass =
                index < COLOR_CLASSES.length
                  ? COLOR_CLASSES[index]
                  : COLOR_CLASSES[COLOR_CLASSES.length - 1]

              return (
                <div
                  key={row.category_id ?? row.name}
                  className="flex items-center justify-between gap-3 rounded-md px-2 py-1"
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <span className={`inline-flex h-2.5 w-2.5 rounded-full ${colorClass}`} />
                    <span className="text-sm truncate">{row.name}</span>
                  </div>
                  <div className="flex items-center gap-4 text-xs">
                    <span className="font-medium">{formatCurrency(row.amount)}</span>
                    <span className="text-muted-foreground w-12 text-right">
                      {percent.toFixed(0)}%
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </DashboardCard>
  )
}

function Top4SpentCategories(spendingCategories) {
  const spendingArray = Array.isArray(spendingCategories) ? spendingCategories : []

  const normalized = spendingArray.map((category) => {
    const amount = parseFloat(category.amount ?? '0') || 0
    return { ...category, amount }
  })

  const sorted = [...normalized].sort((a, b) => b.amount - a.amount)

  const top4 = sorted.slice(0, 4)
  const rest = sorted.slice(4)

  const totalAmount = sorted.reduce((sum, c) => sum + c.amount, 0)

  const otherAmount = rest.reduce((sum, c) => sum + c.amount, 0)

  const rows =
    otherAmount > 0
      ? [
          ...top4,
          {
            category_id: 'other',
            name: 'Other',
            amount: otherAmount,
          },
        ]
      : top4

  return { rows, totalAmount }
}
