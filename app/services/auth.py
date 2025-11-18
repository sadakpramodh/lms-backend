"""Utility helpers for issuing and validating tokens."""
from __future__ import annotations

import secrets
from datetime import datetime, timedelta
from typing import Tuple

from jose import jwt

from ..config import get_settings


def _generate_raw_token() -> str:
    return secrets.token_urlsafe(48)


def issue_token_pair(user_id: str) -> Tuple[str, str, datetime, datetime]:
    settings = get_settings()
    now = datetime.utcnow()
    payload = {"sub": user_id, "iat": now.timestamp()}
    access_exp = now + timedelta(minutes=settings.access_token_ttl_minutes)
    refresh_exp = now + timedelta(hours=settings.refresh_token_ttl_hours)

    payload["exp"] = access_exp.timestamp()
    access_token = jwt.encode(payload, settings.app_secret_key, algorithm="HS256")

    refresh_payload = payload | {"exp": refresh_exp.timestamp(), "type": "refresh"}
    refresh_token = jwt.encode(refresh_payload, settings.app_secret_key, algorithm="HS256")
    return access_token, refresh_token, access_exp, refresh_exp


def issue_session(user_id: str):
    access, refresh, access_exp, refresh_exp = issue_token_pair(user_id)
    return access, refresh, access_exp, refresh_exp
