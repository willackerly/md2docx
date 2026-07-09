# Project Metrics

<!-- FRESHNESS: Update this date every time you modify this file -->
<!-- freshness: 2026-07-08 -->

**Ground truth metrics for automated verification.**

The `Ground Truth (machine-verified)` section below is checked by
`scripts/check-ground-truth.sh` on every run. When a metric drifts from
reality (a file gets added, removed, or a test is dropped), the enforcement
script fails until this file is updated to match — see
`scripts/check-ground-truth.sh`'s `compute_metrics()` for exactly how each
number is computed.

---

## Ground Truth (machine-verified)

```
python_source_files = 2
test_files = 1
test_functions = 7
contracts = 3
shipped_themes = 3
```

| Metric | Meaning | Computed as |
|--------|---------|-------------|
| `python_source_files` | Root-level `.py` files (the two converters) | `ls *.py \| wc -l` |
| `test_files` | Files under `tests/` matching `test_*.py` | `ls tests/test_*.py \| wc -l` |
| `test_functions` | `def test_*` functions in `tests/test_roundtrip.py` | `grep -c '^def test_'` |
| `contracts` | Non-template `CONTRACT-C*.md` files in `architecture/` | `ls architecture/CONTRACT-C*.md \| grep -v TEMPLATE \| wc -l` |
| `shipped_themes` | `.json` files in `themes/` | `ls themes/*.json \| wc -l` |

## Codebase Size (informational, not machine-verified)

- `md2docx.py` — 404 lines (forward converter: theme resolution, deep-merge,
  Markdown line-parser, DOCX emission, provenance stamping)
- `docx2md.py` — 267 lines (reverse converter: style-driven inversion,
  provenance readback)
- `tests/test_roundtrip.py` — 278 lines, 7 test functions, no external test
  framework dependency (runs via `python3 tests/test_roundtrip.py`)

## Testing Status

- **Tests:** 7 total, 7 passing, 0 failing (`python3 tests/test_roundtrip.py`)
- **Coverage shape:** theme deep-merge + resolution order (C1), provenance
  stamp round-trip (C2), full kitchen-sink forward→reverse token-bag
  comparison + structural spot-checks (C3), link-demotion edge case,
  `--no-footer` regression test
- **No skipped tests.** Zero `.skip()`/`pytest.mark.skip` in the suite.

## Contracts

- **Total contracts:** 3 (`C1-THEME-SCHEMA`, `C2-PROVENANCE`, `C3-ROUNDTRIP`)
- **Declared Status:** all 3 at `verified` (each has a passing test —
  see `architecture/CONTRACT-REGISTRY.md`)

## Dependencies

- **Runtime:** `python-docx` (the only third-party dependency)
- **Development/test:** none beyond `python-docx` — the test suite uses
  only the standard library plus the project's own modules
- **Security vulnerabilities:** none tracked (no automated scan configured
  yet — see `TODO.md`)

## Quality Metrics

- **Contract compliance:** `scripts/check-contract-refs.sh` — 0 broken
  `CONTRACT:` references
- **TODO tracking:** `scripts/check-todos.sh` — 0 untracked `TODO:` comments
- **Documentation freshness:** `scripts/check-freshness.sh` — all
  `freshness:` markers current at last check

---

<!-- GROUND TRUTH VERIFICATION

This file is checked by scripts/check-ground-truth.sh, which computes the
same five metrics from the actual repo state and fails the check if any
number in the "Ground Truth (machine-verified)" block above has drifted.

UPDATE PROCESS when you add/remove a source file, test, contract, or theme:
1. Update the metric in the fenced block above.
2. Run scripts/check-ground-truth.sh to confirm it now passes.
3. Update the freshness date at the top of this file.
-->
