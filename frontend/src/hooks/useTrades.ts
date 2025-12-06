import { useState, useEffect } from 'react'
import type { Trade, TradeListResponse } from '@/types'

interface UseTradesOptions {
  page?: number
  pageSize?: number
  status?: 'open' | 'closed'
  symbol?: string
}

interface UseTradesReturn {
  trades: Trade[]
  total: number
  page: number
  pageSize: number
  isLoading: boolean
  error: Error | null
  refetch: () => void
}

export function useTrades(
  teamId: number,
  options: UseTradesOptions = {}
): UseTradesReturn {
  const {
    page = 1,
    pageSize = 20,
    status,
    symbol,
  } = options

  const [trades, setTrades] = useState<Trade[]>([])
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const [refetchTrigger, setRefetchTrigger] = useState(0)

  useEffect(() => {
    const fetchTrades = async () => {
      try {
        setIsLoading(true)
        setError(null)

        // Build query params
        const params = new URLSearchParams({
          page: page.toString(),
          page_size: pageSize.toString(),
        })
        if (status) params.append('status', status)
        if (symbol) params.append('symbol', symbol)

        const response = await fetch(
          `http://localhost:8000/api/teams/${teamId}/trades?${params.toString()}`
        )

        if (!response.ok) {
          throw new Error(`Failed to fetch trades: ${response.statusText}`)
        }

        const data: TradeListResponse = await response.json()
        setTrades(data.data)
        setTotal(data.meta.total)
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Unknown error'))
        setTrades([])
        setTotal(0)
      } finally {
        setIsLoading(false)
      }
    }

    fetchTrades()
  }, [teamId, page, pageSize, status, symbol, refetchTrigger])

  const refetch = () => {
    setRefetchTrigger(prev => prev + 1)
  }

  return {
    trades,
    total,
    page,
    pageSize,
    isLoading,
    error,
    refetch,
  }
}
