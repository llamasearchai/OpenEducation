from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from typing import Any, List, Optional


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


@dataclass
class ContentBlock:
    """A chunk of content from a source."""

    id: str
    body: str
    source_id: str
    title: Optional[str] = None
    terms: List[str] = field(default_factory=list)
    bullets: List[str] = field(default_factory=list)

    def to_dict(self):
        """Convert the object to a dictionary."""
        return {
            "id": self.id,
            "body": self.body,
            "source_id": self.source_id,
            "title": self.title,
            "terms": self.terms,
            "bullets": self.bullets,
        }

    @staticmethod
    def make_id(text: str) -> str:
        return "cb_" + hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]

    @classmethod
    def from_text(cls, *args: Any, **kwargs: Any) -> "ContentBlock":
        """Create a ContentBlock from text with flexible arguments.

        Supported forms:
        - Positional: (title, text, source_id)
        - Positional (legacy): (text, source_id)
        - Keyword: title=..., text=... (or body=...), source_id=...
        """
        title: Optional[str] = None
        text: Optional[str] = None
        source_id: Optional[str] = None

        if kwargs:
            title = kwargs.get("title")
            text = kwargs.get("text") or kwargs.get("body")
            source_id = kwargs.get("source_id")
        elif len(args) == 3:
            # (title, text, source_id)
            title = args[0]
            text = args[1]
            source_id = args[2]
        elif len(args) == 2:
            # (text, source_id)
            text = args[0]
            source_id = args[1]
        else:
            raise TypeError("from_text expects (title, text, source_id) or keyword args title=, text/body=, source_id=")

        if not isinstance(source_id, str) or not source_id:
            raise ValueError("source_id is required")
        if not isinstance(text, str) or not text:
            raise ValueError("text/body is required")

        cid = hashlib.sha256(text.encode()).hexdigest()
        return ContentBlock(id=cid, title=title, body=text, source_id=source_id)

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)
