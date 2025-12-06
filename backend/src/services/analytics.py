"""Analytics service for calculating trading metrics."""

import statistics
from datetime import datetime
from decimal import Decimal

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.analytics import PerformanceSummary
from src.core.exceptions import TeamNotFoundError
from src.db.models import PerformanceMetric, TeamInstance, Trade

log = structlog.get_logger()


class AnalyticsService:
    """Service for calculating trading performance metrics.

    Provides methods to calculate various trading metrics such as P/L,
    win rate, Sharpe ratio, and max drawdown for team instances.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize analytics service.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def _get_team_instance(self, team_id: int) -> TeamInstance:
        """Get team instance by ID.

        Args:
            team_id: Team instance ID

        Returns:
            TeamInstance model

        Raises:
            TeamNotFoundError: If team instance not found
        """
        stmt = select(TeamInstance).where(TeamInstance.id == team_id)
        result = await self.session.execute(stmt)
        team = result.scalar_one_or_none()

        if not team:
            raise TeamNotFoundError(f"Team instance with ID {team_id} not found")

        return team

    async def calculate_total_pnl(self, team_id: int) -> Decimal:
        """Calculate total P/L (realized + unrealized).

        Args:
            team_id: Team instance ID

        Returns:
            Total P/L as Decimal

        Raises:
            TeamNotFoundError: If team instance not found
        """
        team = await self._get_team_instance(team_id)
        total_pnl = team.realized_pnl + team.unrealized_pnl

        log.info(
            "calculated_total_pnl",
            team_id=team_id,
            realized_pnl=str(team.realized_pnl),
            unrealized_pnl=str(team.unrealized_pnl),
            total_pnl=str(total_pnl),
        )

        return total_pnl

    async def calculate_pnl_by_symbol(self, team_id: int) -> dict[str, Decimal]:
        """Calculate P/L by symbol.

        Groups all closed trades by symbol and sums their P/L.

        Args:
            team_id: Team instance ID

        Returns:
            Dictionary mapping symbol to total P/L
        """
        stmt = (
            select(Trade.symbol, func.sum(Trade.pnl).label("total_pnl"))
            .where(Trade.team_instance_id == team_id)
            .where(Trade.status == "closed")
            .where(Trade.pnl.is_not(None))
            .group_by(Trade.symbol)
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        pnl_by_symbol = {symbol: Decimal(str(pnl)) for symbol, pnl in rows}

        log.info(
            "calculated_pnl_by_symbol",
            team_id=team_id,
            symbols=list(pnl_by_symbol.keys()),
            total_symbols=len(pnl_by_symbol),
        )

        return pnl_by_symbol

    async def calculate_win_rate(self, team_id: int) -> float:
        """Calculate win rate.

        Win rate = Count(pnl > 0) / Count(all closed trades)

        Args:
            team_id: Team instance ID

        Returns:
            Win rate as float between 0 and 1
        """
        stmt = (
            select(
                func.count(Trade.id).label("total_trades"),
                func.count(Trade.id).filter(Trade.pnl > 0).label("winning_trades"),
            )
            .where(Trade.team_instance_id == team_id)
            .where(Trade.status == "closed")
            .where(Trade.pnl.is_not(None))
        )

        result = await self.session.execute(stmt)
        row = result.one_or_none()

        if not row or row[0] == 0:
            return 0.0

        total_trades, winning_trades = row
        win_rate = float(winning_trades) / float(total_trades)

        log.info(
            "calculated_win_rate",
            team_id=team_id,
            total_trades=total_trades,
            winning_trades=winning_trades,
            win_rate=win_rate,
        )

        return win_rate

    async def calculate_sharpe_ratio(
        self, team_id: int, risk_free_rate: float = 0.02
    ) -> float:
        """Calculate Sharpe ratio.

        Sharpe Ratio = (Mean Return - Risk Free Rate) / Std Dev of Returns

        Args:
            team_id: Team instance ID
            risk_free_rate: Annual risk-free rate (default: 2%)

        Returns:
            Sharpe ratio as float
        """
        # Get all closed trades P/L ordered by time
        stmt = (
            select(Trade.pnl)
            .where(Trade.team_instance_id == team_id)
            .where(Trade.status == "closed")
            .where(Trade.pnl.is_not(None))
            .order_by(Trade.closed_at)
        )

        result = await self.session.execute(stmt)
        pnl_values = result.scalars().all()

        if not pnl_values or len(pnl_values) < 2:
            return 0.0

        # Convert to float for statistics calculations
        returns = [float(pnl) for pnl in pnl_values]

        try:
            mean_return = statistics.mean(returns)
            std_return = statistics.stdev(returns)

            if std_return == 0:
                return 0.0

            # Adjust risk-free rate to per-trade basis (assuming daily trading)
            daily_risk_free = risk_free_rate / 252  # 252 trading days per year
            sharpe = (mean_return - daily_risk_free) / std_return

            log.info(
                "calculated_sharpe_ratio",
                team_id=team_id,
                mean_return=mean_return,
                std_return=std_return,
                sharpe_ratio=sharpe,
                num_trades=len(returns),
            )

            return sharpe

        except statistics.StatisticsError:
            log.warning("sharpe_calculation_failed", team_id=team_id, reason="statistics_error")
            return 0.0

    async def calculate_max_drawdown(self, team_id: int) -> float:
        """Calculate maximum drawdown from peak equity.

        Max Drawdown = (Peak - Trough) / Peak

        Args:
            team_id: Team instance ID

        Returns:
            Max drawdown as float between 0 and 1
        """
        # Get all closed trades P/L ordered by time
        stmt = (
            select(Trade.pnl)
            .where(Trade.team_instance_id == team_id)
            .where(Trade.status == "closed")
            .where(Trade.pnl.is_not(None))
            .order_by(Trade.closed_at)
        )

        result = await self.session.execute(stmt)
        pnl_values = result.scalars().all()

        if not pnl_values:
            return 0.0

        # Calculate cumulative P/L (equity curve)
        cumulative_pnl = []
        running_total = Decimal("0")
        for pnl in pnl_values:
            running_total += pnl
            cumulative_pnl.append(running_total)

        # Calculate max drawdown
        max_drawdown = Decimal("0")
        peak = cumulative_pnl[0]

        for value in cumulative_pnl:
            if value > peak:
                peak = value

            if peak > 0:
                drawdown = (peak - value) / peak
                if drawdown > max_drawdown:
                    max_drawdown = drawdown

        max_drawdown_float = float(max_drawdown)

        log.info(
            "calculated_max_drawdown",
            team_id=team_id,
            max_drawdown=max_drawdown_float,
            peak_equity=str(peak),
            num_trades=len(pnl_values),
        )

        return max_drawdown_float

    async def get_performance_summary(self, team_id: int) -> PerformanceSummary:
        """Get complete performance summary.

        Calculates all metrics in a single call and returns a comprehensive
        performance summary.

        Args:
            team_id: Team instance ID

        Returns:
            PerformanceSummary with all metrics

        Raises:
            TeamNotFoundError: If team instance not found
        """
        log.info("calculating_performance_summary", team_id=team_id)

        # Get team instance for budget info
        team = await self._get_team_instance(team_id)

        # Calculate all metrics
        total_pnl = team.realized_pnl + team.unrealized_pnl

        # Calculate total_pnl_percent
        if team.initial_budget > 0:
            total_pnl_percent = float(total_pnl / team.initial_budget * 100)
        else:
            total_pnl_percent = 0.0

        # Get trade counts
        stmt = (
            select(
                func.count(Trade.id).label("total_trades"),
                func.count(Trade.id).filter(Trade.pnl > 0).label("winning_trades"),
            )
            .where(Trade.team_instance_id == team_id)
            .where(Trade.status == "closed")
            .where(Trade.pnl.is_not(None))
        )
        result = await self.session.execute(stmt)
        row = result.one_or_none()

        if row and row[0] > 0:
            total_trades, winning_trades = row
            losing_trades = total_trades - winning_trades
            win_rate = float(winning_trades) / float(total_trades)
        else:
            total_trades = 0
            winning_trades = 0
            losing_trades = 0
            win_rate = 0.0

        # Calculate Sharpe ratio and max drawdown
        sharpe_ratio = await self.calculate_sharpe_ratio(team_id)
        max_drawdown = await self.calculate_max_drawdown(team_id)

        summary = PerformanceSummary(
            total_pnl=total_pnl,
            total_pnl_percent=total_pnl_percent,
            win_rate=win_rate,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
        )

        log.info(
            "performance_summary_calculated",
            team_id=team_id,
            total_pnl=str(total_pnl),
            win_rate=win_rate,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
        )

        return summary

    async def aggregate_performance(
        self, team_id: int, period: str = "hourly"
    ) -> PerformanceMetric:
        """Aggregate and store performance metrics for a team instance.

        Calculates current performance metrics and stores them in the
        performance_metrics table for historical tracking.

        Args:
            team_id: Team instance ID
            period: Time period ('hourly', 'daily', 'weekly')

        Returns:
            Created PerformanceMetric instance

        Raises:
            TeamNotFoundError: If team instance not found
            ValueError: If period is invalid
        """
        if period not in ("hourly", "daily", "weekly"):
            raise ValueError(f"Invalid period: {period}. Must be 'hourly', 'daily', or 'weekly'")

        log.info("aggregating_performance", team_id=team_id, period=period)

        # Get team instance to verify it exists
        await self._get_team_instance(team_id)

        # Calculate current metrics
        summary = await self.get_performance_summary(team_id)

        # Create performance metric record
        metric = PerformanceMetric(
            team_instance_id=team_id,
            timestamp=datetime.now(),
            period=period,
            pnl=summary.total_pnl,
            pnl_percent=summary.total_pnl_percent,
            win_rate=summary.win_rate,
            sharpe_ratio=summary.sharpe_ratio,
            max_drawdown=summary.max_drawdown,
            trade_count=summary.total_trades,
        )

        self.session.add(metric)
        await self.session.commit()
        await self.session.refresh(metric)

        log.info(
            "performance_aggregated",
            team_id=team_id,
            period=period,
            metric_id=metric.id,
            pnl=str(metric.pnl),
            trade_count=metric.trade_count,
        )

        return metric

    async def get_performance_history(
        self,
        team_id: int,
        period: str = "hourly",
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 100,
    ) -> list[PerformanceMetric]:
        """Get historical performance metrics for a team instance.

        Retrieves stored performance metrics for trend analysis.

        Args:
            team_id: Team instance ID
            period: Time period filter ('hourly', 'daily', 'weekly')
            start_time: Optional start time filter
            end_time: Optional end time filter
            limit: Maximum number of records to return

        Returns:
            List of PerformanceMetric instances ordered by timestamp (newest first)

        Raises:
            TeamNotFoundError: If team instance not found
        """
        # Verify team exists
        await self._get_team_instance(team_id)

        log.info(
            "fetching_performance_history",
            team_id=team_id,
            period=period,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
        )

        # Build query
        stmt = (
            select(PerformanceMetric)
            .where(PerformanceMetric.team_instance_id == team_id)
            .where(PerformanceMetric.period == period)
            .order_by(PerformanceMetric.timestamp.desc())
            .limit(limit)
        )

        if start_time:
            stmt = stmt.where(PerformanceMetric.timestamp >= start_time)

        if end_time:
            stmt = stmt.where(PerformanceMetric.timestamp <= end_time)

        result = await self.session.execute(stmt)
        metrics = list(result.scalars().all())

        log.info(
            "performance_history_fetched",
            team_id=team_id,
            period=period,
            count=len(metrics),
        )

        return metrics

    async def get_latest_metric(
        self, team_id: int, period: str = "hourly"
    ) -> PerformanceMetric | None:
        """Get the most recent performance metric for a team instance.

        Args:
            team_id: Team instance ID
            period: Time period filter ('hourly', 'daily', 'weekly')

        Returns:
            Latest PerformanceMetric or None if no metrics exist

        Raises:
            TeamNotFoundError: If team instance not found
        """
        # Verify team exists
        await self._get_team_instance(team_id)

        stmt = (
            select(PerformanceMetric)
            .where(PerformanceMetric.team_instance_id == team_id)
            .where(PerformanceMetric.period == period)
            .order_by(PerformanceMetric.timestamp.desc())
            .limit(1)
        )

        result = await self.session.execute(stmt)
        metric = result.scalar_one_or_none()

        log.info(
            "latest_metric_fetched",
            team_id=team_id,
            period=period,
            found=metric is not None,
        )

        return metric
