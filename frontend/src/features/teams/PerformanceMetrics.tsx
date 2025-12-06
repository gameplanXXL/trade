import { Card, CardContent } from '@/components/ui/card'
import type { Team } from '@/types'
import { TrendingUp, TrendingDown, Target, TrendingDown as MaxDrawdownIcon } from 'lucide-react'

interface PerformanceMetricsProps {
  team: Team
}

export function PerformanceMetrics({ team }: PerformanceMetricsProps) {
  const isProfitable = team.pnl_percent > 0
  const isCritical = team.pnl_percent <= -5

  // Color coding based on performance
  let pnlColorClass = 'text-success'
  if (isCritical) {
    pnlColorClass = 'text-critical'
  } else if (!isProfitable) {
    pnlColorClass = 'text-warning'
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      {/* P/L */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-text-secondary">P/L</span>
            {isProfitable ? (
              <TrendingUp className={`h-5 w-5 ${pnlColorClass}`} />
            ) : (
              <TrendingDown className={`h-5 w-5 ${pnlColorClass}`} />
            )}
          </div>
          <div className={`font-mono text-2xl font-bold ${pnlColorClass}`}>
            {isProfitable ? '+' : ''}
            {team.pnl_percent.toFixed(2)}%
          </div>
          <div className={`font-mono text-sm mt-1 ${isProfitable ? 'text-success-muted' : isCritical ? 'text-critical-muted' : 'text-warning-muted'}`}>
            {isProfitable ? '+' : ''}${team.current_pnl.toFixed(2)}
          </div>
        </CardContent>
      </Card>

      {/* Win Rate */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-text-secondary">Win Rate</span>
            <Target className="h-5 w-5 text-accent" />
          </div>
          <div className="font-mono text-2xl font-bold text-text-primary">
            {team.win_rate ? `${team.win_rate.toFixed(1)}%` : 'N/A'}
          </div>
          <div className="text-sm text-text-muted mt-1">
            of all trades
          </div>
        </CardContent>
      </Card>

      {/* Sharpe Ratio */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-text-secondary">Sharpe Ratio</span>
            <TrendingUp className="h-5 w-5 text-purple-500" />
          </div>
          <div className="font-mono text-2xl font-bold text-text-primary">
            N/A
          </div>
          <div className="text-sm text-text-muted mt-1">
            risk-adjusted return
          </div>
        </CardContent>
      </Card>

      {/* Max Drawdown */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-text-secondary">Max Drawdown</span>
            <MaxDrawdownIcon className="h-5 w-5 text-warning" />
          </div>
          <div className="font-mono text-2xl font-bold text-warning">
            {team.max_drawdown ? `${team.max_drawdown.toFixed(2)}%` : 'N/A'}
          </div>
          <div className="text-sm text-text-muted mt-1">
            peak to trough
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
