---
epic: 008
story: 01
title: "Team-Detail-Ansicht mit Tabs"
status: backlog
story_points: 3
covers: [FR40]
---

## Story 8.1: Team-Detail-Ansicht mit Tabs

Als Operator,
möchte ich eine Detail-Ansicht für Team-Instanzen,
damit ich alle Informationen zu einem Team sehen kann.

**Acceptance Criteria:**

**Given** Dashboard mit InstanceCards
**When** ich die Detail-Ansicht implementiere
**Then** existiert `src/features/teams/TeamDetail.tsx`:
```tsx
export function TeamDetail({ teamId }: { teamId: number }) {
  const { team, isLoading } = useTeam(teamId);

  return (
    <div className="space-y-6">
      <TeamHeader team={team} />
      <PerformanceMetrics team={team} />

      <Tabs defaultValue="trades">
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
  );
}
```

**And** Mobile: Bottom-Sheet statt Full-Page
**And** Breadcrumbs: Dashboard > Team "Alpha-LLM"

**Technical Notes:**
- React Router für Navigation
- Lazy Loading für Tab-Contents
- URL-Sync für aktiven Tab

**Prerequisites:** Story 7.4

