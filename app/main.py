from __future__ import annotations
import uuid
from pathlib import Path
from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from . import config
from .extract import extract_text
from .chunking import auto_chunk_text, chunk_with_overrides
from .embeddings import embed_texts
from .qdrant_store import upsert_vectors, ensure_collection, deck_filter
from .flashcards import generate_flashcards
from .anki_export import build_deck
from .models import UploadResponse, HealthResponse, DeckListResponse, DeckMeta
from .llm import generate_qa_from_chunks, answer_from_context
from .catalog import add_deck, list_decks, get_deck


app = FastAPI(title="OpenEducation Embeddings + Qdrant + Anki")


# Static frontend
static_dir = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
def index():
    return (static_dir / "index.html").read_text(encoding="utf-8")


@app.get("/api/health", response_model=HealthResponse)
def health():
    try:
        ensure_collection()
        return HealthResponse(status="ok")
    except Exception as e:
        return HealthResponse(status=f"error: {e}")


@app.post("/api/upload", response_model=UploadResponse)
async def upload(
    files: List[UploadFile] = File(...),
    title: str = Form(""),
    max_tokens: int | None = Form(None),
    overlap_tokens: int | None = Form(None),
    char_size: int | None = Form(None),
    char_overlap: int | None = Form(None),
    collection: str | None = Form(None),
):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    # Save uploads and extract text
    texts: List[str] = []
    for f in files:
        dest = Path(config.UPLOADS_DIR) / f.filename
        data = await f.read()
        dest.write_bytes(data)
        text, _ = extract_text(dest)
        if text:
            texts.append(text)

    if not texts:
        raise HTTPException(status_code=400, detail="No text could be extracted")

    # Chunking (token-aware with auto-config)
    chunks: List[str] = chunk_with_overrides(
        texts,
        max_tokens=max_tokens,
        overlap_tokens=overlap_tokens,
        char_size=char_size,
        char_overlap=char_overlap,
    )

    if not chunks:
        raise HTTPException(status_code=400, detail="No chunks produced from text")

    # Embeddings
    vectors = embed_texts(chunks)

    # Upsert to Qdrant (tag with deck_id)
    deck_title = title.strip() or "Uploaded Deck"
    # generate a deck_id now so we can tag vectors
    job_id = str(uuid.uuid4())
    deck_id = job_id.split("-")[0]
    payloads = [{"type": "chunk", "text": ch, "deck_id": deck_id} for ch in chunks]
    upsert_vectors(vectors, payloads, collection=(collection or None) or config.QDRANT_COLLECTION)

    # Flashcards (heuristics)
    notes = generate_flashcards(chunks)
    # Optional GPT-powered Q/A for richer notes
    if config.USE_GPT_QA:
        gpt_notes = generate_qa_from_chunks(chunks[:10], max_cards_per_chunk=2)
        notes.extend(gpt_notes)
        # Dedupe by front/text
        seen = set()
        deduped = []
        for n in notes:
            key = n.get("text") or n.get("front")
            if key and key not in seen:
                seen.add(key)
                deduped.append(n)
        notes = deduped
    if not notes:
        # create at least some basics from first few chunks
        for ch in chunks[:5]:
            if len(ch) > 40:
                notes.append({"type": "basic", "front": ch[:100] + "…", "back": ch})
    apkg_path = build_deck(deck_title, notes, file_id=deck_id)
    # Save catalog entry
    add_deck(deck_id, deck_title, len(notes))
    return UploadResponse(job_id=job_id, deck_path=f"/api/decks/{deck_id}", deck_id=deck_id, notes=len(notes), title=deck_title)


@app.get("/api/decks/{deck_id}")
def get_deck(deck_id: str):
    apkg_path = Path(config.DECKS_DIR) / f"{deck_id}.apkg"
    if not apkg_path.exists():
        raise HTTPException(status_code=404, detail="Deck not found")
    return FileResponse(str(apkg_path), media_type="application/apkg", filename=f"{deck_id}.apkg")


@app.get("/api/search")
def search(query: str, k: int = 5, deck_id: str | None = None, collection: str | None = None):
    if not query:
        raise HTTPException(status_code=400, detail="Missing query")
    qvec = embed_texts([query])[0]
    from .qdrant_store import search_similar
    from .qdrant_store import search_similar
    qfilter = deck_filter(deck_id) if deck_id else None
    results = search_similar(qvec, limit=k, filter=qfilter, collection=(collection or None) or config.QDRANT_COLLECTION)
    hits = [
        {
            "id": str(r.id),
            "score": r.score,
            "text": (r.payload or {}).get("text", ""),
        }
        for r in results
    ]
    return {"query": query, "results": hits}


@app.get("/api/answer")
def answer(query: str = Query(..., min_length=2), k: int = Query(None), max_ctx: int | None = None, deck_id: str | None = None, sources_only: bool = False, collection: str | None = None):
    if not query:
        raise HTTPException(status_code=400, detail="Missing query")
    topk = k or config.RAG_K
    qvec = embed_texts([query])[0]
    from .qdrant_store import search_similar
    qfilter = deck_filter(deck_id) if deck_id else None
    results = search_similar(qvec, limit=topk, filter=qfilter, collection=(collection or None) or config.QDRANT_COLLECTION)
    contexts = []
    sources = []
    for i, r in enumerate(results):
        txt = (r.payload or {}).get("text", "")
        contexts.append(txt)
        sources.append({"id": str(r.id), "score": r.score, "index": i + 1, "text": txt})
    if sources_only or not config.EXPOSE_ASK:
        return {"answer": "", "sources": sources}
    # Override context budget if provided
    if max_ctx is not None:
        from . import llm as llm_mod
        old = llm_mod.config.RAG_MAX_CONTEXT_TOKENS
        llm_mod.config.RAG_MAX_CONTEXT_TOKENS = max(200, int(max_ctx))
        ans = answer_from_context(query, contexts)
        llm_mod.config.RAG_MAX_CONTEXT_TOKENS = old
    else:
        ans = answer_from_context(query, contexts)
    return {"answer": ans, "sources": sources}


@app.get("/api/config")
def get_config():
    return {
        "use_gpt_qa": config.USE_GPT_QA,
        "expose_ask": config.EXPOSE_ASK,
        "embedding_model": config.EMBEDDING_MODEL,
        "qdrant": {
            "url": bool(config.QDRANT_URL),
            "collection": config.QDRANT_COLLECTION,
        },
    }


@app.get("/api/decks/{deck_id}/sources")
def deck_sources(deck_id: str, fmt: str = "json", collection: str | None = None):
    from .qdrant_store import scroll_all_by_deck
    items = scroll_all_by_deck(deck_id, collection=(collection or None) or config.QDRANT_COLLECTION)
    rows = []
    for p in items:
        payload = p.payload or {}
        rows.append({"id": str(p.id), "deck_id": payload.get("deck_id"), "text": payload.get("text", "")})
    if fmt == "csv":
        import io, csv
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=["id", "deck_id", "text"])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(buf.getvalue(), media_type="text/csv")
    return {"deck_id": deck_id, "count": len(rows), "items": rows}


@app.get("/api/decks", response_model=DeckListResponse)
def decks():
    items = [DeckMeta(**d) for d in list_decks()]
    return DeckListResponse(decks=items)


@app.get("/api/decks/{deck_id}/meta", response_model=DeckMeta)
def deck_meta(deck_id: str):
    d = get_deck(deck_id)
    if not d:
        raise HTTPException(status_code=404, detail="Deck not found")
    return DeckMeta(**d)
