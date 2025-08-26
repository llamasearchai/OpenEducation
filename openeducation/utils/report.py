from __future__ import annotations

import json
import os
from typing import Dict, List

from ..models.card import Card


def manifest(run_dir: str) -> str:
    cards_path = os.path.join(run_dir, "cards.json")
    if not os.path.exists(cards_path):
        raise FileNotFoundError("cards.json missing")
    with open(cards_path, "r", encoding="utf-8") as f:
        cards = [Card(**c) for c in json.load(f)]
    data = {
        "count": len(cards),
        "tags": sorted({t for c in cards for t in c.tags}),
        "sources": sorted({c.source_id for c in cards if c.source_id}),
    }
    out = os.path.join(run_dir, "manifest.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return out


def licensing_report(sources: List[Dict[str, str]], run_dir: str) -> str:
    out = os.path.join(run_dir, "licensing_report.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"sources": sources}, f, indent=2)
    return out
