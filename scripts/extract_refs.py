#!/usr/bin/env python3
"""Extract bib entries for works actually cited in the manuscript.

Reads:
  manuscript/JFQA_IPCA.tex
  manuscript/Appendix.tex
  manuscript/biblibrary.bib

Writes:
  bundle/references.json   (only the cited subset, normalized)

The bib file is 118kB and contains works that the authors never cited; we drop
everything else so the bundle stays small enough to ship in the system prompt.
"""

from __future__ import annotations
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANUSCRIPT = REPO / "manuscript"
TEX = MANUSCRIPT / "JFQA_IPCA.tex"
APPENDIX_TEX = MANUSCRIPT / "Appendix.tex"
BIB = MANUSCRIPT / "biblibrary.bib"
BUNDLE_DIR = REPO / "bundle"

CITE_CMDS = (
    "cite", "citet", "citep", "citealp", "citealt",
    "citeauthor", "citeyear", "citeyearpar", "Citet", "Citep",
)

# Field names we surface in the output. Order is purely cosmetic in the JSON.
KEEP_FIELDS = ("author", "year", "title", "journal", "booktitle",
               "publisher", "volume", "number", "pages", "doi", "url")


# ---- citation extraction -----------------------------------------------------

def extract_citation_keys(text: str) -> set[str]:
    """Find every \\cite-family call and pull out comma-separated keys."""
    cmds = "|".join(re.escape(c) for c in CITE_CMDS)
    pat = re.compile(r"\\(" + cmds + r")(?:\[[^\]]*\])?\s*\{([^}]+)\}")
    keys: set[str] = set()
    for m in pat.finditer(text):
        for k in m.group(2).split(","):
            k = k.strip()
            if k:
                keys.add(k)
    return keys


# ---- bib parsing -------------------------------------------------------------

def _walk_balanced(text: str, start: int) -> int:
    """Return the index of the matching '}' for the '{' at `start`."""
    assert text[start] == "{"
    depth, i = 0, start
    while i < len(text):
        c = text[i]
        if c == "\\" and i + 1 < len(text):
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ValueError(f"unbalanced from {start}")


def _parse_fields(body: str) -> dict[str, str]:
    """Parse 'field = {value}, field = "value", ...' into a dict."""
    out: dict[str, str] = {}
    i = 0
    while i < len(body):
        m = re.match(r"\s*(\w+)\s*=\s*", body[i:])
        if not m:
            break
        name = m.group(1).lower()
        i += m.end()
        if i >= len(body):
            break
        c = body[i]
        if c == "{":
            close = _walk_balanced(body, i)
            out[name] = body[i + 1:close]
            i = close + 1
        elif c == '"':
            j = i + 1
            while j < len(body) and body[j] != '"':
                j += 2 if body[j] == "\\" and j + 1 < len(body) else 1
            out[name] = body[i + 1:j]
            i = j + 1
        else:
            tok = re.match(r"[\w\d]+", body[i:])
            if tok:
                out[name] = tok.group()
                i += tok.end()
            else:
                i += 1
        skip = re.match(r"\s*,\s*", body[i:])
        if skip:
            i += skip.end()
    return out


def parse_bib_file(path: Path) -> dict[str, dict]:
    """Parse a .bib file into {key: {type, ...fields}}."""
    text = path.read_text(encoding="utf-8", errors="replace")
    entries: dict[str, dict] = {}
    i = 0
    while True:
        at = text.find("@", i)
        if at < 0:
            break
        m = re.match(r"@(\w+)\s*\{", text[at:])
        if not m:
            i = at + 1
            continue
        type_ = m.group(1).lower()
        brace_idx = at + m.end() - 1
        try:
            close = _walk_balanced(text, brace_idx)
        except ValueError:
            break
        if type_ in ("string", "preamble", "comment"):
            i = close + 1
            continue
        body = text[brace_idx + 1:close]
        km = re.match(r"\s*([^,\s]+)\s*,\s*", body)
        if not km:
            i = close + 1
            continue
        key = km.group(1)
        fields = _parse_fields(body[km.end():])
        entries[key] = {"type": type_, **fields}
        i = close + 1
    return entries


# ---- output --------------------------------------------------------------

def clean_value(val: str) -> str:
    """Light cleanup of LaTeX residue in a bib value."""
    if not val:
        return ""
    val = val.replace(r"\&", "&").replace(r"\%", "%").replace(r"\_", "_")
    val = re.sub(r"\\textbf\s*\{([^}]*)\}", r"\1", val)
    val = re.sub(r"\\(?:emph|textit|textsl)\s*\{([^}]*)\}", r"\1", val)
    # Brace-protected single letters: {C}apital → Capital
    val = re.sub(r"\{([^{}]*)\}", r"\1", val)
    val = re.sub(r"\s+", " ", val).strip()
    return val


def normalize(key: str, entry: dict) -> dict:
    out = {"key": key, "type": entry.get("type", "")}
    for f in KEEP_FIELDS:
        if f in entry:
            v = clean_value(entry[f])
            if v:
                out[f] = v
    return out


def main() -> None:
    cited: set[str] = set()
    for path in (TEX, APPENDIX_TEX):
        if path.exists():
            cited |= extract_citation_keys(path.read_text(encoding="utf-8"))

    if not BIB.exists():
        raise SystemExit(f"missing {BIB}")
    all_entries = parse_bib_file(BIB)

    refs, missing = [], []
    for k in sorted(cited):
        if k in all_entries:
            refs.append(normalize(k, all_entries[k]))
        else:
            missing.append(k)

    BUNDLE_DIR.mkdir(exist_ok=True)
    out = BUNDLE_DIR / "references.json"
    out.write_text(json.dumps(refs, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"wrote {out.relative_to(REPO)}")
    print(f"  cited keys      : {len(cited)}")
    print(f"  matched in .bib : {len(refs)}")
    print(f"  bib size on disk: {BIB.stat().st_size:,} bytes")
    print(f"  refs.json size  : {out.stat().st_size:,} bytes")
    if missing:
        print(f"  MISSING ({len(missing)}): {sorted(missing)[:10]}{' ...' if len(missing) > 10 else ''}")


if __name__ == "__main__":
    main()
