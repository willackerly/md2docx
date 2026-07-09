# CONTRACT-C3-ROUNDTRIP.1.0

**Version:** 1.0
**Status:** verified
**Owner:** Will Ackerly
**Type:** Component
**Cross-repo Promotability:** No
**Source:** `ROADMAP.md` §7 (Symmetry: DOCX → MD round-trip)

## Why this exists

`md2docx` and `docx2md` are only useful as a pair if editing the generated
DOCX in Word and converting it back doesn't silently lose or invent content.
This contract defines what "faithful round trip" means precisely enough to
test: a **canonical Markdown** spelling that `docx2md` always emits, and the
**style→construct inversion table** it uses to get there. It also names,
honestly, what the current tier does *not* recover — link targets, embedded
source recovery, 3-way merge — so nobody mistakes "round-trips the
constructs this tool understands" for "byte-perfect symmetry."

## Who needs this

- **`docx2md.py`** — directly implements this contract; every inversion rule
  below is a branch in `convert()`.
- **`md2docx.py`** — indirectly: it's the forward half of the pair. Its
  choice of Word styles (`Heading N`, `List Bullet`, paragraph shading, left
  borders, mono-font runs) *is* the vocabulary this contract inverts. A
  forward-converter change to which style marks a construct is a breaking
  change here too.
- **Anyone editing a generated DOCX in Word** and expecting the edits to
  come back as clean Markdown — this contract is the user-facing promise.

## Scenarios (illustrative)

### Scenario 1 — clean round trip

Someone converts `notes.md` (headings, a bullet list, one table, a fenced
code block) to DOCX, opens it in Word, fixes a typo in a table cell, saves,
and runs `docx2md.py notes.docx`. The output is canonical Markdown:
`-` bullets, `**bold**`, a padded pipe table with a separator row, one blank
line between blocks — structurally identical to the original except for the
one corrected cell.

### Scenario 2 — what's honestly lost

Someone's source Markdown has `[the docs](https://example.com/docs)`. The
forward converter demotes this to the plain text `the docs (https://example.com/docs)`
per its link-demotion rule (print-friendly, no hyperlink markup). Running
`docx2md` on the resulting DOCX gets back that plain text — the `[label](url)`
markup is **not** recovered, because the forward tool never stored it as a
Word hyperlink relationship in the first place. This is a documented gap
(`ROADMAP.md` §5.1), not a bug in the reverse tool.

## Interfaces

```python
def convert(docx_path: str | Path) -> str:
    """Reads a .docx file, walks its body in document order, and returns
    canonical Markdown as a single string (trailing newline, no trailing
    whitespace on any line)."""
```

## Behavioral Contracts

| Behavior | Specification |
|----------|--------------|
| `Heading 1`–`Heading 4` style | `#`, `##`, `###`, `####` (level = number of `#`) |
| `List Bullet` style | `- ` prefix |
| Table (first row shaded via `w:shd`) | Pipe table: header row, `\| --- \|` separator row, one row per remaining table row; `\|` inside cell text is escaped as `\\\|` |
| Paragraph with a left border (`w:pBdr/w:left`) | `> ` blockquote prefix |
| Paragraph-level shading (`w:shd` on `w:pPr`) | Fenced code block (accumulated across consecutive shaded paragraphs, emitted as one ` ``` ` block) |
| Run with a mono font (`Consolas`, `Courier New`, `Courier`, `Menlo`, `Monaco`, `DejaVu Sans Mono`, `Cascadia Code`, `Cascadia Mono`) or run-level shading | `` `code` `` inline span — code formatting is exclusive: bold/italic markers inside a code span are suppressed even if the run also carries them |
| Bold run (outside code) | Wrapped in `**` |
| Italic run (outside code) | Wrapped in `*` |
| Bold + italic run (outside code) | Wrapped in `***` |
| Adjacent runs with identical `(code, bold, italic)` formatting | Merged into one segment before emitting, so a word split across multiple Word runs is not fragmented mid-word |
| Page-header text (`sec.header.paragraphs[0]`) | Emitted as a leading `**HEADER TEXT**` line — the inverse of the forward converter's banner promotion |
| Blank/empty paragraphs (spacer paragraphs the forward converter inserts after tables/code blocks) | Dropped — not emitted as empty Markdown blocks |
| Block separation | Exactly one blank line between emitted blocks (`"\n\n".join(...)`) |
| Trailing whitespace | Stripped from every line; output ends with exactly one trailing newline |
| Table cell inline formatting | Header row: bold suppressed (the forward converter strips `**` from header cell markdown before rendering, since the header style already implies bold) |

## Error Contracts

| Error | When | Code |
|-------|------|------|
| `PackageNotFoundError` (from `python-docx`, uncaught) | `docx_path` is not a valid `.docx`/OPC package | process exit code 1 (Python traceback) |
| `SystemExit("not found: <path>")` | CLI given a path that doesn't exist | process exit code 1 |

## Dependencies

- Depends on: `CONTRACT:C2-PROVENANCE.1.0` — `docx2md.py` reads the
  provenance stamp before conversion (informational, does not gate
  conversion if the stamp is absent or malformed)
- Configuration: none
- External: `python-docx`

## Cross-references

- **Source docs:** `ROADMAP.md` §7.1–§7.5 (round-trip design, breadcrumbs,
  the reverse tool's algorithm, the canonical-MD symmetry contract, and
  honest limits)

## Future evolution

- **Canonical-MD equality, not just structural equality.** The current test
  suite (`tests/test_roundtrip.py`) compares a *token bag* (headings,
  bullets, table cells, code lines, bold/italic/code spans as a
  multiset) between the source fixture and the round-tripped output — it
  proves nothing is silently dropped or invented, but does not yet assert
  full line-for-line canonical-MD equality (`docx2md(md2docx(x)) ==
  canonicalize(x)`, `ROADMAP.md` §7.4). Tightening this to exact string
  equality is planned once `md2docx --normalize` (§7.4) exists to produce
  the canonical form of arbitrary input source for comparison.
- **Link recovery, custom XML source part, 3-way merge, table-caption
  breadcrumbs, tracked-changes rejection** — all named in `ROADMAP.md` §7.2
  and §7.5 as explicitly out of scope for this version. Any of these
  landing is additive (new recoverable constructs) and would ship as 1.1;
  a change to the *existing* inversion rules in the table above (e.g.
  switching how bold is detected) would be a breaking 2.0.

## Retirement / supersession plan

Not applicable — this is the initial contract for the round-trip component;
nothing precedes it.

## Implementing Files

- `docx2md.py` — all functions (`runs_to_md`, `table_to_md`, `convert`,
  `print_provenance`, and the low-level XML probes `para_shd_fill`,
  `para_has_left_border`, `run_shd_fill`, `run_is_code`)
- `md2docx.py` — the forward half: the style choices `docx2md.py` inverts
  (`Converter.convert`, `Converter.add_runs`)
- `tests/fixtures/kitchen-sink.md` — the fixture exercising every construct
  in the Behavioral Contracts table above
- `tests/test_roundtrip.py` — `test_roundtrip_kitchen_sink`

## Test Requirements

- [x] Every row in the Behavioral Contracts table has a construct present in
      `tests/fixtures/kitchen-sink.md` — `tests/test_roundtrip.py::test_roundtrip_kitchen_sink`
- [x] Forward → reverse token-bag comparison finds zero lost and zero
      invented tokens — `tests/test_roundtrip.py::test_roundtrip_kitchen_sink`
- [x] Adjacent same-formatted runs merge without fragmenting a word —
      covered by the kitchen-sink fixture's mixed inline-formatting line

## Change History

| Version | Date | Change | Migration |
|---------|------|--------|-----------|
| 1.0 | 2026-07-08 | Initial contract | — |
