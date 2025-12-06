import type { Team } from '@/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { TrendingUp, TrendingDown, Activity } from 'lucide-react'

interface TeamGridProps {
  teams: Team[]
}

/**
 * TeamGrid Component
 *
 * Displays team cards in a responsive grid:
 * - Mobile: Stack (1 column)
 * - Desktop: Grid (2-3 columns)
 */
export function TeamGrid({ teams }: TeamGridProps) {
  if (teams.length === 0) {
    return (
      <div className="mx-auto max-w-7xl px-6 py-12">
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12 text-center">
            <div className="mb-6 rounded-full bg-surface-elevated p-6">
              <TrendingUp className="h-12 w-12 text-accent" />
            </div>
            <h3 className="mb-2 text-xl font-semibold text-text-primary">
              No Teams Configured
            </h3>
            <p className="max-w-md text-text-secondary">
              Create your first trading team to start monitoring the markets
              with AI-powered agents.
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-7xl px-6 py-8">
      <h2 className="mb-6 text-2xl font-bold text-text-primary">Active Teams</h2>

      {/* Responsive Grid: Stack on mobile, Grid on desktop */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {teams.map((team) => (
          <TeamCard key={team.id} team={team} />
        ))}
      </div>
    </div>
  )
}

/**
 * TeamCard Component
 *
 * Displays individual team information with P/L status
 */
function TeamCard({ team }: { team: Team }) {
  const isProfitable = team.pnl_percent >= 0
  const isCritical = team.pnl_percent <= -5
  const isWarning = team.pnl_percent < 0 && team.pnl_percent > -5

  // Determine card border color based on status
  let borderColorClass = 'border-border'
  if (isCritical) {
    borderColorClass = 'border-critical'
  } else if (isWarning) {
    borderColorClass = 'border-warning'
  } else if (isProfitable) {
    borderColorClass = 'border-success'
  }

  return (
    <Card className={`border-l-4 ${borderColorClass} transition-all hover:shadow-lg`}>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-lg text-text-primary">
              {team.name}
            </CardTitle>
            <p className="mt-1 text-sm text-text-secondary">{team.symbol}</p>
          </div>
          <div
            className={`rounded-full px-2 py-1 text-xs font-medium ${
              team.status === 'active'
                ? 'bg-success bg-opacity-10 text-success'
                : team.status === 'paused'
                  ? 'bg-warning bg-opacity-10 text-warning'
                  : 'bg-text-muted bg-opacity-10 text-text-muted'
            }`}
          >
            {team.status.toUpperCase()}
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {/* Budget */}
        <div className="mb-4 flex items-center justify-between">
          <span className="text-sm text-text-secondary">Budget</span>
          <span className="font-mono text-sm font-medium text-text-primary">
            ${team.budget.toLocaleString()}
          </span>
        </div>

        {/* P/L */}
        <div className="flex items-center justify-between">
          <span className="text-sm text-text-secondary">P/L</span>
          <div className="flex items-center gap-2">
            {isProfitable ? (
              <TrendingUp className="h-4 w-4 text-success" />
            ) : (
              <TrendingDown className="h-4 w-4 text-critical" />
            )}
            <span
              className={`font-mono text-sm font-bold ${
                isProfitable ? 'text-success' : 'text-critical'
              }`}
            >
              {isProfitable ? '+' : ''}
              {team.pnl_percent.toFixed(2)}%
            </span>
            <span
              className={`font-mono text-xs ${
                isProfitable ? 'text-success-muted' : 'text-critical-muted'
              }`}
            >
              (${team.current_pnl.toFixed(2)})
            </span>
          </div>
        </div>

        {/* Paper Trading Badge */}
        {team.is_paper_trading && (
          <div className="mt-3 flex items-center gap-1 text-xs text-text-muted">
            <Activity className="h-3 w-3" />
            <span>Paper Trading</span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
