import { useMemo } from 'react'
import type { Team } from '@/types'
import { AlertCircle, AlertTriangle, CheckCircle } from 'lucide-react'

interface HealthBarProps {
  teams: Team[]
}

type HealthStatus = 'healthy' | 'warning' | 'critical'

interface HealthInfo {
  status: HealthStatus
  criticalCount: number
  warningCount: number
}

/**
 * HealthBar Component
 *
 * Displays overall system health based on team P/L:
 * - Green: All teams OK (P/L >= 0%)
 * - Yellow: At least 1 team with warning (0% > P/L > -5%)
 * - Red: At least 1 team critical (P/L <= -5%)
 */
export function HealthBar({ teams }: HealthBarProps) {
  const healthInfo = useMemo((): HealthInfo => {
    if (teams.length === 0) {
      return { status: 'healthy', criticalCount: 0, warningCount: 0 }
    }

    let criticalCount = 0
    let warningCount = 0

    for (const team of teams) {
      const pnl = team.pnl_percent

      if (pnl <= -5) {
        criticalCount++
      } else if (pnl < 0) {
        warningCount++
      }
    }

    // Determine overall status
    let status: HealthStatus = 'healthy'
    if (criticalCount > 0) {
      status = 'critical'
    } else if (warningCount > 0) {
      status = 'warning'
    }

    return { status, criticalCount, warningCount }
  }, [teams])

  const statusConfig = {
    healthy: {
      bgColor: 'bg-success',
      borderColor: 'border-success',
      textColor: 'text-success',
      icon: CheckCircle,
      label: 'All Systems Operational',
    },
    warning: {
      bgColor: 'bg-warning',
      borderColor: 'border-warning',
      textColor: 'text-warning',
      icon: AlertTriangle,
      label: 'Teams Need Attention',
    },
    critical: {
      bgColor: 'bg-critical',
      borderColor: 'border-critical',
      textColor: 'text-critical',
      icon: AlertCircle,
      label: 'Critical Teams Detected',
    },
  }

  const config = statusConfig[healthInfo.status]
  const Icon = config.icon

  return (
    <div
      className={`border-b-4 ${config.borderColor} bg-surface px-6 py-4 shadow-sm transition-colors`}
    >
      <div className="mx-auto flex max-w-7xl items-center justify-between">
        {/* Left: Status Indicator */}
        <div className="flex items-center gap-3">
          <div className={`rounded-full p-2 ${config.bgColor} bg-opacity-10`}>
            <Icon className={`h-6 w-6 ${config.textColor}`} />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-text-primary">
              System Health
            </h2>
            <p className={`text-sm font-medium ${config.textColor}`}>
              {config.label}
            </p>
          </div>
        </div>

        {/* Right: Badges */}
        <div className="flex items-center gap-3">
          {healthInfo.criticalCount > 0 && (
            <div className="flex items-center gap-2 rounded-lg bg-critical bg-opacity-10 px-3 py-2">
              <AlertCircle className="h-4 w-4 text-critical" />
              <span className="text-sm font-semibold text-critical">
                {healthInfo.criticalCount} Critical
              </span>
            </div>
          )}
          {healthInfo.warningCount > 0 && (
            <div className="flex items-center gap-2 rounded-lg bg-warning bg-opacity-10 px-3 py-2">
              <AlertTriangle className="h-4 w-4 text-warning" />
              <span className="text-sm font-semibold text-warning">
                {healthInfo.warningCount} Warning
              </span>
            </div>
          )}
          {teams.length > 0 && healthInfo.status === 'healthy' && (
            <div className="flex items-center gap-2 rounded-lg bg-success bg-opacity-10 px-3 py-2">
              <CheckCircle className="h-4 w-4 text-success" />
              <span className="text-sm font-semibold text-success">
                {teams.length} {teams.length === 1 ? 'Team' : 'Teams'} Active
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
