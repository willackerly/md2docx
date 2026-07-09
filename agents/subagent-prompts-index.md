# Subagent Prompt Index

Catalog of available subagent templates for md2docx. Each entry links to
the full template in `subagent-prompts/`. See `agents/subagent-guidelines.md`
for the rules every invocation follows.

---

## Generation

| Template | Description | LOE | Mode |
|----------|-------------|-----|------|
| [build-theme](subagent-prompts/build-theme.md) | Design and ship a new `themes/*.json` theme against `CONTRACT:C1-THEME-SCHEMA.1.0` | Medium | single |

## Testing

| Template | Description | LOE | Mode |
|----------|-------------|-----|------|
| [verify-roundtrip](subagent-prompts/verify-roundtrip.md) | Verify a change against `CONTRACT:C3-ROUNDTRIP.1.0` — run the round-trip suite, extend `tests/fixtures/kitchen-sink.md` if a construct is uncovered | Medium | single |

<!-- Add new templates here, grouped by category, following the format in
     subagent-prompts/build-theme.md or verify-roundtrip.md. -->
