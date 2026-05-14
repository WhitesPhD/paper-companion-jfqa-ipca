#!/usr/bin/env python3
"""Extract structured metadata from the manuscript into bundle/metadata.json.

Reads:
  manuscript/JFQA_IPCA.tex            (main body — title, authors, abstract, sections, figures)
  manuscript/Tables/Table*.tex        (main tables — caption, label, description)
  manuscript/Tables/AppendixTable*.tex (appendix tables — same fields)
  manuscript/Figures/*.png            (appendix figure inventory)

Writes:
  bundle/metadata.json

Appendix.tex is referenced by the main .tex but missing from the source tree.
Appendix-figure captions are inferred from filename (M1..M9 -> characteristic
group); appendix-table captions/labels come from each table's own .tex.
"""

from __future__ import annotations
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANUSCRIPT = REPO / "manuscript"
TEX = MANUSCRIPT / "JFQA_IPCA.tex"
APPENDIX_TEX = MANUSCRIPT / "Appendix.tex"
TABLES_DIR = MANUSCRIPT / "Tables"
FIGURES_DIR = MANUSCRIPT / "Figures"
BUNDLE_DIR = REPO / "bundle"

# Maps the M1..M9 suffix in appendix figure filenames to the nine
# characteristic groups defined in Table 1. Source: lines 14-90 of Table1.tex.
CHAR_GROUPS = {
    "M1": "Market, size, momentum",
    "M2": "Reversal",
    "M3": "On-chain activity",
    "M4": "Trading activity",
    "M5": "Liquidity",
    "M6": "Speculative demand",
    "M7": "Volatility and downside risk",
    "M8": "Social media activity",
    "M9": "Equity market exposure",
}


# ---- low-level LaTeX helpers -------------------------------------------------

def balanced_braces(text: str, start: int) -> tuple[str, int]:
    """Given text and index of an opening '{', return (content, index_after_closing)."""
    assert text[start] == "{", f"expected '{{' at {start}, got {text[start]!r}"
    depth = 0
    i = start
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
                return text[start + 1:i], i + 1
        i += 1
    raise ValueError(f"unbalanced braces from {start}")


def find_command(text: str, cmd: str, search_from: int = 0):
    """Find first \\cmd{...} after search_from. Returns (content, end_idx) or None."""
    pat = re.compile(r"\\" + re.escape(cmd) + r"\s*\{")
    m = pat.search(text, search_from)
    if not m:
        return None
    brace_idx = m.end() - 1
    content, end = balanced_braces(text, brace_idx)
    return content, end


def strip_thanks(text: str) -> str:
    """Remove \\thanks{...} blocks (balanced-brace aware)."""
    while True:
        m = re.search(r"\\thanks\s*\{", text)
        if not m:
            return text
        _, end = balanced_braces(text, m.end() - 1)
        text = text[:m.start()] + text[end:]


def strip_inline(s: str) -> str:
    """Strip layout/markup commands. Leaves math, \\ref and escaped chars
    (`\\%`, `\\&`, `\\_`) intact — tex_to_md.py resolves those when emitting
    paper.md, so they're preserved here in their LaTeX form."""
    # Unwrap layout environments (keep inner text).
    s = re.sub(r"\\begin\{(flushleft|flushright|center)\}([\s\S]*?)\\end\{\1\}",
               r"\2", s)
    # Old-style font switches (no-arg).
    s = re.sub(r"\\(bf|rm|it|sl|sc|tt|normalfont)\b", "", s)
    s = re.sub(r"\\protect\\setstretch\{[^}]*\}", "", s)
    s = re.sub(r"\\protect\\raggedright", "", s)
    s = re.sub(r"\\protect\\small", "", s)
    s = re.sub(r"\\setstretch\{[^}]*\}", "", s)
    s = re.sub(r"\\(noindent|raggedright|centering|bigskip|medskip|smallskip|"
               r"small|normalsize|footnotesize|scriptsize|tiny|large|Large|huge|Huge)\b", "", s)
    s = re.sub(r"\\(hspace|vspace)\s*\{[^}]*\}", " ", s)
    s = re.sub(r"\\renewcommand\s*\{[^}]+\}\s*\{[^}]*\}", "", s)
    s = re.sub(r"\\textbf\s*\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\emph\s*\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\textit\s*\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\enquote\s*\{([^}]*)\}", r'"\1"', s)
    s = re.sub(r"\\(citet|citep|cite|citeauthor|citeyear|citealp)\s*\{[^}]+\}", "", s)
    s = re.sub(r"\\label\s*\{[^}]+\}", "", s)
    s = re.sub(r"\\url\s*\{([^}]+)\}", r"\1", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


# ---- field extractors --------------------------------------------------------

def parse_title(text: str) -> str:
    res = find_command(text, "title")
    if not res:
        return ""
    raw, _ = res
    raw = raw.replace("\\\\", " ").replace("\n", " ")
    return strip_inline(raw)


def parse_authors(text: str) -> list[dict]:
    res = find_command(text, "author")
    if not res:
        return []
    raw, _ = res

    # Pull out the thanks block before stripping it from the names line.
    thanks_body = ""
    tm = re.search(r"\\thanks\s*\{", raw)
    if tm:
        thanks_body, _ = balanced_braces(raw, tm.end() - 1)

    names_line = strip_thanks(raw).replace("\n", " ").strip()
    names = [n.strip() for n in re.split(r"\s+and\s+", names_line) if n.strip()]

    authors = []
    for name in names:
        email, affiliation, corresponding = "", "", False
        if thanks_body:
            pos = thanks_body.find(name)
            if pos >= 0:
                tail = thanks_body[pos + len(name):pos + len(name) + 40]
                corresponding = "(corresponding author)" in tail
                # Look for "Name [(corresponding author)]?, \url{email}, Affiliation."
                m = re.search(
                    rf"{re.escape(name)}(?:\s*\(corresponding author\))?\s*,\s*"
                    r"\\url\{([^}]+)\}\s*,\s*([^.]+)\.",
                    thanks_body,
                )
                if m:
                    email = m.group(1).strip()
                    affiliation = strip_inline(m.group(2))
        authors.append({
            "name": strip_inline(name),
            "affiliation": affiliation,
            "email": email,
            "corresponding": corresponding,
        })
    return authors


def parse_abstract(text: str) -> str:
    m = re.search(r"\\textbf\s*\{Abstract\}\s*\\\\", text)
    if not m:
        return ""
    start = m.end()
    end_m = re.search(r"\\(section|pagebreak|clearpage)\b", text[start:])
    end = start + end_m.start() if end_m else len(text)
    return strip_inline(text[start:end])


def _slug(s: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return slug[:60]


_LEVEL = {"section": 1, "subsection": 2, "subsubsection": 3, "subsubsection*": 3}
_PREFIX = {1: "sec-", 2: "subsec-", 3: "subsubsec-"}


def parse_sections(text: str, in_appendix: bool = False) -> list[dict]:
    out = []
    # Order matters: longest alternative first so \subsubsection isn't shadowed.
    for m in re.finditer(r"\\(subsubsection\*?|subsection|section)\s*\{", text):
        cmd = m.group(1)
        content, after = balanced_braces(text, m.end() - 1)
        # Label can live inside the braces or on a following line.
        lab_m = re.search(r"\\label\s*\{([^}]+)\}", content)
        label = lab_m.group(1).strip() if lab_m else ""
        if not label:
            tail = text[after:after + 200]
            tail = re.split(r"\\(?:section|subsection|subsubsection|paragraph)\b", tail)[0]
            lab_after = re.search(r"\\label\s*\{([^}]+)\}", tail)
            if lab_after:
                label = lab_after.group(1).strip()
        title = strip_inline(re.sub(r"\\label\s*\{[^}]+\}", "", content))
        line_no = text.count("\n", 0, m.start()) + 1
        level = _LEVEL[cmd]
        prefix = ("app-" if in_appendix else "") + _PREFIX[level]
        out.append({
            "id": prefix + _slug(title),
            "level": level,
            "title": title,
            "label": label,
            "line": line_no,
            "in_appendix": in_appendix,
        })
    return out


def parse_figures(text: str, id_prefix: str = "fig", in_appendix: bool = False) -> list[dict]:
    """Parse \\begin{figure}...\\end{figure} blocks."""
    out = []
    for n, m in enumerate(re.finditer(r"\\begin\{figure\}", text), start=1):
        end_m = re.search(r"\\end\{figure\}", text[m.end():])
        if not end_m:
            continue
        body = text[m.end():m.end() + end_m.start()]
        # Strip the optional float-placement spec (e.g. [h!], [t!]) that follows
        # \begin{figure}. Otherwise it ends up in the description field.
        body = re.sub(r"^\s*\[[^\]]*\]", "", body)

        cap = find_command(body, "caption")
        caption = strip_inline(cap[0]) if cap else ""
        lab = find_command(body, "label")
        label = lab[0].strip() if lab else ""

        # Description: body minus subfigure/includegraphics/caption/label.
        prose = body
        prose = re.sub(r"\\subfigure\s*\[[^\]]*\]\s*\{[^{}]*\\includegraphics(?:\[[^\]]*\])?\s*\{[^}]*\}\s*\}", "", prose)
        prose = re.sub(r"\\includegraphics(?:\[[^\]]*\])?\s*\{[^}]*\}", "", prose)
        prose = re.sub(r"\\caption\s*\{[^}]*\}", "", prose, count=1)
        prose = re.sub(r"\\label\s*\{[^}]*\}", "", prose, count=1)
        description = strip_inline(prose)

        # Subfigures (with sub-captions) first; fall back to bare includegraphics.
        subfigs = []
        for sm in re.finditer(
            r"\\subfigure\s*\[([^\]]*)\]\s*\{[^{}]*\\includegraphics(?:\[[^\]]*\])?\s*\{([^}]+)\}",
            body,
        ):
            subfigs.append({
                "label": strip_inline(sm.group(1)),
                "file": Path(sm.group(2)).name,
            })
        if not subfigs:
            for sm in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\s*\{([^}]+)\}", body):
                subfigs.append({"label": "", "file": Path(sm.group(1)).name})

        out.append({
            "id": f"{id_prefix}{n}",
            "label": label,
            "caption_short": caption,
            "description": description,
            "files": subfigs,
            "in_appendix": in_appendix,
        })
    return out


def parse_table_file(path: Path, fid: str, in_appendix: bool) -> dict | None:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    cap = find_command(text, "caption")
    caption = strip_inline(cap[0]) if cap else ""
    lab = find_command(text, "label")
    label = lab[0].strip() if lab else ""

    # Description: from end-of-caption/label to start of tabular environment.
    cursor = 0
    if cap:
        cursor = max(cursor, cap[1])
    if lab:
        cursor = max(cursor, lab[1])
    tab_m = re.search(r"\\begin\{tabular(?:\*|x)?\}|\\resizebox", text[cursor:])
    description = strip_inline(text[cursor:cursor + tab_m.start()]) if tab_m else ""

    # Body: capture every tabular environment from the first \begin{tabular}
    # through the last \end{tabular}. This keeps multi-panel tables intact
    # (Table 3 etc. embed both panels inside one tabular; some appendix
    # tables put two side-by-side tabulars in the same file).
    body_latex = ""
    first_tab = re.search(r"\\begin\{tabular(?:\*|x)?\}", text)
    if first_tab:
        last_end = None
        for em in re.finditer(r"\\end\{tabular(?:\*|x)?\}", text):
            last_end = em.end()
        if last_end and last_end > first_tab.start():
            body_latex = text[first_tab.start():last_end].strip()

    return {
        "id": fid,
        "label": label,
        "caption_short": caption,
        "description": description,
        "body_latex": body_latex,
        "source_file": str(path.relative_to(MANUSCRIPT)),
        "in_appendix": in_appendix,
    }


def parse_tables_from_input(tex_path: Path, name_pattern: str, id_prefix: str, in_appendix: bool) -> list[dict]:
    """Walk \\input{Tables/...} lines in tex_path in document order and parse each table."""
    if not tex_path.exists():
        return []
    text = tex_path.read_text(encoding="utf-8")
    pat = re.compile(r"\\input\s*\{Tables/(" + name_pattern + r")(?:\.tex)?\}")
    out, seen = [], set()
    for m in pat.finditer(text):
        name = m.group(1)
        if name in seen:
            continue
        seen.add(name)
        num = re.search(r"\d+", name).group()
        parsed = parse_table_file(TABLES_DIR / f"{name}.tex", f"{id_prefix}{num}", in_appendix=in_appendix)
        if parsed:
            out.append(parsed)
    return out


# ---- main --------------------------------------------------------------------

def main() -> None:
    text = TEX.read_text(encoding="utf-8")
    has_appendix = APPENDIX_TEX.exists()
    appendix_text = APPENDIX_TEX.read_text(encoding="utf-8") if has_appendix else ""

    metadata = {
        "title": parse_title(text),
        "authors": parse_authors(text),
        "journal": "Journal of Financial and Quantitative Analysis",
        "year_online": 2025,
        "year_issue": 2026,
        "doi": "10.1017/S0022109025102329",
        "dataverse_doi": "10.7910/DVN/IQR5DH",
        "abstract": parse_abstract(text),
        "sections": parse_sections(text, in_appendix=False)
                  + (parse_sections(appendix_text, in_appendix=True) if has_appendix else []),
        "figures": parse_figures(text, id_prefix="fig", in_appendix=False)
                 + (parse_figures(appendix_text, id_prefix="appfig", in_appendix=True) if has_appendix else []),
        "tables": parse_tables_from_input(TEX, r"Table\d+", "tab", in_appendix=False)
                + parse_tables_from_input(APPENDIX_TEX, r"AppendixTable\d+", "apptab", in_appendix=True),
        "characteristic_groups": CHAR_GROUPS,
    }
    if not has_appendix:
        metadata["notes"] = {"appendix_prose": "Appendix.tex not present; appendix figures/sections omitted."}

    BUNDLE_DIR.mkdir(exist_ok=True)
    out = BUNDLE_DIR / "metadata.json"
    out.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    main_secs = sum(1 for s in metadata["sections"] if not s["in_appendix"])
    app_secs = sum(1 for s in metadata["sections"] if s["in_appendix"])
    main_figs = sum(1 for f in metadata["figures"] if not f["in_appendix"])
    app_figs = sum(1 for f in metadata["figures"] if f["in_appendix"])
    main_tabs = sum(1 for t in metadata["tables"] if not t["in_appendix"])
    app_tabs = sum(1 for t in metadata["tables"] if t["in_appendix"])
    print(f"wrote {out.relative_to(REPO)}")
    print(f"  title          : {metadata['title'][:70]!r}")
    print(f"  authors        : {len(metadata['authors'])}")
    print(f"  abstract chars : {len(metadata['abstract'])}")
    print(f"  sections       : {main_secs} main + {app_secs} appendix")
    print(f"  figures        : {main_figs} main + {app_figs} appendix")
    print(f"  tables         : {main_tabs} main + {app_tabs} appendix")


if __name__ == "__main__":
    main()
