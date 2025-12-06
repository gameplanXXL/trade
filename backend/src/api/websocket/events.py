"""Event emitters for WebSocket real-time updates."""

from typing import Any

from src.core.logging import get_logger

log = get_logger(__name__)


async def emit_team_status(team_id: int, status: str) -> None:
    """Emit team status change event to team room.

    Args:
        team_id: ID of the team instance
        status: New status (active, paused, stopped)
    """
    from src.api.websocket.handler import sio

    room = f"team:{team_id}"
    event_data = {"team_id": team_id, "status": status}

    await sio.emit("team:status_changed", event_data, room=room)
    log.info("emitted_team_status", team_id=team_id, status=status, room=room)


async def emit_trade_executed(team_id: int, trade_data: dict[str, Any]) -> None:
    """Emit trade execution event to team room.

    Args:
        team_id: ID of the team instance
        trade_data: Dictionary containing trade details (from Trade.model_dump() or similar)
    """
    from src.api.websocket.handler import sio

    room = f"team:{team_id}"
    event_data = {"team_id": team_id, **trade_data}

    await sio.emit("trade:executed", event_data, room=room)
    log.info(
        "emitted_trade_executed",
        team_id=team_id,
        trade_id=trade_data.get("id"),
        symbol=trade_data.get("symbol"),
        room=room,
    )


async def emit_alert(team_id: int, alert_type: str, message: str) -> None:
    """Emit alert to global room.

    Args:
        team_id: ID of the team instance
        alert_type: Type of alert (warning, error, info)
        message: Alert message
    """
    from src.api.websocket.handler import sio

    room = "global"
    event_name = f"alert:{alert_type}"
    event_data = {"team_id": team_id, "message": message}

    await sio.emit(event_name, event_data, room=room)
    log.info(
        "emitted_alert",
        team_id=team_id,
        alert_type=alert_type,
        message=message,
        room=room,
    )
