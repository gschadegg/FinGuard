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

export function TransactionDataTable({ columns, pager }) {
  const [categoryOptions, _setCategoryOptions] = useState([
    { value: 'unassigned', label: 'Unassigned' },
    { value: 'groceries', label: 'Groceries' },
    { value: 'insurance', label: 'Insurance' },
    { value: 'rent', label: 'Rent' },
  ])

  useEffect(() => {
    // FETCH AND SET CATEGORY OPTIONS
  }, [])

  const table = useReactTable({
    data: pager.rows ?? [],
    columns,
    pageCount: pager.pageCount,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    meta: {
      updateRow: (rowIndex, updates) => {
        setData((old) => old.map((r, i) => (i === rowIndex ? { ...r, ...updates } : r)))
      },
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
