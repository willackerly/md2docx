# Quick Context

<!-- FRESHNESS: Update this date every time you modify this file -->
<!-- freshness: 2026-07-08 -->
<!-- last-synced: 2026-07-08 — date this file was verified against code -->

**Current state of the project for agents starting a new session.**

---

## Branch & State

- **Active branch:** `main`
- **Last deploy:** not applicable — this is a CLI tool distributed as source, not a deployed service
- **Environment:** any Python 3.9+ with `python-docx` installed
- **Packaging:** none yet — run `python3 md2docx.py` / `python3 docx2md.py` directly (see `ROADMAP.md` §0 for the planned `pyproject.toml` + `pipx` packaging)

## Test Status

- **Unit/round-trip tests:** 7 passing, 0 failing, 0 skipped — `python3 tests/test_roundtrip.py`
- **Coverage shape:** theme deep-merge + template resolution order, provenance stamp fields, full kitchen-sink forward→reverse round trip (structural spot-checks + word-bag comparison), link-demotion edge case, `--no-footer` regression
- **Enforcement scripts:** `check-contract-refs.sh`, `check-todos.sh`, `check-freshness.sh`, `check-ground-truth.sh`, `check-compliance.sh` all pass as of the freshness date above

## What's Next (in priority order)

<!-- This is the SINGLE SOURCE OF TRUTH for priorities.
     TODO.md has task details, but this list sets the order.
     Work top to bottom. -->

1. Package as `pyproject.toml` with a `pipx`-installable entry point (`ROADMAP.md` §0 / §8 P0)
2. Swap the hand-rolled line parser for a `markdown-it-py` CommonMark AST (`ROADMAP.md` §0 — the one architectural decision that unblocks everything else)
3. Real hyperlinks (`w:hyperlink` runs) instead of the current label/URL demotion (`ROADMAP.md` §5.1)
4. Nested lists + real Word numbering instead of the literal-text numbered-list workaround (`ROADMAP.md` §5.2)

## Active Work

**Current focus:** initial public release — the tool pair (v0.2.0), theme
system, round-trip test suite, and rebar Tier 3 scaffolding are complete
and this is the baseline for future work.

**In progress:**
- None — this is a clean baseline commit set, not mid-refactor.

**Recently completed:**
- Forward converter (`md2docx.py`) with theme deep-merge, template
  resolution, and DOCX provenance stamping (core-props stamp shipped in
  v0.2.0)
- Reverse converter (`docx2md.py`): style-driven inversion back to
  canonical Markdown
- Three shipped themes (`neutral`, `plum`, `marked-docs`)
- Three contracts (`C1-THEME-SCHEMA`, `C2-PROVENANCE`, `C3-ROUNDTRIP`),
  all `verified`
- `tests/test_roundtrip.py` — 7 tests, includes a `--no-footer` regression
  fix (the flag was accepted but not wired to the converter before this
  release)
- Rebar Tier 3 enforcement (`.rebarrc`, `.rebar-version`, `scripts/check-*.sh`, `METRICS.md`)

**Blocked:**
- None currently.

## Key Decisions

**Architecture decisions:**
- Style-driven round trip, not byte-for-byte symmetry: the forward
  converter's choice of Word style *is* the contract the reverse converter
  inverts (`architecture/CONTRACT-C3-ROUNDTRIP.1.0.md`)
- Theme-as-data: every visual choice is a JSON key, not a code branch
  (`architecture/CONTRACT-C1-THEME-SCHEMA.1.0.md`)
- Provenance via standard OPC core properties, not a custom file format —
  survives a Word save because it's a part every conforming reader
  preserves (`architecture/CONTRACT-C2-PROVENANCE.1.0.md`)
- Rebar Tier 3 (Enforced), but scoped to what a solo-maintained CLI tool
  actually needs — no rebar Steward, no ASK CLI, no `ci-check.sh`; see
  `.rebarrc` and `architecture/README.md`

**Tech stack:**
- Python 3, stdlib + `python-docx` (the only runtime dependency)
- No test framework dependency — `tests/test_roundtrip.py` runs standalone

**Process decisions:**
- Contract-first for the theme schema, provenance stamp, and round-trip
  guarantee — those three are the parts other code (and future agents)
  depend on staying stable
- Two-tag TODO system (`TODO:` blocks commit, `TRACKED-TASK:` is tracked
  in `TODO.md`) enforced by `scripts/check-todos.sh`

## Context for Agents

**Project scope:** a Markdown↔DOCX converter pair for people who write
documentation in Markdown but need a themed, print-quality Word document
(and, less commonly, need to bring Word edits back into Markdown).

**User personas:** a developer or technical writer converting one-off
Markdown files to DOCX for a non-technical audience; someone who wants a
DOCX round-trip because a collaborator only edits in Word or Google Docs.

**Key constraints:**
- Single-maintainer project — keep the dependency surface minimal
  (`python-docx` only) and the enforcement scripts proportionate to that
  (see `.rebarrc`'s note on why there's no Steward here)
- Public repo (MIT) — nothing project-specific or confidential belongs in
  shipped themes or docs; see `TODO.md` for anything flagged along those
  lines

**Integration points:** none — this is a standalone CLI tool with no
external services, databases, or APIs.

## Current Architecture

**Contracts:**
- `CONTRACT-C1-THEME-SCHEMA.1.0` — verified
- `CONTRACT-C2-PROVENANCE.1.0` — verified
- `CONTRACT-C3-ROUNDTRIP.1.0` — verified

**Components:**
- `md2docx.py` — forward converter (Markdown → DOCX)
- `docx2md.py` — reverse converter (DOCX → canonical Markdown)
- `themes/` — three shipped JSON themes
- `architecture/` — the three contracts + registry
- `scripts/` — rebar Tier 3 enforcement
- `tests/` — round-trip test suite + kitchen-sink fixture

**Dependencies:**
- `python-docx` (runtime)
- Rebar framework v3.0.0 (methodology only — no rebar binaries vendored
  into this repo)

---

## Agent Guidelines for This Project

**When working on this project:**

1. **Check this file first** — understand current state before making changes
2. **Update this file** — when you change project state, update relevant sections
3. **Follow contract-first approach** — a change to theme keys, the
   provenance stamp fields, or the round-trip inversion table touches a
   contract; update the contract alongside the code
4. **Maintain quality gates** — run `scripts/check-*.sh` and
   `python3 tests/test_roundtrip.py` before committing

**Project-specific considerations:**
- The project is two flat Python files at repo root, not a `src/`-layout
  package — enforcement scripts are written for that (see `scripts/README.md`)
- The marking-style banner feature (`**CUI...**` first line) is generic
  and intentionally documented with a placeholder example
  (`**CUI//TEST**`) — never reference a real classification or
  confidentiality marking scheme in this repo

---

**Last updated by:** initial public release (2026-07-08)
**Next review:** when packaging (`pyproject.toml`) lands or the AST rewrite starts
