"""Tests for Team Lifecycle Manager - Story 005-04."""

import asyncio
from decimal import Decimal
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.core.exceptions import (
    TeamNotFoundError,
    TemplateNotFoundError,
    ValidationError,
)
from src.db.models import TeamInstance, TeamInstanceMode, TeamInstanceStatus
from src.services.team_lifecycle import TeamLifecycleManager
from src.teams.schemas import TeamTemplate


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create mock async session."""
    session = AsyncMock()
    session.flush = AsyncMock()
    return session


@pytest.fixture
def mock_team_instance() -> TeamInstance:
    """Create mock team instance."""
    team = MagicMock(spec=TeamInstance)
    team.id = 1
    team.name = "Test Team"
    team.template_name = "conservative_llm"
    team.symbols = ["EUR/USD", "GBP/USD"]
    team.current_budget = Decimal("10000.00")
    team.initial_budget = Decimal("10000.00")
    team.status = TeamInstanceStatus.STOPPED
    team.mode = TeamInstanceMode.PAPER
    return team


@pytest.fixture
def mock_template() -> TeamTemplate:
    """Create mock team template."""
    return TeamTemplate(
        name="Conservative LLM",
        version="1.0.0",
        roles={
            "llm_advisor": {
                "class_name": "LLMAdvisor",
                "params": {"model": "gpt-4"},
            }
        },
        pipeline=[{"agent": "llm_advisor", "method": "analyze"}],
        override_rules=[],
    )


@pytest.fixture
def lifecycle_manager(mock_session: AsyncMock, tmp_path: Path) -> TeamLifecycleManager:
    """Create lifecycle manager with mock session."""
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    return TeamLifecycleManager(session=mock_session, template_dir=template_dir)


class TestStartTeam:
    """Tests for start_team method."""

    async def test_start_team_success(
        self,
        lifecycle_manager: TeamLifecycleManager,
        mock_session: AsyncMock,
        mock_team_instance: TeamInstance,
        mock_template: TeamTemplate,
        tmp_path: Path,
    ) -> None:
        """Test successful team start."""
        # Setup
        template_path = tmp_path / "templates" / "conservative_llm.yaml"
        template_path.write_text("name: Conservative LLM\nroles: {}\npipeline: []\noverride_rules: []")

        lifecycle_manager.repo = AsyncMock()
        lifecycle_manager.repo.get_by_id = AsyncMock(return_value=mock_team_instance)
        lifecycle_manager.repo.update_status = AsyncMock(return_value=mock_team_instance)

        with patch.object(lifecycle_manager.loader, "load_template", return_value=mock_template):
            with patch.object(lifecycle_manager.loader, "validate_template", return_value=[]):
                with patch("src.services.team_lifecycle.TeamOrchestrator") as mock_orch:
                    mock_orch.return_value = MagicMock()

                    # Execute
                    result = await lifecycle_manager.start_team(1)

                    # Verify
                    assert result == mock_team_instance
                    assert 1 in lifecycle_manager._orchestrators
                    assert 1 in lifecycle_manager._tasks
                    lifecycle_manager.repo.update_status.assert_called_once_with(
                        1, TeamInstanceStatus.ACTIVE
                    )

    async def test_start_team_not_found(
        self,
        lifecycle_manager: TeamLifecycleManager,
    ) -> None:
        """Test starting non-existent team raises error."""
        lifecycle_manager.repo = AsyncMock()
        lifecycle_manager.repo.get_by_id = AsyncMock(return_value=None)

        with pytest.raises(TeamNotFoundError) as exc_info:
            await lifecycle_manager.start_team(999)

        assert "not found" in str(exc_info.value)

    async def test_start_team_already_active(
        self,
        lifecycle_manager: TeamLifecycleManager,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test starting already active team raises error."""
        mock_team_instance.status = TeamInstanceStatus.ACTIVE

        lifecycle_manager.repo = AsyncMock()
        lifecycle_manager.repo.get_by_id = AsyncMock(return_value=mock_team_instance)

        with pytest.raises(ValidationError) as exc_info:
            await lifecycle_manager.start_team(1)

        assert "already active" in str(exc_info.value)

    async def test_start_team_insufficient_budget(
        self,
        lifecycle_manager: TeamLifecycleManager,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test starting team with zero budget raises error."""
        mock_team_instance.current_budget = Decimal("0.00")

        lifecycle_manager.repo = AsyncMock()
        lifecycle_manager.repo.get_by_id = AsyncMock(return_value=mock_team_instance)

        with pytest.raises(ValidationError) as exc_info:
            await lifecycle_manager.start_team(1)

        assert "insufficient budget" in str(exc_info.value)

    async def test_start_team_no_symbols(
        self,
        lifecycle_manager: TeamLifecycleManager,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test starting team with no symbols raises error."""
        mock_team_instance.symbols = []

        lifecycle_manager.repo = AsyncMock()
        lifecycle_manager.repo.get_by_id = AsyncMock(return_value=mock_team_instance)

        with pytest.raises(ValidationError) as exc_info:
            await lifecycle_manager.start_team(1)

        assert "no trading symbols" in str(exc_info.value)

    async def test_start_team_invalid_symbol_format(
        self,
        lifecycle_manager: TeamLifecycleManager,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test starting team with invalid symbol format raises error."""
        mock_team_instance.symbols = ["EURUSD"]  # Missing slash

        lifecycle_manager.repo = AsyncMock()
        lifecycle_manager.repo.get_by_id = AsyncMock(return_value=mock_team_instance)

        with pytest.raises(ValidationError) as exc_info:
            await lifecycle_manager.start_team(1)

        assert "Invalid symbol format" in str(exc_info.value)
        assert "EUR/USD" in str(exc_info.value)

    async def test_start_team_template_not_found(
        self,
        lifecycle_manager: TeamLifecycleManager,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test starting team with missing template raises error."""
        lifecycle_manager.repo = AsyncMock()
        lifecycle_manager.repo.get_by_id = AsyncMock(return_value=mock_team_instance)

        with pytest.raises(TemplateNotFoundError) as exc_info:
            await lifecycle_manager.start_team(1)

        assert "not found" in str(exc_info.value)


class TestPauseTeam:
    """Tests for pause_team method."""

    async def test_pause_team_success(
        self,
        lifecycle_manager: TeamLifecycleManager,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test successful team pause."""
        mock_team_instance.status = TeamInstanceStatus.ACTIVE

        lifecycle_manager.repo = AsyncMock()
        lifecycle_manager.repo.get_by_id = AsyncMock(return_value=mock_team_instance)
        lifecycle_manager.repo.update_status = AsyncMock(return_value=mock_team_instance)

        # Simulate running task - create real asyncio.Task
        async def dummy_task():
            await asyncio.sleep(10)

        task = asyncio.create_task(dummy_task())
        lifecycle_manager._tasks[1] = task
        lifecycle_manager._orchestrators[1] = MagicMock()

        # Execute
        result = await lifecycle_manager.pause_team(1)

        # Verify
        assert result == mock_team_instance
        assert 1 not in lifecycle_manager._tasks  # Task removed
        assert 1 in lifecycle_manager._orchestrators  # Orchestrator kept
        lifecycle_manager.repo.update_status.assert_called_once_with(
            1, TeamInstanceStatus.PAUSED
        )

    async def test_pause_team_not_active(
        self,
        lifecycle_manager: TeamLifecycleManager,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test pausing non-active team raises error."""
        mock_team_instance.status = TeamInstanceStatus.STOPPED

        lifecycle_manager.repo = AsyncMock()
        lifecycle_manager.repo.get_by_id = AsyncMock(return_value=mock_team_instance)

        with pytest.raises(ValidationError) as exc_info:
            await lifecycle_manager.pause_team(1)

        assert "Can only pause active teams" in str(exc_info.value)


class TestStopTeam:
    """Tests for stop_team method."""

    async def test_stop_team_success_with_close_positions(
        self,
        lifecycle_manager: TeamLifecycleManager,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test successful team stop with position closing."""
        mock_team_instance.status = TeamInstanceStatus.ACTIVE

        lifecycle_manager.repo = AsyncMock()
        lifecycle_manager.repo.get_by_id = AsyncMock(return_value=mock_team_instance)
        lifecycle_manager.repo.update_status = AsyncMock(return_value=mock_team_instance)

        # Mock _close_all_positions
        lifecycle_manager._close_all_positions = AsyncMock()

        # Simulate running task
        mock_task = AsyncMock()
        mock_task.cancel = MagicMock()
        lifecycle_manager._tasks[1] = mock_task
        lifecycle_manager._orchestrators[1] = MagicMock()

        # Execute
        result = await lifecycle_manager.stop_team(1, close_positions=True)

        # Verify
        assert result == mock_team_instance
        assert 1 not in lifecycle_manager._tasks
        assert 1 not in lifecycle_manager._orchestrators
        lifecycle_manager._close_all_positions.assert_called_once_with(1)
        lifecycle_manager.repo.update_status.assert_called_once_with(
            1, TeamInstanceStatus.STOPPED
        )

    async def test_stop_team_without_close_positions(
        self,
        lifecycle_manager: TeamLifecycleManager,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test team stop without position closing."""
        mock_team_instance.status = TeamInstanceStatus.ACTIVE

        lifecycle_manager.repo = AsyncMock()
        lifecycle_manager.repo.get_by_id = AsyncMock(return_value=mock_team_instance)
        lifecycle_manager.repo.update_status = AsyncMock(return_value=mock_team_instance)

        # Mock _close_all_positions
        lifecycle_manager._close_all_positions = AsyncMock()

        # Simulate running task
        mock_task = AsyncMock()
        mock_task.cancel = MagicMock()
        lifecycle_manager._tasks[1] = mock_task
        lifecycle_manager._orchestrators[1] = MagicMock()

        # Execute
        result = await lifecycle_manager.stop_team(1, close_positions=False)

        # Verify
        assert result == mock_team_instance
        lifecycle_manager._close_all_positions.assert_not_called()

    async def test_stop_team_already_stopped(
        self,
        lifecycle_manager: TeamLifecycleManager,
        mock_team_instance: TeamInstance,
    ) -> None:
        """Test stopping already stopped team returns without error."""
        mock_team_instance.status = TeamInstanceStatus.STOPPED

        lifecycle_manager.repo = AsyncMock()
        lifecycle_manager.repo.get_by_id = AsyncMock(return_value=mock_team_instance)

        # Execute (should not raise)
        result = await lifecycle_manager.stop_team(1)

        # Verify
        assert result == mock_team_instance


class TestGetRunningTeams:
    """Tests for get_running_teams method."""

    def test_get_running_teams_empty(
        self,
        lifecycle_manager: TeamLifecycleManager,
    ) -> None:
        """Test getting running teams when none are running."""
        result = lifecycle_manager.get_running_teams()
        assert result == []

    def test_get_running_teams_multiple(
        self,
        lifecycle_manager: TeamLifecycleManager,
    ) -> None:
        """Test getting multiple running teams."""
        lifecycle_manager._tasks[1] = MagicMock()
        lifecycle_manager._tasks[2] = MagicMock()
        lifecycle_manager._tasks[3] = MagicMock()

        result = lifecycle_manager.get_running_teams()
        assert sorted(result) == [1, 2, 3]


class TestStartupShutdown:
    """Tests for startup and shutdown methods."""

    async def test_startup_restarts_active_teams(
        self,
        lifecycle_manager: TeamLifecycleManager,
        mock_team_instance: TeamInstance,
        tmp_path: Path,
    ) -> None:
        """Test startup restarts all previously active teams."""
        mock_team_instance.status = TeamInstanceStatus.ACTIVE

        lifecycle_manager.repo = AsyncMock()
        lifecycle_manager.repo.get_active_teams = AsyncMock(return_value=[mock_team_instance])
        lifecycle_manager.start_team = AsyncMock(return_value=mock_team_instance)

        await lifecycle_manager.startup()

        lifecycle_manager.start_team.assert_called_once_with(1)

    async def test_shutdown_stops_all_teams(
        self,
        lifecycle_manager: TeamLifecycleManager,
    ) -> None:
        """Test shutdown stops all running teams."""
        lifecycle_manager._tasks[1] = MagicMock()
        lifecycle_manager._tasks[2] = MagicMock()
        lifecycle_manager.stop_team = AsyncMock()

        await lifecycle_manager.shutdown()

        assert lifecycle_manager.stop_team.call_count == 2


class TestCloseAllPositions:
    """Tests for _close_all_positions method."""

    async def test_close_all_positions_success(
        self,
        lifecycle_manager: TeamLifecycleManager,
        mock_session: AsyncMock,
    ) -> None:
        """Test successfully closing all positions."""
        # Create mock trades
        mock_trade1 = MagicMock()
        mock_trade1.status = "open"
        mock_trade1.entry_price = Decimal("1.1000")
        mock_trade1.exit_price = None

        mock_trade2 = MagicMock()
        mock_trade2.status = "open"
        mock_trade2.entry_price = Decimal("1.2000")
        mock_trade2.exit_price = None

        lifecycle_manager.trade_repo = AsyncMock()
        lifecycle_manager.trade_repo.get_open_trades = AsyncMock(
            return_value=[mock_trade1, mock_trade2]
        )

        await lifecycle_manager._close_all_positions(1)

        # Verify trades were closed
        assert mock_trade1.status == "closed"
        assert mock_trade1.exit_price == Decimal("1.1000")
        assert mock_trade1.pnl == 0

        assert mock_trade2.status == "closed"
        assert mock_trade2.exit_price == Decimal("1.2000")
        assert mock_trade2.pnl == 0

        mock_session.flush.assert_called_once()

    async def test_close_all_positions_no_open_trades(
        self,
        lifecycle_manager: TeamLifecycleManager,
    ) -> None:
        """Test closing positions when no trades are open."""
        lifecycle_manager.trade_repo = AsyncMock()
        lifecycle_manager.trade_repo.get_open_trades = AsyncMock(return_value=[])

        # Should not raise
        await lifecycle_manager._close_all_positions(1)
