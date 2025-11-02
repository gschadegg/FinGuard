'use client'

import { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'

export default function DeleteConfirmationModal({ open, onOpenChange, selectedItem, onConfirm }) {
  const [submitting, setSubmitting] = useState(false)

  async function handleConfirm() {
    try {
      setSubmitting(true)
      await onConfirm?.(selectedItem)
      onOpenChange?.(false)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[440px]">
        <DialogHeader>
          <DialogTitle>Delete Category</DialogTitle>
          <DialogDescription>
            Are you sure you want to delete the category{' '}
            {selectedItem?.name ? (
              <span className="font-medium">{selectedItem?.name}</span>
            ) : (
              'this item'
            )}
            ?
            <br />
            <span className="text-destructive">This action cannot be undone.</span>
          </DialogDescription>
        </DialogHeader>

        <DialogFooter className="gap-2">
          <Button
            className={'cursor-pointer'}
            type="button"
            variant="secondary"
            onClick={() => onOpenChange(false)}
            disabled={submitting}
          >
            Cancel
          </Button>
          <Button
            className={'cursor-pointer'}
            type="button"
            variant="destructive"
            onClick={handleConfirm}
            disabled={submitting}
          >
            {submitting ? 'Deleting...' : 'Delete'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
