import os
from typing import List

import genanki

from ..models.card import Card, CardType
from ..models.deck import Deck


class DeckBuilder:
    def __init__(self, deck: Deck, custom_styling: dict = None):
        self.deck = deck
        
        # Default CSS
        css = ".card { font-family: -apple-system, Helvetica, Arial; font-size: 18px; }"
        if custom_styling and "css" in custom_styling:
            css = custom_styling["css"]

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
            css=css,
        )

        self._cloze_model = genanki.Model(
            deck.model_id + 1, # Ensure unique model ID
            "OpenEducation Cloze",
            fields=[{"name": "Text"}, {"name": "Back Extra"}, {"name": "Tags"}],
            templates=[
                {
                    "name": "Cloze Card",
                    "qfmt": "{{cloze:Text}}",
                    "afmt": "{{cloze:Text}}<br><br>{{Back Extra}}",
                }
            ],
            css=css,
            model_type=genanki.Model.CLOZE,
        )

        self._genanki_deck = genanki.Deck(deck.deck_id_int, deck.name, deck.description)
        self._media: List[str] = []

    def add_card(self, card: Card) -> None:
        if card.card_type == CardType.CLOZE:
            note = genanki.Note(
                model=self._cloze_model,
                fields=[card.front, card.back, " ".join(card.tags)]
            )
        else: # Basic card
            note = genanki.Note(
                model=self._model,
                fields=[card.front, card.back, " ".join(card.tags)]
            )
            
        self._genanki_deck.add_note(note)
        for m in card.media:
            if os.path.exists(m):
                self._media.append(m)

    def save(self, apkg_path: str) -> None:
        pkg = genanki.Package(self._genanki_deck)
        if self._media:
            pkg.media_files = self._media
        pkg.write_to_file(apkg_path)
