'use client'

import { useEffect, useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from '@/components/ui/select'

const GROUPS = ['Expenses', 'Entertainment', 'Savings']

export default function CategoryModal({ open, onOpenChange, mode = 'create', initial, onSubmit }) {
  const [name, setName] = useState(initial?.name || '')
  const [group, setGroup] = useState(initial?.group || '')
  const [allotted_amount, setAmount] = useState(initial?.allotted_amount || '')

  useEffect(() => {
    if (open) {
      setName(initial?.name || '')
      setGroup(initial?.group || '')
      setAmount(initial?.allotted_amount || '')
    }
  }, [open, initial])

  const title = mode === 'edit' ? 'Edit Category' : 'Add Category'
  const desc =
    mode === 'edit' ? 'Update your budget category here' : 'Add a new category to your budget'

  function handleSave(e) {
    e.preventDefault()
    if (!name.trim() || !group || !allotted_amount) return
    onSubmit?.(
      {
        name: name.trim(),
        group,
        allotted_amount,
      },
      initial?.id
    )
    onOpenChange?.(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[480px]">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>{desc}</DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSave} className="space-y-4">
          <div className="space-y-2">
            <Label>Category Group</Label>
            <Select value={group} onValueChange={setGroup}>
              <SelectTrigger>
                <SelectValue placeholder="Select a Category Group" />
              </SelectTrigger>
              <SelectContent>
                {GROUPS.map((g) => (
                  <SelectItem key={g} value={g}>
                    {g}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="cat-name">Category Name</Label>
            <Input
              id="cat-name"
              placeholder="e.g., Mortgage, Groceries, Pets"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="cat-amount">Assigned Amount</Label>
            <Input
              id="cat-amount"
              type="number"
              inputMode="decimal"
              step="0.01"
              min="0"
              placeholder="$ 0.00"
              value={allotted_amount}
              onChange={(e) => setAmount(e.target.value)}
              required
            />
          </div>

          <DialogFooter className="gap-2">
            <Button
              className={'cursor-pointer'}
              type="button"
              variant="secondary"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>
            <Button className={'cursor-pointer'} type="submit">
              Save
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
