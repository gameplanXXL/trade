"""User repository for CRUD operations - Story 009-02."""

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User

log = structlog.get_logger()


class UserRepository:
    """Repository for user database operations.

    Encapsulates all CRUD operations for User model.
    No business logic - pure data access layer.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with a database session.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session

    async def create(self, username: str, password_hash: str) -> User:
        """Create a new user.

        Args:
            username: Unique username for the user.
            password_hash: Bcrypt hashed password.

        Returns:
            The newly created User.
        """
        user = User(username=username, password_hash=password_hash)
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)

        log.info("user_created", user_id=user.id, username=username)
        return user

    async def get_by_id(self, user_id: int) -> User | None:
        """Get a user by ID.

        Args:
            user_id: The ID of the user to retrieve.

        Returns:
            The User if found, None otherwise.
        """
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """Get a user by username.

        Args:
            username: The username to search for.

        Returns:
            The User if found, None otherwise.
        """
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def delete(self, user_id: int) -> bool:
        """Delete a user permanently.

        Args:
            user_id: The ID of the user to delete.

        Returns:
            True if deleted, False if not found.
        """
        user = await self.get_by_id(user_id)
        if user is None:
            return False

        await self.session.delete(user)
        await self.session.flush()

        log.info("user_deleted", user_id=user_id, username=user.username)
        return True
