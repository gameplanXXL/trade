import { useState, useEffect } from 'react'
import type { Team } from '@/types'

interface BackendTeamResponse {
  id: number
  name: string
  template_name: string
  status: string
  mode: 'paper' | 'live'
  symbols: string[]
  initial_budget: string
  current_budget: string
  realized_pnl: string
  unrealized_pnl: string
  total_pnl: string
  trade_count: number
  open_positions: number
  created_at: string
  updated_at: string | null
}

function mapBackendToFrontend(backend: BackendTeamResponse): Team {
  const initialBudget = parseFloat(backend.initial_budget)
  const currentBudget = parseFloat(backend.current_budget)
  const totalPnl = parseFloat(backend.total_pnl)
  const pnlPercent = initialBudget > 0 ? (totalPnl / initialBudget) * 100 : 0

  return {
    id: backend.id,
    name: backend.name,
    status: backend.status as Team['status'],
    symbol: backend.symbols.join(', '),
    budget: initialBudget,
    current_budget: currentBudget,
    current_pnl: totalPnl,
    pnl_percent: pnlPercent,
    is_paper_trading: backend.mode === 'paper',
    mode: backend.mode,
    created_at: backend.created_at,
    updated_at: backend.updated_at || backend.created_at,
  }
}

export function useTeam(teamId: number) {
  const [team, setTeam] = useState<Team | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const fetchTeam = async () => {
      try {
        setIsLoading(true)
        const response = await fetch(`http://localhost:8000/api/teams/${teamId}`)

        if (!response.ok) {
          throw new Error(`Failed to fetch team: ${response.statusText}`)
        }

        const json = await response.json()
        const mappedTeam = mapBackendToFrontend(json.data)
        setTeam(mappedTeam)
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Unknown error'))
      } finally {
        setIsLoading(false)
      }
    }

    fetchTeam()
  }, [teamId])

  return { team, isLoading, error }
}
