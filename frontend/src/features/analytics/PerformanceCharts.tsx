import { useEffect, useRef, useState } from 'react'
import { createChart, LineSeries, type IChartApi, type ISeriesApi, type LineData, type UTCTimestamp } from 'lightweight-charts'
import { usePerformanceHistory, type Timeframe } from '@/hooks/usePerformanceHistory'
import { DrawdownChart } from './DrawdownChart'

interface PerformanceChartsProps {
  teamId: number
}

const TIMEFRAMES: { value: Timeframe; label: string }[] = [
  { value: '1D', label: '1 Day' },
  { value: '1W', label: '1 Week' },
  { value: '1M', label: '1 Month' },
  { value: 'All', label: 'All Time' },
]

export function PerformanceCharts({ teamId }: PerformanceChartsProps) {
  const [selectedTimeframe, setSelectedTimeframe] = useState<Timeframe>('1W')
  const { history, isLoading, error } = usePerformanceHistory(teamId, selectedTimeframe)

  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const seriesRef = useRef<ISeriesApi<'Line'> | null>(null)

  // Initialize chart
  useEffect(() => {
    if (!chartContainerRef.current) return

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { color: '#0a0e1a' },
        textColor: '#9ca3af',
      },
      grid: {
        vertLines: { color: '#1f2937' },
        horzLines: { color: '#1f2937' },
      },
      width: chartContainerRef.current.clientWidth,
      height: 300,
      rightPriceScale: {
        borderColor: '#1f2937',
        scaleMargins: {
          top: 0.1,
          bottom: 0.1,
        },
      },
      timeScale: {
        borderColor: '#1f2937',
        timeVisible: true,
        secondsVisible: false,
      },
      crosshair: {
        mode: 1, // Normal crosshair
        vertLine: {
          color: '#6b7280',
          width: 1,
          style: 2, // Dashed
        },
        horzLine: {
          color: '#6b7280',
          width: 1,
          style: 2, // Dashed
        },
      },
    })

    // Add P/L line series
    const lineSeries = chart.addSeries(LineSeries, {
      color: '#10b981',
      lineWidth: 2,
      priceFormat: {
        type: 'price',
        precision: 2,
        minMove: 0.01,
      },
    })

    chartRef.current = chart
    seriesRef.current = lineSeries

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current && chart) {
        chart.applyOptions({
          width: chartContainerRef.current.clientWidth,
        })
      }
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [])

  // Update chart data when history changes
  useEffect(() => {
    if (!seriesRef.current || history.length === 0) return

    const chartData: LineData[] = history.map(point => ({
      time: point.timestamp as UTCTimestamp,
      value: point.pnl,
    }))

    seriesRef.current.setData(chartData)

    // Fit content to show all data
    if (chartRef.current) {
      chartRef.current.timeScale().fitContent()
    }
  }, [history])

  if (error) {
    return (
      <div className="p-4 bg-red-900/20 border border-red-900 rounded-lg">
        <p className="text-sm text-red-400">Failed to load performance data</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Timeframe Selector */}
      <div className="flex items-center gap-2">
        <span className="text-sm text-gray-400">Timeframe:</span>
        <div className="flex gap-1 bg-gray-900 rounded-lg p-1">
          {TIMEFRAMES.map(({ value, label }) => (
            <button
              key={value}
              onClick={() => setSelectedTimeframe(value)}
              className={`
                px-3 py-1.5 text-xs font-medium rounded-md transition-colors
                ${
                  selectedTimeframe === value
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-gray-800'
                }
              `}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* P/L Chart */}
      <div className="space-y-2">
        <h3 className="text-sm font-medium text-gray-400">Profit & Loss</h3>
        {isLoading ? (
          <div className="h-[300px] bg-gray-900 rounded-lg animate-pulse" />
        ) : (
          <div ref={chartContainerRef} className="rounded-lg overflow-hidden" />
        )}
      </div>

      {/* Drawdown Chart */}
      {!isLoading && history.length > 0 && <DrawdownChart data={history} />}
    </div>
  )
}
