#!/usr/bin/env bash
# setup.sh — One-time local setup: symlink the pre-commit hook.
#
# Usage: scripts/setup.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

if [ ! -d ".git" ]; then
  echo "Not a git repository root ($REPO_ROOT) — nothing to install."
  exit 1
fi

mkdir -p .git/hooks
ln -sf ../../scripts/pre-commit.sh .git/hooks/pre-commit
chmod +x scripts/*.sh

echo "OK: .git/hooks/pre-commit -> scripts/pre-commit.sh (symlinked)"
echo "OK: scripts/*.sh made executable"
echo ""
echo "Run the full enforcement suite any time with:"
echo "  scripts/check-contract-refs.sh"
echo "  scripts/check-todos.sh"
echo "  scripts/check-freshness.sh"
echo "  scripts/check-ground-truth.sh"
echo "  scripts/check-compliance.sh"
