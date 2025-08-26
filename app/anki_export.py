from __future__ import annotations
from typing import List, Dict, Any
import genanki
import os
import uuid
from .config import DECKS_DIR


CLOZE_MODEL = genanki.Model(
    1607392319,
    'Cloze (OpenEducation)',
    fields=[{"name": "Text"}, {"name": "Extra"}],
    templates=[
        {
            "name": "Cloze Card",
            "qfmt": "{{cloze:Text}}",
            "afmt": "{{cloze:Text}}<br><br><div class=\"extra\">{{Extra}}</div>",
        }
    ],
    model_type=genanki.Model.CLOZE,
    css='''
    .card { font-family: "OpenAI Sans", Inter, Arial, sans-serif; font-size: 18px; color: #222; }
    .extra { opacity: .8; margin-top: 8px; }
    '''
)

BASIC_MODEL = genanki.Model(
    1091735104,
    'Basic (OpenEducation)',
    fields=[{"name": "Front"}, {"name": "Back"}],
    templates=[
        {
            "name": "Card 1",
            "qfmt": "{{Front}}",
            "afmt": "{{Front}}<hr id=answer>{{Back}}",
        }
    ],
    css='''
    .card { font-family: "OpenAI Sans", Inter, Arial, sans-serif; font-size: 18px; color: #222; }
    '''
)


def build_deck(title: str, notes: List[Dict[str, Any]], file_id: str | None = None) -> str:
    deck_id = int(uuid.uuid4().int % (10**10))
    deck = genanki.Deck(deck_id, title)

    for n in notes:
        if n.get("type") == "cloze":
            note = genanki.Note(model=CLOZE_MODEL, fields=[n.get("text", ""), n.get("extra", "")])
        else:
            note = genanki.Note(model=BASIC_MODEL, fields=[n.get("front", ""), n.get("back", "")])
        deck.add_note(note)

    os.makedirs(DECKS_DIR, exist_ok=True)
    fname = f"{file_id}.apkg" if file_id else f"{deck_id}.apkg"
    apkg_path = os.path.join(DECKS_DIR, fname)
    genanki.Package(deck).write_to_file(apkg_path)
    return apkg_path
