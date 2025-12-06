import type { Alert } from '@/types'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertCircle, AlertTriangle, Info, X } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface AlertListProps {
  alerts: Alert[]
  onDismiss?: (alertId: string) => void
}

/**
 * AlertList Component
 *
 * Displays system alerts with severity-based styling
 * Placeholder implementation - will be enhanced in later stories
 */
export function AlertList({ alerts, onDismiss }: AlertListProps) {
  if (alerts.length === 0) {
    return null
  }

  return (
    <div className="mx-auto max-w-7xl px-6 pb-8">
      <Card>
        <CardHeader>
          <CardTitle className="text-lg text-text-primary">
            System Alerts
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {alerts.map((alert) => (
              <AlertItem
                key={alert.id}
                alert={alert}
                onDismiss={onDismiss}
              />
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

/**
 * AlertItem Component
 *
 * Individual alert with icon and dismiss button
 */
function AlertItem({
  alert,
  onDismiss,
}: {
  alert: Alert
  onDismiss?: (alertId: string) => void
}) {
  const severityConfig = {
    crash: {
      icon: AlertCircle,
      bgColor: 'bg-critical bg-opacity-10',
      borderColor: 'border-critical',
      textColor: 'text-critical',
      iconColor: 'text-critical',
    },
    warning: {
      icon: AlertTriangle,
      bgColor: 'bg-warning bg-opacity-10',
      borderColor: 'border-warning',
      textColor: 'text-warning',
      iconColor: 'text-warning',
    },
    info: {
      icon: Info,
      bgColor: 'bg-accent bg-opacity-10',
      borderColor: 'border-accent',
      textColor: 'text-accent',
      iconColor: 'text-accent',
    },
  }

  const config = severityConfig[alert.severity]
  const Icon = config.icon

  return (
    <div
      className={`flex items-start gap-3 rounded-lg border ${config.borderColor} ${config.bgColor} p-4`}
    >
      <Icon className={`mt-0.5 h-5 w-5 flex-shrink-0 ${config.iconColor}`} />
      <div className="flex-1">
        <p className={`text-sm font-medium ${config.textColor}`}>
          {alert.message}
        </p>
        <p className="mt-1 text-xs text-text-muted">
          {new Date(alert.timestamp).toLocaleString()}
        </p>
      </div>
      {onDismiss && (
        <Button
          variant="ghost"
          size="sm"
          className="h-6 w-6 p-0"
          onClick={() => onDismiss(alert.id)}
        >
          <X className="h-4 w-4 text-text-muted hover:text-text-primary" />
        </Button>
      )}
    </div>
  )
}
