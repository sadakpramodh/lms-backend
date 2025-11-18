"""Authentication endpoints mirroring Supabase flows."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from ....database import DB
from ....dependencies import get_current_session
from ....schemas import (
    AuthRefreshRequest,
    AuthSignInRequest,
    AuthSignUpRequest,
    TokenPair,
)
from ....services.auth import issue_session
from ....config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/sign-up", response_model=TokenPair)
async def sign_up(payload: AuthSignUpRequest) -> TokenPair:
    if DB.get_user_by_email(payload.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    user = DB.create_user(payload.email, payload.full_name, payload.password)
    settings = get_settings()
    if payload.email == settings.default_admin_email:
        DB.permissions[user["id"]] = [
            "disputes.create",
            "disputes.update",
            "disputes.delete",
            "litigation.create",
            "litigation.delete",
            "admin.manage",
        ]
    access, refresh, access_exp, refresh_exp = issue_session(user["id"])
    DB.create_session(user["id"], access, access_exp, refresh, refresh_exp)
    return TokenPair(access_token=access, refresh_token=refresh, expires_in=int((access_exp - datetime.utcnow()).total_seconds()))


@router.post("/sign-in", response_model=TokenPair)
async def sign_in(payload: AuthSignInRequest) -> TokenPair:
    user = DB.get_user_by_email(payload.email)
    if not user or user["password"] != payload.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.get("is_enabled"):
        raise HTTPException(status_code=403, detail="Account disabled")

    access, refresh, access_exp, refresh_exp = issue_session(user["id"])
    DB.create_session(user["id"], access, access_exp, refresh, refresh_exp)
    return TokenPair(access_token=access, refresh_token=refresh, expires_in=int((access_exp - datetime.utcnow()).total_seconds()))


@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: AuthRefreshRequest) -> TokenPair:
    session = DB.get_session(payload.refresh_token)
    if not session or session["refresh_expires_at"] < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    access, refresh, access_exp, refresh_exp = issue_session(session["user_id"])
    DB.create_session(session["user_id"], access, access_exp, refresh, refresh_exp)
    return TokenPair(access_token=access, refresh_token=refresh, expires_in=int((access_exp - datetime.utcnow()).total_seconds()))


@router.post("/sign-out")
async def sign_out(session=Depends(get_current_session)) -> None:
    DB.revoke_session(session["access_token"])
