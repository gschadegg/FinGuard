'use client'
import {
  Select,
  SelectTrigger,
  SelectContent,
  SelectItem,
  SelectValue,
} from '@/components/ui/select'
import { useNotify } from '@/components/notification/NotificationProvider'
import { useState } from 'react'

import { Loader } from 'lucide-react'
import { MoreVertical } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Loader2 } from 'lucide-react'

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

export const columns = [
  {
    accessorKey: 'merchant_name',
    header: 'Payee',
  },
  {
    accessorKey: 'name',
    header: 'Name',
  },
  {
    accessorKey: 'date',
    header: 'Date',
    cell: ({ row }) => {
      const raw = row.original.date
      const d = new Date(raw)
      const formatted = d.toLocaleDateString('en-US', {
        month: '2-digit',
        day: '2-digit',
        year: 'numeric',
      })
      return <span>{formatted}</span>
    },
  },
  {
    accessorKey: 'category',
    header: () => <div>Category</div>,
    cell: ({ row, table }) => {
      // eslint-disable-next-line react-hooks/rules-of-hooks
      const notify = useNotify()
      // eslint-disable-next-line react-hooks/rules-of-hooks
      const [saving, setSaving] = useState(false)
      const category = row.original.category
      const _category_id = row.original.category_id

      const options = table.options.meta.options.category
      const current = category ?? ''

      async function onChange(nextVal) {
        if (nextVal === current) return
        const rowIndex = row.index

        table.options.meta.updateRow(rowIndex, { category: nextVal })
        setSaving(true)

        try {
          // SEND UPDATE REQUEST HERE
          notify({
            type: 'success',
            title: 'Category Updated',
            message: 'Category for transaction has been updated.',
          })
        } catch (_) {
          table.options.meta.updateRow(rowIndex, { category: current })
          notify({
            type: 'error',
            title: 'Error Updating',
            message: 'There was an issue updating category, please try again',
          })
        } finally {
          setSaving(false)
        }
      }

      return (
        <div className="flex items-center gap-2">
          <Select defaultValue={current ?? 'pending'} onValueChange={onChange} disabled={saving}>
            <SelectTrigger className="h-8 w-[140px]">
              <SelectValue placeholder="Unassigned" />
            </SelectTrigger>
            <SelectContent>
              {options.map((o) => (
                <SelectItem key={o.value} value={String(o.value)}>
                  {o.label ?? o.value}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
        </div>
      )
    },
  },
  {
    accessorKey: 'pending',
    header: () => <div className="">Status</div>,
    cell: ({ row }) => {
      const is_pending = parseFloat(row.getValue('pending'))

      return (
        <Badge variant="outline" className="text-right font-medium">
          {is_pending ? 'Pending' : 'Cleared'}
        </Badge>
      )
    },
  },
  {
    accessorKey: 'is_fraud_suspected',
    header: () => <div>Risk Assessment</div>,
    cell: ({ row }) => {
      const { is_fraud_suspected, fraud_score } = row.original

      const score = fraud_score !== null ? Number(fraud_score) : null

      const label =
        score === null
          ? 'In Progress'
          : is_fraud_suspected && score >= 80
            ? 'High'
            : is_fraud_suspected && score >= 40
              ? 'Medium'
              : is_fraud_suspected && score > 0
                ? 'Low'
                : 'No Risk'

      return (
        <Badge variant="outline" className="text-right font-medium">
          <Loader className="text-sky-500" />
          {label}
        </Badge>
      )
    },
  },
  {
    accessorKey: 'amount',
    header: () => <div className="text-right">Amount</div>,
    cell: ({ row }) => {
      const amount = parseFloat(row.getValue('amount'))
      const formatted = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
      }).format(amount)

      return <div className="text-right font-medium">{formatted}</div>
    },
  },
  {
    id: 'actions',
    cell: ({ row }) => {
      const { is_fraud_suspected, _fraud_score } = row.original

      return (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="h-8 w-8 p-0 cursor-pointer">
              <span className="sr-only">Open menu</span>
              <MoreVertical className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>Actions</DropdownMenuLabel>
            {/* NEED THIS TO CHANGE BASED ON RISK LEVEL ONCE ADDED */}
            {is_fraud_suspected ? (
              <DropdownMenuItem className="cursor-pointer" onClick={() => {}}>
                Mark as Safe
              </DropdownMenuItem>
            ) : (
              <DropdownMenuItem className="cursor-pointer" onClick={() => {}}>
                Mark as Fraudulent
              </DropdownMenuItem>
            )}
            {/* <DropdownMenuSeparator />
            <DropdownMenuItem>Other Option</DropdownMenuItem> */}
          </DropdownMenuContent>
        </DropdownMenu>
      )
    },
  },
]
