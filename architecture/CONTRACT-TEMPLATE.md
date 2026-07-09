# CONTRACT-{ID}-{NAME}.{MAJOR}.{MINOR}

<!-- Copy this file to create a new contract.
     Replace all {placeholders} with actual values.
     Remove these HTML comments when done. -->

<!-- VERSIONING:
     - When this contract is superseded, add: SUPERSEDED BY: CONTRACT-{ID}-{NAME}.{NEW}
       and set its Status: to `superseded` (terminal — excluded from maturity weighting)
     - When this contract supersedes another, add: SUPERSEDES: CONTRACT-{ID}-{NAME}.{OLD}
-->

**Version:** {MAJOR}.{MINOR}
**Status:** stub | draft | in-progress | active | verified
<!-- DECLARED maturity — pick exactly one, honestly: `verified` means active +
     passing tests/scenarios prove it (never assumed). See architecture/README.md
     for the full vocabulary. -->
**Owner:** [team or person responsible]
**Type:** Service | Component | Interface | Protocol | Data Model | Operational | Integration Seam
**Cross-repo Promotability:** Yes/No — if yes, name candidate adopting repos
**Source:** [link to a design doc, roadmap section, or issue]

## Why this exists

<!-- REQUIRED. Two or three sentences in domain language a non-engineer could
     read. What user need does this serve? What changes if we don't have it? -->

## Who needs this

<!-- REQUIRED. Distinct list of consumers — other contracts, callers, users. -->

- **Consumer A** — what they need from this contract
- **Consumer B** — what they need

## Scenarios (illustrative)

<!-- REQUIRED. Two or three concrete walk-throughs that make this contract
     vivid. Each scenario should answer: who initiates, what travels through
     this contract, what success looks like, what failure looks like. -->

### Scenario 1 — short title

2-4 sentences. Show the contract being exercised concretely.

### Scenario 2 — short title

2-4 sentences. Pick a different angle (failure path, multi-step, edge case).

## Interfaces

<!-- Define the public interface(s) this contract specifies. -->

```python
def example(arg: str) -> str:
    """One-line description."""
```

## Behavioral Contracts

<!-- Define behaviors that the type system can't enforce.
     These are the things contract tests verify. -->

| Behavior | Specification |
|----------|--------------|
| Example behavior | Example specification |

## Error Contracts

<!-- Define the error types/codes this contract uses. -->

| Error | When | Code |
|-------|------|------|
| Example error | Example condition | Example code |

## Dependencies

<!-- What does this component depend on? Other contracts, external libraries,
     configuration. -->

- Depends on: none / `CONTRACT:{ID}.{VERSION}`
- Configuration: [env var or flag, if any]
- External: [library, if any]

## Cross-references

<!-- Beyond formal dependencies — what does this connect to? -->

- **Source docs:** [ROADMAP.md section, design doc, etc.]

## Future evolution

<!-- OPTIONAL. Required when this contract is provisional or has known horizon
     limits. -->

- Provisional assumption 1.
- Major-bump trigger.

## Retirement / supersession plan

<!-- REQUIRED when this contract supersedes another OR is itself superseded.
     OPTIONAL otherwise. -->

- **Predecessor:** `CONTRACT-<ID>.<old-version>` — retirement criterion: `grep -rn "<old-id>"` returns zero
- **Migration deadline:** YYYY-MM-DD or named phase boundary
- **Migration owner:** [team or person responsible for the cutover]

## Implementing Files

<!-- List all files that implement this contract.
     Keep updated — or regenerate with:
     grep -rn "CONTRACT:{ID}-{NAME}" *.py
-->

- `path/to/file.py` — description

## Test Requirements

<!-- What must be tested? Contract tests are king. -->

- [ ] Every behavior in the table above has a test
- [ ] Every error contract has a test (trigger the error, verify type/code)

## Companion File

<!-- Every contract MAY have a companion file: `CONTRACT-{ID}-{NAME}.impl.md`
     (no version number in the companion filename). Holds tribal knowledge
     that supports the contract but doesn't define behavior. -->

## Change History

| Version | Date | Change | Migration |
|---------|------|--------|-----------|
| 1.0 | YYYY-MM-DD | Initial contract | — |
