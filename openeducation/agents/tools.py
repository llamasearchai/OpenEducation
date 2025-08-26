from __future__ import annotations

import os
import json
from typing import Any, Dict, List

from ..config import AppConfig
from ..utils.io import ensure_dir, write_json, read_json
from ..content.sources import ContentSource
from ..models.content_block import ContentBlock
from ..models.card import Card, CardType
from ..models.deck import Deck
from ..deck.builder import DeckBuilder
from ..anki_connect.push import import_package
from ..llm.openai_wrapper import OpenAIWrapper

# --- Helper utilities ---

def _is_llm_enabled() -> bool:
    value = os.getenv("OPENEDUCATION_LLM_ENABLED", "1").strip().lower()
    return value not in {"0", "false", "no", "off"}


def _split_into_sentences(text: str) -> List[str]:
    # Very lightweight sentence splitter
    sentences = []
    current = []
    for ch in text:
        current.append(ch)
        if ch in {".", "?", "!"}:
            s = "".join(current).strip()
            if s:
                sentences.append(s)
            current = []
    # tail
    tail = "".join(current).strip()
    if tail:
        sentences.append(tail)
    return sentences


def _choose_terms(sentence: str) -> List[str]:
    # Heuristic key-term selection: long words and Capitalized medical terms
    words = [w.strip(" ,;:()[]{}\"'\n\t") for w in sentence.split()]
    candidates = []
    for w in words:
        if len(w) >= 8:
            candidates.append(w)
        elif w[:1].isupper() and len(w) >= 5:
            candidates.append(w)
    # Deduplicate while preserving order
    seen = set()
    result: List[str] = []
    for w in candidates:
        lw = w.lower()
        if lw not in seen and lw.isalpha():
            seen.add(lw)
            result.append(w)
    return result


def _make_cloze(sentence: str) -> str:
    terms = _choose_terms(sentence)
    if not terms:
        # fallback: cloze a mid-length word
        words = [w for w in sentence.split() if len(w) >= 6]
        if not words:
            return f"{{c1::[key concept]}}: {sentence}"
        term = words[0].strip(" ,;:()[]{}\"'\n\t")
        return sentence.replace(term, f"{{c1::{term}}}", 1)
    # Cloze the first key term
    term = terms[0]
    return sentence.replace(term, f"{{c1::{term}}}", 1)


# --- Agent Tools ---

def flashcard_agent(prompt: str, content_blocks: str) -> str:
    """
    Agent that generates flashcards based on content blocks.
    If OPENEDUCATION_LLM_ENABLED is disabled, uses an offline rule-based generator.
    """
    blocks = [ContentBlock(**d) for d in read_json(content_blocks)]
    all_cards: List[Dict[str, Any]] = []

    llm_enabled = _is_llm_enabled()
    llm: OpenAIWrapper | None = None
    if llm_enabled:
        try:
            llm = OpenAIWrapper()
        except Exception as e:
            print(f"LLM initialization failed ({e}). Falling back to offline generation.")
            llm_enabled = False

    for block in blocks:
        chapter_title = block.title
        chapter_text = block.body

        if len(chapter_text) < 200:
            print(f"Skipping short content block: '{chapter_title}'")
            continue

        deck_name = f"Pediatric Cardiology::{chapter_title}"

        if not llm_enabled or llm is None:
            # Offline path: generate 12 cloze cards from sentences
            sentences = _split_into_sentences(chapter_text)
            # Filter reasonable-length sentences
            sentences = [s for s in sentences if 40 <= len(s) <= 240]
            if not sentences:
                sentences = [chapter_text[:240]]
            num_cards = min(20, max(10, min(len(sentences), 15)))
            chosen = sentences[:num_cards]
            for s in chosen:
                cloze = _make_cloze(s)
                card = Card.cloze(
                    text=cloze,
                    extra="",
                    deck_id=deck_name,
                    source_id=chapter_title,
                    tags=["pediatric_cardiology"] + chapter_title.split("::"),
                )
                all_cards.append(card.to_dict())
            continue

        # LLM path
        final_prompt = f"""
        {prompt}

        **Chapter Title:** "{chapter_title}"
        
        **Chapter Content:**
        ---
        {chapter_text[:8000]}
        ---

        Generate 10-20 cloze deletion flashcards based on the key concepts and content.
        The output must be a valid JSON object with a single key "cards", 
        which is a list of objects. Each object should have "front" (the cloze text) 
        and "back" (any extra info). Do NOT include a "deck" field in the card objects.
        """

        response_text = llm.complete(
            system="You are a helpful assistant that generates structured JSON for Anki flashcards.",
            user=final_prompt,
        )
        try:
            generated_cards = json.loads(response_text).get("cards", [])
            for card_data in generated_cards:
                card = Card.cloze(
                    text=card_data["front"],
                    extra=card_data.get("back", ""),
                    deck_id=deck_name,
                    source_id=chapter_title,
                    tags=["pediatric_cardiology"] + chapter_title.split("::"),
                )
                all_cards.append(card.to_dict())
        except (json.JSONDecodeError, KeyError) as e:
            print(
                f"Warning: Could not parse cards for chapter '{chapter_title}'. Error: {e}. Response: {response_text}"
            )

    output_path = os.path.join(os.path.dirname(content_blocks), "cards.json")
    write_json(output_path, all_cards)
    return output_path


def assemble_deck(cards_path: str, deck_name: str, styling: dict = None) -> str:
    """Assemble the Anki deck(s) from generated cards."""
    cards_data = read_json(cards_path)

    # Group cards by deck_id to create subdecks
    decks: Dict[str, Deck] = {}
    for card_data in cards_data:
        deck_id = card_data.get("deck_id", deck_name)
        if deck_id not in decks:
            decks[deck_id] = Deck(id=deck_id, name=deck_id)

    packages: List[str] = []
    for deck_id, deck_obj in decks.items():
        builder = DeckBuilder(deck_obj, custom_styling=styling)
        deck_cards = [c for c in cards_data if c.get("deck_id") == deck_id]
        for c_data in deck_cards:
            builder.add_card(Card(**c_data))

        safe_deck_name = deck_id.replace("::", "_").replace(" ", "").replace("/", "_")
        output_path = os.path.join(os.path.dirname(cards_path), f"{safe_deck_name}.apkg")
        builder.save(output_path)
        packages.append(output_path)
        print(f"Saved deck to {output_path}")

    if not packages:
        raise ValueError("No decks were generated.")

    return packages[0]


def push_to_anki(apkg_path: str) -> str:
    """Push a generated .apkg file to Anki."""
    return import_package(apkg_path)

# --- Tool Mapping ---

agent_tools = {
    "FlashcardAgent": flashcard_agent,
    "assemble_deck": assemble_deck,
    "push_to_anki": push_to_anki,
}
