#!/bin/bash

# OpenEducation - GitHub Publishing Script
# This script sets up git and publishes the repository to GitHub

set -euo pipefail

echo "OpenEducation - Publishing to GitHub"
echo "===================================="

# Check if we're in the right directory
if [ ! -f "README.md" ]; then
    echo "Error: README.md not found. Please run this script from the OpenEducation root directory."
    exit 1
fi

echo "Current directory: $(pwd)"

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    echo "Git repository initialized"
else
    echo "Git repository already exists"
fi

# Configure git user with noreply to avoid email privacy issues (repo-local only)
echo "Configuring git user (noreply)..."
git config --local user.name "Nik Jois"
git config --local user.email "nikjois@users.noreply.github.com"
git config --local tag.gpgSign false

echo "Git user configured: Nik Jois <nikjois@users.noreply.github.com>"

# Add remote origin if not exists
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "Adding remote origin..."
    if [ -n "${GITHUB_TOKEN:-}" ]; then
      git remote add origin https://x-access-token:${GITHUB_TOKEN}@github.com/llamasearchai/OpenEducation.git
    else
      git remote add origin https://github.com/llamasearchai/OpenEducation.git
    fi
    echo "Remote origin added."
else
    echo "Remote origin already exists"
fi

# Ensure large/private artifacts are not tracked
if git ls-files --error-unmatch PediatricCardiology.pdf > /dev/null 2>&1; then
    git rm --cached PediatricCardiology.pdf || true
fi
if git ls-files --error-unmatch data > /dev/null 2>&1; then
    git rm -r --cached data || true
fi

# Apply .gitignore across the repo
git add .

# Create professional commit message
read -r -d '' COMMIT_MESSAGE <<'MSG'
chore(release): prepare OpenEducation release with cleaned assets and CI

- Comprehensive modules and CLI/TUI improvements
- Robust PDF ingestion with hierarchical chapter extraction
- Offline flashcard generation fallback (no LLM required)
- Anki subdeck assembly with custom styling
- Security hardening: caching, rate limiting, noreply email
- Professional .gitignore; removed large/private artifacts from VCS
- CI workflow present; Docker support
MSG

# Commit changes (allow empty commit if nothing to commit)
echo "Committing changes..."
if ! git diff --cached --quiet; then
  git commit -m "$COMMIT_MESSAGE"
else
  echo "No staged changes to commit. Continuing."
fi

# Create and push release branch
BRANCH="release/v1.0.0"
if git rev-parse --verify "$BRANCH" >/dev/null 2>&1; then
  echo "Release branch exists: $BRANCH"
  git checkout "$BRANCH"
else
  echo "Creating release branch: $BRANCH"
  git checkout -b "$BRANCH"
fi

echo "Pushing branch to GitHub..."
if ! git push -u origin "$BRANCH"; then
  echo "Warning: push failed (likely due to missing credentials)."
fi

# Create and push lightweight tag
echo "Tagging release..."
TAG_VER=v1.0.0
if git rev-parse -q --verify refs/tags/${TAG_VER} >/dev/null; then
  echo "Tag ${TAG_VER} exists. Bumping to v1.0.1"
  git tag -d ${TAG_VER} || true
  if git push origin :refs/tags/${TAG_VER}; then :; else echo "Warning: failed to delete remote tag"; fi
  TAG_VER=v1.0.1
fi

git tag ${TAG_VER}
if ! git push origin ${TAG_VER}; then
  echo "Warning: tag push failed (likely due to missing credentials)."
fi

echo "Published branch: $BRANCH"
echo "Published tag: ${TAG_VER}"

echo "Done."
