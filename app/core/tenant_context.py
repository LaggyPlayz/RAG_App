"""Tenant context extraction and enforcement.

Provides dependencies that extract the tenant_id from the authenticated
user's JWT and expose it for downstream query filtering.
"""

from fastapi import Depends, Request

from app.core.security import get_current_user_payload
from app.utils.exceptions import AuthenticationError


async def get_tenant_id(
    request: Request,
    _payload: dict = Depends(get_current_user_payload),
) -> str:
    """Return the authenticated user's tenant_id.

    This dependency is used by repositories and services to scope all
    queries to the current tenant, preventing cross-tenant data access.
    """
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise AuthenticationError("Unable to resolve tenant context")
    return tenant_id


async def get_user_id(
    request: Request,
    _payload: dict = Depends(get_current_user_payload),
) -> str:
    """Return the authenticated user's user_id."""
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise AuthenticationError("Unable to resolve user context")
    return user_id


async def require_tenant_admin(
    request: Request,
    _payload: dict = Depends(get_current_user_payload),
) -> dict:
    """Require the current user to be a tenant administrator."""
    if not getattr(request.state, "is_tenant_admin", False):
        from app.utils.exceptions import AuthorizationError
        raise AuthorizationError("This action requires tenant administrator privileges")
    return _payload
