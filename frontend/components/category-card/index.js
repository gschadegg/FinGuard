'use client'

import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { EllipsisVertical } from 'lucide-react'
import { cn } from '@/lib/utils'

const formatCurrency = (n) =>
  new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(n)

export default function BudgetCategoryCard({
  categoryId,
  name = '',
  spent = 0,
  budget = 0,
  onEdit,
  onDelete,
}) {
  const clamped = Math.max(0, Math.min(spent, budget))
  const percentage = budget > 0 ? Math.round((clamped / budget) * 100) : 0

  const available = Math.max(0, budget - spent)
  const overspent = spent > budget

  return (
    <Card
      className="overflow-hidden py-0 mb-2"
      data-testid={`category-card-${categoryId}`}
      data-name={name}
    >
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          <div className="min-w-0 flex-1 mr-12">
            <div className="flex items-center justify-between">
              <p className="font-medium">{name}</p>

              <p className="text-sm text-muted-foreground">
                Spent {formatCurrency(spent)} of {formatCurrency(budget)}
              </p>
            </div>

            <div className="mt-2 h-2 w-full rounded-full bg-muted/70">
              <div
                className={cn(
                  'h-2 rounded-full transition-all',
                  overspent ? 'bg-destructive' : 'bg-green-500'
                )}
                style={{ width: `${Math.min(100, percentage)}%` }}
              />
            </div>
          </div>

          <div className="flex items-start gap-1 pl-2 shrink-0">
            <div className="text-right mr-1">
              <div className={cn('text-lg font-semibold', overspent && 'text-destructive')}>
                {overspent ? `-${formatCurrency(spent - budget)}` : formatCurrency(available)}
              </div>
              <div className="text-xs text-muted-foreground">
                {overspent ? 'Over' : 'Available'}
              </div>
            </div>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8 cursor-pointer">
                  <EllipsisVertical className="h-4 w-4" />
                  <span className="sr-only">Open menu</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-36">
                <DropdownMenuItem className="cursor-pointer" onClick={() => onEdit(categoryId)}>
                  Edit
                </DropdownMenuItem>
                <Separator className="my-2" />
                <DropdownMenuItem
                  onClick={() => onDelete(categoryId)}
                  className="text-destructive cursor-pointer"
                >
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
