import { TrendingUp, TrendingDown } from 'lucide-react'

interface PnLDisplayProps {
  value: number
  percent: number
}

/**
 * PnLDisplay Component
 *
 * Displays P/L value and percentage with color coding:
 * - Green: P/L > 0%
 * - Red: -5% < P/L <= 0%
 * - Dark Red: P/L <= -5%
 *
 * Uses JetBrains Mono for numbers as per UX Design spec
 */
export function PnLDisplay({ value, percent }: PnLDisplayProps) {
  const isProfitable = percent > 0
  const isCritical = percent <= -5

  // Color coding based on performance
  let colorClass = 'text-success'
  if (isCritical) {
    colorClass = 'text-critical'
  } else if (!isProfitable) {
    colorClass = 'text-warning'
  }

  return (
    <div className="mb-4">
      <div className="flex items-center justify-between">
        <span className="text-sm text-text-secondary">P/L</span>
        <div className="flex items-center gap-2">
          {isProfitable ? (
            <TrendingUp className={`h-5 w-5 ${colorClass}`} />
          ) : (
            <TrendingDown className={`h-5 w-5 ${colorClass}`} />
          )}
        </div>
      </div>

      {/* Large P/L percentage in JetBrains Mono */}
      <div className={`mt-2 font-mono text-3xl font-bold ${colorClass}`}>
        {isProfitable ? '+' : ''}
        {percent.toFixed(2)}%
      </div>

      {/* Absolute value */}
      <div className={`font-mono text-sm ${isProfitable ? 'text-success-muted' : isCritical ? 'text-critical-muted' : 'text-warning-muted'}`}>
        {isProfitable ? '+' : ''}${value.toFixed(2)}
      </div>
    </div>
  )
}
