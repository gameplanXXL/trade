import { useState, useEffect } from 'react'
import type { Team } from '@/types'

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

        const data = await response.json()
        setTeam(data.data)
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
