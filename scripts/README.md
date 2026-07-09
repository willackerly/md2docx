# Scripts

Enforcement scripts for md2docx's rebar Tier 3 (Enforced) adoption. See the
[root README](../README.md) for the project itself, and `../.rebarrc` for
the tier declaration.

md2docx is a solo-maintained CLI tool — it does not run the rebar Steward,
`ci-check.sh`, or `compute-registry.sh` from the broader rebar project.
This is the deliberately small subset of enforcement scripts a Tier 3
solo/cli-tool adopter runs directly (see `.rebarrc`'s `SKIP_BOOTSTRAP_SYNC`
note and the `cli-tool` profile this repo followed).

## Enforcement Checks

Each script is standalone, runs in a few seconds, and exits 0 (pass) or 1 (fail).

| Script | What It Checks |
|--------|---------------|
| `check-contract-refs.sh` | Every `CONTRACT:` ref in source points to a real `architecture/CONTRACT-*.md` file |
| `check-todos.sh` | No untracked `TODO:` comments (two-tag system — see `AGENTS.md`) |
| `check-freshness.sh` | Doc `freshness:` markers aren't stale (>14 days) |
| `check-ground-truth.sh` | `METRICS.md` matches codebase reality (file counts, test counts, contract counts) |
| `check-compliance.sh` | `.rebar-version`, `.rebarrc`, the README badge, and `AGENTS.md` all agree, plus contract maturity weighting |

## Composite / Setup

| Script | When to Run |
|--------|-------------|
| `pre-commit.sh` | Git hook — runs TODOs, contract refs, and ground truth (the fast checks) |
| `setup.sh` | One-time: symlinks `pre-commit.sh` as `.git/hooks/pre-commit` |
| `refresh-context.sh` | Session start / checkpoint — QUICKCONTEXT freshness + worktree state |

## Installation

```bash
scripts/setup.sh   # symlinks the pre-commit hook, chmods scripts/*.sh
```

## Running Everything

There is no `ci-check.sh` in this repo (see the note above). Run the full
suite directly:

```bash
scripts/check-contract-refs.sh
scripts/check-todos.sh
scripts/check-freshness.sh
scripts/check-ground-truth.sh
scripts/check-compliance.sh
python3 tests/test_roundtrip.py
```

## Dependencies

- **bash** — all scripts are bash
- **grep, find, date** — standard Unix tools (both GNU and BSD `date` are handled)
- **python3** with `python-docx` — for `tests/test_roundtrip.py` (not the shell scripts)
