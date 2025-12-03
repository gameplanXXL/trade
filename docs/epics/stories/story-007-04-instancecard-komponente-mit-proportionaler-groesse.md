---
epic: 007
story: 04
title: "InstanceCard Komponente mit proportionaler Größe"
status: backlog
story_points: 5
covers: [FR36, FR37]
---

## Story 7.4: InstanceCard Komponente mit proportionaler Größe

Als Operator,
möchte ich Team-Karten, deren Größe das Budget widerspiegelt,
damit ich die Budget-Evolution visuell erkenne.

**Acceptance Criteria:**

**Given** Dashboard-Übersicht
**When** ich InstanceCard implementiere
**Then** existiert `src/features/dashboard/InstanceCard.tsx`:
```tsx
interface InstanceCardProps {
  team: Team;
  onAction: (action: 'details' | 'pause' | 'close') => void;
}

export function InstanceCard({ team, onAction }: InstanceCardProps) {
  const sizeClass = calculateSizeClass(team.current_budget, totalBudget);
  const statusColor = getStatusColor(team.pnl_percent);

  return (
    <Card className={cn("transition-all", sizeClass, statusColor)}>
      <CardHeader>
        <CardTitle>{team.name}</CardTitle>
        <Badge variant={team.mode === 'live' ? 'purple' : 'gray'}>
          {team.mode}
        </Badge>
      </CardHeader>
      <CardContent>
        <PnLDisplay value={team.total_pnl} percent={team.pnl_percent} />
        <MetricsRow winRate={team.win_rate} drawdown={team.max_drawdown} />
      </CardContent>
      <CardFooter>
        <QuickActions onAction={onAction} />
      </CardFooter>
    </Card>
  );
}
```

**And** Größen-Klassen basierend auf Budget-Anteil:
  - Large: > 30% des Gesamt-Budgets
  - Medium: 15-30%
  - Small: < 15%

**And** Farbcodierung (UX Design):
  - `bg-success/10`: P/L > 0%
  - `bg-warning/10`: -5% < P/L <= 0%
  - `bg-critical/10`: P/L <= -5%

**And** P/L in großer Monospace-Schrift (JetBrains Mono)



## Tasks

- [ ] Size-Calculation Logik
- [ ] Color-Coding nach P/L
- [ ] PnL Display Komponente
- [ ] Quick Actions
- [ ] Responsive Layout
**Technical Notes:**
- CSS Grid mit dynamischen grid-area Sizes
- Framer Motion für Größen-Animationen
- Touch-optimierte Quick-Actions

**Prerequisites:** Story 7.3

