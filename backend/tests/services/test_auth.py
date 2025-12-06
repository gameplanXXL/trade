"""Tests for Authentication Service - Story 009-02."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.db.models import User
from src.services.auth import AuthService


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create mock async session."""
    return AsyncMock()


@pytest.fixture
def auth_service(mock_session: AsyncMock) -> AuthService:
    """Create auth service with mock session."""
    service = AuthService(session=mock_session)
    # Mock the repository
    service.user_repo = AsyncMock()
    return service


@pytest.fixture
def mock_user() -> User:
    """Create mock user."""
    user = MagicMock(spec=User)
    user.id = 1
    user.username = "testuser"
    user.password_hash = AuthService.hash_password("testpassword")
    return user


class TestHashPassword:
    """Tests for hash_password static method."""

    def test_hash_password_returns_string(self) -> None:
        """Test that password hashing returns a string."""
        result = AuthService.hash_password("mypassword")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_hash_password_different_for_same_input(self) -> None:
        """Test that same password produces different hashes (salt)."""
        hash1 = AuthService.hash_password("password123")
        hash2 = AuthService.hash_password("password123")
        assert hash1 != hash2  # Due to different salts


class TestVerifyPassword:
    """Tests for verify_password static method."""

    def test_verify_password_correct(self) -> None:
        """Test that correct password is verified successfully."""
        password = "mypassword123"
        password_hash = AuthService.hash_password(password)
        assert AuthService.verify_password(password, password_hash) is True

    def test_verify_password_incorrect(self) -> None:
        """Test that incorrect password fails verification."""
        password_hash = AuthService.hash_password("correctpassword")
        assert AuthService.verify_password("wrongpassword", password_hash) is False

    def test_verify_password_empty(self) -> None:
        """Test that empty password fails verification."""
        password_hash = AuthService.hash_password("somepassword")
        assert AuthService.verify_password("", password_hash) is False


class TestValidateCredentials:
    """Tests for validate_credentials method."""

    async def test_validate_credentials_success(
        self,
        auth_service: AuthService,
        mock_user: User,
    ) -> None:
        """Test successful credential validation."""
        auth_service.user_repo.get_by_username.return_value = mock_user

        user = await auth_service.validate_credentials("testuser", "testpassword")

        assert user is not None
        assert user.id == 1
        assert user.username == "testuser"
        auth_service.user_repo.get_by_username.assert_called_once_with("testuser")

    async def test_validate_credentials_user_not_found(
        self,
        auth_service: AuthService,
    ) -> None:
        """Test credential validation with non-existent user."""
        auth_service.user_repo.get_by_username.return_value = None

        user = await auth_service.validate_credentials("nonexistent", "password")

        assert user is None
        auth_service.user_repo.get_by_username.assert_called_once_with("nonexistent")

    async def test_validate_credentials_wrong_password(
        self,
        auth_service: AuthService,
        mock_user: User,
    ) -> None:
        """Test credential validation with wrong password."""
        auth_service.user_repo.get_by_username.return_value = mock_user

        user = await auth_service.validate_credentials("testuser", "wrongpassword")

        assert user is None
        auth_service.user_repo.get_by_username.assert_called_once_with("testuser")


class TestCreateUser:
    """Tests for create_user method."""

    async def test_create_user_success(
        self,
        auth_service: AuthService,
    ) -> None:
        """Test successful user creation."""
        new_user = MagicMock(spec=User)
        new_user.id = 2
        new_user.username = "newuser"
        new_user.password_hash = "hashed_password"
        auth_service.user_repo.create.return_value = new_user

        user = await auth_service.create_user("newuser", "newpassword")

        assert user.id == 2
        assert user.username == "newuser"
        auth_service.user_repo.create.assert_called_once()
        # Verify password was hashed (not stored as plain text)
        call_args = auth_service.user_repo.create.call_args
        assert call_args[1]["username"] == "newuser"
        assert call_args[1]["password_hash"] != "newpassword"
        assert len(call_args[1]["password_hash"]) > 0

    async def test_create_user_hashes_password(
        self,
        auth_service: AuthService,
    ) -> None:
        """Test that create_user properly hashes the password."""
        new_user = MagicMock(spec=User)
        new_user.id = 3
        new_user.username = "hashtest"
        auth_service.user_repo.create.return_value = new_user

        await auth_service.create_user("hashtest", "plaintext_password")

        call_args = auth_service.user_repo.create.call_args
        password_hash = call_args[1]["password_hash"]

        # Verify the hash can be verified with the original password
        assert AuthService.verify_password("plaintext_password", password_hash) is True
        assert AuthService.verify_password("wrong_password", password_hash) is False
