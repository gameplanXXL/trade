"""API dependencies for dependency injection."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import Settings, get_settings
from src.core.redis import SessionManager, get_redis_client
from src.db.models import User
from src.db.repositories.user_repo import UserRepository
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


async def get_current_user(
    request: Request,
    session_manager: SessionManagerDep,
    db: DbDep,
) -> User:
    """Get current authenticated user from session cookie.

    Args:
        request: FastAPI request object containing cookies.
        session_manager: Redis session manager dependency.
        db: Database session dependency.

    Returns:
        Authenticated User instance.

    Raises:
        HTTPException: 401 if not authenticated or session expired.
    """
    session_token = request.cookies.get("session")
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "NOT_AUTHENTICATED", "message": "Not authenticated"},
        )

    user_id = await session_manager.get_session(session_token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "SESSION_EXPIRED", "message": "Session expired"},
        )

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "USER_NOT_FOUND", "message": "User not found"},
        )

    return user


# Current user dependency
CurrentUserDep = Annotated[User, Depends(get_current_user)]
