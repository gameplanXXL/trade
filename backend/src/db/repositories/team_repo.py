"""Team instance repository for CRUD operations - Story 005-02."""

from decimal import Decimal

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import TeamInstance, TeamInstanceMode, TeamInstanceStatus

log = structlog.get_logger()


class TeamRepository:
    """Repository for team instance database operations.

    Encapsulates all CRUD operations for TeamInstance model.
    No business logic - pure data access layer.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with a database session.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def create(
        self,
        name: str,
        template_name: str,
        symbols: list[str],
        initial_budget: Decimal,
        mode: TeamInstanceMode = TeamInstanceMode.PAPER,
    ) -> TeamInstance:
        """Create a new team instance.

        Args:
            name: Display name for the team instance.
            template_name: Name of the YAML team template to use.
            symbols: List of trading symbols (canonical format: EUR/USD).
            initial_budget: Starting budget for the team.
            mode: Trading mode (paper or live).

        Returns:
            The newly created TeamInstance.
        """
        team = TeamInstance(
            name=name,
            template_name=template_name,
            symbols=symbols,
            initial_budget=initial_budget,
            current_budget=initial_budget,
            mode=mode,
            status=TeamInstanceStatus.STOPPED,
        )
        self.session.add(team)
        await self.session.flush()
        await self.session.refresh(team)

        log.info(
            "team_created",
            team_id=team.id,
            name=name,
            template=template_name,
            mode=mode.value,
        )
        return team

    async def get_by_id(self, team_id: int) -> TeamInstance | None:
        """Get a team instance by ID.

        Args:
            team_id: The ID of the team to retrieve.

        Returns:
            The TeamInstance if found, None otherwise.
        """
        result = await self.session.execute(
            select(TeamInstance).where(TeamInstance.id == team_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self, status: TeamInstanceStatus | None = None
    ) -> list[TeamInstance]:
        """Get all team instances, optionally filtered by status.

        Args:
            status: Optional status filter.

        Returns:
            List of matching TeamInstances.
        """
        query = select(TeamInstance).order_by(TeamInstance.created_at.desc())
        if status is not None:
            query = query.where(TeamInstance.status == status)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_active_teams(self) -> list[TeamInstance]:
        """Get all active team instances.

        Returns:
            List of teams with ACTIVE status.
        """
        return await self.get_all(status=TeamInstanceStatus.ACTIVE)

    async def update_status(
        self, team_id: int, status: TeamInstanceStatus
    ) -> TeamInstance | None:
        """Update the status of a team instance.

        Args:
            team_id: The ID of the team to update.
            status: The new status.

        Returns:
            The updated TeamInstance if found, None otherwise.
        """
        team = await self.get_by_id(team_id)
        if team is None:
            return None

        old_status = team.status
        team.status = status
        await self.session.flush()
        await self.session.refresh(team)

        log.info(
            "team_status_changed",
            team_id=team_id,
            old_status=old_status.value,
            new_status=status.value,
        )
        return team

    async def update_budget(
        self, team_id: int, new_budget: Decimal
    ) -> TeamInstance | None:
        """Update the current budget of a team instance.

        Args:
            team_id: The ID of the team to update.
            new_budget: The new budget value.

        Returns:
            The updated TeamInstance if found, None otherwise.
        """
        team = await self.get_by_id(team_id)
        if team is None:
            return None

        old_budget = team.current_budget
        team.current_budget = new_budget
        await self.session.flush()
        await self.session.refresh(team)

        log.info(
            "team_budget_updated",
            team_id=team_id,
            old_budget=float(old_budget),
            new_budget=float(new_budget),
        )
        return team

    async def update_pnl(
        self,
        team_id: int,
        realized_pnl: Decimal | None = None,
        unrealized_pnl: Decimal | None = None,
    ) -> TeamInstance | None:
        """Update P/L values for a team instance.

        Args:
            team_id: The ID of the team to update.
            realized_pnl: New realized P/L value (if provided).
            unrealized_pnl: New unrealized P/L value (if provided).

        Returns:
            The updated TeamInstance if found, None otherwise.
        """
        team = await self.get_by_id(team_id)
        if team is None:
            return None

        if realized_pnl is not None:
            team.realized_pnl = realized_pnl
        if unrealized_pnl is not None:
            team.unrealized_pnl = unrealized_pnl

        await self.session.flush()
        await self.session.refresh(team)
        return team

    async def delete(self, team_id: int) -> bool:
        """Delete a team instance permanently.

        Note: Only stopped teams should be deleted.
        Use update_status to stop a team first.

        Args:
            team_id: The ID of the team to delete.

        Returns:
            True if deleted, False if not found.
        """
        team = await self.get_by_id(team_id)
        if team is None:
            return False

        await self.session.delete(team)
        await self.session.flush()

        log.info("team_deleted", team_id=team_id, name=team.name)
        return True
