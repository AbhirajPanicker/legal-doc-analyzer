"""
Document registry — stores metadata about uploaded documents in a simple
JSON file. The interface is kept thin so it can be replaced by a database
without touching the routers.
"""
from __future__ import annotations
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from config import settings

REGISTRY_FILE = Path(__file__).resolve().parent.parent / "document_registry.json"


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

def create_document(
    filename: str,
    original_name: str,
    file_size_bytes: int,
    doc_id: Optional[str] = None,
    user_id: Optional[str] = None,
) -> dict:
    """Create a new document entry with status='processing'."""
    doc_id = doc_id or str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    entry = {
        "id": doc_id,
        "filename": filename,
        "original_name": original_name,
        "upload_time": now,
        "page_count": 0,
        "file_size_bytes": file_size_bytes,
        "status": "processing",
        "error_message": None,
        "ocr_applied": False,
        "scanned_pages": [],
        "user_id": user_id,   # None = legacy / unauthenticated document
    }
    data = _load()
    data[doc_id] = entry
    _save(data)
    return entry


def update_document(doc_id: str, **kwargs) -> Optional[dict]:
    data = _load()
    if doc_id not in data:
        return None
    data[doc_id].update(kwargs)
    _save(data)
    return data[doc_id]


def get_document(doc_id: str) -> Optional[dict]:
    return _load().get(doc_id)


def list_documents() -> list[dict]:
    """Return all documents regardless of owner (admin / legacy use)."""
    data = _load()
    return sorted(data.values(), key=lambda d: d["upload_time"], reverse=True)


def list_documents_for_user(user_id: str) -> list[dict]:
    """Return ONLY documents owned by the given user, newest first."""
    data = _load()
    owned = [d for d in data.values() if d.get("user_id") == user_id]
    return sorted(owned, key=lambda d: d["upload_time"], reverse=True)


def delete_document(doc_id: str) -> bool:
    data = _load()
    if doc_id not in data:
        return False
    del data[doc_id]
    _save(data)
    return True
