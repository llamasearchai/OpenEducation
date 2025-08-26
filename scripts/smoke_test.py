#!/usr/bin/env python3
"""
Simple smoke test for the OpenEducation app.

Usage:
  python scripts/smoke_test.py [--base http://localhost:8000]

Requires the server to be running and OPENAI_API_KEY configured.
"""

import argparse
import sys

import httpx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:8000")
    args = ap.parse_args()
    base = args.base.rstrip("/")

    def url(p):
        return f"{base}{p}"

    print("[1] Health check…", flush=True)
    r = httpx.get(url("/api/health"), timeout=30)
    r.raise_for_status()
    print("    ", r.json())

    print("[2] Upload sample text…", flush=True)
    sample = b"""Sample Notes\n\nPython is a high-level programming language.\nOpenAI develops AI models like GPT.\nIn 2024, text-embedding-3-large has 3072 dimensions.\n"""
    files = [("files", ("sample.txt", sample, "text/plain"))]
    data = {"title": "Smoke Test Deck"}
    r = httpx.post(url("/api/upload"), files=files, data=data, timeout=120)
    r.raise_for_status()
    up = r.json()
    print("    ", up)
    deck_id = up.get("deck_id")
    assert deck_id, "No deck_id returned"

    print("[3] Search…", flush=True)
    r = httpx.get(url("/api/search"), params={"query": "What is OpenAI?", "k": 3, "deck_id": deck_id}, timeout=60)
    r.raise_for_status()
    print("    results:", len(r.json().get("results", [])))

    print("[4] Answer…", flush=True)
    r = httpx.get(url("/api/answer"), params={"query": "What is Python?", "k": 3, "deck_id": deck_id}, timeout=120)
    r.raise_for_status()
    ans = r.json()
    print("    answer:", (ans.get("answer") or "").strip()[:160])
    print("    sources:", len(ans.get("sources", [])))

    print("[5] Export sources (JSON)…", flush=True)
    r = httpx.get(url(f"/api/decks/{deck_id}/sources"), params={"fmt": "json"}, timeout=60)
    r.raise_for_status()
    data = r.json()
    print("    items:", data.get("count"))

    print("[6] Download deck…", flush=True)
    r = httpx.get(url(f"/api/decks/{deck_id}"), timeout=60)
    r.raise_for_status()
    print("    ", "apkg bytes:", len(r.content))

    print("OK — smoke test completed.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Smoke test failed:", repr(e))
        sys.exit(1)
