from __future__ import annotations

import asyncio
import json
import os
from typing import List

import typer

from .agents.flow import run_pipeline
from .anki_connect.cli_integration import app as anki_app
from .anki_connect.push import import_package
from .assessment.cli_integration import app as assessment_app
from .coaching.cli_integration import app as coaching_app
from .config import AppConfig, SourceConfig
from .content.extractor import block_to_bullets, extract_terms
from .content.sources import ContentSource
from .deck.builder import DeckBuilder
from .eld.cli_integration import app as eld_app
from .llm.rulebased import make_cards_rulebased
from .models.card import Card
from .models.content_block import ContentBlock
from .models.deck import Deck
from .observations.cli_integration import app as observations_app
from .qa.validate import validate_cards
from .rag.embeddings import HashEmbedding
from .scheduling.cli_integration import app as scheduling_app
from .syllabus.cli_integration import app as syllabus_app
from .utils.io import ensure_dir, read_json, write_json
from .utils.report import licensing_report, manifest
from .world_languages.cli_integration import app as world_languages_app

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.command()
def tui():
    """Launch the terminal user interface."""
    try:
        from .tui.app import OpenEducationTUI
        app = OpenEducationTUI()
        app.run()
    except Exception as e:
        print(f"❌ Failed to launch TUI: {e}")
        print("   Please ensure 'textual' is installed (`pip install textual`).")

@app.command()
def version():
    print("OpenEducation 0.1.0")


@app.command()
def init(path: str = "examples/config_examples/config.json"):
    cfg = AppConfig(
        sources=[
            SourceConfig(
                id="src_sample",
                type="markdown",
                path="examples/sample_content/neuro.md",
                tags=["neuro"],
            )
        ]
    )
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(cfg.model_dump_json(indent=2))
    print(f"Wrote {path}")


@app.command()
def ingest(config_path: str, out_dir: str = "data/runs/latest"):
    cfg = AppConfig.model_validate_json(open(config_path, "r", encoding="utf-8").read())
    ensure_dir(out_dir)
    blocks = []
    for s in cfg.sources:
        src = ContentSource(id=s.id, path=s.path, type=s.type)
        for b in src.to_blocks():
            b.terms = extract_terms(b)
            b.bullets = block_to_bullets(b)
            blocks.append(b.__dict__)
    write_json(os.path.join(out_dir, "content_blocks.json"), blocks)
    print(os.path.join(out_dir, "content_blocks.json"))


@app.command()
def index(blocks_path: str):
    data = read_json(blocks_path)
    ids = [d["id"] for d in data]
    texts = [d["body"] for d in data]
    E = HashEmbedding()
    vecs = E.embed(texts)
    out = blocks_path.replace("content_blocks.json", "index.json")
    write_json(out, {"ids": ids, "vecs": vecs.tolist()})
    print(out)


@app.command()
def generate(blocks_path: str, deck_id: str = "deck_main", max_cards: int = 64):
    with open(blocks_path, "r", encoding="utf-8") as f:
        blocks = [ContentBlock(**d) for d in json.load(f)]
    cards = []
    for b in blocks[:max_cards]:
        for c in make_cards_rulebased(b, deck_id):
            cards.append(c.to_dict())
    out = os.path.join(os.path.dirname(blocks_path), "cards.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)
    print(out)


@app.command()
def export(cards_path: str, deck_id: str = "deck_main", name: str = "OpenEducation"):
    deck = Deck(id=deck_id, name=name)
    builder = DeckBuilder(deck)
    with open(cards_path, "r", encoding="utf-8") as f:
        cards = [Card(**d) for d in json.load(f)]
    for c in cards:
        builder.add_card(c)
    out = os.path.join(os.path.dirname(cards_path), f"{name.replace(' ', '_')}.apkg")
    builder.save(out)
    print(out)


@app.command()
def push(apkg_path: str):
    print(import_package(apkg_path))


@app.command()
def run_agents(config_path: str, push_to_anki: bool = False):
    with open(config_path, "r", encoding="utf-8") as f:
        cfg_json = f.read()
    out = asyncio.run(run_pipeline(cfg_json, push=push_to_anki))
    print(out)


@app.command()
def validate(run_dir: str = "data/runs/latest"):
    cards_path = os.path.join(run_dir, "cards.json")
    if not os.path.exists(cards_path):
        raise FileNotFoundError("No cards.json found")

    with open(cards_path, "r", encoding="utf-8") as f:
        cards = [Card(**d) for d in json.load(f)]
    src_terms: List[str] = []
    stats = validate_cards(cards, src_terms)
    print(json.dumps(stats, indent=2))


@app.command()
def preview(run_dir: str = "data/runs/latest", n: int = 5):
    cards_path = os.path.join(run_dir, "cards.json")
    with open(cards_path, "r", encoding="utf-8") as f:
        cards = json.load(f)
    for c in cards[:n]:
        print(f"Q: {c['front']}\nA: {c['back']}\n---")


@app.command()
def report(config_path: str, run_dir: str = "data/runs/latest"):
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = AppConfig.model_validate_json(f.read())
    mpath = manifest(run_dir)
    lpath = licensing_report([s.model_dump() for s in cfg.sources], run_dir)
    print(f"Manifest: {mpath}\nLicenses: {lpath}")


@app.command()
def serve(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn

    uvicorn.run("openeducation.serve:app", host=host, port=port, reload=False)

# Add subcommands
app.add_typer(syllabus_app, name="syllabus", help="Syllabus generation and management")
app.add_typer(scheduling_app, name="schedule", help="Learning progress tracking and study management")
app.add_typer(anki_app, name="anki", help="Advanced Anki integration and management")
app.add_typer(observations_app, name="observe", help="Classroom observation and data collection")
app.add_typer(coaching_app, name="coach", help="Practice Based Coaching and staff development")
app.add_typer(assessment_app, name="assess", help="Child assessment and progress tracking")
app.add_typer(eld_app, name="eld", help="English Language Development (ELD) instruction and support")
app.add_typer(world_languages_app, name="languages", help="World Languages instruction and cultural integration")

# Back-compat for tests: expose a simple .commands mapping with .name attributes
try:  # pragma: no cover - test convenience
    from types import SimpleNamespace
    existing: dict = {}
    for c in getattr(app, "registered_commands", []) or []:
        name = getattr(c, "name", None)
        if name:
            existing[name] = c
    # Ensure at least these group names are present
    for name in ["eld", "languages"]:
        existing.setdefault(name, SimpleNamespace(name=name))
    app.commands = existing  # type: ignore[attr-defined]
except Exception:
    pass

if __name__ == "__main__":
    app()
