import { create } from 'zustand'
import type { Team, Alert, TeamStatusUpdate } from '../types'

interface TeamStore {
  // State
  teams: Team[]
  alerts: Alert[]
  isLoading: boolean
  error: string | null

  // Actions
  setTeams: (teams: Team[]) => void
  updateTeamStatus: (teamId: number, status: TeamStatusUpdate) => void
  addAlert: (alert: Alert) => void
  removeAlert: (alertId: string) => void
  clearAlerts: () => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void

  // API Actions
  fetchTeams: () => Promise<void>
}

export const useTeamStore = create<TeamStore>((set) => ({
  // Initial State
  teams: [],
  alerts: [],
  isLoading: false,
  error: null,

  // Mutations
  setTeams: (teams) => set({ teams }),

  updateTeamStatus: (teamId, statusUpdate) =>
    set((state) => ({
      teams: state.teams.map((team) =>
        team.id === teamId
          ? {
              ...team,
              status: statusUpdate.status,
              current_pnl: statusUpdate.current_pnl ?? team.current_pnl,
              pnl_percent: statusUpdate.pnl_percent ?? team.pnl_percent,
              updated_at: new Date().toISOString(),
            }
          : team
      ),
    })),

  addAlert: (alert) =>
    set((state) => ({
      alerts: [alert, ...state.alerts],
    })),

  removeAlert: (alertId) =>
    set((state) => ({
      alerts: state.alerts.filter((alert) => alert.id !== alertId),
    })),

  clearAlerts: () => set({ alerts: [] }),

  setLoading: (loading) => set({ isLoading: loading }),

  setError: (error) => set({ error }),

  // API Fetch
  fetchTeams: async () => {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

    set({ isLoading: true, error: null })

    try {
      const response = await fetch(`${apiUrl}/api/teams`)

      if (!response.ok) {
        throw new Error(`Failed to fetch teams: ${response.statusText}`)
      }

      const data = await response.json()

      // Handle both direct array and wrapped response
      const teams = Array.isArray(data) ? data : data.data || []

      set({ teams, isLoading: false })
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred'
      console.error('Error fetching teams:', errorMessage)
      set({ error: errorMessage, isLoading: false })
    }
  },
}))

export default useTeamStore
