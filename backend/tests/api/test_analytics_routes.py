"""Tests for Analytics REST API endpoints - Story 006-04."""

from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from src.api.schemas.analytics import (
    AgentDecisionResponse,
    PerformanceMetricResponse,
    PerformanceSummary,
)
from src.core.exceptions import TeamNotFoundError
from src.main import app


@pytest.fixture
def mock_analytics_service() -> AsyncMock:
    """Create mock analytics service."""
    return AsyncMock()


@pytest.fixture
def mock_performance_summary() -> PerformanceSummary:
    """Create mock performance summary."""
    return PerformanceSummary(
        total_pnl=Decimal("500.00"),
        total_pnl_percent=5.0,
        win_rate=0.6,
        sharpe_ratio=1.2,
        max_drawdown=0.15,
        total_trades=10,
        winning_trades=6,
        losing_trades=4,
    )


@pytest.fixture
def mock_performance_metrics() -> list[PerformanceMetricResponse]:
    """Create mock performance metrics."""
    metrics = []
    for i in range(3):
        metric = MagicMock(spec=PerformanceMetricResponse)
        metric.id = i + 1
        metric.team_instance_id = 1
        metric.timestamp = datetime(2025, 1, 1, i, 0, 0, tzinfo=UTC)
        metric.period = "hourly"
        metric.pnl = Decimal("100.00") * (i + 1)
        metric.pnl_percent = 1.0 * (i + 1)
        metric.win_rate = 0.5 + (i * 0.1)
        metric.sharpe_ratio = 1.0 + (i * 0.2)
        metric.max_drawdown = 0.1 * (i + 1)
        metric.trade_count = 5 * (i + 1)
        metrics.append(metric)
    return metrics


@pytest.fixture
def mock_agent_decisions() -> list[AgentDecisionResponse]:
    """Create mock agent decision logs."""
    decisions = []
    for i in range(3):
        decision = MagicMock(spec=AgentDecisionResponse)
        decision.id = i + 1
        decision.team_instance_id = 1
        decision.agent_name = "MarketAnalyzer" if i < 2 else "RiskManager"
        decision.decision_type = "SIGNAL"
        decision.data = {"action": "BUY", "symbol": "EUR/USD"}
        decision.confidence = 0.8
        decision.created_at = datetime(2025, 1, 1, i, 0, 0, tzinfo=UTC)
        decisions.append(decision)
    return decisions


class TestGetPerformanceSummary:
    """Tests for GET /api/analytics/teams/{team_id}/summary endpoint."""

    @pytest.mark.asyncio
    async def test_get_performance_summary_success(
        self,
        mock_analytics_service: AsyncMock,
        mock_performance_summary: PerformanceSummary,
    ) -> None:
        """Test successfully getting performance summary."""
        mock_analytics_service.get_performance_summary.return_value = mock_performance_summary

        with patch(
            "src.api.routes.analytics.get_analytics_service",
            return_value=mock_analytics_service,
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get("/api/analytics/teams/1/summary")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_pnl"] == "500.00"
        assert data["total_pnl_percent"] == 5.0
        assert data["win_rate"] == 0.6
        assert data["sharpe_ratio"] == 1.2
        assert data["max_drawdown"] == 0.15
        assert data["total_trades"] == 10
        assert data["winning_trades"] == 6
        assert data["losing_trades"] == 4

        mock_analytics_service.get_performance_summary.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_performance_summary_team_not_found(
        self,
        mock_analytics_service: AsyncMock,
    ) -> None:
        """Test getting performance summary for non-existent team."""
        mock_analytics_service.get_performance_summary.side_effect = TeamNotFoundError(
            "Team instance with ID 999 not found"
        )

        with patch(
            "src.api.routes.analytics.get_analytics_service",
            return_value=mock_analytics_service,
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get("/api/analytics/teams/999/summary")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"]["code"] == "TEAM_NOT_FOUND"
        assert "999" in data["detail"]["message"]


class TestGetPerformanceHistory:
    """Tests for GET /api/analytics/teams/{team_id}/history endpoint."""

    @pytest.mark.asyncio
    async def test_get_performance_history_success(
        self,
        mock_analytics_service: AsyncMock,
        mock_performance_metrics: list[PerformanceMetricResponse],
    ) -> None:
        """Test successfully getting performance history."""
        mock_analytics_service.get_performance_history.return_value = (
            mock_performance_metrics
        )

        with patch(
            "src.api.routes.analytics.get_analytics_service",
            return_value=mock_analytics_service,
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get("/api/analytics/teams/1/history")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3

        mock_analytics_service.get_performance_history.assert_called_once_with(
            team_id=1,
            period="daily",
            start_time=None,
            limit=100,
        )

    @pytest.mark.asyncio
    async def test_get_performance_history_with_filters(
        self,
        mock_analytics_service: AsyncMock,
        mock_performance_metrics: list[PerformanceMetricResponse],
    ) -> None:
        """Test getting performance history with query parameters."""
        mock_analytics_service.get_performance_history.return_value = (
            mock_performance_metrics
        )

        with patch(
            "src.api.routes.analytics.get_analytics_service",
            return_value=mock_analytics_service,
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get(
                    "/api/analytics/teams/1/history",
                    params={
                        "period": "hourly",
                        "since": "2025-01-01T00:00:00Z",
                        "limit": 50,
                    },
                )

        assert response.status_code == status.HTTP_200_OK

        # Verify call arguments
        call_kwargs = mock_analytics_service.get_performance_history.call_args.kwargs
        assert call_kwargs["team_id"] == 1
        assert call_kwargs["period"] == "hourly"
        assert call_kwargs["limit"] == 50
        assert isinstance(call_kwargs["start_time"], datetime)

    @pytest.mark.asyncio
    async def test_get_performance_history_empty(
        self,
        mock_analytics_service: AsyncMock,
    ) -> None:
        """Test getting performance history with no records."""
        mock_analytics_service.get_performance_history.return_value = []

        with patch(
            "src.api.routes.analytics.get_analytics_service",
            return_value=mock_analytics_service,
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get("/api/analytics/teams/1/history")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == []

    @pytest.mark.asyncio
    async def test_get_performance_history_team_not_found(
        self,
        mock_analytics_service: AsyncMock,
    ) -> None:
        """Test getting performance history for non-existent team."""
        mock_analytics_service.get_performance_history.side_effect = TeamNotFoundError(
            "Team instance with ID 999 not found"
        )

        with patch(
            "src.api.routes.analytics.get_analytics_service",
            return_value=mock_analytics_service,
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get("/api/analytics/teams/999/history")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"]["code"] == "TEAM_NOT_FOUND"


class TestGetPnlBySymbol:
    """Tests for GET /api/analytics/teams/{team_id}/pnl-by-symbol endpoint."""

    @pytest.mark.asyncio
    async def test_get_pnl_by_symbol_success(
        self,
        mock_analytics_service: AsyncMock,
    ) -> None:
        """Test successfully getting P/L by symbol."""
        mock_pnl_data = {
            "EUR/USD": Decimal("300.00"),
            "GBP/USD": Decimal("200.00"),
        }
        mock_analytics_service.calculate_pnl_by_symbol.return_value = mock_pnl_data

        with patch(
            "src.api.routes.analytics.get_analytics_service",
            return_value=mock_analytics_service,
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get("/api/analytics/teams/1/pnl-by-symbol")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["EUR/USD"] == "300.00"
        assert data["GBP/USD"] == "200.00"
        assert len(data) == 2

        mock_analytics_service.calculate_pnl_by_symbol.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_pnl_by_symbol_empty(
        self,
        mock_analytics_service: AsyncMock,
    ) -> None:
        """Test getting P/L by symbol with no trades."""
        mock_analytics_service.calculate_pnl_by_symbol.return_value = {}

        with patch(
            "src.api.routes.analytics.get_analytics_service",
            return_value=mock_analytics_service,
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get("/api/analytics/teams/1/pnl-by-symbol")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == {}

    @pytest.mark.asyncio
    async def test_get_pnl_by_symbol_team_not_found(
        self,
        mock_analytics_service: AsyncMock,
    ) -> None:
        """Test getting P/L by symbol for non-existent team."""
        mock_analytics_service.calculate_pnl_by_symbol.side_effect = TeamNotFoundError(
            "Team instance with ID 999 not found"
        )

        with patch(
            "src.api.routes.analytics.get_analytics_service",
            return_value=mock_analytics_service,
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get("/api/analytics/teams/999/pnl-by-symbol")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"]["code"] == "TEAM_NOT_FOUND"


class TestGetAgentActivity:
    """Tests for GET /api/analytics/teams/{team_id}/activity endpoint."""

    @pytest.mark.asyncio
    async def test_get_agent_activity_success(
        self,
        mock_analytics_service: AsyncMock,
        mock_agent_decisions: list[AgentDecisionResponse],
    ) -> None:
        """Test successfully getting agent activity."""
        mock_analytics_service.get_agent_activity.return_value = mock_agent_decisions

        with patch(
            "src.api.routes.analytics.get_analytics_service",
            return_value=mock_analytics_service,
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get("/api/analytics/teams/1/activity")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3

        mock_analytics_service.get_agent_activity.assert_called_once_with(
            team_id=1,
            agent_name=None,
            decision_type=None,
        )

    @pytest.mark.asyncio
    async def test_get_agent_activity_with_filters(
        self,
        mock_analytics_service: AsyncMock,
        mock_agent_decisions: list[AgentDecisionResponse],
    ) -> None:
        """Test getting agent activity with query parameters."""
        filtered_decisions = [mock_agent_decisions[0]]
        mock_analytics_service.get_agent_activity.return_value = filtered_decisions

        with patch(
            "src.api.routes.analytics.get_analytics_service",
            return_value=mock_analytics_service,
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get(
                    "/api/analytics/teams/1/activity",
                    params={
                        "agent": "MarketAnalyzer",
                        "type": "SIGNAL",
                        "limit": 50,
                    },
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1

        mock_analytics_service.get_agent_activity.assert_called_once_with(
            team_id=1,
            agent_name="MarketAnalyzer",
            decision_type="SIGNAL",
        )

    @pytest.mark.asyncio
    async def test_get_agent_activity_limit_applied(
        self,
        mock_analytics_service: AsyncMock,
    ) -> None:
        """Test that limit parameter is correctly applied."""
        # Create 150 mock decisions
        many_decisions = [MagicMock(spec=AgentDecisionResponse) for _ in range(150)]
        mock_analytics_service.get_agent_activity.return_value = many_decisions

        with patch(
            "src.api.routes.analytics.get_analytics_service",
            return_value=mock_analytics_service,
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get(
                    "/api/analytics/teams/1/activity",
                    params={"limit": 100},
                )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Limit should be applied to returned data
        assert len(data) == 100

    @pytest.mark.asyncio
    async def test_get_agent_activity_empty(
        self,
        mock_analytics_service: AsyncMock,
    ) -> None:
        """Test getting agent activity with no decisions."""
        mock_analytics_service.get_agent_activity.return_value = []

        with patch(
            "src.api.routes.analytics.get_analytics_service",
            return_value=mock_analytics_service,
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get("/api/analytics/teams/1/activity")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == []

    @pytest.mark.asyncio
    async def test_get_agent_activity_team_not_found(
        self,
        mock_analytics_service: AsyncMock,
    ) -> None:
        """Test getting agent activity for non-existent team."""
        mock_analytics_service.get_agent_activity.side_effect = TeamNotFoundError(
            "Team instance with ID 999 not found"
        )

        with patch(
            "src.api.routes.analytics.get_analytics_service",
            return_value=mock_analytics_service,
        ):
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get("/api/analytics/teams/999/activity")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert data["detail"]["code"] == "TEAM_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_get_agent_activity_invalid_limit(
        self,
        mock_analytics_service: AsyncMock,
    ) -> None:
        """Test getting agent activity with invalid limit parameter."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # Limit too large (> 1000)
            response = await client.get(
                "/api/analytics/teams/1/activity",
                params={"limit": 2000},
            )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # Limit too small (< 1)
            response = await client.get(
                "/api/analytics/teams/1/activity",
                params={"limit": 0},
            )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
