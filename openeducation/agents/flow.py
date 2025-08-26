from __future__ import annotations

import asyncio
import json

from .tools import (
    assemble_deck,
    build_rag_index,
    generate_cards,
    ingest_sources,
    push_to_anki,
)


def safety_agent(content: str) -> bool:
    """Safety agent to check content appropriateness."""
    # Basic safety check - can be enhanced with actual AI
    unsafe_terms = ["violence", "harm", "illegal"]
    return not any(term in content.lower() for term in unsafe_terms)


def conductor_agent(cfg_json: str, push: bool = False) -> str:
    """Conductor agent that orchestrates the full pipeline."""
    try:
        cfg = json.loads(cfg_json)
        if not safety_agent(json.dumps(cfg)):
            return "Content failed safety check"

        # Step 1: Ingest sources
        blocks_path = ingest_sources(cfg)
        print(f"✓ Ingested sources: {blocks_path}")

        # Step 2: Build RAG index
        index_path = build_rag_index(blocks_path)
        print(f"✓ Built RAG index: {index_path}")

        # Step 3: Generate cards
        cards_path = generate_cards(blocks_path, cfg.get("deck", {}).get("id", "deck_main"))
        print(f"✓ Generated cards: {cards_path}")

        # Step 4: Assemble deck
        apkg_path = assemble_deck(
            cards_path,
            cfg.get("deck", {}).get("id", "deck_main"),
            cfg.get("deck", {}).get("name", "OpenEducation"),
        )
        print(f"✓ Assembled deck: {apkg_path}")

        # Step 5: Push to Anki (optional)
        if push:
            result = push_to_anki(apkg_path)
            print(f"✓ Pushed to Anki: {result}")
            return f"Pipeline completed successfully. {result}"

        return f"Pipeline completed successfully. Deck saved at: {apkg_path}"

    except Exception as e:
        return f"Pipeline failed: {str(e)}"


async def run_pipeline(cfg_json: str, push: bool = False) -> str:
    """Run the full pipeline asynchronously."""
    return await asyncio.get_event_loop().run_in_executor(None, conductor_agent, cfg_json, push)
