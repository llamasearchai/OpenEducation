import os

import genanki
from typing import List
from ..models.card import Card
from ..models.deck import Deck


class DeckBuilder:
    def __init__(self, deck: Deck):
        self.deck = deck
        self._model = genanki.Model(
            deck.model_id,
            "OpenEducation Basic",
            fields=[{"name": "Front"}, {"name": "Back"}, {"name": "Tags"}],
            templates=[
                {
                    "name": "Card 1",
                    "qfmt": "{{Front}}",
                    "afmt": '{{FrontSide}}<hr id="answer">{{Back}}',
                }
            ],
            css=".card { font-family: -apple-system, Helvetica, Arial; font-size: 18px; }",
        )
        self._genanki_deck = genanki.Deck(deck.deck_id_int, deck.name, deck.description)
        self._media: List[str] = []

    def add_card(self, card: Card) -> None:
        note = genanki.Note(model=self._model, fields=[card.front, card.back, " ".join(card.tags)])
        self._genanki_deck.add_note(note)
        for m in card.media:
            if os.path.exists(m):
                self._media.append(m)

    def save(self, apkg_path: str) -> None:
        pkg = genanki.Package(self._genanki_deck)
        if self._media:
            pkg.media_files = self._media
        pkg.write_to_file(apkg_path)
