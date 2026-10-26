"""
User registry — stores hashed credentials in a JSON file.
Follows the same thin-interface pattern as document_registry.py so it can
be swapped for a real database without touching the auth router.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import bcrypt

REGISTRY_FILE = Path(__file__).resolve().parent.parent / "user_registry.json"


def _hash_password(password: str) -> str:
    """Hash password using bcrypt directly, safely handling utf-8 bytes up to 72 bytes."""
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def _verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash."""
    try:
        pwd_bytes = plain_password.encode("utf-8")[:72]
        return bcrypt.checkpw(pwd_bytes, hashed_password.encode("utf-8"))
    except Exception:
        return False


# ── Internal helpers ──────────────────────────────────────────────────────────

def _load() -> dict:
    if REGISTRY_FILE.exists():
        try:
            return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def _save(data: dict) -> None:
    REGISTRY_FILE.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


# ── Public helpers ─────────────────────────────────────────────────────────────

def create_user(email: str, password: str, full_name: str = "") -> dict:
    """
    Create a new user account.
    Raises ValueError if the email is already registered.
    """
    data = _load()
    email_lower = email.strip().lower()

    # Check uniqueness by email
    for entry in data.values():
        if entry["email"] == email_lower:
            raise ValueError(f"Email '{email}' is already registered.")

    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    entry = {
        "id": user_id,
        "email": email_lower,
        "full_name": full_name.strip(),
        "hashed_password": _hash_password(password),
        "created_at": now,
        "is_active": True,
    }
    data[user_id] = entry
    _save(data)
    # Return a safe copy without the hash
    return {k: v for k, v in entry.items() if k != "hashed_password"}


def authenticate_user(email: str, password: str) -> Optional[dict]:
    """
    Verify credentials.  Returns the user dict (without hash) on success,
    or None if the email is unknown or password is wrong.
    """
    data = _load()
    email_lower = email.strip().lower()
    for entry in data.values():
        if entry["email"] == email_lower:
            if _verify_password(password, entry["hashed_password"]):
                return {k: v for k, v in entry.items() if k != "hashed_password"}
            return None   # wrong password — don't leak "user not found" vs "wrong pw"
    return None


def get_user_by_id(user_id: str) -> Optional[dict]:
    data = _load()
    entry = data.get(user_id)
    if not entry:
        return None
    return {k: v for k, v in entry.items() if k != "hashed_password"}


def get_user_by_email(email: str) -> Optional[dict]:
    data = _load()
    email_lower = email.strip().lower()
    for entry in data.values():
        if entry["email"] == email_lower:
            return {k: v for k, v in entry.items() if k != "hashed_password"}
    return None
