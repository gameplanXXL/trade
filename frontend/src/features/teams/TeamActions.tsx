import { useState } from 'react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { MoreVertical, Pause, Play, StopCircle, XCircle } from 'lucide-react'
import type { Team } from '@/types'
import {
  usePauseTeam,
  useResumeTeam,
  useStopTeam,
  useClosePositions,
} from '@/hooks/useTeamActions'

interface TeamActionsProps {
  team: Team
  onComplete?: () => void
}

type ConfirmAction = 'stop' | 'close_positions' | null

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
  }).format(value)
}

/**
 * TeamActions Component
 *
 * Provides dropdown menu with team actions:
 * - Pause (when active)
 * - Resume (when paused)
 * - Close Positions (with confirmation)
 * - Stop Team (with confirmation)
 *
 * Features:
 * - Optimistic UI updates via TanStack Query
 * - Confirmation dialogs for critical actions
 * - Error handling with toast notifications
 * - Disabled state during mutations
 */
export function TeamActions({ team, onComplete }: TeamActionsProps) {
  const [confirmDialog, setConfirmDialog] = useState<ConfirmAction>(null)
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)

  const pauseTeam = usePauseTeam()
  const resumeTeam = useResumeTeam()
  const stopTeam = useStopTeam()
  const closePositions = useClosePositions()

  const isLoading =
    pauseTeam.isPending ||
    resumeTeam.isPending ||
    stopTeam.isPending ||
    closePositions.isPending

  const handlePause = () => {
    pauseTeam.mutate(team.id, {
      onSuccess: () => {
        setIsDropdownOpen(false)
        onComplete?.()
      },
    })
  }

  const handleResume = () => {
    resumeTeam.mutate(team.id, {
      onSuccess: () => {
        setIsDropdownOpen(false)
        onComplete?.()
      },
    })
  }

  const handleStop = () => {
    stopTeam.mutate(team.id, {
      onSuccess: () => {
        setConfirmDialog(null)
        setIsDropdownOpen(false)
        onComplete?.()
      },
      onError: () => {
        setConfirmDialog(null)
      },
    })
  }

  const handleClosePositions = () => {
    closePositions.mutate(team.id, {
      onSuccess: () => {
        setConfirmDialog(null)
        setIsDropdownOpen(false)
        onComplete?.()
      },
      onError: () => {
        setConfirmDialog(null)
      },
    })
  }

  // TODO: Get actual open positions count from team data
  const openPositionsCount = 0
  const exposure = team.budget - (team.current_budget ?? team.budget) // Estimated exposure

  return (
    <>
      <DropdownMenu open={isDropdownOpen} onOpenChange={setIsDropdownOpen}>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon" disabled={isLoading}>
            <MoreVertical className="h-4 w-4" />
            <span className="sr-only">Team-Aktionen</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          {team.status === 'active' && (
            <DropdownMenuItem onClick={handlePause} disabled={isLoading}>
              <Pause className="mr-2 h-4 w-4" />
              Pausieren
            </DropdownMenuItem>
          )}
          {team.status === 'paused' && (
            <DropdownMenuItem onClick={handleResume} disabled={isLoading}>
              <Play className="mr-2 h-4 w-4" />
              Fortsetzen
            </DropdownMenuItem>
          )}
          <DropdownMenuSeparator />
          <DropdownMenuItem
            onClick={() => setConfirmDialog('close_positions')}
            disabled={isLoading}
            className="text-warning focus:text-warning"
          >
            <XCircle className="mr-2 h-4 w-4" />
            Positionen schließen
          </DropdownMenuItem>
          <DropdownMenuItem
            onClick={() => setConfirmDialog('stop')}
            disabled={isLoading}
            className="text-critical focus:text-critical"
          >
            <StopCircle className="mr-2 h-4 w-4" />
            Team stoppen
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Confirmation Dialog: Close Positions */}
      <Dialog
        open={confirmDialog === 'close_positions'}
        onOpenChange={(open) => !open && setConfirmDialog(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Alle Positionen schließen?</DialogTitle>
            <DialogDescription>
              {openPositionsCount > 0 ? (
                <>
                  {openPositionsCount} {openPositionsCount === 1 ? 'Position' : 'Positionen'} mit{' '}
                  {formatCurrency(exposure)} Exposure werden geschlossen.
                </>
              ) : (
                'Alle offenen Positionen dieses Teams werden geschlossen.'
              )}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setConfirmDialog(null)}
              disabled={isLoading}
            >
              Abbrechen
            </Button>
            <Button
              variant="destructive"
              onClick={handleClosePositions}
              disabled={isLoading}
            >
              {closePositions.isPending ? 'Schließe...' : 'Positionen schließen'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Confirmation Dialog: Stop Team */}
      <Dialog
        open={confirmDialog === 'stop'}
        onOpenChange={(open) => !open && setConfirmDialog(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Team stoppen?</DialogTitle>
            <DialogDescription>
              Team "{team.name}" wird gestoppt. Alle offenen Positionen werden geschlossen und
              das Team kann nicht mehr automatisch handeln.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setConfirmDialog(null)}
              disabled={isLoading}
            >
              Abbrechen
            </Button>
            <Button variant="destructive" onClick={handleStop} disabled={isLoading}>
              {stopTeam.isPending ? 'Stoppe...' : 'Team stoppen'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
