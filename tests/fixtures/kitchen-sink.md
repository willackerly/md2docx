**CUI//TEST**

# Kitchen Sink

A fixture exercising every construct `md2docx.py` supports, for
`tests/test_roundtrip.py::test_roundtrip_kitchen_sink`
(`CONTRACT:C3-ROUNDTRIP.1.0`).

This paragraph soft-wraps across
several source lines that should
join into one paragraph in the output.

## Headings

### Level three heading

#### Level four heading

## Lists

- First bullet item
- Second bullet item with **bold**, *italic*, and `inline code`
- Third bullet item

1. First literal numbered item
2. Second literal numbered item

## Table

| Name | Kind | Notes |
| --- | --- | --- |
| neutral | theme | built-in defaults |
| plum | theme | purple accent |
| marked-docs | theme | banner-forward |

## Code

```
def convert(src, out_path):
    return out_path
```

## Blockquote

> A blockquote line that spans
> two source lines and should join into one paragraph.

## Links and horizontal rule

An [absolute link](https://example.com/docs) keeps its label and gets its
URL appended in parens.

---

<!-- this HTML comment must be skipped entirely -->

Final paragraph mixes three separate inline spans in one line: **bold**,
*italic*, and `code`, each its own span rather than nested inside another.
