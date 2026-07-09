# Claude Code Configuration

**Claude-specific settings and context for md2docx.**

---

## Project Context

### What This Project Does

md2docx is a pair of command-line tools: `md2docx.py` converts Markdown to
a themed, styled `.docx`; `docx2md.py` converts that `.docx` back to
canonical Markdown by inverting the same style choices. See `README.md`
for the full picture and `ROADMAP.md` for where it's headed.

### Technology Stack
- **Language:** Python 3 (stdlib + one dependency)
- **Dependency:** `python-docx` (DOCX read/write)
- **Tests:** `tests/test_roundtrip.py` — no test framework, runs standalone
  via `python3 tests/test_roundtrip.py`

### Key Architecture Patterns
- **Contract-driven development** — three contracts in `architecture/`
  cover the theme schema, the provenance stamp, and the round-trip
  guarantee; see `AGENTS.md` § Contract-Driven Development
- **Style-driven round trip** — the forward converter's choice of Word
  style is the contract the reverse converter inverts, not an independent
  format
- **Theme-as-data** — every visual choice is a JSON key (`themes/*.json`),
  never a code branch

---

## Development Workflow

### Starting a Session

This repo has no `SessionStart` hook or `cold-start-checks.sh` — run the
checks manually at the start of a session:

```bash
scripts/check-contract-refs.sh
scripts/check-todos.sh
scripts/check-freshness.sh
scripts/check-ground-truth.sh
python3 tests/test_roundtrip.py
```

**Then orient:**
1. **Read the Cold Start Quad:**
   - `README.md` — project overview
   - `QUICKCONTEXT.md` — current state
   - **VERIFY:** `git log --since='7 days' --oneline | head -20` — cross-reference
     against QUICKCONTEXT claims. If the `last-synced` date is >1 week old,
     treat ALL claims as suspect.
   - `TODO.md` — active work (open items only)
   - `AGENTS.md` — coordination guidelines

2. **Check working-tree state:**
   ```bash
   git status
   git worktree list              # Check for abandoned worktrees
   scripts/refresh-context.sh     # Context freshness report
   ```

### Ending a Session
1. **Update `QUICKCONTEXT.md`** with current project state
2. **Update `TODO.md`** — mark completed items, add newly discovered items
3. **Clean up:** `git worktree prune` if any worktrees were used, commit
   any uncommitted work
4. **Verify:** does `QUICKCONTEXT.md` match `git log --oneline -10`?

### Adding a Feature
1. **Define success** — what construct/behavior is new, and how would
   `tests/test_roundtrip.py` prove it works?
2. **Check the relevant contract** in `architecture/` — does this change
   its Behavioral Contracts table? If so, that's a version bump, not a
   silent edit.
3. **Implement** in `md2docx.py` and/or `docx2md.py`
4. **Test:** extend `tests/fixtures/kitchen-sink.md` and
   `tests/test_roundtrip.py` if the change adds a construct; run the full
   suite
5. **Quality gates** before committing (see below)

### Making Changes
- **Before modifying `deep_merge()`, `resolve_template()`, or any theme
  key:** read `architecture/CONTRACT-C1-THEME-SCHEMA.1.0.md`
- **Before modifying `stamp_provenance()` or `print_provenance()`:** read
  `architecture/CONTRACT-C2-PROVENANCE.1.0.md`
- **Before modifying `docx2md.py`'s inversion logic (`runs_to_md`,
  `table_to_md`, `convert`) or the Word styles `md2docx.py`'s `Converter`
  applies:** read `architecture/CONTRACT-C3-ROUNDTRIP.1.0.md`

---

## Quality Standards

### Contract Compliance
- Both `md2docx.py` and `docx2md.py` declare their contracts in the module
  docstring's first 15 lines
- All `CONTRACT:` refs point to valid files — `scripts/check-contract-refs.sh`
- Behavioral specifications match implementation — the Behavioral
  Contracts table in each `CONTRACT-C*.md` is what tests verify against

### Testing Requirements
- `python3 tests/test_roundtrip.py` green (7/7) before every commit that
  touches `md2docx.py`, `docx2md.py`, or `themes/*.json`
- No skipped tests, ever (see `AGENTS.md` § The Scout Rule)

### Documentation
- Keep `QUICKCONTEXT.md` current with project state
- Track all tasks in `TODO.md` (no untracked `TODO:` comments — enforced
  by `scripts/check-todos.sh`)
- Update `METRICS.md` when file/test/contract/theme counts change, then
  re-run `scripts/check-ground-truth.sh`

---

## Agent Coordination

md2docx does not run the rebar ASK CLI (`ask architect`, `ask product`,
`ask steward`, `ask englead`) — see `AGENTS.md` § Agent Coordination for
why, and `agents/subagent-guidelines.md` for the (rare, small-scale)
multi-agent fan-out protocol this repo does use.

---

## Code Patterns

### Contract Headers
```python
"""md2docx — Markdown → styled DOCX, themed by a JSON template.

CONTRACT:C1-THEME-SCHEMA.1.0
CONTRACT:C2-PROVENANCE.1.0
"""
```

### TODO Tracking
```python
# TRACKED-TASK:TODO.md#markdown-it-py-ast-rewrite specific task description
# NOT: TODO: vague comment (this blocks commit)
```

### Error Handling
CLI errors use `sys.exit("message")` (prints to stderr, exit code 1) for
user-facing failures (missing file, malformed explicit `--template` path).
Uncaught exceptions (malformed JSON, corrupt DOCX) are allowed to
propagate as Python tracebacks — this is a small CLI tool, not a service
that needs to degrade gracefully under arbitrary input.

---

## Project-Specific Context

### Domain Knowledge
See `AGENTS.md` § Project-Specific Guidelines § Domain Knowledge — the
regex-parser limitations, the style-driven-inversion round-trip model, and
the marking-banner feature's generic (non-project-specific) design.

### Integration Points
None — standalone CLI, no external services.

### Deployment Context
None — this is distributed as source (eventually `pipx`-installable per
`ROADMAP.md` §0), not deployed as a service.

### Team Context
- **Rebar tier:** 3 (Enforced) — see `.rebarrc`
- **Team size:** Solo (Will Ackerly)
- **Quality requirements:** round-trip fidelity is the load-bearing
  guarantee; theme schema stability is second

---

## File Ignore Patterns

When working on this project, generally avoid modifying:
- `architecture/CONTRACT-*.md` without also updating the code that
  implements the changed contract (and vice versa)
- `scripts/` — rebar enforcement scripts (unless specifically updating
  rebar tooling)
- `METRICS.md` — update only via the process in `AGENTS.md` § Single
  Source of Truth for Metrics (change the code/tests first, then run
  `scripts/check-ground-truth.sh` to get the new numbers, then update
  this file to match)

Focus on:
- `md2docx.py` / `docx2md.py` implementation
- `themes/*.json`
- `tests/`
- Documentation updates
- Contract specifications

---

## Success Indicators

### Good Session Outcomes
- Clear understanding of current project state
- Changes match the relevant contract (or the contract was updated
  alongside the code, with a version bump)
- `python3 tests/test_roundtrip.py` green before every commit
- Documentation stays current

### Watch Out For
- Untracked `TODO:` comments in code
- `CONTRACT:` references that don't match a file in `architecture/`
- A theme or doc example that leaks project-specific or confidential
  material — this repo is public; keep examples generic
  (`~/docs/example.md`, `**CUI//TEST**`, etc.)
- Stale documentation or `METRICS.md` drift

---

**Remember:** this project uses rebar's contract-driven development
patterns at a scale proportionate to a solo-maintained, two-file CLI tool.
When in doubt, read the relevant contract, run the test suite, and keep
`QUICKCONTEXT.md` / `TODO.md` honest.
