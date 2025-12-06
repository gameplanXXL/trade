import { Button } from '@/components/ui/button'
import { Info, Pause, XCircle } from 'lucide-react'

interface QuickActionsProps {
  onAction: (action: 'details' | 'pause' | 'close') => void
}

/**
 * QuickActions Component
 *
 * Provides quick action buttons for team instances:
 * - Details: View detailed metrics and trade history
 * - Pause: Pause trading operations
 * - Close: Close all open positions (critical action)
 *
 * Touch-optimized with 48px minimum height on mobile devices
 */
export function QuickActions({ onAction }: QuickActionsProps) {
  return (
    <div className="flex w-full gap-2">
      <Button
        variant="outline"
        size="sm"
        onClick={() => onAction('details')}
        className="flex-1 min-h-[48px] md:min-h-0"
      >
        <Info className="mr-1 h-4 w-4" />
        Details
      </Button>

      <Button
        variant="outline"
        size="sm"
        onClick={() => onAction('pause')}
        className="flex-1 min-h-[48px] md:min-h-0"
      >
        <Pause className="mr-1 h-4 w-4" />
        Pause
      </Button>

      <Button
        variant="destructive"
        size="sm"
        onClick={() => onAction('close')}
        className="flex-1 min-h-[48px] md:min-h-0"
      >
        <XCircle className="mr-1 h-4 w-4" />
        Close
      </Button>
    </div>
  )
}
