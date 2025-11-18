"""Reusable FastAPI dependencies for auth and permissions."""
from __future__ import annotations

from datetime import datetime
from typing import Annotated, Dict, List
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import get_settings
from .database import DB

security_scheme = HTTPBearer(auto_error=False)


class Principal(Dict):
    """Simple dict subclass to provide attribute-style hints."""


async def get_current_session(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Security(security_scheme)]
) -> Dict:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    session = DB.get_session(credentials.credentials)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if session["expires_at"] < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Token expired")
    return session


async def get_current_user(session: Dict = Depends(get_current_session)) -> Dict:
    user = DB.users.get(session["user_id"])
    if not user or not user.get("is_enabled"):
        raise HTTPException(status_code=403, detail="User disabled")
    return user


async def require_permissions(
    permissions: List[str],
    user: Dict = Depends(get_current_user),
) -> Dict:
    user_permissions = set(DB.permissions.get(user["id"], []))
    settings = get_settings()
    if user["email"] == settings.default_admin_email:
        DB.permissions[user["id"]] = permissions
        return user

    missing = [perm for perm in permissions if perm not in user_permissions]
    if missing:
        raise HTTPException(status_code=403, detail=f"Missing permissions: {', '.join(missing)}")
    return user


async def require_admin(user: Dict = Depends(get_current_user)) -> Dict:
    settings = get_settings()
    if user["email"] == settings.default_admin_email:
        return user

    if "admin.manage" not in DB.permissions.get(user["id"], []):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
