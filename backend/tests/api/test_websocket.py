"""Tests for WebSocket handler and events - Story 007-01."""

from unittest.mock import AsyncMock, patch

import pytest

from src.api.websocket.events import emit_alert, emit_team_status, emit_trade_executed
from src.api.websocket.handler import sio


@pytest.mark.asyncio
class TestWebSocketHandler:
    """Test WebSocket handler events."""

    async def test_connect_event(self):
        """Test that connect event logs connection."""
        sid = "test-session-123"
        environ = {"HTTP_USER_AGENT": "test-client"}

        with patch("src.api.websocket.handler.log") as mock_log:
            # Import the function directly to test it
            from src.api.websocket.handler import connect

            await connect(sid, environ)

            mock_log.info.assert_called_once_with("websocket_connected", sid=sid)

    async def test_disconnect_event(self):
        """Test that disconnect event logs disconnection."""
        sid = "test-session-123"

        with patch("src.api.websocket.handler.log") as mock_log:
            from src.api.websocket.handler import disconnect

            await disconnect(sid)

            mock_log.info.assert_called_once_with("websocket_disconnected", sid=sid)

    async def test_join_team_with_valid_team_id(self):
        """Test joining a team room with valid team_id."""
        sid = "test-session-123"
        team_id = 42
        data = {"team_id": team_id}

        with patch.object(sio, "enter_room", new_callable=AsyncMock) as mock_enter_room:
            with patch("src.api.websocket.handler.log") as mock_log:
                from src.api.websocket.handler import join_team

                await join_team(sid, data)

                mock_enter_room.assert_called_once_with(sid, f"team:{team_id}")
                mock_log.info.assert_called_once_with(
                    "client_joined_team",
                    sid=sid,
                    team_id=team_id,
                    room=f"team:{team_id}",
                )

    async def test_join_team_without_team_id(self):
        """Test joining a team room without team_id logs warning."""
        sid = "test-session-123"
        data = {}

        with patch.object(sio, "enter_room", new_callable=AsyncMock) as mock_enter_room:
            with patch("src.api.websocket.handler.log") as mock_log:
                from src.api.websocket.handler import join_team

                await join_team(sid, data)

                mock_enter_room.assert_not_called()
                mock_log.warning.assert_called_once_with("join_team_missing_id", sid=sid)

    async def test_leave_team_with_valid_team_id(self):
        """Test leaving a team room with valid team_id."""
        sid = "test-session-123"
        team_id = 42
        data = {"team_id": team_id}

        with patch.object(sio, "leave_room", new_callable=AsyncMock) as mock_leave_room:
            with patch("src.api.websocket.handler.log") as mock_log:
                from src.api.websocket.handler import leave_team

                await leave_team(sid, data)

                mock_leave_room.assert_called_once_with(sid, f"team:{team_id}")
                mock_log.info.assert_called_once_with(
                    "client_left_team",
                    sid=sid,
                    team_id=team_id,
                    room=f"team:{team_id}",
                )

    async def test_leave_team_without_team_id(self):
        """Test leaving a team room without team_id logs warning."""
        sid = "test-session-123"
        data = {}

        with patch.object(sio, "leave_room", new_callable=AsyncMock) as mock_leave_room:
            with patch("src.api.websocket.handler.log") as mock_log:
                from src.api.websocket.handler import leave_team

                await leave_team(sid, data)

                mock_leave_room.assert_not_called()
                mock_log.warning.assert_called_once_with("leave_team_missing_id", sid=sid)


@pytest.mark.asyncio
class TestWebSocketEvents:
    """Test WebSocket event emitters."""

    async def test_emit_team_status(self):
        """Test emitting team status change event."""
        team_id = 42
        status = "active"
        expected_room = f"team:{team_id}"
        expected_event = "team:status_changed"
        expected_data = {"team_id": team_id, "status": status}

        # Mock sio at the handler module level since it's imported from there
        with patch("src.api.websocket.handler.sio") as mock_sio:
            mock_sio.emit = AsyncMock()

            with patch("src.api.websocket.events.log") as mock_log:
                await emit_team_status(team_id, status)

                mock_sio.emit.assert_called_once_with(
                    expected_event, expected_data, room=expected_room
                )
                mock_log.info.assert_called_once_with(
                    "emitted_team_status",
                    team_id=team_id,
                    status=status,
                    room=expected_room,
                )

    async def test_emit_trade_executed(self):
        """Test emitting trade executed event."""
        team_id = 42
        trade_data = {
            "id": 1,
            "ticket": 12345,
            "symbol": "EUR/USD",
            "side": "BUY",
            "size": 0.1,
            "entry_price": 1.1050,
        }
        expected_room = f"team:{team_id}"
        expected_event = "trade:executed"
        expected_data = {"team_id": team_id, **trade_data}

        # Mock sio at the handler module level since it's imported from there
        with patch("src.api.websocket.handler.sio") as mock_sio:
            mock_sio.emit = AsyncMock()

            with patch("src.api.websocket.events.log") as mock_log:
                await emit_trade_executed(team_id, trade_data)

                mock_sio.emit.assert_called_once_with(
                    expected_event, expected_data, room=expected_room
                )
                mock_log.info.assert_called_once_with(
                    "emitted_trade_executed",
                    team_id=team_id,
                    trade_id=trade_data["id"],
                    symbol=trade_data["symbol"],
                    room=expected_room,
                )

    async def test_emit_alert(self):
        """Test emitting alert event."""
        team_id = 42
        alert_type = "warning"
        message = "High drawdown detected"
        expected_room = "global"
        expected_event = f"alert:{alert_type}"
        expected_data = {"team_id": team_id, "message": message}

        # Mock sio at the handler module level since it's imported from there
        with patch("src.api.websocket.handler.sio") as mock_sio:
            mock_sio.emit = AsyncMock()

            with patch("src.api.websocket.events.log") as mock_log:
                await emit_alert(team_id, alert_type, message)

                mock_sio.emit.assert_called_once_with(
                    expected_event, expected_data, room=expected_room
                )
                mock_log.info.assert_called_once_with(
                    "emitted_alert",
                    team_id=team_id,
                    alert_type=alert_type,
                    message=message,
                    room=expected_room,
                )


@pytest.mark.asyncio
class TestWebSocketIntegration:
    """Integration tests for WebSocket with FastAPI."""

    async def test_socket_io_server_initialized(self):
        """Test that Socket.io server is properly initialized."""
        assert sio is not None
        assert sio.async_mode == "asgi"

    async def test_socket_app_wrapped_in_main(self):
        """Test that socket_app is created in main.py."""
        from src.main import socket_app

        assert socket_app is not None
        # Verify it's a Socket.io ASGI app
        assert hasattr(socket_app, "__call__")
