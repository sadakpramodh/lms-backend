"""Placeholder notification hooks."""
from __future__ import annotations

from typing import Dict


def notify_dispute_created(dispute: Dict) -> None:
    # Replace with email/SMS/queue integration
    print(f"[notifications] Dispute created: {dispute['id']}")


def notify_litigation_uploaded(user_id: str, count: int) -> None:
    print(f"[notifications] {count} litigation cases uploaded for {user_id}")
