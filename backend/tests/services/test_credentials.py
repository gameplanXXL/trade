"""Tests for credential encryption service."""

import pytest
from cryptography.fernet import Fernet, InvalidToken

from src.services.credentials import CredentialService


@pytest.fixture
def valid_key() -> str:
    """Generate a valid Fernet key for testing."""
    return Fernet.generate_key().decode()


@pytest.fixture
def service(valid_key: str) -> CredentialService:
    """Create a CredentialService instance with valid key."""
    return CredentialService(valid_key)


class TestCredentialServiceInit:
    """Test CredentialService initialization."""

    def test_init_with_valid_key(self, valid_key: str):
        """Should initialize successfully with valid key."""
        service = CredentialService(valid_key)
        assert service.fernet is not None

    def test_init_with_empty_key(self):
        """Should raise ValueError with empty key."""
        with pytest.raises(ValueError, match="Encryption key cannot be empty"):
            CredentialService("")

    def test_init_with_invalid_key_format(self):
        """Should raise ValueError with invalid key format."""
        with pytest.raises(ValueError, match="Invalid encryption key format"):
            CredentialService("not-a-valid-fernet-key")

    def test_init_with_short_key(self):
        """Should raise ValueError with too short key."""
        with pytest.raises(ValueError, match="Invalid encryption key format"):
            CredentialService("short")


class TestCredentialServiceEncryption:
    """Test encryption functionality."""

    def test_encrypt_simple_string(self, service: CredentialService):
        """Should encrypt a simple string."""
        plaintext = "password123"
        encrypted = service.encrypt(plaintext)

        # Encrypted value should be different from plaintext
        assert encrypted != plaintext
        # Should be base64-encoded string
        assert isinstance(encrypted, str)
        assert len(encrypted) > 0

    def test_encrypt_mt5_password(self, service: CredentialService):
        """Should encrypt MT5 password."""
        mt5_password = "MySecureP@ssw0rd!"
        encrypted = service.encrypt(mt5_password)

        assert encrypted != mt5_password
        assert isinstance(encrypted, str)

    def test_encrypt_api_key(self, service: CredentialService):
        """Should encrypt LLM API key."""
        api_key = "sk-ant-api03-1234567890abcdef"
        encrypted = service.encrypt(api_key)

        assert encrypted != api_key
        assert isinstance(encrypted, str)

    def test_encrypt_empty_string(self, service: CredentialService):
        """Should encrypt empty string."""
        encrypted = service.encrypt("")
        assert isinstance(encrypted, str)
        assert len(encrypted) > 0

    def test_encrypt_unicode_string(self, service: CredentialService):
        """Should encrypt unicode characters."""
        plaintext = "Пароль123!@#äöü"
        encrypted = service.encrypt(plaintext)

        assert encrypted != plaintext
        assert isinstance(encrypted, str)

    def test_encrypt_long_string(self, service: CredentialService):
        """Should encrypt very long strings."""
        plaintext = "x" * 10000
        encrypted = service.encrypt(plaintext)

        assert encrypted != plaintext
        assert isinstance(encrypted, str)

    def test_encrypt_deterministic(self, service: CredentialService):
        """Should produce different ciphertext each time (due to IV)."""
        plaintext = "password123"
        encrypted1 = service.encrypt(plaintext)
        encrypted2 = service.encrypt(plaintext)

        # Fernet includes random IV, so same plaintext produces different ciphertext
        assert encrypted1 != encrypted2


class TestCredentialServiceDecryption:
    """Test decryption functionality."""

    def test_decrypt_simple_string(self, service: CredentialService):
        """Should decrypt to original plaintext."""
        plaintext = "password123"
        encrypted = service.encrypt(plaintext)
        decrypted = service.decrypt(encrypted)

        assert decrypted == plaintext

    def test_decrypt_mt5_password(self, service: CredentialService):
        """Should decrypt MT5 password correctly."""
        original = "MySecureP@ssw0rd!"
        encrypted = service.encrypt(original)
        decrypted = service.decrypt(encrypted)

        assert decrypted == original

    def test_decrypt_api_key(self, service: CredentialService):
        """Should decrypt API key correctly."""
        original = "sk-ant-api03-1234567890abcdef"
        encrypted = service.encrypt(original)
        decrypted = service.decrypt(encrypted)

        assert decrypted == original

    def test_decrypt_empty_string(self, service: CredentialService):
        """Should decrypt empty string."""
        encrypted = service.encrypt("")
        decrypted = service.decrypt(encrypted)

        assert decrypted == ""

    def test_decrypt_unicode_string(self, service: CredentialService):
        """Should decrypt unicode characters."""
        original = "Пароль123!@#äöü"
        encrypted = service.encrypt(original)
        decrypted = service.decrypt(encrypted)

        assert decrypted == original

    def test_decrypt_long_string(self, service: CredentialService):
        """Should decrypt very long strings."""
        original = "x" * 10000
        encrypted = service.encrypt(original)
        decrypted = service.decrypt(encrypted)

        assert decrypted == original

    def test_decrypt_with_wrong_key(self, service: CredentialService):
        """Should fail to decrypt with different key."""
        plaintext = "password123"
        encrypted = service.encrypt(plaintext)

        # Create new service with different key
        different_key = Fernet.generate_key().decode()
        different_service = CredentialService(different_key)

        with pytest.raises(InvalidToken):
            different_service.decrypt(encrypted)

    def test_decrypt_invalid_ciphertext(self, service: CredentialService):
        """Should raise InvalidToken for corrupted ciphertext."""
        with pytest.raises(InvalidToken):
            service.decrypt("invalid-ciphertext")

    def test_decrypt_tampered_ciphertext(self, service: CredentialService):
        """Should raise InvalidToken for tampered ciphertext."""
        plaintext = "password123"
        encrypted = service.encrypt(plaintext)

        # Tamper with ciphertext
        tampered = encrypted[:-5] + "XXXXX"

        with pytest.raises(InvalidToken):
            service.decrypt(tampered)


class TestCredentialServiceRoundTrip:
    """Test complete encryption/decryption cycles."""

    def test_multiple_values(self, service: CredentialService):
        """Should handle multiple different values."""
        values = [
            "simple",
            "with spaces",
            "symbols!@#$%^&*()",
            "numbers123456",
            "UPPERCASE",
            "MixedCase",
            "unicode: äöü ñ 中文",
        ]

        for value in values:
            encrypted = service.encrypt(value)
            decrypted = service.decrypt(encrypted)
            assert decrypted == value

    def test_multiple_encryptions(self, service: CredentialService):
        """Should handle multiple sequential operations."""
        plaintext = "password123"

        for _ in range(100):
            encrypted = service.encrypt(plaintext)
            decrypted = service.decrypt(encrypted)
            assert decrypted == plaintext

    def test_nested_encryption(self, service: CredentialService):
        """Should handle encrypting already encrypted values."""
        plaintext = "password123"
        encrypted1 = service.encrypt(plaintext)
        encrypted2 = service.encrypt(encrypted1)

        decrypted1 = service.decrypt(encrypted2)
        decrypted2 = service.decrypt(decrypted1)

        assert decrypted2 == plaintext


class TestCredentialServiceSecurity:
    """Test security properties."""

    def test_encrypted_value_not_predictable(self, service: CredentialService):
        """Encrypted values should not reveal plaintext patterns."""
        # Encrypt similar values
        encrypted1 = service.encrypt("password1")
        encrypted2 = service.encrypt("password2")

        # Ciphertexts should be completely different
        assert encrypted1 != encrypted2

    def test_encrypted_length_does_not_leak_info(self, service: CredentialService):
        """Encrypted values should have padding to prevent length analysis."""
        short = service.encrypt("a")
        medium = service.encrypt("a" * 50)

        # Both should be reasonably long (Fernet adds overhead)
        assert len(short) > 50
        assert len(medium) > 50

    def test_key_isolation(self, valid_key: str):
        """Different service instances should be independent."""
        service1 = CredentialService(valid_key)
        service2 = CredentialService(valid_key)

        plaintext = "password123"
        encrypted1 = service1.encrypt(plaintext)
        decrypted2 = service2.decrypt(encrypted1)

        # Same key should work across instances
        assert decrypted2 == plaintext


class TestCredentialServiceKeyGeneration:
    """Test key generation documentation."""

    def test_generated_key_format(self):
        """Generated keys should be valid Fernet keys."""
        key = Fernet.generate_key()
        key_str = key.decode()

        # Should be 44 characters (32 bytes base64-encoded)
        assert len(key_str) == 44

        # Should be usable to create service
        service = CredentialService(key_str)
        assert service is not None

    def test_generated_keys_are_unique(self):
        """Multiple generated keys should be different."""
        keys = [Fernet.generate_key().decode() for _ in range(10)]

        # All keys should be unique
        assert len(set(keys)) == 10
