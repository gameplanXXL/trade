import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api'
import type { AgentDecision } from '@/types'

interface UseAgentActivityOptions {
  agent?: string
  type?: string
  limit?: number
}

interface UseAgentActivityReturn {
  decisions: AgentDecision[]
  isLoading: boolean
  error: Error | null
  refetch: () => void
}

export function useAgentActivity(
  teamId: number,
  options: UseAgentActivityOptions = {}
): UseAgentActivityReturn {
  const { agent, type, limit = 100 } = options

  const [decisions, setDecisions] = useState<AgentDecision[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const [refetchTrigger, setRefetchTrigger] = useState(0)

  useEffect(() => {
    const fetchDecisions = async () => {
      try {
        setIsLoading(true)
        setError(null)

        // Build query params
        const params = new URLSearchParams({
          limit: limit.toString(),
        })
        if (agent) params.append('agent', agent)
        if (type) params.append('type', type)

        const response = await apiClient.get<AgentDecision[]>(
          `/api/analytics/teams/${teamId}/activity?${params.toString()}`
        )

        setDecisions(response.data)
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Unknown error'))
        setDecisions([])
      } finally {
        setIsLoading(false)
      }
    }

    fetchDecisions()
  }, [teamId, agent, type, limit, refetchTrigger])

  const refetch = () => {
    setRefetchTrigger(prev => prev + 1)
  }

  return {
    decisions,
    isLoading,
    error,
    refetch,
  }
}
