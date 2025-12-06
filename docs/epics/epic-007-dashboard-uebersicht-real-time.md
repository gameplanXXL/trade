# Epic 7: Dashboard - Übersicht & Real-time

**Epic Goal:** User öffnet Dashboard und sieht alle Team-Instanzen mit Status, P/L und Warnungen in Echtzeit

---

## Story 7.1: WebSocket-Server mit Socket.io ✅

**Status:** completed

Als Operator,
möchte ich Real-time-Updates im Dashboard,
damit ich sofort sehe, wenn sich etwas ändert.

**Acceptance Criteria:**

**Given** Backend mit FastAPI
**When** ich WebSocket-Server implementiere
**Then** existiert `src/api/websocket/handler.py`:
```python
import socketio

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

@sio.event
async def connect(sid, environ):
    """Client verbindet sich"""
    log.info("websocket_connected", sid=sid)

@sio.event
async def disconnect(sid):
    """Client trennt Verbindung"""

@sio.event
async def join_team(sid, data):
    """Client abonniert Team-Updates"""
    team_id = data['team_id']
    await sio.enter_room(sid, f"team:{team_id}")

@sio.event
async def leave_team(sid, data):
    """Client verlässt Team-Room"""
```

**And** Event-Emitter für Backend-Events:
```python
# src/api/websocket/events.py
async def emit_team_status(team_id: int, status: str):
    await sio.emit("team:status_changed", {"team_id": team_id, "status": status}, room=f"team:{team_id}")

async def emit_trade_executed(team_id: int, trade: Trade):
    await sio.emit("trade:executed", trade.model_dump(), room=f"team:{team_id}")

async def emit_alert(team_id: int, alert_type: str, message: str):
    await sio.emit(f"alert:{alert_type}", {"team_id": team_id, "message": message}, room="global")
```

**Technical Notes:**
- python-socketio mit ASGI
- Rooms für Team-spezifische Updates
- Global Room für System-Alerts

**Prerequisites:** Story 1.1

---

## Story 7.2: Frontend WebSocket-Client und Stores

Als Operator,
möchte ich Real-time-Updates im Frontend,
damit das Dashboard automatisch aktualisiert.

**Acceptance Criteria:**

**Given** WebSocket-Server
**When** ich den Frontend-Client implementiere
**Then** existiert `src/lib/socket.ts`:
```typescript
import { io, Socket } from 'socket.io-client';

class WebSocketClient {
  private socket: Socket;

  connect(): void {
    this.socket = io(import.meta.env.VITE_WS_URL);
  }

  joinTeam(teamId: number): void {
    this.socket.emit('join_team', { team_id: teamId });
  }

  onTeamStatusChanged(callback: (data: TeamStatus) => void): void {
    this.socket.on('team:status_changed', callback);
  }

  onTradeExecuted(callback: (data: Trade) => void): void {
    this.socket.on('trade:executed', callback);
  }

  onAlert(callback: (data: Alert) => void): void {
    this.socket.on('alert:warning', callback);
    this.socket.on('alert:crash', callback);
  }
}
```

**And** Zustand Store für Team-State:
```typescript
// src/stores/teamStore.ts
interface TeamStore {
  teams: Team[];
  alerts: Alert[];
  updateTeamStatus: (teamId: number, status: string) => void;
  addAlert: (alert: Alert) => void;
}
```

**And** Auto-Reconnect bei Verbindungsabbruch

**Technical Notes:**
- Socket.io Client v4
- Zustand für State Management
- Reconnect mit exponential backoff

**Prerequisites:** Story 1.5, 7.1

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

**Technical Notes:**
- CSS Grid mit dynamischen grid-area Sizes
- Framer Motion für Größen-Animationen
- Touch-optimierte Quick-Actions

**Prerequisites:** Story 7.3

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

---

**Epic 7 Complete**

**Stories Created:** 5
**FR Coverage:** FR36, FR37, FR38, FR39
**Technical Context Used:** Architecture WebSocket, UX Design Core Experience

---
