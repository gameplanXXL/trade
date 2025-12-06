import { useEffect } from 'react'
import type { Alert } from '@/types'
import { AlertCircle, AlertTriangle, Info, X } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface AlertCardProps {
  alert: Alert
  onDismiss: (alertId: string) => void
  teamName?: string
}

/**
 * AlertCard Component
 *
 * Individual alert card with:
 * - Severity-based styling (crash: red, warning: orange, info: blue)
 * - Dismiss button
 * - Timestamp
 * - Optional team name
 * - Auto-dismiss for warning (30s) and info (10s)
 */
export function AlertCard({ alert, onDismiss, teamName }: AlertCardProps) {
  // Auto-dismiss logic
  useEffect(() => {
    let timer: NodeJS.Timeout | null = null

    if (alert.severity === 'warning') {
      timer = setTimeout(() => {
        onDismiss(alert.id)
      }, 30000) // 30 seconds
    } else if (alert.severity === 'info') {
      timer = setTimeout(() => {
        onDismiss(alert.id)
      }, 10000) // 10 seconds
    }
    // crash alerts stay until manually dismissed

    return () => {
      if (timer) {
        clearTimeout(timer)
      }
    }
  }, [alert.id, alert.severity, onDismiss])

  const severityConfig = {
    crash: {
      icon: AlertCircle,
      bgColor: 'bg-critical',
      textColor: 'text-white',
      iconColor: 'text-white',
      borderColor: 'border-critical',
      // Optional: pulsing animation for critical alerts
      animation: 'animate-pulse',
    },
    warning: {
      icon: AlertTriangle,
      bgColor: 'bg-warning',
      textColor: 'text-gray-900',
      iconColor: 'text-gray-900',
      borderColor: 'border-warning',
      animation: '',
    },
    info: {
      icon: Info,
      bgColor: 'bg-accent',
      textColor: 'text-white',
      iconColor: 'text-white',
      borderColor: 'border-accent',
      animation: '',
    },
  }

  const config = severityConfig[alert.severity]
  const Icon = config.icon

  return (
    <div
      className={`
        ${config.bgColor} ${config.borderColor} ${config.animation}
        flex items-start gap-3 rounded-lg border-2 p-4 shadow-lg
        transition-all duration-300 hover:shadow-xl
      `}
    >
      <Icon className={`mt-0.5 h-5 w-5 flex-shrink-0 ${config.iconColor}`} />
      <div className="flex-1">
        <p className={`text-sm font-semibold ${config.textColor}`}>
          {alert.message}
        </p>
        <div className="mt-1 flex items-center gap-2 text-xs opacity-90">
          {teamName && (
            <>
              <span className={config.textColor}>{teamName}</span>
              <span className={config.textColor}>•</span>
            </>
          )}
          <span className={config.textColor}>
            {new Date(alert.timestamp).toLocaleTimeString('de-DE', {
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit',
            })}
          </span>
        </div>
      </div>
      <Button
        variant="ghost"
        size="sm"
        className="h-6 w-6 p-0 hover:bg-white hover:bg-opacity-20"
        onClick={() => onDismiss(alert.id)}
      >
        <X className={`h-4 w-4 ${config.iconColor}`} />
      </Button>
    </div>
  )
}
