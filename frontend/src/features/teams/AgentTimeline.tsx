import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface AgentTimelineProps {
  teamId: number
}

export function AgentTimeline({ teamId }: AgentTimelineProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Agent Timeline</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-center py-8 text-text-secondary">
          Agent timeline for team #{teamId} will be displayed here.
          <div className="text-sm text-text-muted mt-2">
            This component will be implemented in a future story.
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
