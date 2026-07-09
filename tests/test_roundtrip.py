#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Tests for md2docx.py / docx2md.py.

Exercises CONTRACT:C1-THEME-SCHEMA.1.0, CONTRACT:C2-PROVENANCE.1.0, and
CONTRACT:C3-ROUNDTRIP.1.0 — see architecture/CONTRACT-C1-THEME-SCHEMA.1.0.md,
architecture/CONTRACT-C2-PROVENANCE.1.0.md, and
architecture/CONTRACT-C3-ROUNDTRIP.1.0.md for the specifications these
tests verify.

No test framework required — this is a plain script:
  python3 tests/test_roundtrip.py

(pytest also picks up the test_* functions if you have it installed and
prefer `pytest tests/`, but that is not a requirement of this project.)
"""
import hashlib
import json
import re
import sys
import tempfile
import traceback
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import md2docx  # noqa: E402
import docx2md  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"
THEMES = REPO_ROOT / "themes"


# ---------------------------------------------------------------------------
# CONTRACT:C1-THEME-SCHEMA.1.0
# ---------------------------------------------------------------------------

def test_theme_deep_merge():
    base = {"a": 1, "b": {"x": 1, "y": 2}, "c": [1, 2]}
    over = {"b": {"y": 20}, "c": [9], "d": 4}
    merged = md2docx.deep_merge(base, over)

    assert merged["a"] == 1, "untouched top-level key must survive"
    assert merged["b"]["x"] == 1, "untouched nested key must survive"
    assert merged["b"]["y"] == 20, "overridden nested key must take the new value"
    assert merged["c"] == [9], "non-dict values (lists) replace wholesale, not merge element-wise"
    assert merged["d"] == 4, "new keys in `over` are added"

    # Real schema: overriding one heading level must not blow away the others.
    partial = {"headings": {"h1": {"size_pt": 24}}}
    merged = md2docx.deep_merge(md2docx.DEFAULTS, partial)
    assert merged["headings"]["h1"]["size_pt"] == 24
    assert merged["headings"]["h1"]["color"] == md2docx.DEFAULTS["headings"]["h1"]["color"]
    assert merged["headings"]["h2"] == md2docx.DEFAULTS["headings"]["h2"]
    assert merged["fonts"] == md2docx.DEFAULTS["fonts"]


def test_template_resolution_order():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)

        # 1. Nothing present anywhere -> hard-coded DEFAULTS.
        cfg, tpl_path, msg = md2docx.resolve_template(None, base_dir=base)
        assert cfg == md2docx.DEFAULTS
        assert tpl_path is None
        assert "built-in defaults" in msg

        # 2. themes/neutral.json present -> used.
        (base / "themes").mkdir()
        (base / "themes" / "neutral.json").write_text(
            json.dumps({"name": "Neutral", "fonts": {"body": "Georgia"}}))
        cfg, tpl_path, msg = md2docx.resolve_template(None, base_dir=base)
        assert cfg["fonts"]["body"] == "Georgia"
        assert tpl_path == base / "themes" / "neutral.json"

        # 3. md2docx-template.json next to the script beats themes/neutral.json.
        (base / "md2docx-template.json").write_text(
            json.dumps({"name": "Local Override", "fonts": {"body": "Verdana"}}))
        cfg, tpl_path, msg = md2docx.resolve_template(None, base_dir=base)
        assert cfg["fonts"]["body"] == "Verdana"
        assert tpl_path == base / "md2docx-template.json"

        # 4. An explicit --template flag beats everything, even a bogus one
        #    (which must fail loudly rather than silently fall back).
        explicit = base / "explicit.json"
        explicit.write_text(json.dumps({"name": "Explicit", "fonts": {"body": "Times"}}))
        cfg, tpl_path, msg = md2docx.resolve_template(str(explicit), base_dir=base)
        assert cfg["fonts"]["body"] == "Times"
        assert tpl_path == explicit

        try:
            md2docx.resolve_template(str(base / "does-not-exist.json"), base_dir=base)
            raise AssertionError("expected SystemExit for a missing explicit --template path")
        except SystemExit as e:
            assert "not found" in str(e)


def test_shipped_themes_load():
    shipped = sorted(THEMES.glob("*.json"))
    assert len(shipped) >= 3, "expected at least neutral, plum, and marked-docs"
    required_top_level = set(md2docx.DEFAULTS.keys())
    for theme_path in shipped:
        raw = json.loads(theme_path.read_text(encoding="utf8"))
        merged = md2docx.deep_merge(md2docx.DEFAULTS, raw)
        assert required_top_level.issubset(merged.keys()), f"{theme_path.name} missing schema keys after merge"
        assert "name" in raw, f"{theme_path.name} should declare a 'name' for provenance stamping"


# ---------------------------------------------------------------------------
# CONTRACT:C2-PROVENANCE.1.0
# ---------------------------------------------------------------------------

def test_provenance_stamp():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        src = td / "example.md"
        src.write_text("# Title\n\nHello world.\n", encoding="utf8")
        out = td / "example.docx"

        tpl_path = THEMES / "plum.json"
        cfg = md2docx.deep_merge(md2docx.DEFAULTS, json.loads(tpl_path.read_text(encoding="utf8")))
        md2docx.Converter(cfg, tpl_path=tpl_path).convert(src, out)

        doc = docx2md.Document(str(out))
        cp = doc.core_properties
        prov = json.loads(cp.comments)

        assert set(prov.keys()) == {"t", "tpl", "tplsha", "srcsha", "gen"}
        assert prov["t"] == f"md2docx/{md2docx.TOOL_VERSION}"
        assert prov["tpl"] == "Plum"
        assert prov["tplsha"] is not None and len(prov["tplsha"]) == 16
        assert prov["tplsha"] == hashlib.sha256(tpl_path.read_bytes()).hexdigest()[:16]
        assert prov["srcsha"] == hashlib.sha256(src.read_bytes()).hexdigest()[:16]
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}Z", prov["gen"])

        assert cp.keywords == "md2docx"
        assert cp.category == "Plum"
        assert cp.subject.endswith("example.md")

        # No template at all -> tplsha is JSON null, tpl says so explicitly.
        out2 = td / "example-notpl.docx"
        md2docx.Converter(md2docx.DEFAULTS, tpl_path=None).convert(src, out2)
        prov2 = json.loads(docx2md.Document(str(out2)).core_properties.comments)
        assert prov2["tplsha"] is None
        assert prov2["tpl"] == "built-in defaults"


# ---------------------------------------------------------------------------
# CONTRACT:C3-ROUNDTRIP.1.0
# ---------------------------------------------------------------------------

_STRIP_RE = re.compile(r"[`*#>|\[\]()-]")


def _word_bag(text):
    """Symmetric, structure-agnostic tokenizer: strip markdown punctuation,
    split on whitespace. Applying the SAME function to the source and the
    round-tripped output makes a multiset (Counter) diff a legitimate
    "zero lost / zero invented tokens" check — it does not require
    re-implementing a Markdown parser to be meaningful, because any
    asymmetry it detects is real: something that was words in one text and
    isn't in the other."""
    return Counter(_STRIP_RE.sub(" ", text).split())


def _normalize_source_for_comparison(text):
    """Drop constructs md2docx.py documents as intentionally, entirely
    dropped (not just reformatted): full-line HTML comments and
    horizontal rules. Everything else in the fixture is expected to
    survive the round trip."""
    kept = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("<!--") and s.endswith("-->"):
            continue
        if re.fullmatch(r"-{3,}", s):
            continue
        kept.append(line)
    return "\n".join(kept)


def test_roundtrip_kitchen_sink():
    src = FIXTURES / "kitchen-sink.md"
    source_text = src.read_text(encoding="utf8")

    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "kitchen-sink.docx"
        theme_path = THEMES / "neutral.json"
        cfg = md2docx.deep_merge(md2docx.DEFAULTS, json.loads(theme_path.read_text(encoding="utf8")))
        md2docx.Converter(cfg, tpl_path=theme_path).convert(src, out)

        roundtripped = docx2md.convert(out)

    # Structural spot-checks (fast, readable failure messages before the
    # coarser word-bag diff below).
    assert roundtripped.startswith("**CUI//TEST**"), "banner line must round-trip as the first line"
    assert "# Kitchen Sink" in roundtripped
    assert "### Level three heading" in roundtripped
    assert "#### Level four heading" in roundtripped
    assert "- First bullet item" in roundtripped
    assert "1. First literal numbered item" in roundtripped
    assert "| Name | Kind | Notes |" in roundtripped
    assert "| --- | --- | --- |" in roundtripped
    assert "def convert(src, out_path):" in roundtripped
    assert "```" in roundtripped
    assert "> A blockquote line that spans two source lines" in roundtripped
    assert "**bold**" in roundtripped and "*italic*" in roundtripped and "`code`" in roundtripped

    source_bag = _word_bag(_normalize_source_for_comparison(source_text))
    output_bag = _word_bag(roundtripped)

    lost = source_bag - output_bag
    invented = output_bag - source_bag
    assert not lost, f"tokens present in source but missing after round trip: {dict(lost)}"
    assert not invented, f"tokens present after round trip but absent from source: {dict(invented)}"


def test_link_demotion():
    """CONTRACT:C3-ROUNDTRIP.1.0 Scenario 2 — the documented, honest gap:
    a relative link's target is dropped (label only survives); an
    absolute link keeps both label and URL."""
    assert md2docx.demote_links("[docs](ROADMAP.md)") == "docs"
    assert md2docx.demote_links("[docs](https://example.com/docs)") == "docs (https://example.com/docs)"
    # label == url: no duplication (label already IS the full URL string)
    assert md2docx.demote_links("[https://example.com](https://example.com)") == "https://example.com"
    assert md2docx.demote_links("plain text, no links") == "plain text, no links"


def test_no_footer_flag():
    """--no-footer must actually suppress footer text (footer_on threads
    through Converter.convert to the footer-emission branch)."""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        src = td / "doc.md"
        src.write_text("# Title\n\nBody text.\n", encoding="utf8")
        cfg = md2docx.deep_merge(md2docx.DEFAULTS, {"footer": {"text": "TEST FOOTER"}})

        with_footer = td / "with-footer.docx"
        md2docx.Converter(cfg).convert(src, with_footer, footer_on=True)
        doc = docx2md.Document(str(with_footer))
        assert doc.sections[0].footer.paragraphs[0].text == "TEST FOOTER"

        without_footer = td / "without-footer.docx"
        md2docx.Converter(cfg).convert(src, without_footer, footer_on=False)
        doc2 = docx2md.Document(str(without_footer))
        assert doc2.sections[0].footer.paragraphs[0].text == ""


# ---------------------------------------------------------------------------
# Runner — no test framework required.
# ---------------------------------------------------------------------------

def main():
    tests = [(name, fn) for name, fn in sorted(globals().items())
              if name.startswith("test_") and callable(fn)]
    failures = []
    for name, fn in tests:
        try:
            fn()
        except Exception:
            failures.append(name)
            print(f"FAIL {name}")
            traceback.print_exc()
        else:
            print(f"PASS {name}")

    print()
    print(f"{len(tests) - len(failures)}/{len(tests)} passed")
    if failures:
        print("Failed: " + ", ".join(failures))
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
