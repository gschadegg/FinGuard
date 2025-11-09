/* eslint-disable react-hooks/rules-of-hooks */
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

import { MoreVertical } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Loader2, Loader, ShieldCheck, ShieldAlert } from 'lucide-react'

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

import { useAuth } from '@/components/auth/AuthProvider'
import RiskReviewModal from '@/components/modals/RiskReviewModal'

import { ASSIGN_BUDGET_CATEGORY, SET_FRAUD_REVIEW } from '@/lib/api_urls'
import clsx from 'clsx'
import { useRollups } from '../rollups/RollupProvider'

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
      const notify = useNotify()

      const { makeAuthRequest } = useAuth()

      const [saving, setSaving] = useState(false)

      const _txn_id = row.original.id

      const options = table.options.meta.options.category
      const currentId = String(row.original.budget_category_id ?? '')
      const currentLabel = row.original.budget_category_name ?? 'Unassigned'

      async function onChange(nextVal) {
        if (nextVal === currentId) return
        const rowIndex = row.index
        const nextLabel =
          options.find((o) => String(o.value) === String(nextVal))?.label ?? currentLabel
        table.options.meta.updateRow(rowIndex, {
          category_id: nextVal === '' ? null : Number(nextVal),
          category: nextLabel,
        })
        setSaving(true)

        try {
          const res = await makeAuthRequest(ASSIGN_BUDGET_CATEGORY(_txn_id), {
            method: 'PUT',
            body: JSON.stringify({ category_id: nextVal === 'null' ? null : Number(nextVal) }),
          })
          if (res?.ok) {
            table.options.meta.updateRow(rowIndex, {
              category_id: currentId === 'null' ? null : Number(currentId),
              category: currentLabel,
            })
            notify({
              type: 'success',
              title: 'Category Assigned',
              message: 'Category has been assigned to transaction.',
            })
          } else {
            notify({
              type: 'error',
              title: 'Error Assigning Category',
              message: 'There was an issue assigning a category, please try again',
            })
          }
        } catch (_) {
          table.options.meta.updateRow(rowIndex, {
            category_id: currentId === 'null' ? null : Number(currentId),
            category: currentLabel,
          })
          notify({
            type: 'error',
            title: 'Error Assigning Category',
            message: 'There was an issue assigning a category, please try again',
          })
        } finally {
          setSaving(false)
        }
      }

      return (
        <div className="flex items-center gap-2">
          <Select defaultValue={currentId ?? 'pending'} onValueChange={onChange} disabled={saving}>
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
      const { is_fraud_suspected, fraud_score, risk_level, fraud_review_status } = row.original

      const score = fraud_score !== null ? Number(fraud_score) : null

      const label =
        score === null
          ? 'In Progress'
          : fraud_review_status && fraud_review_status !== 'pending'
            ? 'Reviewed'
            : is_fraud_suspected
              ? 'High'
              : risk_level === 'medium'
                ? 'Medium'
                : risk_level === 'low'
                  ? 'Low'
                  : 'No Risk'

      let icon, colorClass

      switch (label) {
        case 'In Progress':
          icon = <Loader className="text-sky-500" />
          colorClass = 'border-gray-400/40'
          break
        case 'Low':
          icon = <ShieldCheck className="text-green-600" />
          colorClass = 'border-gray-400/40'
          break
        case 'Medium':
          icon = <ShieldCheck className="text-amber-600" />
          colorClass = 'text-amber-600 border-gray-400/40'
          break
        case 'High':
          icon = <ShieldAlert className="text-red-600" />
          colorClass = 'text-red-600 border-gray-400/40'
          break
        case 'Reviewed':
          if (fraud_review_status === 'fraud') {
            icon = <ShieldAlert className="text-red-600" />
            colorClass = 'text-red-600 border-gray-400/40'
          } else {
            icon = <ShieldCheck className=" text-green-600" />
            colorClass = 'text-green-600 border-gray-400/40'
          }
          break
        default:
          icon = <ShieldCheck className="text-gray-500" />
          colorClass = 'text-gray-600 border-gray-400/40'
      }
      return (
        <Badge variant="outline" className={clsx('text-right font-medium', colorClass)}>
          {icon}
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
    cell: ({ row, table }) => {
      const txn = row.original
      const { makeAuthRequest } = useAuth()
      const { refresh } = useRollups()
      const notify = useNotify()
      const [open, setOpen] = useState(false)
      const [saving, setSaving] = useState(false)

      const suspected = !!txn.is_fraud_suspected
      const riskLevel = txn.risk_level || (suspected ? 'high' : 'low')
      const defaultAction = suspected ? 'not_fraud' : 'fraud'

      const actionLabel = 'Risk Review'

      async function handleSubmit(status) {
        try {
          setSaving(true)

          if (table?.options?.meta?.updateRow) {
            table.options.meta.updateRow(row.index, { fraud_review_status: status })
          }

          const res = await makeAuthRequest(SET_FRAUD_REVIEW(txn.id), {
            method: 'PUT',
            body: JSON.stringify({ status }),
          })

          if (!res?.ok) {
            if (table?.options?.meta?.updateRow) {
              table.options.meta.updateRow(row.index, { fraud_review_status: 'pending' })
            }
            notify({
              type: 'error',
              title: 'Risk Review Failed',
              message: 'We are experiencing issues saving your review. Please try again.',
            })
            return
          }

          notify({
            type: 'success',
            title: 'Risk Review Saved',
            message:
              status === 'fraud'
                ? 'Transaction has been marked as Fraudulent.'
                : 'Transaction has been marked as Safe.',
          })
          refresh()
        } catch (_e) {
          if (table?.options?.meta?.updateRow) {
            table.options.meta.updateRow(row.index, { fraud_review_status: 'pending' })
          }
          notify({
            type: 'error',
            title: 'Risk Review Failed',
            message: 'We are experiencing issues saving your review. Please try again.',
          })
        } finally {
          setSaving(false)
        }
      }

      return (
        <>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-8 w-8 p-0 cursor-pointer" disabled={saving}>
                <span className="sr-only">Open menu</span>
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>Actions</DropdownMenuLabel>
              <DropdownMenuItem className="cursor-pointer" onClick={() => setOpen(true)}>
                {actionLabel}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          <RiskReviewModal
            open={open}
            onOpenChange={setOpen}
            riskLevel={riskLevel}
            institution={txn.institution_name || null}
            defaultAction={defaultAction}
            onSubmit={handleSubmit}
          />
        </>
      )
    },
  },
]
