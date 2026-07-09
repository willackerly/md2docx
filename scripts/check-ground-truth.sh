#!/usr/bin/env bash
# check-ground-truth.sh — Verify METRICS.md matches codebase reality.
# rebar-scripts: 2026.03.20
#
# Computes md2docx's project metrics from the repo and compares against the
# claims in the "Ground Truth (machine-verified)" block of METRICS.md.
# Catches "silent success" drift where everything works but documented
# numbers describe a different reality.
#
# Usage: ./scripts/check-ground-truth.sh
# Exit: 0 = all claims match, 1 = drift detected

set -euo pipefail

# Tier gate: ground truth is Tier 3 only (skip for Tier 1-2)
SCRIPT_DIR_GT="$(cd "$(dirname "$0")" && pwd)"
[ -f "$SCRIPT_DIR_GT/_rebar-config.sh" ] && source "$SCRIPT_DIR_GT/_rebar-config.sh" && _rebar_skip 3 && exit 0

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

# METRICS or METRICS.md — this repo ships METRICS.md.
METRICS_FILE="$REPO_ROOT/METRICS"
[ ! -f "$METRICS_FILE" ] && [ -f "$REPO_ROOT/METRICS.md" ] && METRICS_FILE="$REPO_ROOT/METRICS.md"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'
exit_code=0

# ── md2docx's metrics — kept in sync with METRICS.md's "Ground Truth" table ──
compute_metrics() {
  echo "python_source_files=$(ls -- *.py 2>/dev/null | wc -l | tr -d ' ')"
  echo "test_files=$(ls tests/test_*.py 2>/dev/null | wc -l | tr -d ' ')"
  echo "test_functions=$(grep -c '^def test_' tests/test_roundtrip.py 2>/dev/null | tr -d ' ')"
  echo "contracts=$(ls architecture/CONTRACT-C*.md 2>/dev/null | grep -v TEMPLATE | wc -l | tr -d ' ')"
  echo "shipped_themes=$(ls themes/*.json 2>/dev/null | wc -l | tr -d ' ')"
}

# ── Verification engine (do not modify below this line) ──

verify() {
  if [ ! -f "$METRICS_FILE" ]; then
    echo -e "${YELLOW}SKIP${NC}: No METRICS file found"
    echo "  Create a METRICS file with key = value pairs."
    echo "  See scripts/check-ground-truth.sh for examples."
    return 0
  fi

  local computed
  computed=$(compute_metrics)

  if [ -z "$computed" ]; then
    echo "No metrics defined. Customize compute_metrics() in this script."
    return 0
  fi

  while IFS='=' read -r key value; do
    # Skip empty lines and comments
    [ -z "$key" ] && continue
    echo "$key" | grep -q '^[[:space:]]*#' && continue

    key=$(echo "$key" | xargs)
    value=$(echo "$value" | xargs)

    # Look up key in METRICS file
    local documented
    documented=$(grep "^[[:space:]]*${key}[[:space:]]*=" "$METRICS_FILE" 2>/dev/null \
      | head -1 | cut -d'=' -f2 | xargs) || true

    if [ -z "$documented" ]; then
      echo -e "${YELLOW}NEW${NC}:   $key = $value  (not in METRICS file)"
    elif [ "$value" = "$documented" ]; then
      echo -e "${GREEN}OK${NC}:    $key = $value"
    else
      echo -e "${RED}DRIFT${NC}: $key — METRICS says $documented, code says $value"
      exit_code=1
    fi
  done <<< "$computed"
}

echo "=== Ground Truth Verification ==="
echo ""
verify
echo ""

if [ $exit_code -eq 0 ]; then
  echo -e "${GREEN}All documented metrics match codebase reality${NC}"
else
  echo -e "${RED}Metric drift detected — update METRICS.md to match reality${NC}"
fi

exit $exit_code
