# Changelog

All notable changes to this project will be documented here.

## [1.0.1] - 2025-08-26
### Added
- CLI console script entrypoint (`openeducation`) via `pyproject.toml`.
- Dev tooling and configs: Ruff, Mypy, Tox, Hatch; CI runs lint + types + tests.
- Makefile targets: `venv`, `install`, `lint`, `types`, `test`.
- README developer setup with uv/Hatch/Tox/Make workflows.

### Changed
- General test hardening; full suite now green locally (47 tests).
- Improved ELD lesson vocabulary extraction with fallback heuristics.
- Default `created_by` for world languages curricula set to `curriculum_system`.

### Fixed
- `ContentBlock.from_text` API compatibility across call sites and tests.
- Rule-based card generation crash (`block.metadata` → use actual fields).
- FastAPI type annotations compatibility for Python 3.9 (Optional syntax).
- Requirements: use `python-dotenv`; add `numpy` and `typer`; dedupe `pypdf`.
- Duplicate imports and minor cleanup.

## [0.1.0-beta.1] - YYYY-MM-DD
### Added
- Initial public BETA: Embeddings + Qdrant + Anki deck export + RAG answering
- UI with OpenAI Sans; upload, search, Ask panels
- Dockerfile and Docker Compose; local or remote Qdrant
- CI workflows (syntax, compose health, secrets scan) and Release prerelease
- Publishing docs, PR/issue templates, MIT license

### Security
- Git-ignored secrets and data paths; secret scanner script and workflow

### Notes
- This is a BETA release. APIs and UI may change.
