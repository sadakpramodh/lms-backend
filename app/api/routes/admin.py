from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends

from ....database import DB
from ....dependencies import require_admin
from ....schemas import AccessToggleRequest, AdminUserSummary, PermissionUpdate, Profile

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=List[AdminUserSummary])
async def list_users(admin=Depends(require_admin)) -> List[AdminUserSummary]:
    summaries: List[AdminUserSummary] = []
    for user_id, profile in DB.profiles.items():
        permissions = DB.permissions.get(user_id, [])
        summaries.append(
            AdminUserSummary(
                profile=Profile(**profile),
                permissions=permissions,
                last_sign_in=None,
            )
        )
    return summaries


@router.post("/permissions")
async def update_permissions(payload: PermissionUpdate, admin=Depends(require_admin)):
    DB.permissions[payload.user_id] = payload.permissions


@router.post("/access")
async def toggle_access(payload: AccessToggleRequest, admin=Depends(require_admin)):
    profile = DB.profiles.get(payload.user_id)
    if profile:
        profile["is_enabled"] = payload.is_enabled
    user = DB.users.get(payload.user_id)
    if user:
        user["is_enabled"] = payload.is_enabled
