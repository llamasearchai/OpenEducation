from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


def _id(seed: str) -> int:
    return int(hashlib.sha1(seed.encode("utf-8")).hexdigest()[:8], 16)


@dataclass
class Deck:
    id: str
    name: str
    description: str = ""
    parent_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    cards: List[Dict[str, Any]] = field(default_factory=list)
    media: List[str] = field(default_factory=list)

    @property
    def model_id(self) -> int:
        return _id(self.name + ":model")

    @property
    def deck_id_int(self) -> int:
        return _id(self.id)

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)
