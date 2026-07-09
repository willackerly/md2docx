# Subagent Guidelines

Shared behavioral contract for any subagent invocation on md2docx. Read
this before starting work if you were pointed at a template in
`agents/subagent-prompts/`.

md2docx is a small, solo-maintained CLI tool (two ~300-400 line Python
files, a handful of themes, one test file). Multi-agent fan-out at this
scale is rare — the value of a written protocol is in the occasional
case where two agents (or an agent and the maintainer) touch the repo at
overlapping times, not in coordinating a large swarm.

## Context Loading Order

1. **This file** — you're here
2. **Your assigned template** from `agents/subagent-prompts/<template>.md`
3. **QUICKCONTEXT.md** — project orientation (branch, test status, active work)
4. **The contract(s) your task touches**, in `architecture/CONTRACT-*.md`

## The Rules

### Rule 1: Worktree isolation for code changes

If you are writing code (not just reading/analyzing), work in a `git
worktree`, not directly on `main`:

```bash
git worktree add ../md2docx-<task-slug> -b <task-slug>
```

Read-only tasks (research, review, audits) may run in the main working
tree.

### Rule 2: Commit after every logical chunk

Don't accumulate uncommitted changes across a long session — a crash or a
lost terminal loses anything uncommitted. One fix = one commit, following
`conventions` (see `AGENTS.md` § Contract-Driven Development for the
commit message format: `<type>(<contract-id>): <description>`).

### Rule 3: Strict file ownership

If your task specifies which files you may touch, honor that allowlist.
Absent an explicit allowlist, stay within files directly related to your
assigned task. `md2docx.py`, `docx2md.py`, and the files under
`architecture/` and `scripts/` are shared, high-conflict surfaces — if two
tasks touch the same one, coordinate before both proceed.

### Rule 4: No removals without explicit authorization

Add freely — types, functions, tests, files. Don't remove or rename
something you didn't add unless the task explicitly says to, since you
may not be able to see everything that depends on it.

### Rule 5: Measure before and after

Run `python3 tests/test_roundtrip.py` before your first change and after
each fix. If it regressed, that's signal — don't guess.

### Rule 6: Run the relevant enforcement scripts before finishing

```bash
scripts/check-contract-refs.sh
scripts/check-todos.sh
python3 tests/test_roundtrip.py
```

### Rule 7: Commit before completing

A worktree is only durable once its work is committed. Uncommitted changes
in a worktree that gets pruned are lost work.

## Verify Before Relying

If a task brief (from the maintainer, from another agent's findings, or
from a stale doc) makes a specific factual claim — a file path, a function
name, a line number, "the tests already pass" — and you find it doesn't
match source, stop and note the discrepancy rather than building on it.
Docs and memory are recall, not ground truth; the diff and the test run
are.

## Results & Output

Write results to the location specified in your task. If none is
specified and your task produced a written finding (not just a code
change), write it to `agents/results/<template-name>-<scope>.md`.

## Architectural Change Detection

If your work reveals or requires any of the following, don't silently
proceed — flag it in your results instead:

- A change to `architecture/CONTRACT-C1-THEME-SCHEMA.1.0.md`'s schema keys
  (breaks every theme in `themes/`)
- A change to `architecture/CONTRACT-C2-PROVENANCE.1.0.md`'s stamp fields
  (breaks `docx2md.py`'s provenance readback)
- A change to `architecture/CONTRACT-C3-ROUNDTRIP.1.0.md`'s inversion table
  (breaks the round-trip guarantee)
- A new third-party dependency
- Anything that would change `md2docx.py`'s or `docx2md.py`'s public CLI
  flags or output format
