from __future__ import annotations
from typing import List, Dict, Any
from openai import OpenAI
from . import config
import math

try:
    import tiktoken
except Exception:
    tiktoken = None


def get_client() -> OpenAI:
    if not config.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set")
    return OpenAI(api_key=config.OPENAI_API_KEY)


QA_SYSTEM_PROMPT = (
    "You are a helpful assistant that writes concise study flashcards. "
    "Given a text chunk, extract 1-3 high-yield Q/A pairs. "
    "Questions should be factual and answerable from the chunk alone. "
    "Answers should be brief (1-2 sentences). Return JSON with an array under 'cards'."
)


def generate_qa_from_chunks(chunks: List[str], max_cards_per_chunk: int = 2) -> List[Dict[str, Any]]:
    if not chunks:
        return []
    client = get_client()
    model = config.GPT_MODEL
    results: List[Dict[str, Any]] = []
    for ch in chunks:
        prompt = (
            f"Text:\n\n{ch}\n\n"
            f"Write up to {max_cards_per_chunk} Q/A pairs in JSON as {{'cards':[{{'q':'...','a':'...'}}]}}."
        )
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": QA_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            content = resp.choices[0].message.content or "{}"
        except Exception:
            # Skip gracefully on API errors
            content = "{}"
        try:
            import json as pyjson
            data = pyjson.loads(content)
            cards = data.get("cards") or []
            for c in cards:
                q = (c.get("q") or "").strip()
                a = (c.get("a") or "").strip()
                if q and a:
                    results.append({"type": "basic", "front": q, "back": a})
        except Exception:
            continue
    return results


ANSWER_SYSTEM_PROMPT = (
    "You are a helpful study assistant. Answer the question using ONLY the provided context. "
    "Cite sources inline as [1], [2], ... referring to the numbered context items. "
    "If the answer is not in the context, say you don't know. Be concise."
)


def _get_enc():
    if not tiktoken:
        return None
    try:
        return tiktoken.get_encoding("cl100k_base")
    except Exception:
        return None


def pack_context(chunks: List[str], max_tokens: int) -> List[str]:
    enc = _get_enc()
    packed: List[str] = []
    total = 0
    for ch in chunks:
        t = len(enc.encode(ch)) if enc else max(1, int(len(ch) / 4))
        if total + t > max_tokens and packed:
            break
        packed.append(ch)
        total += t
    return packed


def answer_from_context(question: str, context_chunks: List[str]) -> str:
    """Answer a question from context using GPT."""
    if not context_chunks:
        return "I don't know."
    client = get_client()
    max_ctx = config.RAG_MAX_CONTEXT_TOKENS
    ctx = pack_context(context_chunks, max_ctx)
    # Build numbered context block
    numbered = "\n\n".join([f"[{i+1}] {c}" for i, c in enumerate(ctx)])
    user = f"Context:\n{numbered}\n\nQuestion: {question}\nAnswer:"
    try:
        resp = client.chat.completions.create(
            model=config.GPT_MODEL,
            messages=[
                {"role": "system", "content": ANSWER_SYSTEM_PROMPT},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception:
        return "I don't know."
