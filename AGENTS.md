# Agent Guidelines

<!-- FRESHNESS: Update this date every time you modify this file -->
<!-- freshness: 2026-07-08 -->

**How AI agents work effectively on md2docx.**

---

## Quick Start for New Agents (Cold Start / Read Before Coding)

### Essential Reading Order (5 minutes)
1. **README.md** — what is this project?
2. **QUICKCONTEXT.md** — what's true right now? (test status, active work, "What's Next")
3. **VERIFY:** Run `git log --since='7 days' --oneline | head -20` and
   cross-reference against QUICKCONTEXT claims. Flag any discrepancies.
4. **TODO.md** — what needs doing? (open items only, scannable in 10 seconds)
5. **This file** — how do we work together?

### Project Context
- **Project type:** CLI tool (two Python scripts + JSON themes)
- **Team size:** Solo (Will Ackerly)
- **Rebar tier:** 3 (Enforced) — contract refs, TODO tracking, freshness,
  ground truth, and compliance all enforced; see `.rebarrc` for why the
  full rebar Steward / ASK CLI is deliberately not part of this repo
- **Quality standards:** contract-first for the theme schema, provenance
  stamp, and round-trip guarantee; `python3 tests/test_roundtrip.py` green
  before every commit that touches `md2docx.py` or `docx2md.py`

---

## Contract-Driven Development

### Core Principle
**Don't implement without a contract. Don't modify code without checking its contract.**

Three components have behavioral specifications in `architecture/CONTRACT-*.md`:

| Contract | Covers |
|----------|--------|
| `CONTRACT:C1-THEME-SCHEMA.1.0` | Theme JSON keys, deep-merge semantics, template resolution order |
| `CONTRACT:C2-PROVENANCE.1.0` | DOCX core-properties provenance stamp fields |
| `CONTRACT:C3-ROUNDTRIP.1.0` | Canonical-MD round-trip guarantee (`docx2md`'s style→construct inversion) |

### The Four Contract Principles
1. **Don't implement without a contract** — if you're adding a fourth
   schema-level surface (a new theme key, a new provenance field, a new
   inversion rule), it needs a contract or a version bump to an existing one
2. **Don't modify code without checking its contract** — before changing
   `deep_merge()`, `stamp_provenance()`, or anything in `docx2md.py`'s
   inversion logic, read the relevant `CONTRACT-C*.md` file
3. **Don't update a contract without searching all implementations** —
   `grep -rn "CONTRACT:C1-THEME-SCHEMA" *.py themes/`
4. **Contract changes that break interfaces** → think it through before
   committing; this is a solo project, so "plan mode" means writing the
   change out in the contract's Change History table before touching code,
   not a multi-agent review

### Contract Linking

```python
"""md2docx — Markdown → styled DOCX, themed by a JSON template.

CONTRACT:C1-THEME-SCHEMA.1.0
CONTRACT:C2-PROVENANCE.1.0
"""
```

Both `md2docx.py` and `docx2md.py` declare their contracts in the module
docstring, within the first 15 lines. `scripts/check-contract-refs.sh`
verifies every `CONTRACT:` reference resolves to a real file.

---

## Agent Coordination

md2docx does not run the rebar ASK CLI or persistent role-based agents
(`ask architect`, `ask product`, `ask steward`, `ask englead`) — it's a
solo-maintained project small enough that the maintainer fills those roles
directly. If you're an agent working here, act as your own architect and
reviewer: read the relevant contract before changing behavior, and check
`scripts/check-compliance.sh` / `scripts/check-ground-truth.sh` the way a
steward agent would.

For **multi-agent fan-out** (rare at this scale — two ~300-400 line
Python files), see `agents/subagent-guidelines.md` and the available
templates in `agents/subagent-prompts-index.md`.

---

## Single Source of Truth for Metrics

Every quantitative claim in documentation has ONE authoritative source:
`METRICS.md`. `scripts/check-ground-truth.sh` verifies it against the
actual repo (file counts, test counts, contract counts). When you add or
remove a source file, a test, a contract, or a theme, update `METRICS.md`
and re-run the script — don't hand-edit the count anywhere else.

---

## Testing Cascade

**Fast inner loop, one rigorous gate before committing.** This project is
small enough that T0-T2 cover it; there's no deployed service, so
visual/E2E tiers (T4-T5) don't apply.

| Tier | Name | Speed | When to Run |
|------|------|-------|-------------|
| **T0** | Syntax | <1s | Every meaningful edit — `python3 -c "import md2docx, docx2md"` |
| **T1** | Targeted | <2s | Manually exercise the CLI on a scratch `.md` file while iterating |
| **T2** | Full suite | <2s | Before every commit — `python3 tests/test_roundtrip.py` (all 7 tests, no framework needed) |

**Quality enforcement (run before committing):**
```bash
scripts/check-contract-refs.sh
scripts/check-todos.sh
scripts/check-ground-truth.sh
python3 tests/test_roundtrip.py
```

### The Scout Rule: Zero Tolerance for Broken Tests

**You're a scout. Leave the camp cleaner than you found it.**

| Situation | Action |
|-----------|--------|
| Test fails after your change | Fix the code or fix the test |
| Test was already failing before your change | Fix it NOW — you found it, you own it |
| Skipped test | Fix the skip. Scope it properly or delete. Never leave a `skip`. |
| Obsolete test (behavior removed) | Remove carefully. Verify the behavior is actually gone. |

**Forbidden phrases:** "pre-existing failure," "not caused by our
changes," "flaky" without a root cause. This is a 7-test suite with zero
skips — keep it that way.

---

## Two-Tag System

### TODO Tracking
- **`TODO:` in code** = untracked = **blocks commit** (`scripts/check-todos.sh`)
- **`TRACKED-TASK:` in code** = tracked in `TODO.md` = commit allowed

```python
# BAD: This blocks commit
# TODO: handle escaped pipes in table cells

# GOOD: This is tracked and commit-safe
# TRACKED-TASK:TODO.md#markdown-it-py-ast-rewrite handle escaped pipes (fixed by the AST swap)
```

---

## Session Lifecycle

### Checkpoint (every few commits, or when context feels stale)
- Update `QUICKCONTEXT.md` (at minimum: timestamp + what shipped)
- Commit work-in-progress
- Re-run `python3 tests/test_roundtrip.py`

### Session End
- Update `QUICKCONTEXT.md` with current state (not aspirational)
- Update `TODO.md` — check off completed items, add newly discovered items
- Clean up worktrees if any were used: `git worktree list` → `git worktree prune`
- Verify: does `QUICKCONTEXT.md` match `git log --oneline -10`?

---

## Priority and Issue Tracking Rules

### Priority Tracking
- **`QUICKCONTEXT.md` "What's Next"** = the single source of truth for priorities
- **`TODO.md`** = detailed task list with context, NOT a separate priority list
- If both files have a priority ordering, `QUICKCONTEXT.md` wins

### Issue Tracking
- **`TODO.md` "Known Issues"** = what's broken + workaround + fix tracking
- **Cross-reference, don't duplicate.** One canonical entry per issue.

---

## Project-Specific Guidelines

### Domain Knowledge
- The forward converter (`md2docx.py`) is a **regex-based line parser**,
  not a real Markdown AST — it has known limits (see `TODO.md` § Known
  Issues) that `ROADMAP.md` §0 addresses by swapping to `markdown-it-py`.
  Don't patch around individual parser bugs; they're a known class fixed
  by that rewrite.
- The round-trip contract is **style-driven inversion**, not byte-for-byte
  symmetry. The forward converter's choice of Word style (`Heading 2`,
  `List Bullet`, a shaded paragraph, a left border) is itself the
  contract; changing which style marks a construct is a breaking change
  to `CONTRACT:C3-ROUNDTRIP.1.0`, not a free-standing bug fix.
- The marking-style banner feature (a `**CUI...**`-shaped first line) is
  generic and intentionally documented with a placeholder example
  (`**CUI//TEST**` in `tests/fixtures/kitchen-sink.md`). Never introduce a
  real classification or confidentiality marking string into this repo —
  it's public.

### Code Patterns
- Both scripts are single-file, stdlib + `python-docx` only. Don't add a
  new third-party dependency without updating `README.md`'s Install
  section and noting it in `METRICS.md`.
- Theme files (`themes/*.json`) are pure data — no theme should require a
  code change to load; `test_shipped_themes_load` in
  `tests/test_roundtrip.py` enforces this generically for any new file
  dropped into `themes/`.

### Integration Points
None — standalone CLI, no external services/APIs/databases.

---

## Autonomy Levels

### Current: Guided Development
- **READ** any project file to understand context
- **MODIFY** code within the three established contracts
- **CREATE** tests, documentation, new themes, new contracts (for genuinely
  new surfaces)
- **RUN** quality checks and enforcement scripts
- **UPDATE** `QUICKCONTEXT.md`, `TODO.md`, and `METRICS.md`

### What Requires Extra Care
- **Breaking a contract's Behavioral Contracts table** — requires a
  version bump and a Change History entry, not a silent edit
- **New third-party dependency** — note it in `README.md` and `METRICS.md`
- **Removing the marking-banner feature** — it's explicitly called out in
  `ROADMAP.md` as worth keeping; don't drop it without discussion

---

## Success Metrics

- Round-trip test suite stays at 0 failing, 0 skipped
- `scripts/check-compliance.sh` and `scripts/check-ground-truth.sh` pass
- Documentation (`README.md`, `ROADMAP.md`, `QUICKCONTEXT.md`) stays
  accurate to what the code actually does

---

**Remember:** this is a small, solo-maintained tool. The contracts and
enforcement scripts exist to keep the theme schema, provenance stamp, and
round-trip guarantee stable as the codebase grows toward `ROADMAP.md`'s AST
rewrite — not to simulate a large team's process on a two-file project.
