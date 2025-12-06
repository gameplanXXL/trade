---
epic: 008
story: 02
title: "Trade-Historie mit Sortierung und Filterung"
status: completed
story_points: 3
covers: [FR41]
---

## Story 8.2: Trade-Historie mit Sortierung und Filterung

Als Operator,
möchte ich die Trade-Historie einer Instanz sehen,
damit ich alle ausgeführten Trades analysieren kann.

**Acceptance Criteria:**

**Given** Team-Detail-Ansicht
**When** ich TradeHistory implementiere
**Then** existiert `src/features/analytics/TradeHistory.tsx`:
```tsx
export function TradeHistory({ teamId }: { teamId: number }) {
  const { trades, isLoading } = useTrades(teamId);

  const columns = [
    { key: 'opened_at', label: 'Zeit', sortable: true },
    { key: 'symbol', label: 'Symbol', filterable: true },
    { key: 'side', label: 'Typ', filterable: true },
    { key: 'size', label: 'Größe' },
    { key: 'entry_price', label: 'Entry' },
    { key: 'exit_price', label: 'Exit' },
    { key: 'pnl', label: 'P/L', sortable: true },
    { key: 'status', label: 'Status' },
  ];

  return (
    <DataTable
      data={trades}
      columns={columns}
      pagination={{ pageSize: 20 }}
      onSort={handleSort}
      onFilter={handleFilter}
    />
  );
}
```

**And** TanStack Table für Sortierung/Filterung
**And** P/L-Spalte farbcodiert (Grün/Rot)
**And** Export als CSV

**Technical Notes:**
- Server-Side Pagination für große Datenmengen
- Virtualisierung für Performance
- Responsive: Weniger Spalten auf Mobile

**Prerequisites:** Story 8.1

