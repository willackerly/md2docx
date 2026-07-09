# md2docx — Generalization Roadmap

*Hand-off plan for turning `md2docx.py` (working single-file prototype) into a
robust, themeable MD→DOCX tool. Current prototype: regex line-parser +
python-docx, themed by a JSON template (see `themes/`), CUI-style banner
promotion, soft-wrap joining. It works; this plan is about where it breaks and
what to build next.*

---

## 0. The one architectural decision that matters

**Replace the hand-rolled line parser with a real CommonMark AST.**

Use `markdown-it-py` (CommonMark-compliant, GFM tables/strikethrough via plugins,
pure Python, actively maintained). Walk the token stream with a renderer class;
the theme stays pure data.

Why first: every feature below (nested lists, footnotes, callouts, syntax
highlighting, images) is a token handler on an AST, but a fragile regex special
case on the current parser. The prototype already mis-handles: nested emphasis
(`**bold *italic* bold**`), escaped pipes in table cells, backticks inside code
spans, multi-paragraph list items, indented code blocks, setext headings, hard
line breaks. One afternoon of AST swap deletes all of those bugs at once.

Shape:

```
md2docx/
  core.py        # AST walk → docx (importable: convert(src, theme, out))
  themes.py      # JSONC load, extends-chain, schema validation
  tables.py      # wide-table strategy (see §2)
  images.py      # image resolution + SVG rasterize (see §3)
  cli.py         # argparse wrapper, console_script entry point
  themes/        # prebaked themes (see §4)
  tests/         # golden corpus + visual regression (see §6)
```

Package with `pyproject.toml`, entry point `md2docx`, installable via `pipx`.
Keep `convert()` importable — scripting integrations should call the library,
not shell out.

---

## 1. Code blocks (heavy use — make them first-class)

| Feature | Approach | Priority |
| :--- | :--- | :--- |
| Syntax highlighting | Pygments tokenizer → colored runs. Language from the fence info string (```` ```python ````). Token-color map lives in the theme (`code.highlight: {keyword, string, comment, ...}`) so light/dark themes restyle code too. Soft dependency: no Pygments → plain monospace, warn once. | P1 |
| Long-line handling | Print has no horizontal scroll. Tiered, in theme config: (1) wrap with a visible continuation glyph (`↩`) and hanging indent; (2) optional auto-shrink — compute the block's max line length, step font down to a floor (default 7pt) before wrapping. | P0 |
| Block container | Render the block inside a 1×1 borderless table cell with fill instead of per-paragraph shading: gives real padding, a box border option, and `cantSplit` control for short blocks (keep-together ≤ N lines; long blocks must break across pages). | P1 |
| Fidelity details | Preserve leading whitespace exactly (`xml:space="preserve"`), tabs → configurable spaces, trailing blank line trimmed. Optional line numbers (theme flag). | P0/P2 |
| Inline code | Already styled; add proper padding via character shading + non-breaking behavior for short spans. | P1 |

---

## 2. Tables (frequent + the wide-table problem)

**Baseline improvements (P0):**
- Column alignment from the separator row (`:---`, `:---:`, `---:`) — currently ignored.
- Header row repeats on page breaks (`w:tblHeader`).
- Column widths proportional to content (measure max rendered length per column, clamp min/max) instead of Word autofit guessing.
- Theme options: zebra striping, first-column emphasis, cell padding, border color/weight.

**Wide-table strategy — auto-select by measured width (the interesting part):**

Compute an estimated natural width (columns × per-column content width at the
theme's cell font). Then walk an escalation ladder, each rung configurable and
cap-able in the theme (`table.wide_strategy: ["shrink", "landscape", "chunk", "cards"]`):

1. **Fits portrait** → render normally.
2. **Shrink** — step cell font down (default floor 8pt) and tighten padding. Cheap, handles the 10–20% overflow case.
3. **Landscape section** — the "new page, horizontal" idea, and it's very doable in OOXML: close the current section, emit the table in a new section with `w:orient="landscape"` (swapped page dims), then resume portrait. Reader sees a rotated page just for that table. This should be the workhorse for genuinely wide tables.
4. **Column chunking** — split columns into groups that each fit, repeating the key (first) column in every chunk, stacked vertically with "(cont'd)" captions. Best for very wide, many-row matrices where landscape still isn't enough.
5. **Record cards** — transpose each row into a label/value mini-table. Best when rows are entities and columns are attributes; reads beautifully in portrait. Offer as an explicit per-table override rather than an automatic guess.

Per-table override via an HTML comment directive the tool already skips today —
make it meaningful: `<!-- md2docx: table=landscape -->` above a table beats the
auto-heuristic. Directives are the cleanest general escape hatch; reserve the
namespace now (`<!-- md2docx: key=value ... -->`).

---

## 3. Images (SVG / PNG / JPG references)

- **PNG/JPG (P0):** `![alt](path)` → `add_picture`, path resolved relative to the source MD, scaled to content width (never upscale), alt text stored as accessible description. Optional caption from the alt or title text: italic, small, centered, auto-numbered "Figure N" (theme-controlled).
- **SVG (P0):** two options, recommend (b) now, (a) later:
  - (a) Native dual-part embedding (Word 2016+ supports real SVG with a PNG fallback part) — highest fidelity, but hand-rolled OOXML relationships; a P2 upgrade.
  - (b) **Rasterize at 2× DPI** via `cairosvg` (pip-only, no system deps) → embed PNG. Soft dependency; if missing, emit the link text and a warning with the line number.
- **Remote URLs:** off by default (a doc build should not phone home); `--fetch-remote` opt-in with timeout. Security posture matters if the theme's marking/banner feature is in use on these docs.
- **Mermaid fences (P2):** if `mmdc` is on PATH, render ```` ```mermaid ```` blocks to embedded diagrams; otherwise style as a code block with a notice.
- **Broken references:** never hard-fail the whole build — placeholder box with the path, warning to stderr, nonzero exit only under `--strict`.

---

## 4. Theming: JSONC, prebaked themes, branding

- **JSONC (P0):** allow `//` and `/* */` comments (strip before `json.loads`, or take the tiny `pyjson5` dep). Ship each prebaked theme as a heavily commented `.jsonc` that doubles as the documentation (the current `_comment` string key in the shipped `.json` themes is a stopgap for this).
- **`extends` (P0):** `"extends": "neutral"` deep-merges over a parent theme (the merge code already exists — see `deep_merge()` in `md2docx.py`). Themes resolve by name from the registry (below), by path, or built-in.
- **Theme registry (P0):** `md2docx/themes/` shipped with the package + user dir `~/.config/md2docx/themes/`. `-t plum` resolves by name. Prebaked set:
  - `neutral` — the current built-in defaults, documented (shipped).
  - `plum` — a purple-accented house style (shipped).
  - `marked-docs` — banner-forward: black marking-style header/footer on every page, restrained palette, portion-marking-friendly (shipped).
  - `compact-print` — smaller everything, tighter spacing, for long technical docs (planned).
  - `brief` — big headings, generous whitespace, for exec one-pagers (planned).
- **Logo/branding in the theme, not the MD (P0):**
  ```jsonc
  "branding": {
    "logo": { "path": "~/assets/logo.png",
              "width_in": 1.4,
              "placement": "first-page",   // first-page | every-page | none
              "align": "left" },
    "cover_page": false                    // P1: title/subtitle/date cover from H1+frontmatter
  }
  ```
  Implementation: Word's first-page-header mechanism (`w:titlePg`) puts the logo on page 1 only while a marking banner or footer text runs on every page — they compose cleanly. `every-page` just uses the default header. SVG logos go through the §3 rasterizer.
- **Header/footer tokens (P0):** `{page}` / `{pages}` (real PAGE/NUMPAGES field codes — page numbers are the most-missed feature of the prototype), `{title}` (first H1 or frontmatter), `{date}`.
- **Schema + validation (P1):** publish a JSON Schema for the theme format → editor autocomplete, and friendly "unknown key 'headerfill', did you mean 'header_fill'?" errors on load.

---

## 5. Markdown coverage to close (roughly ordered by how soon it'll bite)

1. **Real hyperlinks (P0)** — clickable `w:hyperlink` runs (relationship per URL) instead of the current "label (url)" demotion; keep demotion as a theme option for print. Internal `#anchor` links → Word bookmarks on headings.
2. **Nested lists + real numbering (P0)** — indent-level detection is free with the AST; ordered lists get a proper `numbering.xml` instance per list so numbering restarts correctly (kills the current literal-text workaround).
3. **Callout/admonition boxes (P1)** — convention: blockquote starting with `**Note:**`, `**Warning:**` etc. renders as a filled, bordered box with a type color from the theme.
4. **Table of contents (P1)** — `toc: true` in theme or `[TOC]` marker → insert a native TOC field (headings already use real Heading styles, so Word populates it; readers press F9 or it fills on open). Pairs with bookmarks from item 1.
5. **YAML frontmatter (P1)** — parse into doc properties (title/author/date) and expose as header/footer tokens; don't render it.
6. **Strikethrough, task lists (P1)** — `~~x~~` → strike run; `- [ ]` / `- [x]` → ☐/☒ glyphs.
7. **Footnotes (P2)** — real Word footnotes need hand-built `footnotes.xml`; markdown-it has the plugin; worth it eventually, not soon.
8. **HTML passthrough policy (P2)** — define graceful degradation for `<br>` (line break), `<sup>/<sub>` (run properties), `<details>` (render summary bold + body indented); everything else stripped with a warning.
9. **h5/h6, horizontal rule as a styled divider, hard line breaks** (P1, trivial with AST).

---

## 6. Quality & tooling

- **Golden corpus tests:** real-world docs (the kind with headings, tables, code, blockquotes, and marking banners) are the corpus. Convert each; assert structural invariants (heading/table/image counts, no dropped text vs. source token stream, banner in header XML). `tests/fixtures/kitchen-sink.md` + `tests/test_roundtrip.py` are the first slice of this.
- **Visual regression:** render page 1 via `qlmanage -t` (no Word needed) and image-diff against checked-in baselines. Full-PDF diff via Word automation only in a manual pre-release pass (Word scripting is flaky: sandbox path limits, modal-dialog AppleEvent timeouts).
- **Warnings discipline:** every unsupported construct emits `file:line: message`; `--strict` turns warnings into failure. Silent feature-dropping is how trust in a doc tool dies.
- **Google Docs import check** (manual, per release): if generated DOCX files get uploaded to Google Docs, verify headers/footers, table shading, and landscape sections survive the import.

---

## 7. Symmetry: DOCX → MD round-trip

Goal: someone edits the generated DOCX in Word (or Google Docs) and we can get a
faithful MD back — knowing which template produced it, what changed, and merging
those changes into the source of truth. Perfect byte-symmetry is impossible (MD
has many spellings for the same rendering), so the design is: **canonical MD +
style-driven inversion + embedded provenance + 3-way merge.**

### 7.1 Why this is tractable at all

The forward converter is a *deterministic function from MD constructs to Word
styles*. If the reverse tool knows the template, it inverts the mapping:
`Heading 2` → `##`, `List Bullet` → `- `, monospace-shaded run → `` ` ``,
theme's header-fill on row 1 → table header, left-bordered gray indent →
blockquote, code-fill paragraphs → fenced block. Human editing in Word is
style-preserving by default (typing into a paragraph inherits its style), so
style-based inversion survives most real-world edits.

**Design rule that follows:** the forward converter should apply formatting via
*named custom styles* (`MD Code Block`, `MD Blockquote`, `MD Table Header`…)
rather than direct run/paragraph formatting wherever possible. Named styles are
the reverse tool's ground truth; direct formatting is guesswork. This also makes
themes cleaner (restyle = redefine styles).

### 7.2 Breadcrumbs, in order of survivability

| Mechanism | What to store | Survives Word edits | Survives Google Docs | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Core properties** (`docProps/core.xml`) | Compact JSON in `comments`: tool/version, template name, template hash (16-hex), source hash, timestamp; full source path in `subject`; `keywords: md2docx`; `category`: template name | Yes — standard OPC part, Word preserves and shows in File → Info | Partially (title/subject/keywords usually survive export) | **SHIPPED in v0.2.0** |
| **Custom XML part** (`customXml/item1.xml`) | The *entire source MD* (and optionally the resolved theme JSON), so the DOCX carries its own origin | Yes — custom XML parts are designed to persist through editing | **No — stripped on GDocs import** | P0 of this workstream |
| **Table captions** (`w:tblCaption`) + alt text | Per-table: original MD table form + which wide-table strategy was applied (landscape/chunk/cards), so the reverse tool can un-transform | Yes | Mostly no | P1 |
| **Heading bookmarks** | Stable anchor slugs on each heading (also powers internal links / TOC) | Yes | Weakly | P1 |
| **Content controls (SDTs)** per block, tagged with source line ranges | Fine-grained block↔line mapping for surgical merge | Yes — SDTs are built for document assembly | No | P2 — invasive; only if per-line merge fidelity proves necessary |

### 7.3 The reverse tool (`docx2md`)

1. Read core props → recover template identity (name + hash → fetch exact theme even if the file was renamed) → build the inverse style map.
2. Extract the embedded source MD from the custom XML part (if present) — this is the **merge base**.
3. Walk `document.xml`: invert styles to MD constructs; tables → pipe tables (consult `tblCaption` breadcrumbs to un-transform landscape/chunked/card tables); hyperlinks → `[label](url)`; images → extract from `word/media/` into an assets dir, emit `![alt](path)` using the alt text the forward pass stored.
4. Emit **canonical MD** (see 7.4).
5. **3-way merge**: base = embedded original MD; theirs = regenerated MD from the edited DOCX; mine = current MD on disk (which may have moved on since the DOCX was generated — detectable because its hash no longer matches `srcsha`). Use `git merge-file` semantics; conflicts surface as normal conflict markers. This turns "someone edited the Word doc" from a disaster into a mergeable branch.
6. **Fidelity report**: anything that didn't invert cleanly (direct formatting with no style, unknown constructs, images added in Word) is listed with locations rather than silently dropped or invented.

### 7.4 Canonical MD (the symmetry contract)

Define one canonical spelling (like Prettier): `-` bullets, `**` bold, fenced
code with language tags, pipe tables padded to uniform width, one blank line
between blocks. Guarantee: `docx2md(md2docx(x)) == canonicalize(x)`. Ship
`md2docx --normalize` so sources can be pre-canonicalized; after that the
round-trip is idempotent and diffs are pure signal. Add a `--check` CI mode
that round-trips every doc and fails on fidelity loss.

### 7.5 Honest limits

- **Google Docs is the weak link**: it strips custom XML, SDTs, and most custom
  properties on import. A GDocs-edited doc round-trips at "style-inference only"
  tier — still workable (headings/lists/tables map), but without the embedded
  merge base. If GDocs editing is the primary workflow, keep the merge base
  *outside* the file (e.g., `srcsha` → git object lookup: the hash already
  stamped in core props is enough to find the exact source version in the repo).
- **Formatting invented in Word** (manual colors, text boxes, floating images)
  has no MD equivalent — the fidelity report flags it; the merge keeps the text.
- **Tracked changes**: reject-or-accept before reverse conversion; `docx2md`
  should refuse files with pending revisions rather than guess.

---

## 8. Suggested phasing

| Phase | Contents | Effort (rough) |
| :--- | :--- | :--- |
| **P0 — foundation** | markdown-it-py AST swap; package layout + CLI; JSONC themes + registry + `extends`; logo/branding + first-page header; page-number tokens; real hyperlinks; nested lists/numbering; PNG/JPG + SVG-rasterize images; wide-table rungs 1–3 (shrink + landscape); code-block wrap/shrink; warnings framework | ~1 week |
| **P1 — polish** | Pygments highlighting; callout boxes; TOC + bookmarks; table alignment/zebra/header-repeat; column-chunking + record-card table modes; frontmatter; schema validation; strikethrough/task lists; golden + visual tests | ~1 week |
| **P2 — depth** | Footnotes; native SVG embedding; mermaid; HTML passthrough; cover pages; pipx publishing; per-table/per-block directive vocabulary | as needed |
| **Symmetry track** (parallel, see §7) | P0: named custom styles in forward converter; embed source MD as custom XML part; canonical-MD normalizer. P1: `docx2md` style-inversion + 3-way merge + fidelity report; table-caption breadcrumbs. P2: SDT block tagging. Core-properties provenance stamp already shipped (v0.2.0). | ~1 week for P0+P1 |

**Two things to keep from the prototype:** the marking-banner promotion (it's a
genuinely useful, un-Googleable behavior) and the theme deep-merge. **One thing
to retire:** every regex in the parsing path.
