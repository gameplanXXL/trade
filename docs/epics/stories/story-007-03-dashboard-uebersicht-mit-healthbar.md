---
epic: 007
story: 03
title: "Dashboard-Übersicht mit HealthBar"
status: backlog
story_points: 3
covers: [FR36, FR37]
---

## Story 7.3: Dashboard-Übersicht mit HealthBar

Als Operator,
möchte ich eine Übersichtsseite mit Gesamt-Status,
damit ich auf einen Blick sehe, ob alles OK ist.

**Acceptance Criteria:**

**Given** Frontend-Projekt und API
**When** ich die Dashboard-Übersicht implementiere
**Then** existiert `src/features/dashboard/DashboardView.tsx`:
```tsx
export function DashboardView() {
  const { teams, alerts } = useTeamStore();

  return (
    <div className="min-h-screen bg-background">
      <HealthBar teams={teams} />
      <TeamGrid teams={teams} />
      <AlertList alerts={alerts} />
    </div>
  );
}
```

**And** `HealthBar` Komponente (UX Design):
  - Grün: Alle Teams OK (P/L >= 0)
  - Gelb: Mindestens 1 Team mit Warning (0 > P/L > -5%)
  - Rot: Mindestens 1 Team kritisch (P/L <= -5%)
  - Badge zeigt Anzahl kritischer/warnender Teams

**And** Dark-Mode Default mit UX-Design-Farben

**Technical Notes:**
- Responsive: Mobile = Stack, Desktop = Grid
- Initial Load via REST, Updates via WebSocket
- Skeleton-Loading während Fetch

**Prerequisites:** Story 1.5, 7.2

