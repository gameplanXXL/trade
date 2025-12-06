---
epic: 008
story: 06
title: "Team-Aktionen (Pause, Resume, Stop, Close Positions)"
status: done
story_points: 3
covers: [FR46, FR47]
completed_at: 2025-12-06
---

## Story 8.6: Team-Aktionen (Pause, Resume, Stop, Close Positions)

Als Operator,
möchte ich Teams pausieren, stoppen und Positionen schließen,
damit ich auf Situationen reagieren kann.

**Acceptance Criteria:**

**Given** Team-Detail und InstanceCard
**When** ich Team-Actions implementiere
**Then** existieren Quick-Actions:
```tsx
export function TeamActions({ team, onComplete }: TeamActionsProps) {
  const pauseTeam = usePauseTeam();
  const resumeTeam = useResumeTeam();
  const stopTeam = useStopTeam();
  const closePositions = useClosePositions();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <MoreVertical />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        {team.status === 'active' && (
          <DropdownMenuItem onClick={() => pauseTeam.mutate(team.id)}>
            <Pause /> Pausieren
          </DropdownMenuItem>
        )}
        {team.status === 'paused' && (
          <DropdownMenuItem onClick={() => resumeTeam.mutate(team.id)}>
            <Play /> Fortsetzen
          </DropdownMenuItem>
        )}
        <DropdownMenuItem
          onClick={() => setConfirmDialog('close_positions')}
          className="text-warning"
        >
          <XCircle /> Positionen schließen
        </DropdownMenuItem>
        <DropdownMenuItem
          onClick={() => setConfirmDialog('stop')}
          className="text-critical"
        >
          <StopCircle /> Team stoppen
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
```

**And** Confirmation-Modal für kritische Aktionen:
```tsx
<ConfirmationModal
  open={confirmDialog === 'close_positions'}
  title="Alle Positionen schließen?"
  description={`${team.open_positions} Positionen mit ${formatCurrency(team.exposure)} Exposure werden geschlossen.`}
  confirmText="Positionen schließen"
  variant="critical"
  onConfirm={() => closePositions.mutate(team.id)}
  onCancel={() => setConfirmDialog(null)}
/>
```

**And** Mobile: Swipe-to-Reveal für Quick-Actions

**Technical Notes:**
- Optimistic UI Updates
- Error-Handling mit Toast
- Disabled während Loading

**Prerequisites:** Story 5.4, Story 8.1

---

## Implementation Notes (2025-12-06)

**Story vollständig umgesetzt:**

- ✅ `src/features/teams/TeamActions.tsx`:
  - DropdownMenu mit allen Aktionen
  - Pause (wenn active), Resume (wenn paused)
  - Close Positions mit Confirmation Modal
  - Stop Team mit Confirmation Modal
- ✅ Hooks in `src/hooks/useTeamActions.ts`:
  - `usePauseTeam()`, `useResumeTeam()`
  - `useStopTeam()`, `useClosePositions()`
  - TanStack Query Mutations
- ✅ `ConfirmationModal` Komponente für kritische Aktionen
- ✅ Optimistic UI Updates
- ✅ Error-Handling mit Toast Notifications
- ✅ Disabled State während Loading
- ✅ Farbcodierung: warning für Close, critical für Stop
