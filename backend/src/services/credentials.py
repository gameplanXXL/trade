"""Credential encryption service using Fernet (AES-128-CBC with HMAC).

This service provides symmetric encryption for sensitive data like MT5 passwords
and LLM API keys. The encryption key must be stored securely in environment
variables and should never be logged or committed to version control.

Key Generation:
    To generate a new Fernet encryption key, use:

    >>> from cryptography.fernet import Fernet
    >>> key = Fernet.generate_key()
    >>> print(key.decode())

    The generated key is a 32-byte URL-safe base64-encoded string (44 chars).
    Store this in your .env file as ENCRYPTION_KEY.

Example:
    >>> from config.settings import get_settings
    >>> settings = get_settings()
    >>> service = CredentialService(settings.encryption_key)
    >>> encrypted = service.encrypt("my_secret_password")
    >>> decrypted = service.decrypt(encrypted)
    >>> assert decrypted == "my_secret_password"
"""

from cryptography.fernet import Fernet


class CredentialService:
    """Service for encrypting and decrypting credentials.

    Uses Fernet symmetric encryption (AES-128-CBC with HMAC) to protect
    sensitive data at rest. All encryption/decryption operations are
    deterministic and reversible with the correct key.

    Args:
        encryption_key: A 44-character base64-encoded Fernet key.

    Raises:
        ValueError: If the encryption key is invalid or improperly formatted.
    """

    def __init__(self, encryption_key: str):
        """Initialize the credential service with an encryption key.

        Args:
            encryption_key: Base64-encoded Fernet key (44 characters).

        Raises:
            ValueError: If key format is invalid.
        """
        if not encryption_key:
            raise ValueError("Encryption key cannot be empty")

        try:
            self.fernet = Fernet(encryption_key.encode())
        except Exception as e:
            raise ValueError(f"Invalid encryption key format: {e}") from e

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a plaintext string.

        Args:
            plaintext: The sensitive data to encrypt.

        Returns:
            Base64-encoded encrypted string (ciphertext).

        Example:
            >>> service = CredentialService(key)
            >>> encrypted = service.encrypt("password123")
            >>> # encrypted is now safe to store in database
        """
        return self.fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a ciphertext string.

        Args:
            ciphertext: The base64-encoded encrypted string.

        Returns:
            The original plaintext string.

        Raises:
            cryptography.fernet.InvalidToken: If ciphertext is corrupted or
                was encrypted with a different key.

        Example:
            >>> service = CredentialService(key)
            >>> plaintext = service.decrypt(encrypted_value)
            >>> # plaintext contains the original sensitive data
        """
        return self.fernet.decrypt(ciphertext.encode()).decode()
