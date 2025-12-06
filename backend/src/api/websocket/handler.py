"""WebSocket handler with Socket.io for real-time updates."""

import socketio

from src.core.logging import get_logger

log = get_logger(__name__)

# Create async Socket.io server with ASGI mode
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")


@sio.event
async def connect(sid: str, environ: dict) -> None:
    """Handle client connection.

    Args:
        sid: Session ID
        environ: WSGI environment dict
    """
    log.info("websocket_connected", sid=sid)


@sio.event
async def disconnect(sid: str) -> None:
    """Handle client disconnection.

    Args:
        sid: Session ID
    """
    log.info("websocket_disconnected", sid=sid)


@sio.event
async def join_team(sid: str, data: dict) -> None:
    """Client subscribes to team-specific updates.

    Args:
        sid: Session ID
        data: Dictionary containing team_id
    """
    team_id = data.get("team_id")
    if not team_id:
        log.warning("join_team_missing_id", sid=sid)
        return

    room_name = f"team:{team_id}"
    await sio.enter_room(sid, room_name)
    log.info("client_joined_team", sid=sid, team_id=team_id, room=room_name)


@sio.event
async def leave_team(sid: str, data: dict) -> None:
    """Client unsubscribes from team-specific updates.

    Args:
        sid: Session ID
        data: Dictionary containing team_id
    """
    team_id = data.get("team_id")
    if not team_id:
        log.warning("leave_team_missing_id", sid=sid)
        return

    room_name = f"team:{team_id}"
    await sio.leave_room(sid, room_name)
    log.info("client_left_team", sid=sid, team_id=team_id, room=room_name)
