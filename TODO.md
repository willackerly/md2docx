# TODO

<!-- FRESHNESS: Update this date every time you modify this file -->
<!-- freshness: 2026-07-08 -->
<!-- last-synced: 2026-07-08 — date this file was verified against code -->

Active tasks only. Scan in 10 seconds, not 5 minutes.
Priorities live in QUICKCONTEXT.md "What's Next" — that is the single source of truth.

---

## Open Items

<!-- P0 items pulled from ROADMAP.md §8's phasing table; see the linked
     section for full context on each. -->

- [ ] Replace the regex line-parser with a `markdown-it-py` CommonMark AST — `ROADMAP.md` §0
- [ ] Package as `pyproject.toml` with a `pipx`-installable `md2docx` entry point — `ROADMAP.md` §0, §8
- [ ] Real hyperlinks (`w:hyperlink` runs) instead of label/URL-in-parens demotion — `ROADMAP.md` §5.1
- [ ] Nested lists + real Word numbering (retire the literal-text numbered-list workaround) — `ROADMAP.md` §5.2
- [ ] PNG/JPG image support (`![alt](path)` → `add_picture`) — `ROADMAP.md` §3
- [ ] Wide-table strategy: shrink + landscape-section rungs — `ROADMAP.md` §2
- [ ] Warnings framework (`file:line: message` for every unsupported construct, `--strict` mode) — `ROADMAP.md` §6

## Known Issues & Blockers

<!-- One canonical entry per issue. Cross-reference, don't duplicate.
     If an issue also appears in QUICKCONTEXT, point there: "See QUICKCONTEXT §X" -->

- **Regex parser mis-handles several constructs** — nested emphasis
  (`**bold *italic* bold**`), escaped pipes in table cells, backticks
  inside code spans, multi-paragraph list items, indented code blocks,
  setext headings, and hard line breaks all parse incorrectly or not at
  all today. Fix: the AST rewrite (`ROADMAP.md` §0) fixes all of these at
  once — not worth patching individually first.
- **`docx2md.py` doesn't reject files with pending tracked changes** —
  `ROADMAP.md` §7.5 says it should refuse rather than guess; the current
  implementation just converts whatever `python-docx` hands it, which may
  silently accept or reject tracked-change text unpredictably depending on
  how Word stored it. No test currently exercises this path.
- **Relative link targets are dropped, not recoverable** — by design (see
  `architecture/CONTRACT-C3-ROUNDTRIP.1.0.md` Scenario 2 and
  `tests/test_roundtrip.py::test_link_demotion`), but worth remembering
  when writing source Markdown that will round-trip: use absolute URLs if
  the link needs to survive a DOCX round trip.

### Gotchas

- **Template resolution silently falls back for the *default* search, but
  not for an explicit `-t` flag.** `md2docx.py -t missing.json` exits with
  an error; `md2docx.py` with no flag and no `themes/neutral.json` present
  falls back to hard-coded defaults with just a printed message. This is
  intentional (`architecture/CONTRACT-C1-THEME-SCHEMA.1.0.md`) but has
  surprised people expecting symmetric behavior.

## Discoveries

<!-- Format: checkbox, type tag, contract ref, description. -->

- [ ] **DISCOVERY** `none` — `docx2md.py`'s tracked-changes handling
  (see Known Issues above) has no contract coverage yet; needs one before
  `ROADMAP.md` §7.5's "refuse rather than guess" behavior is implemented,
  so the refusal criteria are specified rather than ad-hoc.

## Code Debt

<!-- Items tracked via `TRACKED-TASK:` comments in source code. -->

_None currently — `scripts/check-todos.sh` confirms zero untracked `TODO:`
comments in `md2docx.py` / `docx2md.py` / `tests/test_roundtrip.py`._

---

<details>
<summary><strong>Completed</strong> (click to expand)</summary>

<!-- Move completed items here. Archive items older than 2 weeks.
     For full history, see git log. -->

- [x] Forward converter with theme deep-merge + provenance stamping (v0.2.0) — completed 2026-07-08
- [x] Reverse converter (style-driven inversion to canonical Markdown) — completed 2026-07-08
- [x] Three shipped themes (`neutral`, `plum`, `marked-docs`) — completed 2026-07-08
- [x] `--no-footer` regression fix (flag was accepted but not wired to the converter) — completed 2026-07-08
- [x] Round-trip test suite (`tests/test_roundtrip.py`, 7 tests) — completed 2026-07-08
- [x] Three contracts + registry, rebar Tier 3 enforcement scripts — completed 2026-07-08

</details>

---

<!-- MAINTENANCE NOTES:

ADDING ITEMS:
1. Every `TODO:` comment in code MUST have a corresponding entry here
2. Convert `TODO:` → `TRACKED-TASK:` in code after adding here
3. Include enough context that a cold-start agent understands the task

COMPLETING ITEMS:
1. Check the box [x] and add completion date
2. Move to the collapsed Completed section
3. Remove the corresponding `TRACKED-TASK:` comment from code

KEEPING IT SHORT:
- This file should have <50 lines of open items
- Completed items go in the collapsed section (or just git log)
- Archive completed items older than 2 weeks
- Priorities are NOT tracked here — they're in QUICKCONTEXT.md "What's Next"

DRIFT RISK:
This file is HIGH drift risk. Agents complete tasks but forget to update here.
The `last-synced` date tells you when this was last verified against actual
code state. If it's >1 week old, verify against git log before starting work.
-->
