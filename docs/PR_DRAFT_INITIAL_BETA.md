# PR: Initial Public BETA Release

## Summary
- Introduces end-to-end pipeline: Upload → Extract → Chunk → Embed → Store → Flashcards → Anki export
- Adds semantic search and RAG answering with deck scoping and citations
- Provides Docker/Compose, CI (syntax, compose health, secrets scan), and prerelease workflow

## Features
- Embeddings: OpenAI `text-embedding-3-large` (3072 dims)
- Vector DB: Qdrant (embedded or remote), deck-tagged payloads
- Flashcards: Cloze + Basic (heuristics) and optional GPT Q/A
- Anki export: genanki models with OpenAI Sans
- RAG: Answer endpoint with context packing and sources
- UI: Upload with advanced options, search, Ask, sources export

## Ops & Security
- .gitignore for env/data/artifacts
- `scripts/check_secrets.py` and Secrets Scan workflow
- Compose CI health check (no secrets); optional smoke test via secret
- MIT license; governance docs (CONTRIBUTING, SECURITY), PR/issue templates

## Testing
- Manual smoke: `make run` (then upload, search, ask, export, download)
- CLI smoke: `make smoke` (requires `OPENAI_API_KEY`)
- Compose health: `docker compose up --build`, then hit `/api/health`

## Notes
- Public BETA: APIs and UI may change. Feedback welcome.

## Checklist
- [x] No secrets committed (`make check-secrets`)
- [x] Local run verified
- [x] Smoke test passed locally
- [x] Docs updated (README, PUBLISHING, ROADMAP)
