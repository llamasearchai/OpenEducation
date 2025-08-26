from openeducation.llm.rulebased import make_cards_rulebased
from openeducation.models.content_block import ContentBlock


def test_block_and_cards():
    b = ContentBlock.from_text("Title", "This is a test block. It has several sentences.", "src1")
    cards = make_cards_rulebased(b, deck_id="d1")
    assert len(cards) >= 1
    assert cards[0].front
    assert cards[0].back
