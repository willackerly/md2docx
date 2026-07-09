# Template: Build Theme

> Design and ship a new `themes/*.json` theme file for md2docx, conforming
> to `CONTRACT:C1-THEME-SCHEMA.1.0`. Use when adding a new prebaked visual
> style (e.g. `compact-print`, `brief` — see `ROADMAP.md` §4 for the
> planned set).

## Metadata

| Field | Value |
|-------|-------|
| **Category** | generation |
| **Mode** | single-invocation |
| **Isolation** | worktree (modifies files) |
| **Estimated tokens** | ~5K-10K per invocation |

## Parameters

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| `THEME_NAME` | yes | The theme's `name` field and filename stem | `compact-print` |
| `INTENT` | yes | One or two sentences: what this theme is for, who reaches for it | "Smaller everything, tighter spacing, for long technical docs that need to fit more content per page." |
| `BASE` | no | Which shipped theme to start from (default: `neutral`) | `neutral` |

## Task

Create `themes/<THEME_NAME>.json` per `CONTRACT:C1-THEME-SCHEMA.1.0`.

1. Read `architecture/CONTRACT-C1-THEME-SCHEMA.1.0.md` — every key you can
   set, what deep-merge means for it, and what happens if you omit a key
   (it inherits from `md2docx.py`'s `DEFAULTS`, not from `BASE` — `themes/`
   files are independent JSON files, not a real `extends` chain yet; see
   `ROADMAP.md` §4 for the planned `extends` feature).
2. Look at `themes/neutral.json`, `themes/plum.json`, and
   `themes/marked-docs.json` for the shape and the `_comment` convention
   (a `_comment` string key documenting the theme's intent and any
   non-obvious choices — this repo doesn't have JSONC comment support yet).
3. Only override keys that matter for `INTENT`. Don't restate the full
   schema — deep-merge means an omitted key silently falls back to
   `DEFAULTS`.
4. Add a test case to `tests/test_roundtrip.py::test_shipped_themes_load`
   is generic and already covers any new file in `themes/*.json`
   automatically — you do not need to add a new test function unless the
   theme introduces a new *behavior* (it shouldn't; themes are pure data).
5. Update `ROADMAP.md` §4's theme registry list if the theme was listed
   there as "planned" — move it to "shipped."
6. Update `METRICS.md`'s `shipped_themes` count and re-run
   `scripts/check-ground-truth.sh`.
7. Mention the new theme in `README.md`'s theme list.

## Context Files

Read these before starting:
- `architecture/CONTRACT-C1-THEME-SCHEMA.1.0.md` — the schema contract
- `themes/neutral.json`, `themes/plum.json`, `themes/marked-docs.json` — existing themes
- `ROADMAP.md` §4 — planned theme registry

## Output Format

A new file `themes/<THEME_NAME>.json`, plus the doc updates listed in
step 4-7 above. No separate results file needed — the diff is the result.

## Success Criteria

- `python3 tests/test_roundtrip.py` passes (in particular
  `test_shipped_themes_load`)
- `scripts/check-ground-truth.sh` passes after the `METRICS.md` update
- The theme has a `name` field and a `_comment` field explaining its intent
- Every color value is a 6-hex-digit string with no `#` prefix

## Anti-Patterns

- Do NOT restate every schema key "to be safe" — only override what
  `INTENT` requires.
- Do NOT invent new top-level schema keys (e.g. a `branding` block) —
  `md2docx.py`'s `Converter` doesn't read them yet; that's `ROADMAP.md`
  §4 future work, not a theme-authoring task.
- Do NOT set `footer.text` to anything resembling a real classification
  or confidentiality marking as the *default* — this repo ships publicly;
  keep shipped theme footers empty or clearly illustrative (see
  `themes/marked-docs.json` for the pattern: the marking-style banner is a
  document-level opt-in via the source `.md`'s first line, not a
  theme-level default).
