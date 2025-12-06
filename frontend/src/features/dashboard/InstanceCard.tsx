import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import type { Team } from '@/types'
import { PnLDisplay } from './PnLDisplay'
import { MetricsRow } from './MetricsRow'
import { QuickActions } from './QuickActions'
import { useNavigate } from 'react-router-dom'

interface InstanceCardProps {
  team: Team
  totalBudget: number
  onAction: (action: 'details' | 'pause' | 'close') => void
}

/**
 * Calculate size class based on budget proportion
 * - Large: > 30% of total budget
 * - Medium: 15-30% of total budget
 * - Small: < 15% of total budget
 */
function calculateSizeClass(budget: number, totalBudget: number): string {
  if (totalBudget === 0) return 'col-span-1'

  const budgetPercent = (budget / totalBudget) * 100

  if (budgetPercent > 30) {
    return 'col-span-2 row-span-2' // Large
  } else if (budgetPercent >= 15) {
    return 'col-span-1 row-span-2' // Medium
  } else {
    return 'col-span-1 row-span-1' // Small
  }
}

/**
 * Get status color class based on P/L percentage
 * - Success: P/L > 0%
 * - Warning: -5% < P/L <= 0%
 * - Critical: P/L <= -5%
 */
function getStatusColor(pnlPercent: number): string {
  if (pnlPercent > 0) {
    return 'bg-success bg-opacity-5 border-l-success'
  } else if (pnlPercent > -5) {
    return 'bg-warning bg-opacity-5 border-l-warning'
  } else {
    return 'bg-critical bg-opacity-5 border-l-critical'
  }
}

/**
 * InstanceCard Component
 *
 * Displays team instance with proportional sizing based on budget.
 * Features:
 * - Size reflects budget allocation (large >30%, medium 15-30%, small <15%)
 * - Color coding by P/L performance
 * - Large P/L display in JetBrains Mono
 * - Paper/Live badge
 * - Quick actions for details, pause, close
 */
export function InstanceCard({ team, totalBudget, onAction }: InstanceCardProps) {
  const navigate = useNavigate()
  const currentBudget = team.current_budget ?? team.budget
  const sizeClass = calculateSizeClass(currentBudget, totalBudget)
  const statusColor = getStatusColor(team.pnl_percent)

  // Determine mode from is_paper_trading if mode is not set
  const mode = team.mode ?? (team.is_paper_trading ? 'paper' : 'live')

  const handleAction = (action: 'details' | 'pause' | 'close') => {
    if (action === 'details') {
      navigate(`/teams/${team.id}`)
    } else {
      onAction(action)
    }
  }

  return (
    <Card
      className={cn(
        'border-l-4 transition-all hover:shadow-lg',
        sizeClass,
        statusColor
      )}
    >
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg text-text-primary">
              {team.name}
            </CardTitle>
            <p className="mt-1 text-sm text-text-secondary">{team.symbol}</p>
          </div>
          <Badge variant={mode === 'live' ? 'purple' : 'gray'}>
            {mode.toUpperCase()}
          </Badge>
        </div>
      </CardHeader>

      <CardContent>
        {/* P/L Display - Large and prominent */}
        <PnLDisplay value={team.current_pnl} percent={team.pnl_percent} />

        {/* Budget Information */}
        <div className="mb-4 flex items-center justify-between">
          <span className="text-sm text-text-secondary">Budget</span>
          <span className="font-mono text-sm font-medium text-text-primary">
            ${currentBudget.toLocaleString()}
          </span>
        </div>

        {/* Trading Metrics */}
        <MetricsRow winRate={team.win_rate} maxDrawdown={team.max_drawdown} />
      </CardContent>

      <CardFooter>
        <QuickActions onAction={handleAction} />
      </CardFooter>
    </Card>
  )
}
