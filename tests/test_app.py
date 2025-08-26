import io

import pytest


class _Col:
    def __init__(self, name):
        self.name = name


class _Cols:
    def __init__(self, names):
        self.collections = [_Col(n) for n in names]


class FakePoint:
    def __init__(self, pid, vector, payload):
        self.id = pid
        self.vector = vector
        self.payload = payload


class FakeHit:
    def __init__(self, pid, score, payload):
        self.id = pid
        self.score = score
        self.payload = payload


class FakeQdrant:
    def __init__(self):
        self._cols = {}

    def get_collections(self):
        return _Cols(list(self._cols.keys()))

    def create_collection(self, collection_name, vectors_config):
        self._cols.setdefault(collection_name, [])

    def upsert(self, collection_name, points):
        self._cols.setdefault(collection_name, [])
        for p in points:
            self._cols[collection_name].append(FakePoint(p.id, p.vector, p.payload))

    def search(self, collection_name, query_vector, limit, query_filter=None):
        # naive score: count matching tokens in payload text
        items = self._cols.get(collection_name, [])
        hits = []
        for i, p in enumerate(items[: limit]):
            txt = (p.payload or {}).get("text", "")
            score = float(min(1.0, len(txt) / 1000.0))
            hits.append(FakeHit(p.id, score, p.payload))
        return hits

    def scroll(self, collection_name, scroll_filter=None, with_payload=True, with_vectors=False, limit=100, offset=None):
        items = self._cols.get(collection_name, [])
        return items[: limit], None


@pytest.fixture(autouse=True)
def _isolate_env(tmp_path, monkeypatch):
    # Isolate data directories for tests
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("QDRANT_PATH", str(tmp_path / "qdrant"))
    monkeypatch.setenv("USE_GPT_QA", "false")
    # Ensure modules pick up env
    yield


@pytest.fixture
def app_client(monkeypatch):
    # Patch embeddings and LLM
    from app import embeddings as emb_mod
    from app import llm as llm_mod
    from app import qdrant_store as qs

    def fake_embed_texts(texts, model=None):
        # return 3072-dim zero vectors
        return [[0.0] * 3072 for _ in texts]

    def fake_answer_from_context(question, context_chunks):
        return "Test answer"

    monkeypatch.setattr(emb_mod, "embed_texts", fake_embed_texts)
    monkeypatch.setattr(llm_mod, "answer_from_context", fake_answer_from_context)

    # Patch Qdrant client factory
    fake_client = FakeQdrant()
    monkeypatch.setattr(qs, "get_client", lambda: fake_client)

    # Build FastAPI test client
    from fastapi.testclient import TestClient

    from app.main import app
    return TestClient(app)


def test_chunking_basic():
    from app.chunking import auto_chunk_text
    text = "Python is a programming language. It is widely used." * 10
    chunks = auto_chunk_text(text)
    assert isinstance(chunks, list)
    assert chunks, "Expected non-empty chunks"


def test_flashcards_generation():
    from app.flashcards import generate_flashcards
    chunks = [
        "OpenAI develops AI models. GPT-4 is an example."
    ]
    notes = generate_flashcards(chunks)
    assert isinstance(notes, list)
    assert any(n.get("type") in {"cloze", "basic"} for n in notes)


def test_upload_search_answer_flow(app_client):
    # Upload a small text file
    content = b"This is a sample document. OpenAI builds models."
    files = {"files": ("sample.txt", io.BytesIO(content), "text/plain")}
    r = app_client.post("/api/upload", files=files, data={"title": "Test Deck"})
    assert r.status_code == 200, r.text
    up = r.json()
    assert up.get("deck_id") and up.get("deck_path")

    deck_id = up["deck_id"]

    # Search
    r = app_client.get("/api/search", params={"query": "OpenAI", "deck_id": deck_id})
    assert r.status_code == 200, r.text
    j = r.json()
    assert isinstance(j.get("results"), list)

    # Answer (with patched LLM)
    r = app_client.get("/api/answer", params={"query": "What is mentioned?", "deck_id": deck_id})
    assert r.status_code == 200, r.text
    a = r.json()
    assert "sources" in a
    # Since LLM is patched, answer should be deterministic
    assert a.get("answer") in {"", "Test answer"}


def test_static_ui_present(app_client):
    r = app_client.get("/")
    assert r.status_code == 200
    assert "Upload to Generate Anki Deck" in r.text
