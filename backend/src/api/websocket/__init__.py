"""WebSocket module for real-time updates."""

from src.api.websocket.events import emit_alert, emit_team_status, emit_trade_executed
from src.api.websocket.handler import sio

__all__ = ["sio", "emit_team_status", "emit_trade_executed", "emit_alert"]
