Publishing OpenEducation

This guide walks through publishing the app to GitHub and (optionally) enabling CI.

1) Prepare the repo

- Ensure sensitive files are excluded (see `.gitignore`).
- Verify the app runs locally: `uvicorn app.main:app --reload --port 8000`.
- Optionally run the smoke test: `make smoke`.
- Run a secret scan: `make check-secrets`.
- Review `git status` to ensure no private files will be committed.

Pre-publish commit & PR hygiene

- Rewrite local history into a small set of professional commits (optional):

```
git rebase -i HEAD~N  # squash/fixup as needed
```

- Prefer opening PRs from feature branches and merging via squash-merge to keep a clean history.

Set commit author (optional)

```
git config user.name "Nik Jois"
git config user.email "you@example.com"
```

2) Create GitHub repo

- Create `llamasearchai/OpenEducation` on GitHub (or your fork).
- Add the remote and push:

```
git init
git remote add origin git@github.com:llamasearchai/OpenEducation.git
git add -A
git commit -m "Initial publish: OpenEducation embeddings + Qdrant + Anki"
git branch -M main
git push -u origin main
```

3) Configure secrets (for CI smoke test)

- In GitHub → Settings → Secrets and variables → Actions → New repository secret:
  - `OPENAI_API_KEY`: your API key

4) CI (optional)

- This repo includes `.github/workflows/ci.yml`. It performs a syntax check and will attempt a smoke test if `OPENAI_API_KEY` is present. The smoke test spins up the app and hits basic endpoints.

5) Releases (optional)

- Tag a release after verifying locally:

```
git tag -a v0.1.0 -m "Initial release"
git push origin v0.1.0
```

6) Release tag and notes

- Create a version tag and push it to trigger the Release workflow:

```
git tag -a v0.1.0 -m "v0.1.0"
git push origin v0.1.0
```

- The workflow will create a GitHub Release with generated notes and the template from `.github/RELEASE_TEMPLATE.md`.

7) Repo description and topics

- With GitHub CLI:

```
gh repo edit llamasearchai/OpenEducation \
  --description "Embeddings + Qdrant + Anki decks + RAG answering. Upload PDFs/DOCs and auto-generate study flashcards." \
  --add-topic embeddings --add-topic qdrant --add-topic anki --add-topic rag --add-topic openai \
  --add-topic fastapi --add-topic vector-search --add-topic flashcards --add-topic cloze --add-topic study-tools
```

8) Post-publish

- Update README badges and links if needed.
- Consider enabling GitHub Pages for docs if you expand documentation.

Branch protection (recommended)

- Protect `main`: require PR reviews, status checks (CI, Compose CI, Secrets Scan), and squash merges.
- Dismiss stale approvals on new commits.

PR etiquette

- Prefer small, focused PRs with clear descriptions and screenshots when helpful.
- Ensure `make check-secrets` and CI pass before requesting review.
- Use Conventional Commits style (feat:, fix:, chore:, docs:) to keep history tidy.
