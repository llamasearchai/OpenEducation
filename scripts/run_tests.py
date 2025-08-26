#!/usr/bin/env python3
"""
Lightweight test runner for environments without pytest.
Runs the repository's core and integration tests and exits non-zero on failure.
"""
from __future__ import annotations

import pathlib
import sys
import tempfile


def main() -> int:
    try:
        from tests.test_core import test_block_and_cards
        from tests.test_integration import test_end_to_end
    except Exception as exc:
        print(f"Failed to import tests: {exc}")
        return 1

    print("Running unit test: test_block_and_cards")
    test_block_and_cards()
    print("Passed: test_block_and_cards")

    print("Running integration test: test_end_to_end")
    class TmpPath(pathlib.Path):
        _flavour = pathlib._windows_flavour if pathlib.os.name == 'nt' else pathlib._posix_flavour

    with tempfile.TemporaryDirectory() as td:
        test_end_to_end(TmpPath(td))
    print("Passed: test_end_to_end")
    return 0


if __name__ == "__main__":
    sys.exit(main())

