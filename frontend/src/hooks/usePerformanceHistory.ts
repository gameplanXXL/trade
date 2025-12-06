import { useState, useEffect } from 'react'
import { apiClient } from '@/lib/api'

export type Timeframe = '1D' | '1W' | '1M' | 'All'

export interface PerformanceDataPoint {
  timestamp: number // Unix timestamp in seconds
  pnl: number
  drawdown: number
  balance: number
}

interface PerformanceMetricResponse {
  id: number
  team_instance_id: number
  timestamp: string
  period: string
  pnl: string
  pnl_percent: number
  win_rate: number
  sharpe_ratio: number | null
  max_drawdown: number
  trade_count: number
}

interface UsePerformanceHistoryReturn {
  history: PerformanceDataPoint[]
  isLoading: boolean
  error: Error | null
  refetch: () => void
}

// Map timeframe to period and calculate since timestamp
function getTimeframeParams(timeframe: Timeframe): { period: string; since?: string } {
  const now = new Date()
  
  switch (timeframe) {
    case '1D':
      const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000)
      return { period: 'hourly', since: oneDayAgo.toISOString() }
    case '1W':
      const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
      return { period: 'hourly', since: oneWeekAgo.toISOString() }
    case '1M':
      const oneMonthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
      return { period: 'daily', since: oneMonthAgo.toISOString() }
    case 'All':
    default:
      return { period: 'daily' }
  }
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

        const params = getTimeframeParams(timeframe)
        const queryString = new URLSearchParams({
          period: params.period,
          ...(params.since && { since: params.since }),
        }).toString()

        const response = await apiClient.get<PerformanceMetricResponse[]>(
          `/api/analytics/teams/${teamId}/history?${queryString}`
        )

        // Transform backend response to frontend format
        const transformedData: PerformanceDataPoint[] = response.data.map(metric => ({
          timestamp: Math.floor(new Date(metric.timestamp).getTime() / 1000), // Convert to Unix timestamp
          pnl: parseFloat(metric.pnl),
          drawdown: metric.max_drawdown,
          balance: parseFloat(metric.pnl), // Using pnl as balance for now
        }))

        setHistory(transformedData)
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
