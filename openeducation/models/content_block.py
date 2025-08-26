from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from typing import Dict, List


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


@dataclass
class ContentBlock:
    id: str
    title: str
    body: str
    bullets: List[str] = field(default_factory=list)
    terms: List[str] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    @staticmethod
    def make_id(text: str) -> str:
        return "cb_" + hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]

    @classmethod
    def from_text(
        cls, title: str, text: str, source_id: str, language: str = "en", license: str = "unknown"
    ) -> "ContentBlock":
        return cls(
            id=cls.make_id(title + text),
            title=title,
            body=text,
            metadata={
                "source_id": source_id,
                "language": language,
                "license": license,
                "timestamp": _now_iso(),
            },
        )

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)
