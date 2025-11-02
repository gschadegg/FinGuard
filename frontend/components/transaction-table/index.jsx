'use client'

import {
  flexRender,
  getCoreRowModel,
  useReactTable,
  getPaginationRowModel,
} from '@tanstack/react-table'
import { useState, useEffect } from 'react'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { DataTablePagination } from './pagination'
import TableSkeleton from './skeleton'

import { useAuth } from '@/components/auth/AuthProvider'
import { GET_BUDGET_CATEGORIES } from '@/lib/api_urls'
import { useNotify } from '@/components/notification/NotificationProvider'

export function TransactionDataTable({ columns, pager }) {
  const { makeAuthRequest } = useAuth()
  const notify = useNotify()
  const [categoryOptions, setCategoryOptions] = useState([{ value: 'null', label: 'Unassigned' }])

  useEffect(() => {
    let cancelled = false
    const fetchCategories = async () => {
      try {
        const res = await makeAuthRequest(GET_BUDGET_CATEGORIES)
        if (res?.ok) {
          const { categories = [] } = res
          if (categories.length > 0) {
            if (!cancelled) {
              setCategoryOptions([
                { value: 'null', label: 'Unassigned' },
                ...categories.map((c) => ({
                  value: String(c.id),
                  label: c.name,
                })),
              ])
            }
          }
        }
      } catch {
        if (!cancelled) {
          notify({
            type: 'error',
            title: 'Budget Error',
            message: 'Experienced issues fetching budget categories, please try again.',
          })
        }
      }
    }
    fetchCategories()
    return () => {
      cancelled = true
    }
  }, [makeAuthRequest, notify])

  const table = useReactTable({
    data: pager.rows ?? [],
    columns,
    pageCount: pager.pageCount,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    meta: {
      updateRow: (rowIndex, updates) => pager.updateRow(rowIndex, updates),
      options: { category: categoryOptions },
    },
    manualPagination: true,
    state: { pagination: { pageIndex: pager.pageIndex, pageSize: pager.pageSize } },
    onPaginationChange: (updater) => {
      const next =
        typeof updater === 'function'
          ? updater({ pageIndex: pager.pageIndex, pageSize: pager.pageSize })
          : updater
      if (next.pageSize !== pager.pageSize) pager.setPageSize(next.pageSize)
      if (next.pageIndex !== pager.pageIndex) pager.setPageIndex(next.pageIndex)
    },
  })

  return (
    <div>
      <div className="overflow-hidden rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
                    <TableHead key={header.id}>
                      {header.isPlaceholder
                        ? null
                        : flexRender(header.column.columnDef.header, header.getContext())}
                    </TableHead>
                  )
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {pager.isLoading ? (
              <TableSkeleton colSpan={columns.length} />
            ) : table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow key={row.id} data-state={row.getIsSelected() && 'selected'}>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-24 text-center">
                  No results.{`${JSON.stringify(pager)}`}
                  {pager?.error} {pager?.isLoading}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      <DataTablePagination table={table} loading={pager.isLoading} canNext={pager.hasMore} />
    </div>
  )
}
