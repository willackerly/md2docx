# CONSUMES — external contract dependencies

<!-- last-synced: 2026-07-08 -->
<!-- format: rebar-consumes-v1 -->

This file declares which **external contracts** (owned by other rebar
repos) md2docx depends on.

**Current state: no entries.** md2docx is a standalone, single-repo
project — its three contracts (`architecture/CONTRACT-C1-THEME-SCHEMA.1.0.md`,
`CONTRACT-C2-PROVENANCE.1.0.md`, `CONTRACT-C3-ROUNDTRIP.1.0.md`) are all
owned locally, and it doesn't consume any contract from another rebar
repo. The file is kept (rather than deleted) so the format is documented
here for whoever adds the first real entry, and so
`scripts/check-compliance.sh`'s federation check (Check 8) has something
to find and correctly report as "present, no entries" rather than
"missing."

---

## Format

Each consumed contract is a top-level `## <owner_repo>/<contract_id>.<version>`
section with required and optional fields:

```markdown
## <owner_repo>/<contract_id>.<version>
- **owner_repo:** <owner_repo>
- **contract_id:** <contract_id>
- **version_pinned:** <MAJOR.MINOR.PATCH>
- **pin_date:** <YYYY-MM-DD>
- **rationale:** <why this project depends on it>
- **notify_on_change:** true   # OPTIONAL hint to owner
```

(Illustrative form only — placeholders, not a real entry. A real entry
replaces every `<...>` with a concrete value, e.g. `## rebar/C1-AGENTS.2.0`
with `owner_repo: rebar`, `contract_id: C1-AGENTS`, and so on.)

### Required fields

| Field | Format | Purpose |
|-------|--------|---------|
| `owner_repo` | bare repo name (e.g., `rebar`, `blindpipe`) | which rebar-adopting repo owns this contract |
| `contract_id` | `<prefix><N>-<NAME>` (e.g., `C1-AGENTS`) | the contract identifier in the owner's `architecture/` |
| `version_pinned` | semver `MAJOR.MINOR.PATCH` | the version your code is implemented against |
| `pin_date` | `YYYY-MM-DD` | when you pinned this version (helps owner age out stale pins) |
| `rationale` | one-line prose | why your project depends on this contract |

### Optional fields

| Field | Default | Purpose |
|-------|---------|---------|
| `notify_on_change` | (owner's call) | hint to owner: `true` = "I want notifications," `false` = "I'm a stable-pin acceptor, skip me," absent = "owner decides" |
| `extension_contracts` | `[]` | local contract IDs that augment the consumed contract |
| `notes` | (none) | free-form prose — known incompatibilities, planned upgrade, etc. |

### Composition over inheritance

If a future dependency needs more than the owner provides, write a local
contract that documents how it relates to the upstream one rather than
encoding "extends" semantics in this file.

---

## Tooling that uses this file

- **`rebar contract drift-check`** — would compare `version_pinned` to the
  owner's current version and flag deltas, if this file ever declares a
  real entry. `scripts/check-compliance.sh` (Check 8) verifies drift-check
  is wired into CI *once* an entry exists — with zero entries, that check
  is a no-op.
- **Owner-side `scan-consumers.sh`** (not shipped in this repo — md2docx
  is a consumer, not a rebar-contract owner other repos would scan for)

---

## Adoption

If md2docx ever depends on a contract from another rebar-adopting repo,
add a `## <owner>/<contract>.<version>` section here following the format
above. Until then, this file intentionally has no entries.
