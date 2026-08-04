"""JWT token management and password hashing.

Provides `create_access_token`, `create_refresh_token`, `verify_token`,
password hashing/verification, and a `get_current_user` FastAPI dependency.
"""

from datetime import datetime, timedelta, timezone

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.utils.exceptions import AuthenticationError, TokenExpiredError

_settings = get_settings()
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_bearer_scheme = HTTPBearer(auto_error=False)


# ── Password Hashing ──

def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _pwd_context.verify(plain_password, hashed_password)


# ── JWT Tokens ──

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=_settings.jwt_access_token_expire_minutes)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, _settings.jwt_secret_key, algorithm=_settings.jwt_algorithm)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=_settings.jwt_refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, _settings.jwt_secret_key, algorithm=_settings.jwt_algorithm)


def verify_token(token: str, expected_type: str = "access") -> dict:
    """Decode and validate a JWT token. Returns the payload dict."""
    try:
        payload = jwt.decode(token, _settings.jwt_secret_key, algorithms=[_settings.jwt_algorithm])
    except JWTError as exc:
        raise AuthenticationError("Invalid or malformed token") from exc

    if payload.get("type") != expected_type:
        raise AuthenticationError(f"Expected token type '{expected_type}', got '{payload.get('type')}'")

    exp = payload.get("exp")
    if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
        raise TokenExpiredError("Token has expired")

    return payload


# ── FastAPI Dependencies ──

async def get_current_user_payload(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> dict:
    """Extract and validate the JWT from the Authorization header.

    Returns the token payload dict with at minimum: sub, tenant_id.
    For endpoints that are optionally authenticated, use `get_optional_user_payload`.
    """
    if credentials is None:
        raise AuthenticationError("Missing authorization header")

    payload = verify_token(credentials.credentials, expected_type="access")

    if not payload.get("sub"):
        raise AuthenticationError("Token missing subject claim")
    if not payload.get("tenant_id"):
        raise AuthenticationError("Token missing tenant_id claim")

    # Attach to request state for downstream access
    request.state.user_id = payload["sub"]
    request.state.tenant_id = payload["tenant_id"]
    request.state.is_tenant_admin = payload.get("is_tenant_admin", False)

    return payload


async def get_optional_user_payload(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> dict | None:
    """Like get_current_user_payload but returns None instead of raising."""
    if credentials is None:
        return None
    try:
        return await get_current_user_payload(request, credentials)
    except AuthenticationError:
        return None
