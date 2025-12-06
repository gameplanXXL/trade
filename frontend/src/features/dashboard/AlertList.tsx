import type { Alert } from '@/types'
import { AlertCard } from './AlertCard'
import { useTeamStore } from '@/stores/teamStore'

interface AlertListProps {
  alerts: Alert[]
  onDismiss: (alertId: string) => void
}

/**
 * Priority mapping for sorting
 * crash = 0 (highest), warning = 1, info = 2 (lowest)
 */
const SEVERITY_PRIORITY = {
  crash: 0,
  warning: 1,
  info: 2,
} as const

/**
 * AlertList Component
 *
 * Displays system alerts in fixed position (bottom-right) with:
 * - Priority-based sorting (crash > warning > info)
 * - Maximum 5 visible alerts
 * - Individual AlertCard components with auto-dismiss
 */
export function AlertList({ alerts, onDismiss }: AlertListProps) {
  const { teams } = useTeamStore()

  if (alerts.length === 0) {
    return null
  }

  // Sort alerts by priority (crash first, then warning, then info)
  const sortedAlerts = [...alerts].sort((a, b) => {
    return SEVERITY_PRIORITY[a.severity] - SEVERITY_PRIORITY[b.severity]
  })

  // Limit to maximum 5 alerts
  const visibleAlerts = sortedAlerts.slice(0, 5)

  // Helper to get team name
  const getTeamName = (teamId: number): string | undefined => {
    return teams.find((team) => team.id === teamId)?.name
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2">
      {visibleAlerts.map((alert) => (
        <AlertCard
          key={alert.id}
          alert={alert}
          onDismiss={onDismiss}
          teamName={getTeamName(alert.team_id)}
        />
      ))}
    </div>
  )
}
