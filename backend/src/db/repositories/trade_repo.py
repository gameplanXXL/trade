"""Trade repository for CRUD operations - Story 008-02."""

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Trade

log = structlog.get_logger()


class TradeRepository:
    """Repository for trade database operations.

    Encapsulates all CRUD operations for Trade model.
    No business logic - pure data access layer.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with a database session.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def get_by_team_id(
        self,
        team_id: int,
        limit: int = 20,
        offset: int = 0,
        status: str | None = None,
        symbol: str | None = None,
    ) -> tuple[list[Trade], int]:
        """Get trades for a specific team with pagination and filtering.

        Args:
            team_id: The ID of the team instance.
            limit: Maximum number of trades to return.
            offset: Number of trades to skip.
            status: Optional status filter (open, closed).
            symbol: Optional symbol filter (e.g., EUR/USD).

        Returns:
            Tuple of (trades list, total count).
        """
        # Base query
        query = select(Trade).where(Trade.team_instance_id == team_id)

        # Apply filters
        if status is not None:
            query = query.where(Trade.status == status)
        if symbol is not None:
            query = query.where(Trade.symbol == symbol)

        # Count query
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        # Data query with pagination and ordering
        query = query.order_by(Trade.opened_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        trades = list(result.scalars().all())

        log.debug(
            "trades_fetched",
            team_id=team_id,
            count=len(trades),
            total=total,
            limit=limit,
            offset=offset,
        )
        return trades, total

    async def get_by_id(self, trade_id: int) -> Trade | None:
        """Get a trade by ID.

        Args:
            trade_id: The ID of the trade to retrieve.

        Returns:
            The Trade if found, None otherwise.
        """
        result = await self.session.execute(select(Trade).where(Trade.id == trade_id))
        return result.scalar_one_or_none()

    async def get_open_trades(self, team_id: int) -> list[Trade]:
        """Get all open trades for a team.

        Args:
            team_id: The ID of the team instance.

        Returns:
            List of open trades.
        """
        result = await self.session.execute(
            select(Trade)
            .where(Trade.team_instance_id == team_id, Trade.status == "open")
            .order_by(Trade.opened_at.desc())
        )
        return list(result.scalars().all())
