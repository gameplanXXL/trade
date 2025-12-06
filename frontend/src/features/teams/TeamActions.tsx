import { useState } from 'react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Button } from '@/components/ui/button'
import { ConfirmationModal } from '@/components/ConfirmationModal'
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
  const openPositionsCount = 0 as number
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

      {/* Confirmation Modal: Close Positions */}
      <ConfirmationModal
        open={confirmDialog === 'close_positions'}
        title="Alle Positionen schließen?"
        description={
          openPositionsCount > 0
            ? `${openPositionsCount} ${openPositionsCount === 1 ? 'Position' : 'Positionen'} mit ${formatCurrency(exposure)} Exposure werden geschlossen.`
            : 'Alle offenen Positionen dieses Teams werden geschlossen.'
        }
        confirmText="Positionen schließen"
        variant="warning"
        onConfirm={handleClosePositions}
        onCancel={() => setConfirmDialog(null)}
        isLoading={closePositions.isPending}
      />

      {/* Confirmation Modal: Stop Team */}
      <ConfirmationModal
        open={confirmDialog === 'stop'}
        title="Team stoppen?"
        description={`Team "${team.name}" wird gestoppt. Alle offenen Positionen werden geschlossen und das Team kann nicht mehr automatisch handeln.`}
        confirmText="Team stoppen"
        variant="destructive"
        onConfirm={handleStop}
        onCancel={() => setConfirmDialog(null)}
        isLoading={stopTeam.isPending}
      />
    </>
  )
}
