"""Team Lifecycle Manager for orchestrating team start/stop/pause - Story 005-04."""

import asyncio
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import TeamNotFoundError, TemplateNotFoundError, ValidationError
from src.db.models import TeamInstance, TeamInstanceStatus
from src.db.repositories.team_repo import TeamRepository
from src.db.repositories.trade_repo import TradeRepository
from src.teams.loader import TeamLoader
from src.teams.orchestrator import TeamOrchestrator

log = structlog.get_logger()


class TeamLifecycleManager:
    """Manages the lifecycle of team instances.

    Responsible for:
    - Starting teams (loading templates, creating orchestrators)
    - Stopping teams (shutting down orchestrators, optionally closing positions)
    - Pausing teams (stopping trading loop, keeping state)
    - Tracking running teams in memory
    """

    def __init__(
        self,
        session: AsyncSession,
        template_dir: Path | None = None,
    ) -> None:
        """Initialize the lifecycle manager.

        Args:
            session: Database session for repository operations.
            template_dir: Directory containing team YAML templates.
        """
        self.session = session
        self.repo = TeamRepository(session)
        self.trade_repo = TradeRepository(session)
        self.loader = TeamLoader()
        self.template_dir = template_dir or Path("team_templates")

        # In-memory tracking of running orchestrators and their tasks
        self._orchestrators: dict[int, TeamOrchestrator] = {}
        self._tasks: dict[int, asyncio.Task] = {}

        log.info(
            "lifecycle_manager_initialized",
            template_dir=str(self.template_dir),
        )

    async def start_team(self, team_id: int) -> TeamInstance:
        """Start a team instance.

        1. Load team from database
        2. Validate team can be started (budget > 0, symbols valid)
        3. Load and validate template
        4. Create orchestrator
        5. Start trading loop as background task
        6. Update status to ACTIVE

        Args:
            team_id: ID of the team to start.

        Returns:
            Updated TeamInstance.

        Raises:
            TeamNotFoundError: If team doesn't exist.
            TemplateNotFoundError: If template file not found.
            ValidationError: If team cannot be started.
        """
        team = await self.repo.get_by_id(team_id)
        if team is None:
            raise TeamNotFoundError(f"Team with ID {team_id} not found")

        if team.status == TeamInstanceStatus.ACTIVE:
            raise ValidationError(f"Team {team_id} is already active")

        if team_id in self._orchestrators:
            raise ValidationError(f"Team {team_id} already has an orchestrator running")

        # Validate budget
        if team.current_budget <= 0:
            raise ValidationError(
                f"Team {team_id} has insufficient budget: {team.current_budget}"
            )

        # Validate symbols
        if not team.symbols or len(team.symbols) == 0:
            raise ValidationError(f"Team {team_id} has no trading symbols configured")

        # Validate symbol format (basic check for canonical format: XXX/YYY)
        for symbol in team.symbols:
            if "/" not in symbol or len(symbol.split("/")) != 2:
                raise ValidationError(
                    f"Invalid symbol format '{symbol}'. Expected canonical format like 'EUR/USD'"
                )

        # Load template
        template_path = self.template_dir / f"{team.template_name}.yaml"
        if not template_path.exists():
            raise TemplateNotFoundError(
                f"Template '{team.template_name}' not found at {template_path}"
            )

        template = self.loader.load_template(template_path)

        # Validate template
        validation_errors = self.loader.validate_template(template)
        if validation_errors:
            raise ValidationError(
                f"Template validation failed: {', '.join(validation_errors)}"
            )

        # Create orchestrator
        orchestrator = TeamOrchestrator(template)
        self._orchestrators[team_id] = orchestrator

        # Start trading loop
        task = asyncio.create_task(
            self._trading_loop(team_id, team.symbols),
            name=f"team_{team_id}_trading_loop",
        )
        self._tasks[team_id] = task

        # Update status
        team = await self.repo.update_status(team_id, TeamInstanceStatus.ACTIVE)

        log.info(
            "team_started",
            team_id=team_id,
            name=team.name,
            template=team.template_name,
            symbols=team.symbols,
        )

        return team

    async def pause_team(self, team_id: int) -> TeamInstance:
        """Pause a running team.

        1. Cancel trading loop task
        2. Keep orchestrator in memory (preserves state)
        3. Update status to PAUSED

        Args:
            team_id: ID of the team to pause.

        Returns:
            Updated TeamInstance.

        Raises:
            TeamNotFoundError: If team doesn't exist.
            ValidationError: If team is not active.
        """
        team = await self.repo.get_by_id(team_id)
        if team is None:
            raise TeamNotFoundError(f"Team with ID {team_id} not found")

        if team.status != TeamInstanceStatus.ACTIVE:
            raise ValidationError(f"Can only pause active teams, current status: {team.status}")

        # Cancel trading loop
        if team_id in self._tasks:
            self._tasks[team_id].cancel()
            try:
                await self._tasks[team_id]
            except asyncio.CancelledError:
                pass
            del self._tasks[team_id]

        # Update status (keep orchestrator for potential resume)
        team = await self.repo.update_status(team_id, TeamInstanceStatus.PAUSED)

        log.info("team_paused", team_id=team_id, name=team.name)

        return team

    async def stop_team(self, team_id: int, close_positions: bool = True) -> TeamInstance:
        """Stop a team completely.

        1. Automatically close all open positions (if close_positions=True)
        2. Cancel trading loop task
        3. Remove orchestrator from memory
        4. Update status to STOPPED

        Args:
            team_id: ID of the team to stop.
            close_positions: Whether to close all open positions (default: True).

        Returns:
            Updated TeamInstance.

        Raises:
            TeamNotFoundError: If team doesn't exist.
        """
        team = await self.repo.get_by_id(team_id)
        if team is None:
            raise TeamNotFoundError(f"Team with ID {team_id} not found")

        if team.status == TeamInstanceStatus.STOPPED:
            log.warning("team_already_stopped", team_id=team_id)
            return team

        # Close all positions before stopping
        if close_positions:
            await self._close_all_positions(team_id)

        # Cancel trading loop
        if team_id in self._tasks:
            self._tasks[team_id].cancel()
            try:
                await self._tasks[team_id]
            except asyncio.CancelledError:
                pass
            del self._tasks[team_id]

        # Remove orchestrator
        if team_id in self._orchestrators:
            del self._orchestrators[team_id]

        # Update status
        team = await self.repo.update_status(team_id, TeamInstanceStatus.STOPPED)

        log.info("team_stopped", team_id=team_id, name=team.name)

        return team

    async def resume_team(self, team_id: int) -> TeamInstance:
        """Resume a paused team.

        Uses existing orchestrator if available, otherwise creates new one.

        Args:
            team_id: ID of the team to resume.

        Returns:
            Updated TeamInstance.

        Raises:
            TeamNotFoundError: If team doesn't exist.
            ValidationError: If team is not paused.
        """
        team = await self.repo.get_by_id(team_id)
        if team is None:
            raise TeamNotFoundError(f"Team with ID {team_id} not found")

        if team.status != TeamInstanceStatus.PAUSED:
            raise ValidationError(
                f"Can only resume paused teams, current status: {team.status}"
            )

        # Use existing orchestrator or create new one
        if team_id not in self._orchestrators:
            return await self.start_team(team_id)

        # Restart trading loop with existing orchestrator
        task = asyncio.create_task(
            self._trading_loop(team_id, team.symbols),
            name=f"team_{team_id}_trading_loop",
        )
        self._tasks[team_id] = task

        # Update status
        team = await self.repo.update_status(team_id, TeamInstanceStatus.ACTIVE)

        log.info("team_resumed", team_id=team_id, name=team.name)

        return team

    def get_running_teams(self) -> list[int]:
        """Get IDs of all running teams.

        Returns:
            List of team IDs with active trading loops.
        """
        return list(self._tasks.keys())

    def get_orchestrator(self, team_id: int) -> TeamOrchestrator | None:
        """Get the orchestrator for a team.

        Args:
            team_id: ID of the team.

        Returns:
            TeamOrchestrator if running, None otherwise.
        """
        return self._orchestrators.get(team_id)

    async def startup(self) -> None:
        """Start all previously active teams on application startup.

        Call this during application lifespan startup.
        """
        active_teams = await self.repo.get_active_teams()

        for team in active_teams:
            try:
                # Reset to STOPPED first to avoid validation error
                await self.repo.update_status(team.id, TeamInstanceStatus.STOPPED)
                await self.start_team(team.id)
                log.info("team_auto_started", team_id=team.id, name=team.name)
            except Exception as e:
                log.error(
                    "team_auto_start_failed",
                    team_id=team.id,
                    name=team.name,
                    error=str(e),
                )

    async def shutdown(self) -> None:
        """Stop all running teams on application shutdown.

        Call this during application lifespan shutdown.
        """
        running_teams = self.get_running_teams()

        for team_id in running_teams:
            try:
                await self.stop_team(team_id)
            except Exception as e:
                log.error(
                    "team_shutdown_failed",
                    team_id=team_id,
                    error=str(e),
                )

        log.info("lifecycle_manager_shutdown", stopped_teams=len(running_teams))

    async def _close_all_positions(self, team_id: int) -> None:
        """Close all open positions for a team.

        This is called automatically when stopping a team to ensure
        clean shutdown with no open positions.

        Args:
            team_id: ID of the team whose positions should be closed.
        """
        try:
            # Get all open trades for the team
            open_trades = await self.trade_repo.get_open_trades(team_id)

            if not open_trades:
                log.info("no_open_positions_to_close", team_id=team_id)
                return

            log.info(
                "closing_all_positions",
                team_id=team_id,
                open_position_count=len(open_trades),
            )

            # Close each position
            # TODO: Replace with actual MT5 position closing when MT5 integration is ready
            # For now, we just mark them as closed in the database
            for trade in open_trades:
                trade.status = "closed"
                trade.closed_at = datetime.now(UTC)
                # Set exit_price to entry_price for now (will be replaced with actual market price)
                if trade.exit_price is None:
                    trade.exit_price = trade.entry_price
                    trade.pnl = 0  # Zero P/L for emergency closes

            await self.session.flush()

            log.info(
                "positions_closed",
                team_id=team_id,
                closed_count=len(open_trades),
            )

        except Exception as e:
            log.error(
                "close_positions_error",
                team_id=team_id,
                error=str(e),
                error_type=type(e).__name__,
            )
            # Don't raise - we want to continue with team shutdown even if closing fails

    async def _trading_loop(
        self,
        team_id: int,
        symbols: list[str],
        interval_seconds: float = 60.0,
    ) -> None:
        """Main trading loop for a team.

        Runs continuously, executing trading cycles at regular intervals.
        Handles exceptions gracefully to prevent loop termination.

        Args:
            team_id: ID of the team.
            symbols: Trading symbols to process.
            interval_seconds: Time between trading cycles.
        """
        orchestrator = self._orchestrators.get(team_id)
        if orchestrator is None:
            log.error("trading_loop_no_orchestrator", team_id=team_id)
            return

        log.info(
            "trading_loop_started",
            team_id=team_id,
            symbols=symbols,
            interval_seconds=interval_seconds,
        )

        while True:
            try:
                # Get market data (placeholder - will be replaced with MT5 data)
                market_data = await self._get_market_data(symbols)

                # Run trading cycle
                decisions = await orchestrator.run_cycle(market_data)

                # Process decisions (logging for now)
                if decisions:
                    log.info(
                        "trading_loop_decisions",
                        team_id=team_id,
                        decision_count=len(decisions),
                    )

                # Wait for next cycle
                await asyncio.sleep(interval_seconds)

            except asyncio.CancelledError:
                log.info("trading_loop_cancelled", team_id=team_id)
                raise
            except Exception as e:
                log.error(
                    "trading_loop_error",
                    team_id=team_id,
                    error=str(e),
                    error_type=type(e).__name__,
                )
                # Continue loop despite errors
                await asyncio.sleep(interval_seconds)

    async def _get_market_data(self, symbols: list[str]) -> dict[str, Any]:
        """Get market data for symbols.

        Placeholder implementation - will be replaced with MT5 integration.

        Args:
            symbols: List of trading symbols.

        Returns:
            Market data keyed by symbol.
        """
        # TODO: Replace with actual MT5 market data
        return {symbol: {"price": 0.0, "timestamp": None} for symbol in symbols}
