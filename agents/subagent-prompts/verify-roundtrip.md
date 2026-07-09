# Template: Verify Roundtrip

> Verify a change against `CONTRACT:C3-ROUNDTRIP.1.0` — run the round-trip
> test suite, and if the change adds a Markdown construct or a Word style
> mapping not yet covered, extend `tests/fixtures/kitchen-sink.md` and
> `tests/test_roundtrip.py` to cover it. Use after any change to
> `md2docx.py`'s parsing/rendering loop or `docx2md.py`'s inversion logic.

## Metadata

| Field | Value |
|-------|-------|
| **Category** | testing |
| **Mode** | single-invocation |
| **Isolation** | worktree (modifies test files) |
| **Estimated tokens** | ~5K-15K per invocation |

## Parameters

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| `CHANGE_DESCRIPTION` | yes | What changed in `md2docx.py` or `docx2md.py` | "Added `~~strikethrough~~` support" |
| `NEW_CONSTRUCT` | no | The specific Markdown construct or Word style mapping introduced, if any | "strikethrough run -> `~~text~~`" |

## Task

1. Run `python3 tests/test_roundtrip.py`. If it fails, that's your first
   finding — report the failing test name and the assertion message
   verbatim; don't paraphrase.
2. Read `architecture/CONTRACT-C3-ROUNDTRIP.1.0.md`'s Behavioral Contracts
   table. If `NEW_CONSTRUCT` isn't a row in that table, the contract needs
   a version bump (minor, if additive) — draft the new row and hand it
   back as a finding rather than editing the contract yourself unless your
   task explicitly authorizes it (contract changes get plan-mode review
   per `AGENTS.md` § Contract-Driven Development).
3. If `NEW_CONSTRUCT` is provided, add a minimal example to
   `tests/fixtures/kitchen-sink.md` and confirm
   `test_roundtrip_kitchen_sink`'s word-bag comparison still passes with
   zero lost/invented tokens (see the tokenizer's docstring in
   `tests/test_roundtrip.py` for what "token" means here — it's a
   structure-agnostic word-bag, not a full Markdown AST diff).
4. If the change is intentionally lossy (something the forward converter
   now drops on purpose, the way relative link URLs already are — see
   `test_link_demotion`), add the drop to
   `_normalize_source_for_comparison()` in `tests/test_roundtrip.py` with
   a comment explaining why, and add a dedicated unit test analogous to
   `test_link_demotion` documenting the exact before/after behavior.

## Context Files

Read these before starting:
- `architecture/CONTRACT-C3-ROUNDTRIP.1.0.md` — the round-trip contract
- `tests/test_roundtrip.py` — the test suite, especially the `_word_bag`
  and `_normalize_source_for_comparison` docstrings
- `tests/fixtures/kitchen-sink.md` — the fixture

## Output Format

Either: a passing test suite with no fixture/contract changes needed
(nothing further to do), or a diff to `tests/fixtures/kitchen-sink.md` /
`tests/test_roundtrip.py` plus a finding describing any contract version
bump the maintainer should review.

## Success Criteria

- `python3 tests/test_roundtrip.py` reports `N/N passed` with the new
  construct exercised
- No test was weakened (loosened an assertion, added a skip) to make it
  pass — see `AGENTS.md` § The Scout Rule

## Anti-Patterns

- Do NOT delete or loosen an existing assertion in
  `test_roundtrip_kitchen_sink` to make a new construct's round trip
  "pass" — if the new construct breaks an existing guarantee, that's a
  real regression to report, not a test to relax.
- Do NOT silently expand `_normalize_source_for_comparison()`'s drop list
  without a paired unit test — an undocumented drop there would hide real
  data loss instead of proving it's intentional.
