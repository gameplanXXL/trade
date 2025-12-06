# WebSocket Integration Documentation

## Overview

The WebSocket integration provides real-time updates for the trading platform dashboard. It enables automatic synchronization of team status, trade executions, and alerts without manual refreshing.

## Architecture

### Components

1. **WebSocketClient** (`src/lib/socket.ts`)
   - Singleton instance managing Socket.IO connection
   - Handles connection lifecycle and reconnection logic
   - Provides event subscription/unsubscription methods

2. **Team Store** (`src/stores/teamStore.ts`)
   - Zustand store for managing team state
   - Provides actions to update team status and alerts
   - Syncs with WebSocket events automatically

3. **useWebSocket Hook** (`src/hooks/useWebSocket.ts`)
   - React hook for managing WebSocket subscriptions
   - Automatically connects/disconnects based on component lifecycle
   - Integrates with team store for state updates

## Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=http://localhost:8000
```

For production, update these to point to your server.

## Usage

### Basic Usage in Components

```typescript
import { useWebSocket } from '@/hooks/useWebSocket'

function MyComponent() {
  const { isConnected, joinTeam, leaveTeam } = useWebSocket()

  return (
    <div>
      <p>WebSocket Status: {isConnected ? 'Connected' : 'Disconnected'}</p>
    </div>
  )
}
```

### Subscribing to Team Updates

The WebSocket client automatically subscribes to team updates. To join a specific team room:

```typescript
import { useWebSocket } from '@/hooks/useWebSocket'

function TeamDetail({ teamId }: { teamId: number }) {
  const { joinTeam, leaveTeam } = useWebSocket()

  useEffect(() => {
    joinTeam(teamId)
    return () => leaveTeam(teamId)
  }, [teamId, joinTeam, leaveTeam])

  // Team updates will be reflected in the store automatically
  const team = useTeamStore((state) =>
    state.teams.find((t) => t.id === teamId)
  )

  return <div>{team?.status}</div>
}
```

### Accessing Alerts

Alerts are automatically added to the store when received:

```typescript
import { useTeamStore } from '@/stores/teamStore'

function AlertDisplay() {
  const alerts = useTeamStore((state) => state.alerts)
  const removeAlert = useTeamStore((state) => state.removeAlert)

  return (
    <div>
      {alerts.map((alert) => (
        <div key={alert.id} onClick={() => removeAlert(alert.id)}>
          {alert.message}
        </div>
      ))}
    </div>
  )
}
```

## WebSocket Events

The client listens to the following events:

### `team:status_changed`

Emitted when a team's status changes.

**Payload:**
```typescript
{
  team_id: number
  status: 'active' | 'paused' | 'stopped' | 'warning' | 'critical'
  current_pnl?: number
  pnl_percent?: number
}
```

### `trade:executed`

Emitted when a trade is executed.

**Payload:**
```typescript
{
  id: number
  team_instance_id: number
  ticket: number
  symbol: string
  side: 'BUY' | 'SELL'
  size: number
  entry_price: number
  // ... other trade fields
}
```

### `alert:warning`, `alert:crash`, `alert:info`

Emitted when system alerts are generated.

**Payload:**
```typescript
{
  id: string
  team_id: number
  severity: 'warning' | 'crash' | 'info'
  message: string
  timestamp: string
}
```

## Reconnection Logic

The WebSocket client implements exponential backoff for reconnection:

- **Initial delay:** 1 second
- **Maximum delay:** 30 seconds
- **Maximum attempts:** 5

The delay doubles with each failed attempt up to the maximum delay.

### Connection States

1. **Connecting:** Initial connection attempt
2. **Connected:** Successfully connected to server
3. **Disconnected:** Connection lost or closed
4. **Reconnecting:** Attempting to reconnect with backoff

## Error Handling

The WebSocket client logs connection errors to the console. In production, you may want to:

1. Display a notification to users when connection is lost
2. Implement a UI indicator showing connection status
3. Add analytics tracking for connection issues

## Testing

### Manual Testing

1. Start the backend server
2. Start the frontend dev server
3. Open browser DevTools → Network → WS
4. Verify WebSocket connection is established
5. Trigger a team status change from backend
6. Verify the frontend updates automatically

### Connection Loss Testing

1. Stop the backend server while frontend is running
2. Observe reconnection attempts in console
3. Restart backend server
4. Verify automatic reconnection

## Performance Considerations

- **Connection pooling:** Only one WebSocket connection per client
- **Event batching:** Store updates are batched by React
- **Memory management:** Event listeners are cleaned up on unmount
- **Reconnection limits:** Prevents infinite reconnection loops

## Security

- WebSocket connections use the same origin policy as the API
- Session cookies are included in WebSocket handshake
- Authentication is handled at the server level

## Troubleshooting

### WebSocket Not Connecting

1. Check `VITE_WS_URL` environment variable
2. Verify backend WebSocket server is running
3. Check browser console for connection errors
4. Ensure no CORS issues (should use same origin)

### Events Not Received

1. Verify WebSocket is connected
2. Check if `joinTeam()` was called for team-specific events
3. Verify event names match backend implementation
4. Check browser console for subscription errors

### Frequent Disconnections

1. Check server logs for connection issues
2. Verify network stability
3. Check if server is timing out idle connections
4. Consider adjusting reconnection parameters

## Future Enhancements

- [ ] Add connection status indicator in UI
- [ ] Implement message queue for offline events
- [ ] Add WebSocket metrics/monitoring
- [ ] Support for authenticated WebSocket connections
- [ ] Implement ping/pong for connection health checks
