# CONTRACT-C1-THEME-SCHEMA.1.0

**Version:** 1.0
**Status:** verified
**Owner:** Will Ackerly
**Type:** Data Model
**Cross-repo Promotability:** No
**Source:** `ROADMAP.md` §4 (Theming: JSONC, prebaked themes, branding)

## Why this exists

md2docx renders every document through a JSON theme instead of hard-coded
styling, so one tool produces visually distinct DOCX output (a neutral
default, a branded house style, a marking-forward variant for banner-carrying
documents) without a code change. This contract is what lets a theme author
write a two-line JSON override and trust it composes predictably with the
built-in defaults, and what lets `docx2md` know which keys are safe to ignore
when inverting a document back to Markdown.

## Who needs this

- **`md2docx.py` `Converter`** — reads every key in this schema to style
  headings, tables, code blocks, blockquotes, footers, and the marking banner.
- **Theme authors** (`themes/*.json`) — need to know which keys exist, which
  are required vs. optional, and that omitted keys silently inherit the
  built-in default rather than erroring.
- **`docx2md.py`** — indirectly: it infers structure from *styles* the
  forward converter applied using this schema (mono font, shading fill,
  left border), so a schema change to those specific keys is a breaking
  change for the round-trip contract (`CONTRACT:C3-ROUNDTRIP.1.0`).

## Scenarios (illustrative)

### Scenario 1 — theme author ships a minimal override

A theme author writes `{"name": "Brief", "headings": {"h1": {"size_pt": 24}}}`
and points `-t` at it. Every other key — fonts, table styling, code block
fill, footer text — falls back to the built-in defaults via `deep_merge()`.
The author never has to restate the full schema to change one value.

### Scenario 2 — missing template file

A user runs `md2docx.py -t missing.json report.md`. `resolve_template()`
detects the explicit path doesn't exist and exits with
`template not found: missing.json` (exit code 1) rather than silently
falling back to defaults — an explicit `-t` is a promise, not a hint.

## Interfaces

```python
DEFAULTS: dict  # the full schema, hard-coded, in md2docx.py

def deep_merge(base: dict, over: dict) -> dict:
    """Recursively merge `over` onto `base`. Dict values merge key-by-key;
    any non-dict value (including lists) in `over` replaces the
    corresponding value in `base` wholesale. Keys present only in `base`
    are kept untouched."""

def resolve_template(explicit: str | None) -> tuple[dict, Path | None, str]:
    """Returns (merged_cfg, template_path_or_None, human_readable_message)."""
```

## Behavioral Contracts

| Behavior | Specification |
|----------|--------------|
| Schema keys | `fonts.{body,mono}`, `base.{size_pt,color,space_after_pt}`, `headings.{h1,h2,h3,h4}.{size_pt,color}` + `headings.{bold,space_before_pt,space_after_pt}`, `table.{style,header_fill,header_color,header_bold,cell_size_pt}`, `code.{fill,color,block_size_pt}`, `blockquote.{color,size_pt,border_color,border_size_eighths,indent_in}`, `footer.{text,color,size_pt,bold}`, `cui_banner.{detect,size_pt,bold,color}` |
| Colors | 6-hex-digit strings, no `#` prefix (e.g. `"9C3D9E"`), consumed by `rgb()` |
| Omitted key | Falls back to the value in `DEFAULTS` (or the parent theme, if the theme itself is layered) — never an error |
| Unknown top-level key (e.g. `name`, `_comment`) | Passed through untouched; ignored by the converter, available to tooling (e.g. `cfg.get("name")` feeds the provenance stamp's `tpl` field) |
| Resolution order | 1) `--template` / `-t` flag, 2) `md2docx-template.json` next to the script, 3) `themes/neutral.json` next to the script, 4) hard-coded `DEFAULTS` |
| Explicit `--template` path that doesn't exist | `sys.exit("template not found: <path>")`, exit code 1 — does **not** fall back |
| No template found anywhere (default search) | Falls back to `DEFAULTS` silently; prints `template: built-in defaults (...)` to stdout |
| `deep_merge` on nested dicts | Recurses — `over["headings"]["h1"]` merges onto `base["headings"]["h1"]` key-by-key, not as a wholesale replacement |

## Error Contracts

| Error | When | Code |
|-------|------|------|
| `SystemExit("template not found: <path>")` | `-t/--template` given an explicit path that doesn't exist | process exit code 1 |
| `json.JSONDecodeError` (uncaught) | Template file contains invalid JSON | process exit code 1 (Python traceback) |

## Dependencies

- Depends on: none (self-contained; stdlib `json` only)
- Configuration: `-t`/`--template` CLI flag
- External: none

## Cross-references

- **Source docs:** `ROADMAP.md` §4 (JSONC, `extends`, theme registry —
  planned superset of this contract)
- **Shipped themes:** `themes/neutral.json`, `themes/plum.json`,
  `themes/marked-docs.json`

## Future evolution

- `ROADMAP.md` §4 plans JSONC (comments) and an `extends` chain (theme
  inherits from a named parent theme, not just the hard-coded `DEFAULTS`).
  When that lands, bump to 2.0 — `extends` changes resolution order
  semantics from "flag > 2 files > hard-coded" to an arbitrary chain.
- A `branding.logo` block (path, width, placement) is planned per
  `ROADMAP.md` §4 and will be a minor (1.1) addition — themes omitting it
  keep working unchanged.

## Implementing Files

- `md2docx.py` — `DEFAULTS`, `deep_merge()`, `resolve_template()`
- `themes/neutral.json` — the base theme (identical values to `DEFAULTS`)
- `themes/plum.json` — purple-accented house style, deep-merges over neutral
- `themes/marked-docs.json` — banner-forward variant, deep-merges over neutral

## Test Requirements

- [x] `deep_merge()` recursive-merge behavior — `tests/test_roundtrip.py::test_theme_deep_merge`
- [x] Resolution order (flag > local override > shipped neutral > hard-coded) — `tests/test_roundtrip.py::test_template_resolution_order`
- [x] Every shipped theme in `themes/` parses and deep-merges without error — `tests/test_roundtrip.py::test_shipped_themes_load`

## Change History

| Version | Date | Change | Migration |
|---------|------|--------|-----------|
| 1.0 | 2026-07-08 | Initial contract | — |
