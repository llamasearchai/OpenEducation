from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


def _id(seed: str) -> str:
    return "card_" + hashlib.md5(seed.encode("utf-8")).hexdigest()[:10]


@dataclass
class Card:
    id: str
    front: str
    back: str
    type: str = "basic"
    cloze_text: Optional[str] = None
    media: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    source_id: Optional[str] = None
    deck_id: Optional[str] = None
    difficulty: float = 0.5
    confidence: float = 0.5
    provenance: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def basic(
        cls,
        front: str,
        back: str,
        source_id: str = "",
        deck_id: str = "",
        tags: Optional[List[str]] = None,
    ) -> "Card":
        return cls(
            id=_id(front + back),
            front=front,
            back=back,
            source_id=source_id,
            deck_id=deck_id,
            tags=tags or [],
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
