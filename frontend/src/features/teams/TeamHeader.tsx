import { Badge } from '@/components/ui/badge'
import type { Team } from '@/types'
import { ArrowLeft } from 'lucide-react'
import { Link } from 'react-router-dom'

interface TeamHeaderProps {
  team: Team
}

export function TeamHeader({ team }: TeamHeaderProps) {
  const statusVariant = {
    active: 'success' as const,
    paused: 'warning' as const,
    stopped: 'gray' as const,
    warning: 'warning' as const,
    critical: 'critical' as const,
  }[team.status]

  const modeVariant = team.mode === 'paper' ? 'purple' as const : 'default' as const

  return (
    <div className="space-y-4">
      {/* Breadcrumbs */}
      <div className="flex items-center gap-2 text-sm text-text-secondary">
        <Link
          to="/"
          className="flex items-center gap-1 hover:text-text-primary transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Dashboard
        </Link>
        <span>/</span>
        <span className="text-text-primary">{team.name}</span>
      </div>

      {/* Team Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-3xl font-bold text-text-primary">{team.name}</h1>
          <div className="flex items-center gap-2">
            <Badge variant={statusVariant}>
              {team.status.toUpperCase()}
            </Badge>
            <Badge variant={modeVariant}>
              {team.mode === 'paper' ? 'PAPER' : 'LIVE'}
            </Badge>
          </div>
        </div>

        <div className="text-right">
          <div className="text-sm text-text-secondary">{team.symbol}</div>
          <div className="text-xs text-text-muted">
            Created {new Date(team.created_at).toLocaleDateString()}
          </div>
        </div>
      </div>
    </div>
  )
}
