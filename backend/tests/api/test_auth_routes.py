"""Tests for Auth REST API endpoints - Story 009-02."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from src.db.models import User
from src.main import app
from src.services.auth import AuthService


@pytest.fixture
def mock_user() -> User:
    """Create mock user."""
    user = MagicMock(spec=User)
    user.id = 1
    user.username = "testuser"
    user.password_hash = AuthService.hash_password("testpassword")
    user.created_at = datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)
    return user


@pytest.fixture
def mock_session_manager() -> AsyncMock:
    """Create mock session manager."""
    manager = AsyncMock()
    manager.create_session = AsyncMock()
    manager.get_session = AsyncMock()
    manager.delete_session = AsyncMock()
    return manager


class TestLogin:
    """Tests for POST /api/auth/login endpoint."""

    @pytest.mark.asyncio
    async def test_login_success(self, mock_user: User, mock_session_manager: AsyncMock) -> None:
        """Test successful login creates session and sets cookie."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with patch("src.api.routes.auth.AuthService") as mock_auth_service_class:
                # Mock AuthService.validate_credentials
                mock_auth_service = AsyncMock()
                mock_auth_service.validate_credentials.return_value = mock_user
                mock_auth_service_class.return_value = mock_auth_service

                with patch("src.api.deps.SessionManager", return_value=mock_session_manager):
                    response = await client.post(
                        "/api/auth/login",
                        json={"username": "testuser", "password": "testpassword"},
                    )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Login successful"
        assert "session" in response.cookies

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self) -> None:
        """Test login with invalid credentials returns 401."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with patch("src.api.routes.auth.AuthService") as mock_auth_service_class:
                # Mock AuthService.validate_credentials to return None (invalid)
                mock_auth_service = AsyncMock()
                mock_auth_service.validate_credentials.return_value = None
                mock_auth_service_class.return_value = mock_auth_service

                response = await client.post(
                    "/api/auth/login",
                    json={"username": "wronguser", "password": "wrongpassword"},
                )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"]["code"] == "INVALID_CREDENTIALS"
        assert "session" not in response.cookies

    @pytest.mark.asyncio
    async def test_login_missing_fields(self) -> None:
        """Test login with missing fields returns 422."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/auth/login", json={"username": "testuser"})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLogout:
    """Tests for POST /api/auth/logout endpoint."""

    @pytest.mark.asyncio
    async def test_logout_success(self, mock_user: User, mock_session_manager: AsyncMock) -> None:
        """Test successful logout deletes session and cookie."""
        from src.api.deps import get_current_user, get_session_manager

        async def mock_get_current_user():
            return mock_user

        async def mock_get_session_manager():
            return mock_session_manager

        app.dependency_overrides[get_current_user] = mock_get_current_user
        app.dependency_overrides[get_session_manager] = mock_get_session_manager

        try:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                # Set a session cookie
                client.cookies.set("session", "test_session_token")

                response = await client.post("/api/auth/logout")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["message"] == "Logout successful"
            # Verify session was deleted from Redis
            mock_session_manager.delete_session.assert_called_once()
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_logout_not_authenticated(self) -> None:
        """Test logout without authentication returns 401."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/auth/logout")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetMe:
    """Tests for GET /api/auth/me endpoint."""

    @pytest.mark.asyncio
    async def test_get_me_success(self, mock_user: User) -> None:
        """Test getting current user info returns user data."""
        from src.api.deps import get_current_user

        async def mock_get_current_user():
            return mock_user

        app.dependency_overrides[get_current_user] = mock_get_current_user

        try:
            async with AsyncClient(
                transport=ASGITransport(app=app), base_url="http://test"
            ) as client:
                response = await client.get("/api/auth/me")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "data" in data
            assert data["data"]["id"] == 1
            assert data["data"]["username"] == "testuser"
            assert "created_at" in data["data"]
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_me_not_authenticated(self) -> None:
        """Test /me endpoint without authentication returns 401."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert data["detail"]["code"] == "NOT_AUTHENTICATED"


class TestSessionCookieConfiguration:
    """Tests for session cookie security configuration."""

    @pytest.mark.asyncio
    async def test_session_cookie_security_attributes(
        self, mock_user: User, mock_session_manager: AsyncMock
    ) -> None:
        """Test that session cookie has correct security attributes."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            with patch("src.api.routes.auth.AuthService") as mock_auth_service_class:
                mock_auth_service = AsyncMock()
                mock_auth_service.validate_credentials.return_value = mock_user
                mock_auth_service_class.return_value = mock_auth_service

                with patch("src.api.deps.SessionManager", return_value=mock_session_manager):
                    response = await client.post(
                        "/api/auth/login",
                        json={"username": "testuser", "password": "testpassword"},
                    )

        # Get the Set-Cookie header
        set_cookie_header = response.headers.get("set-cookie", "")

        # Verify httponly flag is set
        assert "httponly" in set_cookie_header.lower()

        # Verify samesite is set to lax
        assert "samesite=lax" in set_cookie_header.lower()

        # Verify max-age is set (24 hours = 86400 seconds)
        assert "max-age=86400" in set_cookie_header.lower()
