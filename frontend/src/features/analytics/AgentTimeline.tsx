import { useState, useEffect, useRef } from 'react'
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
import { ChevronDown, ChevronUp } from 'lucide-react'

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
  const [expandedDecisions, setExpandedDecisions] = useState<Set<number>>(new Set())
  const [autoScroll, setAutoScroll] = useState(true)
  const timelineRef = useRef<HTMLDivElement>(null)
  const prevDecisionsCountRef = useRef(0)

  const { decisions, isLoading, error } = useAgentActivity(teamId, {
    agent: filters.agent,
    type: filters.type,
    limit: 100,
  })

  const uniqueAgents = getUniqueAgents(decisions)
  const uniqueTypes = getUniqueTypes(decisions)

  // Auto-scroll to top when new decisions arrive
  useEffect(() => {
    if (autoScroll && decisions.length > prevDecisionsCountRef.current) {
      timelineRef.current?.scrollTo({ top: 0, behavior: 'smooth' })
    }
    prevDecisionsCountRef.current = decisions.length
  }, [decisions.length, autoScroll])

  const toggleExpanded = (decisionId: number) => {
    setExpandedDecisions((prev) => {
      const next = new Set(prev)
      if (next.has(decisionId)) {
        next.delete(decisionId)
      } else {
        next.add(decisionId)
      }
      return next
    })
  }

  const handleScroll = () => {
    // Disable auto-scroll when user manually scrolls away from top
    if (timelineRef.current && timelineRef.current.scrollTop > 50) {
      setAutoScroll(false)
    }
  }

  const scrollToTop = () => {
    timelineRef.current?.scrollTo({ top: 0, behavior: 'smooth' })
    setAutoScroll(true)
  }

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
          <div className="relative">
            <div
              ref={timelineRef}
              onScroll={handleScroll}
              className="max-h-[600px] overflow-y-auto pr-2 scroll-smooth"
            >
              <Timeline>
                {decisions.map((decision) => {
                  const isExpanded = expandedDecisions.has(decision.id)
                  return (
                    <TimelineItem key={decision.id}>
                      <TimelineIcon type={decision.decision_type} />
                      <TimelineContent>
                        <div
                          className="cursor-pointer hover:bg-surface-hover rounded-lg p-2 -m-2 transition-colors"
                          onClick={() => toggleExpanded(decision.id)}
                        >
                          <div className="flex items-start justify-between gap-2">
                            <TimelineTitle>
                              {decision.agent_name}: {decision.decision_type}
                            </TimelineTitle>
                            <div className="flex items-center gap-2">
                              <Badge variant={getDecisionTypeBadgeVariant(decision.decision_type)}>
                                {decision.decision_type}
                              </Badge>
                              {isExpanded ? (
                                <ChevronUp className="h-4 w-4 text-text-muted" />
                              ) : (
                                <ChevronDown className="h-4 w-4 text-text-muted" />
                              )}
                            </div>
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

                          {/* Expanded Details */}
                          {isExpanded && (
                            <div className="mt-3 pt-3 border-t border-border space-y-2">
                              <div className="text-xs">
                                <div className="font-semibold text-text-primary mb-1">Full Details:</div>
                                <pre className="bg-surface-secondary p-2 rounded text-text-secondary overflow-x-auto">
                                  {JSON.stringify(decision.data, null, 2)}
                                </pre>
                              </div>
                              <div className="text-xs text-text-muted">
                                <div>ID: {decision.id}</div>
                                <div>Team Instance: {decision.team_instance_id}</div>
                                <div>Timestamp: {new Date(decision.created_at).toLocaleString('de-DE')}</div>
                              </div>
                            </div>
                          )}
                        </div>
                      </TimelineContent>
                    </TimelineItem>
                  )
                })}
              </Timeline>
            </div>

            {/* Scroll to Top Button */}
            {!autoScroll && (
              <button
                onClick={scrollToTop}
                className="absolute bottom-4 right-4 bg-accent text-white p-2 rounded-full shadow-lg hover:bg-accent/90 transition-colors"
                title="Scroll to newest entries"
              >
                <ChevronUp className="h-5 w-5" />
              </button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
