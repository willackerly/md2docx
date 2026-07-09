# CONTRACT-C2-PROVENANCE.1.0

**Version:** 1.0
**Status:** verified
**Owner:** Will Ackerly
**Type:** Data Model
**Cross-repo Promotability:** No
**Source:** `ROADMAP.md` §7.2 (Breadcrumbs, in order of survivability)

## Why this exists

A generated DOCX file, once it leaves the tool, carries no memory of how it
was produced unless something stamps that information into the file itself.
Without a provenance stamp, `docx2md` has no way to know which theme shaped
the document's styles (needed to invert them back to Markdown constructs) or
whether the source `.md` file has drifted since the DOCX was generated. This
contract defines the minimal, standards-compliant breadcrumb that survives a
round trip through Word: the DOCX core properties (`docProps/core.xml`), a
standard Office Open XML part every conforming reader preserves.

## Who needs this

- **`docx2md.py` `print_provenance()`** — reads the stamp back and reports
  it (tool/version, template identity, source hash, generation time) so a
  human editing the reverse-converted Markdown knows what produced it.
- **Future 3-way-merge tooling** (`ROADMAP.md` §7.3, not yet built) — will
  compare `srcsha` against the current source file's hash to detect drift
  before merging Word edits back into the Markdown source of truth.
- **Anyone auditing a DOCX file's origin** — File → Info in Word surfaces
  `subject`, `keywords`, and `category` directly; `comments` requires
  reading the raw XML or running `docx2md` against the file.

## Scenarios (illustrative)

### Scenario 1 — round trip identifies its own template

Someone converts `report.md` with `-t themes/plum.json`, edits the resulting
`report.docx` in Word, and later runs `docx2md.py report.docx`. The tool
prints the provenance stamp to stderr before converting: tool version,
`tpl: "Plum"`, the 16-hex template hash, the 16-hex source hash, and the UTC
generation timestamp — enough to identify exactly which theme file produced
the styling, even if `themes/plum.json` has since changed on disk.

### Scenario 2 — no template used

Someone runs `md2docx.py notes.md` with no `themes/neutral.json` present and
no `-t` flag — pure hard-coded `DEFAULTS`. The stamp still writes:
`tpl: "built-in defaults"` and `tplsha: null` (no file to hash), so the
absence of a template is recorded, not silently omitted.

## Interfaces

```python
def stamp_provenance(doc: Document, src: Path, tpl_path: Path | None, cfg: dict) -> None:
    """Mutates doc.core_properties in place. Does not return a value and
    does not raise under normal operation (best-effort stamp)."""

def print_provenance(doc: Document) -> None:
    """Reads doc.core_properties and prints a human-readable summary to
    stderr. Never raises on malformed/missing provenance — degrades to
    printing what's available."""
```

## Behavioral Contracts

| Behavior | Specification |
|----------|--------------|
| `core_properties.comments` | Compact JSON (`json.dumps(..., separators=(",", ":"))`) with exactly the keys: `t` (`"md2docx/<TOOL_VERSION>"`), `tpl` (theme's `name` field, or `"built-in defaults"`), `tplsha` (16-hex sha256 of the template file, or JSON `null`), `srcsha` (16-hex sha256 of the source `.md` file, always present), `gen` (UTC timestamp, `%Y-%m-%dT%H:%MZ`) |
| `core_properties.subject` | The resolved absolute path of the source file, right-truncated to the last 255 characters (`str(...)[-255:]`) |
| `core_properties.keywords` | Always the literal string `"md2docx"` |
| `core_properties.category` | The same value as `comments.tpl` |
| Hash truncation | Both `tplsha` and `srcsha` are `hashlib.sha256(...).hexdigest()[:16]` — first 16 hex characters (64 bits), not a full 64-char digest |
| `tplsha` when no template file | `None` in Python → serializes as JSON `null` (key is present, value is null — not omitted) |
| `field length` | Every core-properties field this contract writes is capped at or below 255 characters, honoring the OOXML convention several tools (including older Word versions) enforce for these fields |
| Stamping failure mode | Best-effort — `stamp_provenance()` does not catch or suppress exceptions; a read failure on the source file (already read once by the converter) or template file propagates as an uncaught exception, matching the rest of the tool's fail-fast posture |
| `print_provenance()` output stream | stderr, never stdout — stdout is reserved for the converted Markdown when `docx2md.py` output is redirected (`docx2md.py file.docx > out.md`) |
| `print_provenance()` on missing stamp | Prints `(no comments JSON found)` and continues; does not raise |

## Error Contracts

This contract has no dedicated error types — provenance stamping is
best-effort and additive. See `CONTRACT-C1-THEME-SCHEMA.1.0` for template
resolution errors, which occur before `stamp_provenance()` is ever called.

## Dependencies

- Depends on: `CONTRACT:C1-THEME-SCHEMA.1.0` for `cfg.get("name")` (the `tpl`
  field's value) and the resolved `tpl_path` (the file that gets hashed)
- Configuration: none (always runs; not togglable via a flag)
- External: none (stdlib `hashlib`, `json`, `datetime`)

## Cross-references

- **Source docs:** `ROADMAP.md` §7.2 — the provenance stamp is the first
  breadcrumb of the round-trip design; §7.2 documents three further
  breadcrumb mechanisms not yet implemented (custom XML part, table
  captions, heading bookmarks)

## Future evolution

- `ROADMAP.md` §7.2 plans a **custom XML part** (`customXml/item1.xml`)
  carrying the entire source Markdown, so a DOCX file could regenerate its
  own merge base without a separate git lookup. That is additive — a new
  OPC part — and does not change this contract's core-properties fields; it
  would likely become `CONTRACT-C2-PROVENANCE.2.0` given it changes what
  "the provenance of this file" means (a full source snapshot, not just a
  hash).
- Google Docs strips custom XML parts and most non-standard properties on
  import (`ROADMAP.md` §7.5) — core properties (`subject`, `keywords`,
  `category`) survive a Google Docs round trip more reliably than
  `comments`, which is why the source path is duplicated into `subject`
  rather than relying on `comments` alone.

## Implementing Files

- `md2docx.py` — `stamp_provenance()`
- `docx2md.py` — `print_provenance()`

## Test Requirements

- [x] Stamp round-trips through a save/reload and contains all five
      `comments` keys — `tests/test_roundtrip.py::test_provenance_stamp`
- [x] `tplsha` is `null` when converting with no template file present —
      `tests/test_roundtrip.py::test_provenance_stamp`
- [x] `srcsha` matches an independently computed `sha256(...)[:16]` of the
      source file — `tests/test_roundtrip.py::test_provenance_stamp`

## Change History

| Version | Date | Change | Migration |
|---------|------|--------|-----------|
| 1.0 | 2026-07-08 | Initial contract (documents the stamp shipped in tool v0.2.0) | — |
