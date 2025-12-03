"""API dependencies for dependency injection."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import Settings, get_settings
from src.core.redis import SessionManager, get_redis_client
from src.db.session import get_db

# Settings dependency
SettingsDep = Annotated[Settings, Depends(get_settings)]

# Database dependency
DbDep = Annotated[AsyncSession, Depends(get_db)]


async def get_redis() -> AsyncGenerator[Redis]:
    """Get Redis client as dependency."""
    client = get_redis_client()
    try:
        yield client
    finally:
        await client.aclose()


# Redis dependency
RedisDep = Annotated[Redis, Depends(get_redis)]


async def get_session_manager(redis: RedisDep) -> SessionManager:
    """Get session manager as dependency."""
    return SessionManager(redis)


# Session manager dependency
SessionManagerDep = Annotated[SessionManager, Depends(get_session_manager)]
