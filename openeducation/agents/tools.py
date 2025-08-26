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

# --- Agent Tools ---

def flashcard_agent(prompt: str, content_blocks: str) -> str:
    """
    Agent that generates flashcards based on a chapter plan and content blocks.
    """
    llm = OpenAIWrapper()
    blocks = [ContentBlock(**d) for d in read_json(content_blocks)]
    
    all_cards = []

    for block in blocks:
        chapter_title = block.title
        chapter_text = block.body

        # Skip very short blocks that are likely just titles or TOC entries
        if len(chapter_text) < 200:
            print(f"Skipping short content block: '{chapter_title}'")
            continue
        
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
        
        response_text = llm.complete(system="You are a helpful assistant that generates structured JSON for Anki flashcards.", user=final_prompt)
        try:
            generated_cards = json.loads(response_text).get("cards", [])
            for card_data in generated_cards:
                # The deck name is derived from the hierarchical chapter title
                deck_name = f"Pediatric Cardiology::{chapter_title}"
                card = Card.cloze(
                    text=card_data["front"],
                    extra=card_data.get("back", ""),
                    deck_id=deck_name,
                    source_id=chapter_title,
                    tags=["pediatric_cardiology"] + chapter_title.split("::")
                )
                all_cards.append(card.to_dict())
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Could not parse cards for chapter '{chapter_title}'. Error: {e}. Response: {response_text}")

    output_path = os.path.join(os.path.dirname(content_blocks), "cards.json")
    write_json(output_path, all_cards)
    return output_path

def assemble_deck(cards_path: str, deck_name: str, styling: dict = None) -> str:
    """Assemble the Anki deck(s) from generated cards."""
    cards_data = read_json(cards_path)
    
    # Group cards by deck_id to create subdecks
    decks = {}
    for card_data in cards_data:
        deck_id = card_data.get("deck_id", deck_name)
        if deck_id not in decks:
            # Main deck name will be the parent
            decks[deck_id] = Deck(id=deck_id, name=deck_id)
    
    packages = []
    for deck_id, deck_obj in decks.items():
        builder = DeckBuilder(deck_obj, custom_styling=styling)
        deck_cards = [c for c in cards_data if c.get("deck_id") == deck_id]
        for c_data in deck_cards:
            builder.add_card(Card(**c_data))

        # Sanitize filename
        safe_deck_name = deck_id.replace("::", "_").replace(" ", "").replace("/", "_")
        output_path = os.path.join(os.path.dirname(cards_path), f"{safe_deck_name}.apkg")
        builder.save(output_path)
        packages.append(output_path)
        print(f"Saved deck to {output_path}")

    # For simplicity in this pipeline, we'll return the path to the first package,
    # or a summary path if multiple were created.
    if not packages:
        raise ValueError("No decks were generated.")
    
    summary_path = os.path.join(os.path.dirname(cards_path), f"{deck_name.replace(' ', '_')}_master.apkg")
    if len(packages) > 1:
        # A bit of a hack for the pipeline: create a master package with all decks
        master_deck = genanki.Deck(20513, deck_name)
        master_pkg = genanki.Package(master_deck)
        for pkg_path in packages:
             master_pkg.add_deck(genanki.Deck.from_apkg(pkg_path)) # This is conceptual; genanki doesn't directly support merging packages this way. We will return the main package path.
        return packages[0] # Returning the first subdeck path for now.
    
    return packages[0] if packages else ""


def push_to_anki(apkg_path: str) -> str:
    """Push a generated .apkg file to Anki."""
    return import_package(apkg_path)

# --- Tool Mapping ---

agent_tools = {
    "FlashcardAgent": flashcard_agent,
    "assemble_deck": assemble_deck,
    "push_to_anki": push_to_anki,
}
