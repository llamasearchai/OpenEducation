#!/usr/bin/env python3
"""Quick-and-dirty secret scan.

Looks for common API key patterns and prints any suspicious hits.
Returns non-zero if any suspected secret is found.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PATTERNS = [
    ("OpenAI sk-", re.compile(r"sk-[A-Za-z0-9]{20,}")),
    ("AWS", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("Generic API key", re.compile(r"api[_-]?key\s*[:=]\s*['\"][A-Za-z0-9_-]{16,}['\"]", re.I)),
]

IGNORE_DIRS = {".git", ".venv", "venv", "node_modules", "qdrant_data", "data", ".mypy_cache", "__pycache__"}
IGNORE_FILES = {"requirements.txt", ".env.example"}


def should_skip(path: Path) -> bool:
    for part in path.parts:
        if part in IGNORE_DIRS:
            return True
    return path.name in IGNORE_FILES


def main() -> int:
    hits = []
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if should_skip(p):
            continue
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for name, rx in PATTERNS:
            for m in rx.finditer(txt):
                line_num = txt[: m.start()].count("\n") + 1
                hits.append((name, p, line_num))
    if hits:
        print("Potential secrets found:")
        for name, p, ln in hits:
            print(f"- {name}: {p} (line {ln})")
        return 1
    else:
        print("No obvious secrets detected.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
