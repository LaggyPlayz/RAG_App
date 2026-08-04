"""Fernet-based symmetric encryption for database connection credentials.

The encryption key is derived from the ENCRYPTION_KEY environment variable.
All database passwords and connection strings are encrypted at rest.
"""

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings
from app.utils.exceptions import AppError

_settings = get_settings()


def _get_fernet() -> Fernet:
    """Derive a valid Fernet key from the configured encryption key.

    Fernet requires a 32-byte URL-safe base64-encoded key.  If the
    configured key isn't already in that format we derive one via SHA-256.
    """
    raw_key = _settings.encryption_key.encode()
    try:
        # If it's already a valid Fernet key, use it directly
        Fernet(raw_key)
        return Fernet(raw_key)
    except (ValueError, Exception):
        # Derive a 32-byte key via SHA-256 and base64 encode
        derived = hashlib.sha256(raw_key).digest()
        key = base64.urlsafe_b64encode(derived)
        return Fernet(key)


_fernet = _get_fernet()


def encrypt_value(plaintext: str) -> str:
    """Encrypt a plaintext string and return the ciphertext as a UTF-8 string."""
    if not plaintext:
        return ""
    return _fernet.encrypt(plaintext.encode()).decode()


def decrypt_value(ciphertext: str) -> str:
    """Decrypt a ciphertext string back to plaintext."""
    if not ciphertext:
        return ""
    try:
        return _fernet.decrypt(ciphertext.encode()).decode()
    except InvalidToken as exc:
        raise AppError(
            "Failed to decrypt credential — encryption key may have changed",
            details={"hint": "Re-encrypt credentials or restore the original ENCRYPTION_KEY"},
        ) from exc
