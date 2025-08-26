from __future__ import annotations

import re
from typing import List

from ..models.content_block import ContentBlock


def extract_terms(block: ContentBlock) -> List[str]:
    words = re.findall(r"[A-Za-z]{5,}", block.body)
    uniq = sorted(set(w.lower() for w in words))
    return uniq[:20]


def block_to_bullets(block: ContentBlock) -> List[str]:
    bullets = re.findall(r"^-\\s+(.+)$", block.body, flags=re.M)
    if bullets:
        return bullets[:10]
    sents = re.split(r"(?<=[.!?])\\s+", block.body)
    return [s.strip() for s in sents[:5] if s.strip()]
