from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Source:
    id: str
    type: str
    path: str
    tags: List[str]
    license: Optional[str] = None
