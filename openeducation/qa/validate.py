from __future__ import annotations

import re
from typing import Dict, List

from ..models.card import Card


def deduplicate(cards: List[Card]) -> List[Card]:
    seen = set()
    unique = []
    for c in cards:
        key = (c.front.strip().lower(), c.back.strip().lower())
        if key not in seen:
            seen.add(key)
            unique.append(c)
    return unique


def flesch_reading_ease(text: str) -> float:
    words = re.findall(r"[a-zA-Z]+", text)
    if not words:
        return 0.0
    syllables = sum(len(re.findall(r"[aeiouy]+", w.lower())) for w in words)
    sentences = max(1, len(re.split(r"[.!?]", text)))
    W, S, Y = len(words), sentences, syllables
    return 206.835 - 1.015 * (W / S) - 84.6 * (Y / W)


def coverage(terms_src: List[str], terms_cards: List[str]) -> float:
    if not terms_src:
        return 0.0
    return len(set(terms_cards) & set(terms_src)) / len(set(terms_src))


def validate_cards(cards: List[Card], terms_src: List[str]) -> Dict[str, float]:
    cards = deduplicate(cards)
    avg_fre = sum(flesch_reading_ease(c.back) for c in cards) / len(cards)
    cov = coverage(terms_src, [c.front for c in cards])
    return {"count": len(cards), "avg_fre": avg_fre, "coverage": cov}
