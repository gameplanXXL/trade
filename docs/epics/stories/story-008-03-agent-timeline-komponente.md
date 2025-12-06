---
epic: 008
story: 03
title: "Agent-Timeline Komponente"
status: completed
story_points: 3
covers: [FR42, FR44]
completed_at: 2025-12-06
---

## Story 8.3: Agent-Timeline Komponente

Als Operator,
möchte ich die Timeline der Agent-Entscheidungen sehen,
damit ich nachvollziehen kann, was das System entschieden hat.

**Acceptance Criteria:**

**Given** Team-Detail-Ansicht
**When** ich AgentTimeline implementiere
**Then** existiert `src/features/analytics/AgentTimeline.tsx`:
```tsx
export function AgentTimeline({ teamId }: { teamId: number }) {
  const { decisions, isLoading } = useAgentActivity(teamId);

  return (
    <Timeline>
      {decisions.map(decision => (
        <TimelineItem key={decision.id}>
          <TimelineIcon type={decision.decision_type} />
          <TimelineContent>
            <TimelineTitle>
              {decision.agent_name}: {decision.decision_type}
            </TimelineTitle>
            <TimelineDescription>
              {formatDecisionData(decision.data)}
            </TimelineDescription>
            <TimelineTime>{formatTime(decision.created_at)}</TimelineTime>
          </TimelineContent>
        </TimelineItem>
      ))}
    </Timeline>
  );
}
```

**And** Decision-Typen visuell unterschieden:
  - Signal (BUY/SELL/HOLD): Blau
  - Warning: Orange
  - Rejection: Rot
  - Override: Lila

**And** Filterbar nach Agent und Typ

**Technical Notes:**
- Virtualisierte Liste für Performance
- Auto-Scroll zu neuesten Einträgen
- Details on-click expandieren

**Prerequisites:** Story 8.1, Story 6.3

