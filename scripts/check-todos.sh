#!/usr/bin/env bash
# check-todos.sh — Enforce the two-tag TODO tracking system
# rebar-scripts: 2026.03.20
#
# Usage: ./scripts/check-todos.sh [directories...]
# Default: repo root (md2docx.py, docx2md.py, tests/ all live at top level —
# this is a flat, single-package CLI tool, not a src/-layout project)
#
# Rules:
#   - TODO: in code = untracked = BLOCKS COMMIT
#   - TRACKED-TASK: in code = tracked in TODO.md = allowed
#
# Exit code: 0 = no untracked TODOs, 1 = untracked TODOs found

set -euo pipefail

if [ $# -gt 0 ]; then
  DIRS=("$@")
else
  DIRS=(".")
fi

# Count untracked TODOs (exclude TRACKED-TASK lines and comments about the system)
untracked=$(grep -rn "TODO:" \
  --include="*.py" --include="*.go" --include="*.ts" --include="*.tsx" \
  --include="*.js" --include="*.rs" --include="*.jsx" \
  "${DIRS[@]}" 2>/dev/null \
  | grep -v "TRACKED-TASK:" \
  | grep -v "TODO\.md" \
  | grep -v "check-todos" \
  | grep -v "node_modules\|vendor\|dist\|\.git/\|\.claude/worktrees" \
  || true)

# Count tracked tasks (informational)
tracked=$(grep -rn "TRACKED-TASK:" \
  --include="*.py" --include="*.go" --include="*.ts" --include="*.tsx" \
  --include="*.js" --include="*.rs" --include="*.jsx" \
  "${DIRS[@]}" 2>/dev/null \
  | grep -v "node_modules\|vendor\|dist\|\.git/\|\.claude/worktrees" \
  || true)

tracked_count=$(echo "$tracked" | grep -c . 2>/dev/null || echo 0)
[ -z "$tracked" ] && tracked_count=0

if [ -n "$untracked" ]; then
  untracked_count=$(echo "$untracked" | grep -c .)
  echo "FAIL: $untracked_count untracked TODO(s) found:"
  echo ""
  echo "$untracked"
  echo ""
  echo "Before committing, you must either:"
  echo "  1. Fix the TODO immediately (remove it), OR"
  echo "  2. Add it to TODO.md and convert to: TRACKED-TASK: description"
  echo ""
  echo "Also found $tracked_count tracked tasks (OK)."
  exit 1
else
  echo "OK: 0 untracked TODOs. $tracked_count tracked tasks."
  exit 0
fi
