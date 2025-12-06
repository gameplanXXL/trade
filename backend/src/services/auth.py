"""Authentication service for user validation and password management - Story 009-02."""

import bcrypt
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User
from src.db.repositories.user_repo import UserRepository

log = structlog.get_logger()


class AuthService:
    """Service for authentication operations.

    Handles password hashing, validation, and user authentication.
    Business logic layer for auth-related operations.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the service with a database session.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session
        self.user_repo = UserRepository(session)

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt.

        Args:
            password: Plain text password to hash.

        Returns:
            Bcrypt hashed password as a string.
        """
        salt = bcrypt.gensalt()
        password_bytes = password.encode("utf-8")
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify a password against a hash.

        Args:
            password: Plain text password to verify.
            password_hash: Bcrypt hash to compare against.

        Returns:
            True if password matches hash, False otherwise.
        """
        password_bytes = password.encode("utf-8")
        hash_bytes = password_hash.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hash_bytes)

    async def validate_credentials(self, username: str, password: str) -> User | None:
        """Validate user credentials.

        Args:
            username: Username to authenticate.
            password: Plain text password to verify.

        Returns:
            User instance if credentials are valid, None otherwise.
        """
        user = await self.user_repo.get_by_username(username)
        if user is None:
            log.warning("login_failed_user_not_found", username=username)
            return None

        if not self.verify_password(password, user.password_hash):
            log.warning("login_failed_invalid_password", username=username, user_id=user.id)
            return None

        log.info("login_successful", username=username, user_id=user.id)
        return user

    async def create_user(self, username: str, password: str) -> User:
        """Create a new user with hashed password.

        Args:
            username: Unique username for the new user.
            password: Plain text password (will be hashed).

        Returns:
            The newly created User instance.
        """
        password_hash = self.hash_password(password)
        return await self.user_repo.create(username=username, password_hash=password_hash)
