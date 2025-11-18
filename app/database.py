"""In-memory persistence to simulate a database."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid

from pydantic import EmailStr


class InMemoryDB:
    def __init__(self) -> None:
        self.users: Dict[str, Dict[str, Any]] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.profiles: Dict[str, Dict[str, Any]] = {}
        self.alert_settings: Dict[str, Dict[str, Any]] = {}
        self.disputes: Dict[str, Dict[str, Any]] = {}
        self.litigation_cases: Dict[str, Dict[str, Any]] = {}
        self.permissions: Dict[str, List[str]] = defaultdict(list)

    # --- User helpers -----------------------------------------------------
    def create_user(self, email: EmailStr, full_name: str, password: str) -> Dict[str, Any]:
        user_id = str(uuid.uuid4())
        now = datetime.utcnow()
        record = {
            "id": user_id,
            "email": email,
            "full_name": full_name,
            "password": password,
            "created_at": now,
            "updated_at": now,
            "is_enabled": True,
        }
        self.users[user_id] = record
        self.profiles[user_id] = {
            "user_id": user_id,
            "full_name": full_name,
            "avatar_url": None,
            "is_enabled": True,
            "created_at": now,
            "updated_at": now,
        }
        self.alert_settings[user_id] = {
            "user_id": user_id,
            "email_alerts": True,
            "sms_alerts": False,
        }
        return record

    def get_user_by_email(self, email: EmailStr) -> Optional[Dict[str, Any]]:
        return next((user for user in self.users.values() if user["email"] == email), None)

    # --- Session helpers --------------------------------------------------
    def create_session(self, user_id: str, token: str, expires_at: datetime, refresh_token: str, refresh_expires_at: datetime) -> Dict[str, Any]:
        session = {
            "user_id": user_id,
            "access_token": token,
            "refresh_token": refresh_token,
            "expires_at": expires_at,
            "refresh_expires_at": refresh_expires_at,
        }
        self.sessions[token] = session
        self.sessions[refresh_token] = session
        return session

    def get_session(self, token: str) -> Optional[Dict[str, Any]]:
        return self.sessions.get(token)

    def revoke_session(self, token: str) -> None:
        session = self.sessions.pop(token, None)
        if session:
            self.sessions.pop(session.get("refresh_token"), None)
            self.sessions.pop(session.get("access_token"), None)

    # --- Generic CRUD helpers --------------------------------------------
    def upsert(self, table: Dict[str, Dict[str, Any]], record_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if record_id not in table:
            table[record_id] = {"id": record_id}
        table[record_id].update(payload)
        return table[record_id]

    def insert(self, table: Dict[str, Dict[str, Any]], payload: Dict[str, Any]) -> Dict[str, Any]:
        record_id = payload.get("id") or str(uuid.uuid4())
        payload["id"] = record_id
        table[record_id] = payload
        return payload

    def delete(self, table: Dict[str, Dict[str, Any]], record_id: str) -> None:
        table.pop(record_id, None)


DB = InMemoryDB()
