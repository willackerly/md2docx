# Contract Registry

md2docx is a solo-maintained CLI tool (no rebar Steward, no
`compute-registry.sh` — see `architecture/README.md`), so this registry is
hand-maintained. `scripts/check-contract-refs.sh` is the enforcement
mechanism that keeps every `CONTRACT:` reference in source honest against
the files listed here.

**To verify it's current:**
```bash
scripts/check-contract-refs.sh
```

---

## Components

| ID | Version | Status | Impl Files | Purpose |
|----|---------|--------|------------|---------|
| C1-THEME-SCHEMA | 1.0 | verified | 4 | Theme JSON schema, deep-merge semantics, template resolution order |
| C2-PROVENANCE | 1.0 | verified | 2 | DOCX core-properties round-trip provenance stamp |
| C3-ROUNDTRIP | 1.0 | verified | 4 | Canonical-MD round-trip guarantee (docx2md's style→construct inversion) |

## Contract Files

- `CONTRACT-C1-THEME-SCHEMA.1.0.md`
- `CONTRACT-C2-PROVENANCE.1.0.md`
- `CONTRACT-C3-ROUNDTRIP.1.0.md`

## Owners

All three contracts: Will Ackerly (sole maintainer).

## Known Consumers

Single-repo project — no external (cross-repo) consumers yet. If md2docx is
ever vendored or imported by another project, that project should add a
`CONSUMES.md` declaring which contract version it pins to (see
`CONSUMES.md` in this repo for the format).

## Quick Audit (manual — no `compute-registry.sh` in this repo)

```bash
# Contracts with no implementing code (orphaned contracts)
for f in architecture/CONTRACT-C*.md; do
  id=$(basename "$f" .md | sed 's/CONTRACT-//')
  count=$(grep -l "CONTRACT:$id" -- *.py 2>/dev/null | wc -l)
  [ "$count" -eq 0 ] && echo "ORPHAN: $f (0 implementing files)"
done

# Code with contract refs pointing to non-existent contracts
scripts/check-contract-refs.sh
```
