import pytest
from app.core.security import create_access_token, verify_token
from app.core.encryption import decrypt_value, encrypt_value


def test_jwt_token_generation_and_decoding():
    payload = {"sub": "user-123", "tenant_id": "tenant-abc", "is_tenant_admin": True}
    token = create_access_token(payload)

    decoded = verify_token(token, expected_type="access")
    assert decoded["sub"] == "user-123"
    assert decoded["tenant_id"] == "tenant-abc"
    assert decoded["is_tenant_admin"] is True


def test_credential_fernet_encryption():
    secret_pass = "super_secret_db_password_123!"
    encrypted = encrypt_value(secret_pass)

    assert encrypted != secret_pass
    decrypted = decrypt_value(encrypted)
    assert decrypted == secret_pass
