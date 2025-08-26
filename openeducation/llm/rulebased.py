from __future__ import annotations
from typing import List
from ..models.content_block import ContentBlock
from ..models.card import Card
from ..content.extractor import extract_terms, block_to_bullets


def make_cards_rulebased(block: ContentBlock, deck_id: str) -> List[Card]:
    bullets = block_to_bullets(block)
    terms = extract_terms(block)
    cards: List[Card] = []
    if bullets:
        title = block.title or "this section"
        front = f"What is the key idea of: {title}?"
        back = bullets[0]
        cards.append(
            Card.basic(
                front,
                back,
                source_id=block.source_id,
                deck_id=deck_id,
                tags=["definition"],
            )
        )
    for t in terms[:3]:
        front = f"Define: {t}"
        back = f"{t}: {bullets[0] if bullets else (block.body[:180]+'...')}"
        cards.append(
            Card.basic(
                front,
                back,
                source_id=block.source_id,
                deck_id=deck_id,
                tags=["term"],
            )
        )
    return cards
