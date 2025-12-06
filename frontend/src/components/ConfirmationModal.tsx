import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'

interface ConfirmationModalProps {
  open: boolean
  onOpenChange?: (open: boolean) => void
  title: string
  description: string
  confirmText?: string
  cancelText?: string
  variant?: 'default' | 'destructive' | 'warning'
  onConfirm: () => void
  onCancel: () => void
  isLoading?: boolean
}

/**
 * Reusable Confirmation Modal Component
 *
 * Used for critical actions that require user confirmation.
 * Supports different variants for visual feedback:
 * - default: Regular confirmation (blue)
 * - destructive: Dangerous action (red)
 * - warning: Warning action (yellow/orange)
 */
export function ConfirmationModal({
  open,
  onOpenChange,
  title,
  description,
  confirmText = 'Bestätigen',
  cancelText = 'Abbrechen',
  variant = 'default',
  onConfirm,
  onCancel,
  isLoading = false,
}: ConfirmationModalProps) {
  const handleOpenChange = (newOpen: boolean) => {
    if (!newOpen && !isLoading) {
      onCancel()
    }
    onOpenChange?.(newOpen)
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>{description}</DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button variant="outline" onClick={onCancel} disabled={isLoading}>
            {cancelText}
          </Button>
          <Button
            variant={variant === 'default' ? 'default' : 'destructive'}
            onClick={onConfirm}
            disabled={isLoading}
          >
            {isLoading ? 'Wird ausgeführt...' : confirmText}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
