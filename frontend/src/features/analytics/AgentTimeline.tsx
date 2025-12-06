import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Timeline,
  TimelineItem,
  TimelineIcon,
  TimelineContent,
  TimelineTitle,
  TimelineDescription,
  TimelineTime,
} from '@/components/ui/timeline'
import { useAgentActivity } from '@/hooks/useAgentActivity'
import type { AgentDecision, DecisionType } from '@/types'

interface AgentTimelineProps {
  teamId: number
}

interface DecisionFilters {
  agent: string | undefined
  type: DecisionType | undefined
}

function formatDecisionData(data: Record<string, unknown>): string {
  // Extract meaningful information from decision data
  if ('signal' in data && 'symbol' in data) {
    return `${data.signal} ${data.symbol} ${data.confidence ? `(${(Number(data.confidence) * 100).toFixed(1)}%)` : ''}`
  }
  if ('message' in data) {
    return String(data.message)
  }
  if ('reason' in data) {
    return String(data.reason)
  }
  // Fallback: show first meaningful value
  const entries = Object.entries(data).filter(([key]) => key !== 'timestamp')
  if (entries.length > 0) {
    return entries.map(([key, value]) => `${key}: ${value}`).join(', ')
  }
  return 'No details available'
}

function formatTime(timestamp: string): string {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)

  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`
  return date.toLocaleDateString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function getDecisionTypeBadgeVariant(type: DecisionType): 'default' | 'warning' | 'critical' | 'purple' {
  const upperType = type.toUpperCase()
  if (upperType === 'SIGNAL') return 'default'
  if (upperType === 'WARNING') return 'warning'
  if (upperType === 'REJECTION') return 'critical'
  if (upperType === 'OVERRIDE') return 'purple'
  return 'default'
}

function getUniqueAgents(decisions: AgentDecision[]): string[] {
  const agents = new Set(decisions.map(d => d.agent_name))
  return Array.from(agents).sort()
}

function getUniqueTypes(decisions: AgentDecision[]): DecisionType[] {
  const types = new Set(decisions.map(d => d.decision_type))
  return Array.from(types).sort()
}

export function AgentTimeline({ teamId }: AgentTimelineProps) {
  const [filters, setFilters] = useState<DecisionFilters>({
    agent: undefined,
    type: undefined,
  })

  const { decisions, isLoading, error } = useAgentActivity(teamId, {
    agent: filters.agent,
    type: filters.type,
    limit: 100,
  })

  const uniqueAgents = getUniqueAgents(decisions)
  const uniqueTypes = getUniqueTypes(decisions)

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Agent Timeline</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-critical">
            Error loading agent activity: {error.message}
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Agent Timeline</CardTitle>
        <div className="flex flex-wrap gap-2 mt-4">
          <div className="flex gap-2 items-center">
            <span className="text-sm text-text-secondary">Agent:</span>
            <button
              onClick={() => setFilters(prev => ({ ...prev, agent: undefined }))}
              className={`px-3 py-1 text-xs rounded-md transition-colors ${
                !filters.agent
                  ? 'bg-accent text-white'
                  : 'bg-surface-secondary text-text-secondary hover:bg-surface-hover'
              }`}
            >
              All
            </button>
            {uniqueAgents.map(agent => (
              <button
                key={agent}
                onClick={() => setFilters(prev => ({ ...prev, agent }))}
                className={`px-3 py-1 text-xs rounded-md transition-colors ${
                  filters.agent === agent
                    ? 'bg-accent text-white'
                    : 'bg-surface-secondary text-text-secondary hover:bg-surface-hover'
                }`}
              >
                {agent}
              </button>
            ))}
          </div>
          <div className="flex gap-2 items-center">
            <span className="text-sm text-text-secondary">Type:</span>
            <button
              onClick={() => setFilters(prev => ({ ...prev, type: undefined }))}
              className={`px-3 py-1 text-xs rounded-md transition-colors ${
                !filters.type
                  ? 'bg-accent text-white'
                  : 'bg-surface-secondary text-text-secondary hover:bg-surface-hover'
              }`}
            >
              All
            </button>
            {uniqueTypes.map(type => (
              <button
                key={type}
                onClick={() => setFilters(prev => ({ ...prev, type }))}
                className={`px-3 py-1 text-xs rounded-md transition-colors ${
                  filters.type === type
                    ? 'bg-accent text-white'
                    : 'bg-surface-secondary text-text-secondary hover:bg-surface-hover'
                }`}
              >
                {type}
              </button>
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="text-center py-8 text-text-secondary">
            Loading agent activity...
          </div>
        ) : decisions.length === 0 ? (
          <div className="text-center py-8 text-text-secondary">
            No agent decisions found for this team.
          </div>
        ) : (
          <div className="max-h-[600px] overflow-y-auto pr-2">
            <Timeline>
              {decisions.map((decision, index) => (
                <TimelineItem key={decision.id}>
                  <TimelineIcon type={decision.decision_type} />
                  <TimelineContent>
                    <div className="flex items-start justify-between gap-2">
                      <TimelineTitle>
                        {decision.agent_name}: {decision.decision_type}
                      </TimelineTitle>
                      <Badge variant={getDecisionTypeBadgeVariant(decision.decision_type)}>
                        {decision.decision_type}
                      </Badge>
                    </div>
                    <TimelineDescription>
                      {formatDecisionData(decision.data)}
                    </TimelineDescription>
                    {decision.confidence !== null && (
                      <TimelineDescription className="text-text-muted">
                        Confidence: {(decision.confidence * 100).toFixed(1)}%
                      </TimelineDescription>
                    )}
                    <TimelineTime>{formatTime(decision.created_at)}</TimelineTime>
                  </TimelineContent>
                </TimelineItem>
              ))}
            </Timeline>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
