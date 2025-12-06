"""Tests for Analytics REST API endpoints - Story 006-04."""

from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from src.api.schemas.analytics import (
    ActivitySummary,
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
        from src.api.routes.analytics import get_analytics_service

        mock_analytics_service.get_performance_summary.return_value = mock_performance_summary

        async def mock_get_analytics_service():
            return mock_analytics_service

        app.dependency_overrides[get_analytics_service] = mock_get_analytics_service

        try:
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_performance_summary_team_not_found(
        self,
        mock_analytics_service: AsyncMock,
    ) -> None:
        """Test getting performance summary for non-existent team."""
        from src.api.routes.analytics import get_analytics_service

        mock_analytics_service.get_performance_summary.side_effect = TeamNotFoundError(
            "Team instance with ID 999 not found"
        )

        async def mock_get_analytics_service():
            return mock_analytics_service

        app.dependency_overrides[get_analytics_service] = mock_get_analytics_service

        try:
        finally:
            app.dependency_overrides.clear()

class TestGetPerformanceHistory:
    """Tests for GET /api/analytics/teams/{team_id}/history endpoint."""

    @pytest.mark.asyncio
    async def test_get_performance_history_success(
        self,
        mock_analytics_service: AsyncMock,
        mock_performance_metrics: list[PerformanceMetricResponse],
    ) -> None:
        """Test successfully getting performance history."""
        from src.api.routes.analytics import get_analytics_service

        mock_analytics_service.get_performance_history.return_value = (
            mock_performance_metrics
        )

        async def mock_get_analytics_service():
            return mock_analytics_service

        app.dependency_overrides[get_analytics_service] = mock_get_analytics_service

        try:
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_performance_history_with_filters(
        self,
        mock_analytics_service: AsyncMock,
        mock_performance_metrics: list[PerformanceMetricResponse],
    ) -> None:
        """Test getting performance history with query parameters."""
        from src.api.routes.analytics import get_analytics_service

        mock_analytics_service.get_performance_history.return_value = (
            mock_performance_metrics
        )

        async def mock_get_analytics_service():
            return mock_analytics_service

        app.dependency_overrides[get_analytics_service] = mock_get_analytics_service

        try:
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_performance_history_empty(
        self,
        mock_analytics_service: AsyncMock,
    ) -> None:
        """Test getting performance history with no records."""
        mock_analytics_service.get_performance_history.return_value = []

        from src.api.routes.analytics import get_analytics_service

        async def mock_get_analytics_service():
            return mock_analytics_service

        app.dependency_overrides[get_analytics_service] = mock_get_analytics_service

        try:
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_performance_history_team_not_found(
        self,
        mock_analytics_service: AsyncMock,
    ) -> None:
        """Test getting performance history for non-existent team."""
        mock_analytics_service.get_performance_history.side_effect = TeamNotFoundError(
            "Team instance with ID 999 not found"
        )

        from src.api.routes.analytics import get_analytics_service

        async def mock_get_analytics_service():
            return mock_analytics_service

        app.dependency_overrides[get_analytics_service] = mock_get_analytics_service

        try:
        finally:
            app.dependency_overrides.clear()

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

        from src.api.routes.analytics import get_analytics_service

        async def mock_get_analytics_service():
            return mock_analytics_service

        app.dependency_overrides[get_analytics_service] = mock_get_analytics_service

        try:
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_pnl_by_symbol_empty(
        self,
        mock_analytics_service: AsyncMock,
    ) -> None:
        """Test getting P/L by symbol with no trades."""
        mock_analytics_service.calculate_pnl_by_symbol.return_value = {}

        from src.api.routes.analytics import get_analytics_service

        async def mock_get_analytics_service():
            return mock_analytics_service

        app.dependency_overrides[get_analytics_service] = mock_get_analytics_service

        try:
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_pnl_by_symbol_team_not_found(
        self,
        mock_analytics_service: AsyncMock,
    ) -> None:
        """Test getting P/L by symbol for non-existent team."""
        mock_analytics_service.calculate_pnl_by_symbol.side_effect = TeamNotFoundError(
            "Team instance with ID 999 not found"
        )

        from src.api.routes.analytics import get_analytics_service

        async def mock_get_analytics_service():
            return mock_analytics_service

        app.dependency_overrides[get_analytics_service] = mock_get_analytics_service

        try:
        finally:
            app.dependency_overrides.clear()

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

        from src.api.routes.analytics import get_analytics_service

        async def mock_get_analytics_service():
            return mock_analytics_service

        app.dependency_overrides[get_analytics_service] = mock_get_analytics_service

        try:
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_agent_activity_with_filters(
        self,
        mock_analytics_service: AsyncMock,
        mock_agent_decisions: list[AgentDecisionResponse],
    ) -> None:
        """Test getting agent activity with query parameters."""
        filtered_decisions = [mock_agent_decisions[0]]
        mock_analytics_service.get_agent_activity.return_value = filtered_decisions

        from src.api.routes.analytics import get_analytics_service

        async def mock_get_analytics_service():
            return mock_analytics_service

        app.dependency_overrides[get_analytics_service] = mock_get_analytics_service

        try:
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_agent_activity_limit_applied(
        self,
        mock_analytics_service: AsyncMock,
    ) -> None:
        """Test that limit parameter is correctly applied."""
        # Create 150 mock decisions
        many_decisions = [MagicMock(spec=AgentDecisionResponse) for _ in range(150)]
        mock_analytics_service.get_agent_activity.return_value = many_decisions

        from src.api.routes.analytics import get_analytics_service

        async def mock_get_analytics_service():
            return mock_analytics_service

        app.dependency_overrides[get_analytics_service] = mock_get_analytics_service

        try:
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_agent_activity_empty(
        self,
        mock_analytics_service: AsyncMock,
    ) -> None:
        """Test getting agent activity with no decisions."""
        mock_analytics_service.get_agent_activity.return_value = []

        from src.api.routes.analytics import get_analytics_service

        async def mock_get_analytics_service():
            return mock_analytics_service

        app.dependency_overrides[get_analytics_service] = mock_get_analytics_service

        try:
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_agent_activity_team_not_found(
        self,
        mock_analytics_service: AsyncMock,
    ) -> None:
        """Test getting agent activity for non-existent team."""
        mock_analytics_service.get_agent_activity.side_effect = TeamNotFoundError(
            "Team instance with ID 999 not found"
        )

        from src.api.routes.analytics import get_analytics_service

        async def mock_get_analytics_service():
            return mock_analytics_service

        app.dependency_overrides[get_analytics_service] = mock_get_analytics_service

        try:
        finally:
            app.dependency_overrides.clear()

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
        finally:
            app.dependency_overrides.clear()
