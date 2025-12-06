"""Authentication REST API endpoints - Story 009-02."""

import secrets

import structlog
from fastapi import APIRouter, HTTPException, Request, Response, status

from src.api.deps import CurrentUserDep, DbDep, SessionManagerDep
from src.api.schemas.auth import LoginRequest, LoginResponse, LogoutResponse, MeResponse, UserResponse
from src.config.settings import get_settings
from src.services.auth import AuthService

settings = get_settings()

log = structlog.get_logger()

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Session cookie configuration
SESSION_COOKIE_NAME = "session"
SESSION_TTL = 86400  # 24 hours in seconds


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    data: LoginRequest,
    response: Response,
    session_manager: SessionManagerDep,
    db: DbDep,
) -> LoginResponse:
    """Authenticate user and create session.

    Validates credentials, creates session in Redis, and sets httponly cookie.

    Args:
        data: Login credentials (username and password).
        response: FastAPI response object for setting cookies.
        session_manager: Redis session manager dependency.
        db: Database session dependency.

    Returns:
        LoginResponse with success message.

    Raises:
        HTTPException: 401 if credentials are invalid.
    """
    auth_service = AuthService(db)
    user = await auth_service.validate_credentials(data.username, data.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_CREDENTIALS", "message": "Invalid username or password"},
        )

    # Generate secure session token
    session_token = secrets.token_urlsafe(32)

    # Store session in Redis
    await session_manager.create_session(session_token, user.id, ttl=SESSION_TTL)

    # Set httponly cookie
    # secure=True only in production (HTTPS), false in development (HTTP)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_token,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        max_age=SESSION_TTL,
    )

    log.info("user_logged_in", user_id=user.id, username=user.username)
    return LoginResponse(user=UserResponse.model_validate(user))


@router.post("/logout", response_model=LogoutResponse, status_code=status.HTTP_200_OK)
async def logout(
    request: Request,
    response: Response,
    session_manager: SessionManagerDep,
    user: CurrentUserDep,
) -> LogoutResponse:
    """Logout current user and destroy session.

    Removes session from Redis and deletes cookie.
    Requires authentication (CurrentUserDep validates session).

    Args:
        request: FastAPI request object for getting session token.
        response: FastAPI response object for deleting cookies.
        session_manager: Redis session manager dependency.
        user: Current authenticated user (from session).

    Returns:
        LogoutResponse with success message.
    """
    # Delete session from Redis
    session_token = request.cookies.get(SESSION_COOKIE_NAME)
    if session_token:
        await session_manager.delete_session(session_token)

    # Delete cookie
    response.delete_cookie(key=SESSION_COOKIE_NAME)

    log.info("user_logged_out", user_id=user.id, username=user.username)
    return LogoutResponse()


@router.get("/me", response_model=MeResponse, status_code=status.HTTP_200_OK)
async def get_current_user_info(user: CurrentUserDep) -> MeResponse:
    """Get current authenticated user information.

    Requires authentication (CurrentUserDep validates session).

    Args:
        user: Current authenticated user (from session).

    Returns:
        MeResponse with user data.
    """
    return MeResponse(data=user)
