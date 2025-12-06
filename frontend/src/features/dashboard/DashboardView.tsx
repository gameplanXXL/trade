import { useEffect } from 'react'
import { useTeamStore } from '@/stores/teamStore'
import { HealthBar } from './HealthBar'
import { TeamGrid } from './TeamGrid'
import { AlertList } from './AlertList'

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
  const { teams, alerts, fetchTeams, removeAlert, isLoading, error } = useTeamStore()

  // Fetch teams on mount
  useEffect(() => {
    fetchTeams()
  }, [fetchTeams])

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
