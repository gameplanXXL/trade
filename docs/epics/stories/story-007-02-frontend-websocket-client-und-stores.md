---
epic: 007
story: 02
title: "Frontend WebSocket-Client und Stores"
status: done
story_points: 3
covers: [FR39]
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

