import { useState, useEffect } from 'react'

export type Timeframe = '1D' | '1W' | '1M' | 'All'

export interface PerformanceDataPoint {
  timestamp: number // Unix timestamp in seconds
  pnl: number
  drawdown: number
  balance: number
}

interface PerformanceHistoryResponse {
  data: PerformanceDataPoint[]
  meta: {
    timestamp: string
  }
}

interface UsePerformanceHistoryReturn {
  history: PerformanceDataPoint[]
  isLoading: boolean
  error: Error | null
  refetch: () => void
}

export function usePerformanceHistory(
  teamId: number,
  timeframe: Timeframe = 'All'
): UsePerformanceHistoryReturn {
  const [history, setHistory] = useState<PerformanceDataPoint[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const [refetchTrigger, setRefetchTrigger] = useState(0)

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setIsLoading(true)
        setError(null)

        const params = new URLSearchParams({
          timeframe: timeframe,
        })

        const response = await fetch(
          `http://localhost:8000/api/analytics/teams/${teamId}/history?${params.toString()}`
        )

        if (!response.ok) {
          throw new Error(`Failed to fetch performance history: ${response.statusText}`)
        }

        const data: PerformanceHistoryResponse = await response.json()
        setHistory(data.data)
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Unknown error'))
        setHistory([])
      } finally {
        setIsLoading(false)
      }
    }

    fetchHistory()
  }, [teamId, timeframe, refetchTrigger])

  const refetch = () => {
    setRefetchTrigger(prev => prev + 1)
  }

  return {
    history,
    isLoading,
    error,
    refetch,
  }
}
