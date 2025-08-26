from __future__ import annotations
from typing import List, Dict, Any
from pathlib import Path
import json
from datetime import datetime
from .config import DATA_DIR

CATALOG_PATH = Path(DATA_DIR) / "catalog.json"


def _read() -> Dict[str, Any]:
    if not CATALOG_PATH.exists():
        return {"decks": []}
    try:
        return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"decks": []}


def _write(data: Dict[str, Any]) -> None:
    CATALOG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def add_deck(deck_id: str, title: str, notes: int) -> None:
    data = _read()
    decks = data.get("decks", [])
    now = datetime.utcnow().isoformat() + "Z"
    decks.append({
        "deck_id": deck_id,
        "title": title,
        "notes": notes,
        "created_at": now,
    })
    data["decks"] = decks[-200:]
    _write(data)


def list_decks() -> List[Dict[str, Any]]:
    data = _read()
    return list(reversed(data.get("decks", [])))


def get_deck(deck_id: str) -> Dict[str, Any] | None:
    for d in list_decks():
        if d.get("deck_id") == deck_id:
            return d
    return None
