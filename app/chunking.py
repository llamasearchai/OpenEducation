from __future__ import annotations

from typing import List
from . import config
import re
import hashlib

try:
    import tiktoken
except Exception:  # pragma: no cover
    tiktoken = None


def split_sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip() for p in parts if p and p.strip()]


def _get_tokenizer():
    if tiktoken is None:
        return None
    try:
        return tiktoken.get_encoding("cl100k_base")
    except Exception:
        return None


def count_tokens(text: str) -> int:
    enc = _get_tokenizer()
    if not enc:
        # cheap fallback estimate ~4 chars/token
        return max(1, int(len(text) / 4))
    return len(enc.encode(text))


def chunk_text_tokens(text: str, max_tokens: int | None = None, overlap_tokens: int | None = None) -> List[str]:
    max_tokens = max_tokens or config.MAX_CHUNK_TOKENS
    overlap_tokens = overlap_tokens or config.OVERLAP_TOKENS
    enc = _get_tokenizer()
    if not enc:
        # Fallback to char-based chunking with rough sizes
        approx_chars = max_tokens * 4
        approx_overlap = overlap_tokens * 4
        return chunk_text_chars(text, approx_chars, approx_overlap)

    toks = enc.encode(text)
    chunks = []
    i = 0
    n = len(toks)
    while i < n:
        j = min(i + max_tokens, n)
        chunk = enc.decode(toks[i:j])
        chunks.append(chunk)
        if j == n:
            break
        i = max(0, j - overlap_tokens)
    return chunks


def chunk_text_chars(text: str, chunk_size: int | None = None, overlap: int | None = None) -> List[str]:
    chunk_size = chunk_size or config.CHUNK_SIZE_CHARS
    overlap = overlap or config.CHUNK_OVERLAP_CHARS
    if len(text) <= chunk_size:
        return [text]
    chunks: List[str] = []
    i = 0
    n = len(text)
    while i < n:
        j = min(i + chunk_size, n)
        chunks.append(text[i:j])
        if j == n:
            break
        i = max(0, j - overlap)
    return chunks


def auto_chunk_text(text: str) -> List[str]:
    # Prefer token-based chunking; fall back to chars
    chunks = chunk_text_tokens(text)
    # Basic deduping of near-identical chunks
    seen = set()
    unique = []
    for ch in chunks:
        key = hashlib.md5(ch.strip().encode("utf-8")).hexdigest()
        if key not in seen and len(ch.strip()) > 10:
            seen.add(key)
            unique.append(ch)
    return unique


def chunk_with_overrides(texts: List[str],
                         max_tokens: int | None = None,
                         overlap_tokens: int | None = None,
                         char_size: int | None = None,
                         char_overlap: int | None = None) -> List[str]:
    chunks: List[str] = []
    if max_tokens or overlap_tokens:
        mt = max_tokens or config.MAX_CHUNK_TOKENS
        ot = overlap_tokens or config.OVERLAP_TOKENS
        for t in texts:
            chunks.extend(chunk_text_tokens(t, mt, ot))
    elif char_size or char_overlap:
        cs = char_size or config.CHUNK_SIZE_CHARS
        co = char_overlap or config.CHUNK_OVERLAP_CHARS
        for t in texts:
            chunks.extend(chunk_text_chars(t, cs, co))
    else:
        for t in texts:
            chunks.extend(auto_chunk_text(t))
    # dedupe
    seen = set()
    uniq = []
    for ch in chunks:
        key = hashlib.md5(ch.strip().encode("utf-8")).hexdigest()
        if key not in seen and len(ch.strip()) > 10:
            seen.add(key)
            uniq.append(ch)
    return uniq
