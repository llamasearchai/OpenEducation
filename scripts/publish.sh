#!/usr/bin/env bash
set -euo pipefail

# Helper script to publish the repo as a public BETA to GitHub.
# Requirements: git, gh (GitHub CLI), and an authenticated session (`gh auth login`).

REPO_SLUG=${REPO_SLUG:-"llamasearchai/OpenEducation"}
AUTHOR_NAME=${AUTHOR_NAME:-"Nik Jois"}
AUTHOR_EMAIL=${AUTHOR_EMAIL:-""}
DESCRIPTION=${DESCRIPTION:-"Embeddings + Qdrant + Anki decks + RAG answering. Upload PDFs/DOCs and auto-generate study flashcards."}

need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing $1. Please install it." >&2; exit 1; }; }
need git
need gh

echo "Publishing to: $REPO_SLUG"

if [ ! -d .git ]; then
  echo "Initializing git repo..."
  git init
fi

if [ -n "$AUTHOR_EMAIL" ]; then
  git config user.name "$AUTHOR_NAME"
  git config user.email "$AUTHOR_EMAIL"
else
  git config user.name "$AUTHOR_NAME"
fi

# Ensure main branch
if git show-ref --verify --quiet refs/heads/main; then
  git checkout main
else
  if git rev-parse --verify HEAD >/dev/null 2>&1; then
    git branch -M main
  else
    git checkout -b main || true
  fi
fi

echo "Adding all files..."
git add -A

if git rev-parse --verify HEAD >/dev/null 2>&1; then
  # There are commits; create a new one if there are staged changes
  if ! git diff --cached --quiet; then
    git commit -m "chore: prepare initial beta publish"
  else
    echo "No staged changes to commit."
  fi
else
  git commit -m "feat: initial beta release"
fi

# Set remote if missing
if ! git remote get-url origin >/dev/null 2>&1; then
  echo "Setting origin to git@github.com:$REPO_SLUG.git"
  git remote add origin "git@github.com:$REPO_SLUG.git"
fi

echo "Pushing main..."
git push -u origin main

echo "Setting repo description and topics via gh CLI..."
gh repo edit "$REPO_SLUG" \
  --description "$DESCRIPTION" \
  --add-topic embeddings --add-topic qdrant --add-topic anki --add-topic rag --add-topic openai \
  --add-topic fastapi --add-topic vector-search --add-topic flashcards --add-topic cloze --add-topic study-tools || true

# Optional: set OPENAI_API_KEY secret if provided
if [ -n "${OPENAI_API_KEY:-}" ]; then
  echo "OPENAI_API_KEY present in env; setting repo secret via gh..."
  echo -n "$OPENAI_API_KEY" | gh secret set OPENAI_API_KEY --repo "$REPO_SLUG" || true
fi

# Create a prerelease tag if it doesn't exist
TAG=${TAG:-"v0.1.0-beta.1"}
if ! git rev-parse "$TAG" >/dev/null 2>&1; then
  echo "Tagging $TAG..."
  git tag -a "$TAG" -m "$TAG"
  git push origin "$TAG"
else
  echo "Tag $TAG already exists. Skipping."
fi

echo "Publish complete. Check releases and actions on GitHub: https://github.com/$REPO_SLUG"
