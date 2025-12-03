"""Tests for Budget Manager."""

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.db.models import TeamInstance, Trade
from src.services.budget_manager import BudgetError, BudgetManager


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create mock async session."""
    return AsyncMock()


@pytest.fixture
def budget_manager(mock_session: AsyncMock) -> BudgetManager:
    """Create budget manager with mock session."""
    return BudgetManager(session=mock_session)


@pytest.fixture
def mock_team_instance() -> TeamInstance:
    """Create mock team instance."""
    team = MagicMock(spec=TeamInstance)
    team.id = 1
    team.name = "Test Team"
    team.initial_budget = Decimal("10000.00")
    team.current_budget = Decimal("10000.00")
    team.realized_pnl = Decimal("0.00")
    team.unrealized_pnl = Decimal("0.00")
    return team


class TestGetTeamInstance:
    """Tests for get_team_instance method."""

    async def test_get_team_instance_found(
        self,
        budget_manager: BudgetManager,
        mock_session: AsyncMock,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test getting existing team instance."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_team_instance
        mock_session.execute.return_value = mock_result

        team = await budget_manager.get_team_instance(1)

        assert team.id == 1
        assert team.name == "Test Team"

    async def test_get_team_instance_not_found(
        self,
        budget_manager: BudgetManager,
        mock_session: AsyncMock,
    ) -> None:
        """Test getting non-existent team instance raises error."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        with pytest.raises(BudgetError) as exc_info:
            await budget_manager.get_team_instance(999)

        assert "not found" in str(exc_info.value)


class TestAllocateBudget:
    """Tests for allocate_budget method."""

    async def test_allocate_budget_success(
        self,
        budget_manager: BudgetManager,
        mock_session: AsyncMock,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test successful budget allocation."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_team_instance
        mock_session.execute.return_value = mock_result

        new_budget = await budget_manager.allocate_budget(1, Decimal("1000.00"))

        assert new_budget == Decimal("9000.00")
        mock_session.flush.assert_called_once()

    async def test_allocate_budget_insufficient(
        self,
        budget_manager: BudgetManager,
        mock_session: AsyncMock,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test allocation with insufficient budget raises error."""
        mock_team_instance.current_budget = Decimal("500.00")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_team_instance
        mock_session.execute.return_value = mock_result

        with pytest.raises(BudgetError) as exc_info:
            await budget_manager.allocate_budget(1, Decimal("1000.00"))

        assert "Insufficient budget" in str(exc_info.value)


class TestReleaseBudget:
    """Tests for release_budget method."""

    async def test_release_budget_with_profit(
        self,
        budget_manager: BudgetManager,
        mock_session: AsyncMock,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test releasing budget with profit."""
        mock_team_instance.current_budget = Decimal("9000.00")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_team_instance
        mock_session.execute.return_value = mock_result

        new_budget = await budget_manager.release_budget(
            1, Decimal("1000.00"), Decimal("100.00")
        )

        assert new_budget == Decimal("10100.00")
        assert mock_team_instance.realized_pnl == Decimal("100.00")

    async def test_release_budget_with_loss(
        self,
        budget_manager: BudgetManager,
        mock_session: AsyncMock,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test releasing budget with loss."""
        mock_team_instance.current_budget = Decimal("9000.00")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_team_instance
        mock_session.execute.return_value = mock_result

        new_budget = await budget_manager.release_budget(
            1, Decimal("1000.00"), Decimal("-50.00")
        )

        assert new_budget == Decimal("9950.00")
        assert mock_team_instance.realized_pnl == Decimal("-50.00")


class TestUpdateUnrealizedPnl:
    """Tests for update_unrealized_pnl method."""

    async def test_update_unrealized_pnl(
        self,
        budget_manager: BudgetManager,
        mock_session: AsyncMock,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test updating unrealized P/L."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_team_instance
        mock_session.execute.return_value = mock_result

        await budget_manager.update_unrealized_pnl(1, Decimal("250.00"))

        assert mock_team_instance.unrealized_pnl == Decimal("250.00")
        mock_session.flush.assert_called_once()


class TestRecordTradeOpen:
    """Tests for record_trade_open method."""

    async def test_record_trade_open(
        self,
        budget_manager: BudgetManager,
        mock_session: AsyncMock,
    ) -> None:
        """Test recording a new trade."""
        await budget_manager.record_trade_open(
            team_instance_id=1,
            ticket=123,
            symbol="EUR/USD",
            side="BUY",
            size=Decimal("0.1"),
            entry_price=Decimal("1.08500"),
            stop_loss=Decimal("1.08000"),
            spread_cost=Decimal("2.00"),
            magic_number=12345,
            comment="Test trade",
        )

        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()


class TestRecordTradeClose:
    """Tests for record_trade_close method."""

    async def test_record_trade_close(
        self,
        budget_manager: BudgetManager,
        mock_session: AsyncMock,
    ) -> None:
        """Test closing a trade."""
        mock_trade = MagicMock(spec=Trade)
        mock_trade.id = 1
        mock_trade.ticket = 123
        mock_trade.status = "open"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_trade
        mock_session.execute.return_value = mock_result

        await budget_manager.record_trade_close(
            trade_id=1,
            exit_price=Decimal("1.08600"),
            pnl=Decimal("10.00"),
        )

        assert mock_trade.exit_price == Decimal("1.08600")
        assert mock_trade.pnl == Decimal("10.00")
        assert mock_trade.status == "closed"
        assert mock_trade.closed_at is not None

    async def test_record_trade_close_not_found(
        self,
        budget_manager: BudgetManager,
        mock_session: AsyncMock,
    ) -> None:
        """Test closing non-existent trade raises error."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        with pytest.raises(BudgetError) as exc_info:
            await budget_manager.record_trade_close(999, Decimal("1.0"), Decimal("0"))

        assert "not found" in str(exc_info.value)

    async def test_record_trade_close_already_closed(
        self,
        budget_manager: BudgetManager,
        mock_session: AsyncMock,
    ) -> None:
        """Test closing already closed trade raises error."""
        mock_trade = MagicMock(spec=Trade)
        mock_trade.id = 1
        mock_trade.status = "closed"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_trade
        mock_session.execute.return_value = mock_result

        with pytest.raises(BudgetError) as exc_info:
            await budget_manager.record_trade_close(1, Decimal("1.0"), Decimal("0"))

        assert "already closed" in str(exc_info.value)


class TestGetOpenTrades:
    """Tests for get_open_trades method."""

    async def test_get_open_trades(
        self,
        budget_manager: BudgetManager,
        mock_session: AsyncMock,
    ) -> None:
        """Test getting open trades."""
        mock_trades = [MagicMock(spec=Trade), MagicMock(spec=Trade)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_trades
        mock_session.execute.return_value = mock_result

        trades = await budget_manager.get_open_trades(1)

        assert len(trades) == 2


class TestGetTradeByTicket:
    """Tests for get_trade_by_ticket method."""

    async def test_get_trade_by_ticket_found(
        self,
        budget_manager: BudgetManager,
        mock_session: AsyncMock,
    ) -> None:
        """Test getting trade by ticket."""
        mock_trade = MagicMock(spec=Trade)
        mock_trade.ticket = 123
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_trade
        mock_session.execute.return_value = mock_result

        trade = await budget_manager.get_trade_by_ticket(1, 123)

        assert trade.ticket == 123

    async def test_get_trade_by_ticket_not_found(
        self,
        budget_manager: BudgetManager,
        mock_session: AsyncMock,
    ) -> None:
        """Test getting non-existent trade by ticket."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        trade = await budget_manager.get_trade_by_ticket(1, 999)

        assert trade is None


class TestGetBudgetSummary:
    """Tests for get_budget_summary method."""

    async def test_get_budget_summary(
        self,
        budget_manager: BudgetManager,
        mock_session: AsyncMock,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test getting budget summary."""
        mock_team_instance.current_budget = Decimal("10500.00")
        mock_team_instance.realized_pnl = Decimal("400.00")
        mock_team_instance.unrealized_pnl = Decimal("100.00")
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_team_instance
        mock_session.execute.return_value = mock_result

        summary = await budget_manager.get_budget_summary(1)

        assert summary["team_instance_id"] == 1
        assert summary["initial_budget"] == Decimal("10000.00")
        assert summary["current_budget"] == Decimal("10500.00")
        assert summary["realized_pnl"] == Decimal("400.00")
        assert summary["unrealized_pnl"] == Decimal("100.00")
        assert summary["total_equity"] == Decimal("10600.00")
        assert summary["total_return_pct"] == Decimal("6.00")


class TestTeamInstanceModel:
    """Tests for TeamInstance model fields."""

    def test_team_instance_defaults(self) -> None:
        """Test TeamInstance default values."""
        # This tests the model definition, not actual DB behavior
        team = TeamInstance(name="Test Team")

        assert team.name == "Test Team"
        # Defaults are set by SQLAlchemy, so we check the class definition
        assert TeamInstance.initial_budget.default.arg == Decimal("10000.00")
        assert TeamInstance.current_budget.default.arg == Decimal("10000.00")
        assert TeamInstance.realized_pnl.default.arg == Decimal("0.00")
        assert TeamInstance.unrealized_pnl.default.arg == Decimal("0.00")


class TestTradeModel:
    """Tests for Trade model fields."""

    def test_trade_status_default(self) -> None:
        """Test Trade status default."""
        assert Trade.status.default.arg == "open"

    def test_trade_spread_cost_default(self) -> None:
        """Test Trade spread_cost default."""
        assert Trade.spread_cost.default.arg == Decimal("0.00")
