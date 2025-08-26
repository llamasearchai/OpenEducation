from __future__ import annotations

import os
from typing import Any, Dict

from ..config import AppConfig
from ..content.extractor import block_to_bullets, extract_terms
from ..content.sources import ContentSource
from ..deck.builder import DeckBuilder
from ..llm.rulebased import make_cards_rulebased
from ..models.card import Card
from ..models.content_block import ContentBlock
from ..models.deck import Deck
from ..rag.embeddings import HashEmbedding
from ..utils.io import ensure_dir, read_json, write_json


def ingest_sources(cfg: Dict[str, Any]) -> str:
    """Ingest content from configured sources and return blocks path."""
    config = AppConfig.model_validate(cfg)
    ensure_dir(config.data_dir)
    blocks = []
    for s in config.sources:
        src = ContentSource(id=s.id, path=s.path, type=s.type)
        for b in src.to_blocks():
            b.terms = extract_terms(b)
            b.bullets = block_to_bullets(b)
            blocks.append(b.__dict__)
    blocks_path = os.path.join(config.data_dir, "content_blocks.json")
    write_json(blocks_path, blocks)
    return blocks_path


def build_rag_index(blocks_path: str) -> str:
    """Build RAG index from content blocks."""
    data = read_json(blocks_path)
    ids = [d["id"] for d in data]
    texts = [d["body"] for d in data]
    E = HashEmbedding()
    vecs = E.embed(texts)
    index_path = blocks_path.replace("content_blocks.json", "index.json")
    write_json(index_path, {"ids": ids, "vecs": vecs.tolist()})
    return index_path


def generate_cards(blocks_path: str, deck_id: str = "deck_main", max_cards: int = 64) -> str:
    """Generate cards from content blocks."""
    blocks = [ContentBlock(**d) for d in read_json(blocks_path)]
    cards = []
    for b in blocks[:max_cards]:
        for c in make_cards_rulebased(b, deck_id):
            cards.append(c.to_dict())
    cards_path = os.path.join(os.path.dirname(blocks_path), "cards.json")
    write_json(cards_path, cards)
    return cards_path


def assemble_deck(cards_path: str, deck_id: str = "deck_main", name: str = "OpenEducation") -> str:
    """Assemble Anki deck from cards."""
    deck = Deck(id=deck_id, name=name)
    builder = DeckBuilder(deck)
    cards = [Card(**d) for d in read_json(cards_path)]
    for c in cards:
        builder.add_card(c)
    apkg_path = os.path.join(os.path.dirname(cards_path), f"{name.replace(' ', '_')}.apkg")
    builder.save(apkg_path)
    return apkg_path


def push_to_anki(apkg_path: str) -> str:
    """Push deck to Anki via AnkiConnect."""
    from ..anki_connect.push import import_package

    result = import_package(apkg_path)
    return f"Imported {len(result.get('added', []))} notes to Anki"
