import { useEffect, useRef } from 'react'
import { createChart, AreaSeries, type IChartApi, type ISeriesApi, type AreaData } from 'lightweight-charts'
import type { PerformanceDataPoint } from '@/hooks/usePerformanceHistory'

interface DrawdownChartProps {
  data: PerformanceDataPoint[]
}

export function DrawdownChart({ data }: DrawdownChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const seriesRef = useRef<ISeriesApi<any> | null>(null)

  useEffect(() => {
    if (!chartContainerRef.current) return

    // Create chart
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
      height: 200,
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
    })

    // Add area series with inverted colors (red for drawdown)
    const areaSeries = chart.addSeries(AreaSeries, {
      topColor: 'rgba(239, 68, 68, 0.5)',
      bottomColor: 'rgba(239, 68, 68, 0.1)',
      lineColor: '#ef4444',
      lineWidth: 2,
      priceFormat: {
        type: 'percent',
        precision: 2,
      },
    })

    chartRef.current = chart
    seriesRef.current = areaSeries

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

  useEffect(() => {
    if (!seriesRef.current || data.length === 0) return

    // Convert data to chart format
    // Drawdown is negative, so we invert it for display
    const chartData: AreaData[] = data.map(point => ({
      time: point.timestamp as any,
      value: -point.drawdown, // Invert to show as negative area
    }))

    seriesRef.current.setData(chartData)

    // Fit content
    if (chartRef.current) {
      chartRef.current.timeScale().fitContent()
    }
  }, [data])

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-medium text-gray-400">Drawdown</h3>
      <div ref={chartContainerRef} className="rounded-lg overflow-hidden" />
    </div>
  )
}
