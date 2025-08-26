from __future__ import annotations

import re
from typing import Any, Dict, List


def find_candidates(text: str) -> List[str]:
    # Heuristic entity/term candidates: Proper Nouns, ALLCAPS, numbers with units
    caps = re.findall(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b", text)
    acr = re.findall(r"\b([A-Z]{2,}(?:-[A-Z]{2,})*)\b", text)
    nums = re.findall(r"\b(\d+(?:\.\d+)?\s?(?:%|[A-Za-z]{1,4}))\b", text)
    terms = list(dict.fromkeys([*caps, *acr, *nums]))  # dedupe, keep order
    # filter too-short/boring tokens
    return [t for t in terms if len(t) >= 3 and not t.isdigit()]


def make_cloze(sentence: str, start_index: int = 1, max_clozes: int = 2) -> tuple[str, int]:
    """Return (cloze_text, next_index). Replaces up to max_clozes terms with cN."""
    cands = find_candidates(sentence)
    idx = start_index
    used = set()
    text = sentence
    for term in cands:
        if idx - start_index >= max_clozes:
            break
        if term in used:
            continue
        # Word-boundary replacement, first occurrence only
        pattern = re.compile(rf"\b{re.escape(term)}\b")
        if pattern.search(text):
            text = pattern.sub(f"{{{{c{idx}::{term}}}}}", text, count=1)
            used.add(term)
            idx += 1
    return text, idx


def generate_cloze_notes(chunks: List[str]) -> List[Dict[str, Any]]:
    notes = []
    cloze_idx = 1
    for ch in chunks:
        # split into sentences; create cloze from 1-2 best sentences
        sents = re.split(r"(?<=[.!?])\s+", ch)
        for s in sents[:2]:
            s = s.strip()
            if len(s) < 40:
                continue
            cloze, cloze_idx = make_cloze(s, cloze_idx)
            if "{{c" in cloze:
                notes.append({"type": "cloze", "text": cloze, "extra": ""})
    return notes


def generate_basic_qa_notes(chunks: List[str]) -> List[Dict[str, Any]]:
    notes = []
    for ch in chunks:
        # definition pattern: Term: definition
        for line in ch.splitlines():
            line = line.strip()
            if ":" in line and len(line) > 20 and len(line.split(":")) >= 2:
                term, rest = line.split(":", 1)
                if 3 <= len(term) <= 80 and len(rest) >= 10:
                    notes.append({"type": "basic", "front": term.strip(), "back": rest.strip()})
        # Q pattern: lines starting with Q/A
        for line in ch.splitlines():
            if line.lower().startswith("q:") and "a:" in ch.lower():
                # crude capture; skip overcomplication
                pass
    return notes


def generate_flashcards(chunks: List[str]) -> List[Dict[str, Any]]:
    # Merge multiple generators and dedupe by text/front
    notes = []
    seen = set()
    for n in generate_cloze_notes(chunks) + generate_basic_qa_notes(chunks):
        key = n.get("text") or n.get("front")
        if key and key not in seen:
            seen.add(key)
            notes.append(n)
    # Fallback: ensure at least one basic note for short inputs
    if not notes and chunks:
        sample = chunks[0].strip()
        if len(sample) > 10:
            front = sample.split(". ")[0][:100]
            notes.append({"type": "basic", "front": front, "back": sample})
    return notes
