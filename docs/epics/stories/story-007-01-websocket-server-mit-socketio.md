---
epic: 007
story: 01
title: "WebSocket-Server mit Socket.io"
status: backlog
story_points: 3
covers: [FR39]
---

## Story 7.1: WebSocket-Server mit Socket.io

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

