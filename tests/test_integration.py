import os

from openeducation.cli import export, generate, index, ingest


def test_end_to_end(tmp_path):
    cfg = "examples/config_examples/config.json"
    ingest(cfg, out_dir=tmp_path)
    blocks_path = os.path.join(tmp_path, "content_blocks.json")
    index(blocks_path)
    generate(blocks_path, deck_id="deck_neuro", max_cards=10)
    cards_path = os.path.join(tmp_path, "cards.json")
    assert os.path.exists(cards_path)
    export(cards_path, deck_id="deck_neuro", name="TestDeck")
    apkg = os.path.join(tmp_path, "TestDeck.apkg")
    assert os.path.exists(apkg)
