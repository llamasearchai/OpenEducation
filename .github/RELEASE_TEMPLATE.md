# OpenEducation v0.1.0-beta.1

Highlights
- Initial public BETA: Upload → Extract → Token-chunk → Embed (OpenAI text-embedding-3-large) → Store (Qdrant) → Generate flashcards (Cloze, Basic, GPT Q/A) → Export Anki deck (.apkg)
- RAG Answering API with deck scoping, token packing, and sources list
- Simple web UI with OpenAI Sans; semantic search and Ask panes

Changes
- Backend: FastAPI endpoints for upload, search, answer, deck download, deck catalog, sources export
- Qdrant: Local embedded or remote server; deck-aware filtering; export via scroll
- Anki: genanki models with OpenAI Sans; Cloze + Basic cards
- LLM: Optional GPT Q/A generation; controllable via env
- Chunking: Token-based with overlap and char-based fallback; per-upload overrides
- Docker/Compose: App + optional Qdrant service
- CI/CD: Syntax check, compose health, secrets scan; prerelease workflow
- Docs: README, PUBLISHING, CONTRIBUTING, SECURITY; Makefile; smoke test script

Upgrade notes
- This is a BETA. Endpoints and UI may evolve. No migrations expected at this stage.
- If switching from embedded Qdrant to server mode, set `QDRANT_URL` and (optionally) `QDRANT_API_KEY`.

Thanks
- Author: Nik Jois (@nikjois)
