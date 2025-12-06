import { useEffect, useCallback } from 'react'
import { useTeamStore } from '@/stores/teamStore'
import { useAlertStore } from '@/stores/alertStore'
import { wsClient } from '@/lib/socket'
import { HealthBar } from './HealthBar'
import { TeamGrid } from './TeamGrid'
import { AlertList } from './AlertList'
import { toast } from '@/hooks/useToast'
import type { Alert, TeamStatusUpdate } from '@/types'

/**
 * DashboardView Component
 *
 * Main dashboard page showing:
 * - System health status (HealthBar)
 * - Active teams grid (TeamGrid)
 * - System alerts (AlertList)
 *
 * Data is fetched from Zustand store and updated via WebSocket
 */
export function DashboardView() {
  const { teams, fetchTeams, updateTeamStatus, isLoading, error } = useTeamStore()
  const { alerts, addAlert, removeAlert } = useAlertStore()

  // WebSocket callbacks
  const handleAlert = useCallback(
    (alert: Alert) => {
      addAlert(alert)

      // Show toast notification for new alerts
      const severityVariant = {
        crash: 'destructive',
        warning: 'warning',
        info: 'info',
      } as const

      toast({
        variant: severityVariant[alert.severity],
        title: alert.severity === 'crash' ? 'Critical Alert' : alert.severity === 'warning' ? 'Warning' : 'Info',
        description: alert.message,
      })
    },
    [addAlert]
  )

  const handleTeamStatusChanged = useCallback(
    (statusUpdate: TeamStatusUpdate) => {
      updateTeamStatus(statusUpdate.team_id, statusUpdate)
    },
    [updateTeamStatus]
  )

  // Fetch teams on mount
  useEffect(() => {
    fetchTeams()
  }, [fetchTeams])

  // WebSocket connection lifecycle
  useEffect(() => {
    // Connect WebSocket
    wsClient.connect()

    // Subscribe to alert events
    wsClient.onAlert(handleAlert)
    wsClient.onTeamStatusChanged(handleTeamStatusChanged)

    // Cleanup on unmount
    return () => {
      wsClient.offAlert(handleAlert)
      wsClient.offTeamStatusChanged(handleTeamStatusChanged)
      wsClient.disconnect()
    }
  }, [handleAlert, handleTeamStatusChanged])

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-background">
        <div className="mx-auto max-w-7xl px-6 py-12">
          <div className="rounded-lg border border-critical bg-critical bg-opacity-10 p-6 text-center">
            <h2 className="mb-2 text-xl font-semibold text-critical">
              Error Loading Dashboard
            </h2>
            <p className="text-text-secondary">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  // Loading state - show skeleton
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <HealthBar teams={[]} />
        <div className="mx-auto max-w-7xl px-6 py-12">
          <div className="animate-pulse space-y-4">
            <div className="h-8 w-48 rounded bg-surface"></div>
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-48 rounded-lg bg-surface"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <HealthBar teams={teams} />
      <TeamGrid teams={teams} />
      <AlertList alerts={alerts} onDismiss={removeAlert} />
    </div>
  )
}
