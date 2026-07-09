# md2docx

> **rebar v3.0.0** | **Tier 3: ENFORCED** | [What is rebar?](https://github.com/willackerly/rebar)

**Markdown ⇄ DOCX, themed by a JSON template, with a round-trip story.**

Two small command-line tools, no server, no framework:

- **`md2docx.py`** — converts Markdown to a styled `.docx`, themed by a JSON
  file. Headings, lists, tables, fenced code, inline formatting, blockquotes,
  and an optional marking-style banner all map to real Word styles.
- **`docx2md.py`** — converts that `.docx` back to canonical Markdown by
  inverting the same style choices, so editing the generated document in
  Word (or Google Docs) and converting it back doesn't silently lose or
  invent content.

---

## Install

```bash
pip install python-docx
```

That's the only dependency. Then run either script directly:

```bash
python3 md2docx.py notes.md
python3 docx2md.py notes.docx
```

(No packaging/entry-point yet — see `ROADMAP.md` §0 for the planned
`pyproject.toml` + `pipx install md2docx`.)

---

## Usage

### Markdown → DOCX

```bash
python3 md2docx.py file.md [more.md ...]            # writes <name>.docx next to each source
python3 md2docx.py -t themes/plum.json file.md      # explicit theme
python3 md2docx.py -o outdir file.md [more.md ...]  # write outputs into a directory
python3 md2docx.py -o out.docx file.md              # single input, explicit output path
python3 md2docx.py --no-footer file.md              # suppress footer text
```

**Markdown support:** h1–h4; bullet lists; literal numbered lists;
N-column pipe tables (first row = shaded header); fenced code blocks;
inline `` `code` ``, `**bold**`, `*italic*`; links (relative links keep
their label, absolute URLs get `(url)` appended — a print-friendly
demotion, not real hyperlinks yet); blockquotes; horizontal rules and
HTML comments are skipped; soft-wrapped lines join into one paragraph.

**Marking-style banner:** if the very first non-blank line of the source
is exactly `**SOMETHING**` starting with the literal text `CUI` (e.g.
`**CUI//TEST**`), it's promoted to the page header and replaces the
footer text — see `themes/marked-docs.json` for a theme designed around
this. The banner detection convention is generic (any `**CUI...**`-shaped
line); it doesn't reference any particular real-world marking scheme.

### DOCX → Markdown

```bash
python3 docx2md.py file.docx [-o out.md]      # default output next to input
```

Prints a provenance summary to stderr (see below) and writes canonical
Markdown next to the input, or to the path given with `-o`.

---

## Theme system

Every visual choice — fonts, colors, table shading, code block fill,
blockquote border, footer text, the marking banner's styling — lives in a
JSON theme file, not in the code. Themes deep-merge over a hard-coded
default: a theme only needs to specify the keys it wants to change.

**Template resolution order:**

1. `-t`/`--template` flag, if given
2. `md2docx-template.json` next to the script (a local override — not
   shipped in this repo)
3. `themes/neutral.json` next to the script
4. Hard-coded built-in defaults

**Shipped themes:**

| Theme | Description |
|-------|-------------|
| `themes/neutral.json` | The built-in defaults, as a documented, diffable file |
| `themes/plum.json` | A purple-accented house style |
| `themes/marked-docs.json` | Banner-forward: black-on-white, built for documents that carry a marking-style banner on every page |

Example — overriding just the H1 color and the table header fill:

```json
{
  "name": "My Theme",
  "headings": { "h1": { "color": "1D3557" } },
  "table": { "header_fill": "E8EEF5" }
}
```

Full key reference, deep-merge semantics, and resolution-order edge cases
are the subject of `architecture/CONTRACT-C1-THEME-SCHEMA.1.0.md`. JSONC
(`//` comments in theme files) and an `extends` chain between named themes
are planned — see `ROADMAP.md` §4 — but not implemented yet; today's theme
files are plain JSON with an informal `_comment` string key.

---

## Provenance stamp

Every generated `.docx` gets a compact JSON stamp written into its DOCX
core properties (`docProps/core.xml` — a standard Office Open XML part
every conforming reader preserves):

```
--- provenance stamp ---
  t: md2docx/0.2.0
  tpl: Plum
  tplsha: 5e2f...  (16-hex sha256 of the template file)
  srcsha: a91c...  (16-hex sha256 of the source .md file)
  gen: 2026-07-08T21:04Z
  subject (source path): ~/docs/example.md
  category (template):   Plum
  keywords: md2docx
------------------------
```

`docx2md.py` reads this back and prints it to stderr before converting —
it's how the reverse tool knows which theme produced a document's styling,
and (via `srcsha`) whether the original source file has changed since the
DOCX was generated. Full field-by-field spec:
`architecture/CONTRACT-C2-PROVENANCE.1.0.md`.

---

## Round-trip story

`md2docx` and `docx2md` are designed as a pair, not two independent tools:
the forward converter applies Word styles as a *deterministic function* of
Markdown constructs (`Heading 2` for `##`, a shaded+bordered paragraph for
a code block, a left-bordered indent for a blockquote, a mono-font shaded
run for inline code, and so on), and the reverse converter inverts that
same mapping.

That makes a real workflow possible: generate a `.docx`, hand it to
someone who edits it in Word, run `docx2md.py` on the result, and get back
**canonical Markdown** — one blank line between blocks, `-` bullets,
`**bold**`, no trailing whitespace — rather than a mess of Word's internal
formatting choices. `tests/test_roundtrip.py` proves this for every
construct the tools support: it converts `tests/fixtures/kitchen-sink.md`
forward, then back, and asserts the round trip loses nothing and invents
nothing (a structure-agnostic word-bag comparison — see the test file for
exactly what that means and what's deliberately out of scope, like
relative-link URLs and true byte-for-byte canonical-MD equality).

Honest limits — Google Docs strips non-standard OPC parts on import, links
are demoted rather than preserved as real hyperlinks, and 3-way merge
tooling doesn't exist yet — are documented in `ROADMAP.md` §7.5 and in
`architecture/CONTRACT-C3-ROUNDTRIP.1.0.md`.

**Where this is headed:** `ROADMAP.md` is the full hand-off plan — a
CommonMark AST rewrite, wide-table strategies, image support, JSONC
themes with an `extends` chain, and the rest of the symmetry track
(custom-XML source embedding, 3-way merge, a fidelity report).

---

## Development

```bash
pip install python-docx
python3 tests/test_roundtrip.py     # 7 tests, no test framework required
scripts/setup.sh                    # installs the pre-commit hook (once)
scripts/check-contract-refs.sh      # CONTRACT: refs resolve to real files
scripts/check-todos.sh              # no untracked TODO: comments
scripts/check-ground-truth.sh       # METRICS.md matches the repo
scripts/check-compliance.sh         # rebar badge / tier / contract maturity
```

See `QUICKCONTEXT.md` for current project state, `TODO.md` for open work,
and `AGENTS.md` / `CLAUDE.md` for how this repo expects an AI coding agent
to work in it.

---

## License

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 Will Ackerly.
