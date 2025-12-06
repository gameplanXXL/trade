import { AgentTimeline as AgentTimelineAnalytics } from '@/features/analytics/AgentTimeline'

interface AgentTimelineProps {
  teamId: number
}

export function AgentTimeline({ teamId }: AgentTimelineProps) {
  return <AgentTimelineAnalytics teamId={teamId} />
}
