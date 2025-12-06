interface MetricsRowProps {
  winRate?: number
  maxDrawdown?: number
}

/**
 * MetricsRow Component
 *
 * Displays compact trading metrics:
 * - Win Rate (percentage)
 * - Max Drawdown (percentage)
 *
 * Designed for minimal space usage in InstanceCard
 */
export function MetricsRow({ winRate, maxDrawdown }: MetricsRowProps) {
  return (
    <div className="flex items-center justify-between text-xs text-text-secondary">
      {winRate !== undefined && (
        <div className="flex items-center gap-1">
          <span>Win Rate:</span>
          <span className="font-mono font-medium text-text-primary">
            {winRate.toFixed(1)}%
          </span>
        </div>
      )}

      {maxDrawdown !== undefined && (
        <div className="flex items-center gap-1">
          <span>Max DD:</span>
          <span className={`font-mono font-medium ${maxDrawdown <= -5 ? 'text-critical' : 'text-text-primary'}`}>
            {maxDrawdown.toFixed(1)}%
          </span>
        </div>
      )}
    </div>
  )
}
