---
epic: 007
story: 05
title: "Alert-System mit visueller Priorität"
status: completed
story_points: 3
covers: [FR38]
---

## Story 7.5: Alert-System mit visueller Priorität

Als Operator,
möchte ich Warnungen prominent angezeigt bekommen,
damit ich kritische Situationen sofort erkenne.

**Acceptance Criteria:**

**Given** WebSocket-Events für Alerts
**When** ich das Alert-System implementiere
**Then** existiert `src/features/dashboard/AlertList.tsx`:
```tsx
export function AlertList({ alerts }: { alerts: Alert[] }) {
  const sortedAlerts = sortByPriority(alerts);

  return (
    <div className="fixed bottom-4 right-4 space-y-2">
      {sortedAlerts.map(alert => (
        <AlertCard
          key={alert.id}
          alert={alert}
          onDismiss={() => dismissAlert(alert.id)}
        />
      ))}
    </div>
  );
}
```

**And** Alert-Typen:
  - `crash`: Rot, höchste Priorität, bleibt bis dismissed
  - `warning`: Orange, mittlere Priorität, auto-dismiss nach 30s
  - `info`: Blau, niedrige Priorität, auto-dismiss nach 10s

**And** Kritische Instanzen werden in Grid nach oben sortiert
**And** Optional: Subtiles Pulsing für kritische Alerts

**Technical Notes:**
- Toast-Notifications für neue Alerts
- Alert-History im Store
- Max 5 sichtbare Alerts gleichzeitig

**Prerequisites:** Story 7.2, 7.3

