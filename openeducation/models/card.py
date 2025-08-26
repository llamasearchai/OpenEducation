from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class CardType(Enum):
    BASIC = "basic"
    CLOZE = "cloze"


def _id(seed: str) -> str:
    return "card_" + hashlib.md5(seed.encode("utf-8")).hexdigest()[:10]


@dataclass
class Card:
    id: str
    front: str
    back: str
    card_type: CardType = CardType.BASIC
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

    @classmethod
    def cloze(
        cls, text: str, extra: str, deck_id: str, source_id: str, tags: List[str] = []
    ) -> Card:
        id = uuid.uuid4().hex
        return Card(id=id, deck_id=deck_id, front=text, back=extra, card_type=CardType.CLOZE, tags=tags, source_id=source_id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "deck_id": self.deck_id,
            "front": self.front,
            "back": self.back,
            "card_type": self.card_type.value,
            "tags": self.tags,
            "media": self.media,
            "source_id": self.source_id,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
