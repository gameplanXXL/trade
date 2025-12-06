import { useTeam } from '@/hooks/useTeam'
import { TeamHeader } from './TeamHeader'
import { PerformanceMetrics } from './PerformanceMetrics'
import { TradeHistory } from './TradeHistory'
import { AgentTimeline } from './AgentTimeline'
import { PerformanceCharts } from './PerformanceCharts'
import { TeamSettings } from './TeamSettings'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useSearchParams } from 'react-router-dom'

interface TeamDetailProps {
  teamId: number
}

export function TeamDetail({ teamId }: TeamDetailProps) {
  const { team, isLoading, error } = useTeam(teamId)
  const [searchParams, setSearchParams] = useSearchParams()

  const activeTab = searchParams.get('tab') || 'trades'

  const handleTabChange = (value: string) => {
    setSearchParams({ tab: value })
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-text-secondary">Loading team details...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-critical">
          Error loading team: {error.message}
        </div>
      </div>
    )
  }

  if (!team) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-text-secondary">Team not found</div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-6 space-y-6">
      <TeamHeader team={team} />
      <PerformanceMetrics team={team} />

      <Tabs value={activeTab} onValueChange={handleTabChange}>
        <TabsList>
          <TabsTrigger value="trades">Trade-Historie</TabsTrigger>
          <TabsTrigger value="timeline">Agent-Timeline</TabsTrigger>
          <TabsTrigger value="charts">Performance-Charts</TabsTrigger>
          <TabsTrigger value="settings">Einstellungen</TabsTrigger>
        </TabsList>

        <TabsContent value="trades">
          <TradeHistory teamId={teamId} />
        </TabsContent>
        <TabsContent value="timeline">
          <AgentTimeline teamId={teamId} />
        </TabsContent>
        <TabsContent value="charts">
          <PerformanceCharts teamId={teamId} />
        </TabsContent>
        <TabsContent value="settings">
          <TeamSettings team={team} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
