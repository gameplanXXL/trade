"""Redis client configuration and session management."""

from redis.asyncio import ConnectionPool, Redis

from src.config.settings import get_settings

settings = get_settings()

# Connection pool for async Redis operations
_pool: ConnectionPool | None = None


def get_redis_pool() -> ConnectionPool:
    """Get or create Redis connection pool."""
    global _pool
    if _pool is None:
        _pool = ConnectionPool.from_url(
            settings.redis_url,
            max_connections=20,
            decode_responses=True,
        )
    return _pool


def get_redis_client() -> Redis:
    """Get Redis client instance.

    Returns:
        Redis: Async Redis client
    """
    return Redis(connection_pool=get_redis_pool())


async def close_redis_pool() -> None:
    """Close Redis connection pool."""
    global _pool
    if _pool is not None:
        await _pool.disconnect()
        _pool = None


# Session management constants
SESSION_PREFIX = "session:"
SESSION_TTL = 86400  # 24 hours in seconds


class SessionManager:
    """Redis-based session management."""

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def create_session(self, token: str, user_id: int, ttl: int = SESSION_TTL) -> None:
        """Create a new session.

        Args:
            token: Session token
            user_id: User ID to associate with session
            ttl: Time to live in seconds (default: 24 hours)
        """
        await self.redis.set(f"{SESSION_PREFIX}{token}", str(user_id), ex=ttl)

    async def get_session(self, token: str) -> int | None:
        """Get user ID from session token.

        Args:
            token: Session token

        Returns:
            User ID if session exists, None otherwise
        """
        user_id = await self.redis.get(f"{SESSION_PREFIX}{token}")
        return int(user_id) if user_id else None

    async def delete_session(self, token: str) -> bool:
        """Delete a session.

        Args:
            token: Session token

        Returns:
            True if session was deleted, False if it didn't exist
        """
        result = await self.redis.delete(f"{SESSION_PREFIX}{token}")
        return result > 0

    async def refresh_session(self, token: str, ttl: int = SESSION_TTL) -> bool:
        """Refresh session TTL.

        Args:
            token: Session token
            ttl: New TTL in seconds

        Returns:
            True if session was refreshed, False if it didn't exist
        """
        return await self.redis.expire(f"{SESSION_PREFIX}{token}", ttl)
