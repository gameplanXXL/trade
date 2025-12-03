# Epic 8: Dashboard - Details & Konfiguration

**Epic Goal:** User kann Instanz-Details einsehen (Trade-Historie, Timeline, Charts) und neue Instanzen über die UI erstellen

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

---

## Story 8.4: Performance-Charts mit TradingView

Als Operator,
möchte ich Performance-Charts sehen,
damit ich Trends visuell analysieren kann.

**Acceptance Criteria:**

**Given** Team-Detail-Ansicht und Performance-Historie
**When** ich PerformanceCharts implementiere
**Then** existiert `src/features/analytics/PerformanceCharts.tsx`:
```tsx
import { createChart } from 'lightweight-charts';

export function PerformanceCharts({ teamId }: { teamId: number }) {
  const { history } = usePerformanceHistory(teamId);
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const chart = createChart(chartRef.current!, {
      layout: { background: { color: '#0a0e1a' } },
      // ...
    });

    const pnlSeries = chart.addLineSeries({ color: '#10b981' });
    pnlSeries.setData(history.map(h => ({ time: h.timestamp, value: h.pnl })));

    return () => chart.remove();
  }, [history]);

  return (
    <div className="space-y-4">
      <div ref={chartRef} className="h-64" />
      <DrawdownChart data={history} />
    </div>
  );
}
```

**And** Charts:
  - P/L-Verlauf (Line Chart)
  - Drawdown-Verlauf (Area Chart, invertiert)
  - Win-Rate über Zeit (optional)

**And** Timeframe-Selector: 1D, 1W, 1M, All

**Technical Notes:**
- TradingView Lightweight Charts
- Dark-Theme matching UX Design
- Responsive Chart-Größe

**Prerequisites:** Story 8.1, Story 6.2

---

## Story 8.5: Team-Erstellung via UI

Als Operator,
möchte ich neue Team-Instanzen über die UI erstellen,
damit ich ohne CLI neue Teams starten kann.

**Acceptance Criteria:**

**Given** Dashboard und REST-API
**When** ich TeamCreate implementiere
**Then** existiert `src/features/teams/TeamCreate.tsx`:
```tsx
export function TeamCreate() {
  const { templates } = useTemplates();
  const createTeam = useCreateTeam();

  const form = useForm<TeamCreateInput>({
    defaultValues: {
      name: '',
      template_name: 'conservative_llm',
      symbols: ['EUR/USD'],
      budget: 10000,
      mode: 'paper',
    },
  });

  const onSubmit = async (data: TeamCreateInput) => {
    await createTeam.mutateAsync(data);
    navigate('/dashboard');
  };

  return (
    <Form {...form}>
      <FormField name="name" label="Team-Name" />
      <FormField name="template_name" label="Template" type="select" options={templates} />
      <FormField name="symbols" label="Symbole" type="multi-select" />
      <FormField name="budget" label="Budget (€)" type="number" />
      <FormField name="mode" label="Modus" type="toggle" options={['paper', 'live']} />

      {form.watch('mode') === 'live' && (
        <Alert variant="warning">
          Live-Trading verwendet echtes Geld. Nur nach erfolgreicher Paper-Phase empfohlen.
        </Alert>
      )}

      <Button type="submit">Team erstellen</Button>
    </Form>
  );
}
```

**And** Validation:
  - Name: Required, 3-50 Zeichen
  - Budget: Min 100€
  - Symbols: Min 1

**And** Template-Preview zeigt Rollen und Pipeline

**Technical Notes:**
- React Hook Form für Form-Handling
- Zod für Validation
- Optimistic Update nach Submit

**Prerequisites:** Story 5.3, Story 7.3

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

**Epic 8 Complete**

**Stories Created:** 6
**FR Coverage:** FR40, FR41, FR42, FR43, FR44, FR45, FR46, FR47, FR48
**Technical Context Used:** Architecture API Design, UX Design Key User Journeys

---
