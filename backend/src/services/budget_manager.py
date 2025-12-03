"""Budget Manager for Team Instance virtual accounting."""

from datetime import UTC, datetime
from decimal import Decimal

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import TradingError
from src.db.models import TeamInstance, Trade

log = structlog.get_logger()


class BudgetError(TradingError):
    """Budget-related error."""

    code = "BUDGET_ERROR"


class BudgetManager:
    """Manages virtual budget and P/L tracking per team instance.

    Handles:
    - Budget allocation on trade open
    - Budget release on trade close
    - P/L tracking (realized and unrealized)
    - Trade persistence in database
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize Budget Manager.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    async def get_team_instance(self, team_instance_id: int) -> TeamInstance:
        """Get team instance by ID.

        Args:
            team_instance_id: Team instance ID

        Returns:
            TeamInstance object

        Raises:
            BudgetError: If team instance not found
        """
        result = await self.session.execute(
            select(TeamInstance).where(TeamInstance.id == team_instance_id)
        )
        team = result.scalar_one_or_none()

        if team is None:
            raise BudgetError(
                f"Team instance {team_instance_id} not found",
                details={"team_instance_id": team_instance_id},
            )

        return team

    async def allocate_budget(
        self,
        team_instance_id: int,
        position_value: Decimal,
    ) -> Decimal:
        """Allocate budget for a new trade.

        Deducts position value from current budget.

        Args:
            team_instance_id: Team instance ID
            position_value: Value to allocate (position size)

        Returns:
            New current budget after allocation

        Raises:
            BudgetError: If insufficient budget
        """
        team = await self.get_team_instance(team_instance_id)

        if team.current_budget < position_value:
            raise BudgetError(
                f"Insufficient budget: need {position_value}, have {team.current_budget}",
                details={
                    "team_instance_id": team_instance_id,
                    "required": str(position_value),
                    "available": str(team.current_budget),
                },
            )

        team.current_budget -= position_value
        await self.session.flush()

        log.info(
            "budget_allocated",
            team_instance_id=team_instance_id,
            allocated=str(position_value),
            new_budget=str(team.current_budget),
        )

        return team.current_budget

    async def release_budget(
        self,
        team_instance_id: int,
        position_value: Decimal,
        pnl: Decimal,
    ) -> Decimal:
        """Release budget when closing a trade.

        Returns position value plus P/L to current budget.
        Updates realized P/L.

        Args:
            team_instance_id: Team instance ID
            position_value: Original position value
            pnl: Profit/Loss from the trade

        Returns:
            New current budget after release
        """
        team = await self.get_team_instance(team_instance_id)

        team.current_budget += position_value + pnl
        team.realized_pnl += pnl
        await self.session.flush()

        log.info(
            "budget_released",
            team_instance_id=team_instance_id,
            position_value=str(position_value),
            pnl=str(pnl),
            new_budget=str(team.current_budget),
            total_realized_pnl=str(team.realized_pnl),
        )

        return team.current_budget

    async def update_unrealized_pnl(
        self,
        team_instance_id: int,
        unrealized_pnl: Decimal,
    ) -> None:
        """Update unrealized P/L for a team instance.

        Called periodically as position values change.

        Args:
            team_instance_id: Team instance ID
            unrealized_pnl: Total unrealized P/L for all open positions
        """
        team = await self.get_team_instance(team_instance_id)
        team.unrealized_pnl = unrealized_pnl
        await self.session.flush()

        log.debug(
            "unrealized_pnl_updated",
            team_instance_id=team_instance_id,
            unrealized_pnl=str(unrealized_pnl),
        )

    async def record_trade_open(
        self,
        team_instance_id: int,
        ticket: int,
        symbol: str,
        side: str,
        size: Decimal,
        entry_price: Decimal,
        stop_loss: Decimal | None = None,
        take_profit: Decimal | None = None,
        spread_cost: Decimal = Decimal("0"),
        magic_number: int = 0,
        comment: str | None = None,
    ) -> Trade:
        """Record a new trade in the database.

        Args:
            team_instance_id: Team instance ID
            ticket: Trade ticket from execution
            symbol: Symbol (canonical format)
            side: Trade side (BUY/SELL)
            size: Trade size in lots
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            spread_cost: Spread cost at entry
            magic_number: Magic number for identification
            comment: Optional comment

        Returns:
            Created Trade object
        """
        trade = Trade(
            team_instance_id=team_instance_id,
            ticket=ticket,
            symbol=symbol,
            side=side,
            size=size,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            spread_cost=spread_cost,
            status="open",
            magic_number=magic_number,
            comment=comment,
        )

        self.session.add(trade)
        await self.session.flush()

        log.info(
            "trade_recorded",
            trade_id=trade.id,
            ticket=ticket,
            team_instance_id=team_instance_id,
            symbol=symbol,
            side=side,
            size=str(size),
            entry_price=str(entry_price),
        )

        return trade

    async def record_trade_close(
        self,
        trade_id: int,
        exit_price: Decimal,
        pnl: Decimal,
    ) -> Trade:
        """Record trade closure in the database.

        Args:
            trade_id: Trade ID to close
            exit_price: Exit price
            pnl: Realized P/L

        Returns:
            Updated Trade object

        Raises:
            BudgetError: If trade not found or already closed
        """
        result = await self.session.execute(
            select(Trade).where(Trade.id == trade_id)
        )
        trade = result.scalar_one_or_none()

        if trade is None:
            raise BudgetError(
                f"Trade {trade_id} not found",
                details={"trade_id": trade_id},
            )

        if trade.status == "closed":
            raise BudgetError(
                f"Trade {trade_id} is already closed",
                details={"trade_id": trade_id},
            )

        trade.exit_price = exit_price
        trade.pnl = pnl
        trade.status = "closed"
        trade.closed_at = datetime.now(UTC)
        await self.session.flush()

        log.info(
            "trade_closed",
            trade_id=trade.id,
            ticket=trade.ticket,
            exit_price=str(exit_price),
            pnl=str(pnl),
        )

        return trade

    async def get_open_trades(self, team_instance_id: int) -> list[Trade]:
        """Get all open trades for a team instance.

        Args:
            team_instance_id: Team instance ID

        Returns:
            List of open Trade objects
        """
        result = await self.session.execute(
            select(Trade)
            .where(Trade.team_instance_id == team_instance_id)
            .where(Trade.status == "open")
            .order_by(Trade.opened_at.desc())
        )
        return list(result.scalars().all())

    async def get_trade_by_ticket(
        self,
        team_instance_id: int,
        ticket: int,
    ) -> Trade | None:
        """Get a trade by ticket number.

        Args:
            team_instance_id: Team instance ID
            ticket: Trade ticket

        Returns:
            Trade object or None
        """
        result = await self.session.execute(
            select(Trade)
            .where(Trade.team_instance_id == team_instance_id)
            .where(Trade.ticket == ticket)
        )
        return result.scalar_one_or_none()

    async def get_budget_summary(self, team_instance_id: int) -> dict:
        """Get budget summary for a team instance.

        Args:
            team_instance_id: Team instance ID

        Returns:
            Dict with budget details
        """
        team = await self.get_team_instance(team_instance_id)

        return {
            "team_instance_id": team_instance_id,
            "initial_budget": team.initial_budget,
            "current_budget": team.current_budget,
            "realized_pnl": team.realized_pnl,
            "unrealized_pnl": team.unrealized_pnl,
            "total_equity": team.current_budget + team.unrealized_pnl,
            "total_return_pct": (
                (team.current_budget + team.unrealized_pnl - team.initial_budget)
                / team.initial_budget
                * 100
            ).quantize(Decimal("0.01")),
        }
