#!/usr/bin/env python3
"""Convert the LaTeX manuscript to a single readable Markdown bundle.

Reads:
  manuscript/JFQA_IPCA.tex
  manuscript/Appendix.tex
  bundle/metadata.json        (figure/table/section registries)
  bundle/references.json      (cited works for citation substitution)

Writes:
  bundle/paper.md

Strategy: no pandoc dependency. Targeted substitutions in a fixed order —
math environments are normalised to KaTeX-friendly form; citations and
\\ref-style cross-references resolve against the two JSON registries; figure
and table blocks are stripped from the body and re-emitted as placeholder
lines at the end ([FIGURE figN], [TABLE tabN]) so the model can request them
on demand without bloating the per-turn prompt.
"""

from __future__ import annotations
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANUSCRIPT = REPO / "manuscript"
TEX = MANUSCRIPT / "JFQA_IPCA.tex"
APPENDIX_TEX = MANUSCRIPT / "Appendix.tex"
BUNDLE_DIR = REPO / "bundle"


# ---- balanced-brace utilities ------------------------------------------------

def walk_balanced(text: str, start: int) -> int:
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


def replace_balanced(text: str, cmd: str, fn) -> str:
    """For every \\cmd{...} (balanced braces), call fn(arg) and substitute."""
    pat = re.compile(r"\\" + re.escape(cmd) + r"\s*\{")
    out, i = [], 0
    while i < len(text):
        m = pat.search(text, i)
        if not m:
            out.append(text[i:])
            break
        out.append(text[i:m.start()])
        brace_idx = m.end() - 1
        close = walk_balanced(text, brace_idx)
        out.append(fn(text[brace_idx + 1:close]))
        i = close + 1
    return "".join(out)


# ---- registries --------------------------------------------------------------

def build_lookups(metadata: dict):
    """label → display string for figures, tables, and appendix sections."""
    fig, tab, sec = {}, {}, {}

    main_n = app_n = 0
    for f in metadata["figures"]:
        if f["in_appendix"]:
            app_n += 1
            disp = f"A{app_n}"
        else:
            main_n += 1
            disp = str(main_n)
        if f["label"]:
            fig[f["label"]] = disp

    main_n = app_n = 0
    for t in metadata["tables"]:
        if t["in_appendix"]:
            app_n += 1
            disp = f"A{app_n}"
        else:
            main_n += 1
            disp = str(main_n)
        if t["label"]:
            tab[t["label"]] = disp

    # Top-level sections: Roman numerals in the main body, A, B, C, D in the
    # appendix — these match the journal-style counters set in the .tex.
    # Subsections get A, B, C reset per parent section. The author writes
    # cross-refs as "Section \ref{sec:X}.\ref{subsec:Y}", so subsection refs
    # just need to resolve to "A" / "B" etc.
    romans = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"]
    letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]

    def annotate(group_sections):
        top_idx = -1
        sub_idx = 0
        for s in group_sections:
            if s["level"] == 1:
                top_idx += 1
                sub_idx = 0
            elif s["level"] == 2 and s["label"]:
                if sub_idx < len(letters):
                    sec[s["label"]] = letters[sub_idx]
                sub_idx += 1

    main_sections = [s for s in metadata["sections"] if not s["in_appendix"]]
    app_sections = [s for s in metadata["sections"] if s["in_appendix"]]

    for i, s in enumerate([x for x in main_sections if x["level"] == 1]):
        if s["label"]:
            sec[s["label"]] = romans[i]
    for i, s in enumerate([x for x in app_sections if x["level"] == 1]):
        if s["label"]:
            sec[s["label"]] = letters[i]

    annotate(main_sections)
    annotate(app_sections)

    return fig, tab, sec


def format_authors(authors_str: str) -> str:
    """Last-name-only formatting: 'Smith', 'Smith and Jones', 'Smith et al.'."""
    if not authors_str:
        return ""
    parts = [a.strip() for a in re.split(r"\s+and\s+", authors_str) if a.strip()]
    last = []
    for p in parts:
        last.append(p.split(",", 1)[0].strip() if "," in p else p.strip().split()[-1])
    if len(last) == 0:
        return ""
    if len(last) == 1:
        return last[0]
    if len(last) == 2:
        return f"{last[0]} and {last[1]}"
    return f"{last[0]} et al."


def cite_for(key: str, refs: dict) -> tuple[str, str]:
    """(authors, year) — fallback to (key, '?') if not found."""
    e = refs.get(key)
    if not e:
        return (key, "?")
    return (format_authors(e.get("author", "")), e.get("year", "?"))


# ---- top-level conversion ----------------------------------------------------

CITE_CMDS = ("citet", "citep", "citealp", "citealt", "cite",
             "citeauthor", "citeyear", "citeyearpar", "Citet", "Citep")
PAREN_CITE = {"citep", "citealp", "Citep", "citeyearpar"}


def convert_citations(text: str, refs: dict) -> str:
    cmds = "|".join(re.escape(c) for c in CITE_CMDS)
    pat = re.compile(r"\\(" + cmds + r")(?:\[[^\]]*\])?\s*\{([^}]+)\}")

    def sub(m: re.Match) -> str:
        cmd = m.group(1)
        keys = [k.strip() for k in m.group(2).split(",") if k.strip()]
        parts = []
        for k in keys:
            a, y = cite_for(k, refs)
            if cmd == "citeauthor":
                parts.append(a)
            elif cmd in ("citeyear", "citeyearpar"):
                parts.append(y)
            elif cmd in PAREN_CITE:
                parts.append(f"{a}, {y}")
            else:
                parts.append(f"{a} ({y})")
        if cmd == "citeyearpar":
            return "(" + "; ".join(parts) + ")"
        if cmd in PAREN_CITE:
            return "(" + "; ".join(parts) + ")"
        return "; ".join(parts)

    return pat.sub(sub, text)


def convert_refs(text: str, fig: dict, tab: dict, sec: dict) -> str:
    """Resolve \\ref{} and \\eqref{} against the three lookups."""
    def sub_ref(m):
        label = m.group(1).strip()
        if label in fig:
            return fig[label]
        if label in tab:
            return tab[label]
        if label in sec:
            return sec[label]
        # Equation refs typically use \eqref or have eq: prefix — leave a hint.
        return f"[{label}]"
    text = re.sub(r"\\ref\s*\{([^}]+)\}", sub_ref, text)
    text = re.sub(r"\\eqref\s*\{([^}]+)\}", lambda m: f"({sub_ref(m)})", text)
    return text


def convert_math_envs(text: str) -> str:
    """Normalise display math to $$…$$ with aligned innards where needed."""
    # \begin{equation*?} … \end{equation*?}
    text = re.sub(
        r"\\begin\{equation\*?\}([\s\S]+?)\\end\{equation\*?\}",
        lambda m: "$$\n" + m.group(1).strip() + "\n$$",
        text,
    )
    # \begin{align*?} … \end{align*?}  →  $$\begin{aligned}…\end{aligned}$$
    text = re.sub(
        r"\\begin\{align\*?\}([\s\S]+?)\\end\{align\*?\}",
        lambda m: "$$\n\\begin{aligned}\n" + m.group(1).strip() + "\n\\end{aligned}\n$$",
        text,
    )
    # \[ … \]  →  $$ … $$
    text = re.sub(
        r"\\\[([\s\S]+?)\\\]",
        lambda m: "$$" + m.group(1).strip() + "$$",
        text,
    )
    # \( … \)  →  $ … $
    text = re.sub(
        r"\\\(([\s\S]+?)\\\)",
        lambda m: "$" + m.group(1).strip() + "$",
        text,
    )
    # Drop \label{} inside math
    text = re.sub(r"\\label\s*\{[^}]+\}", "", text)
    return text


def strip_figures(text: str) -> str:
    """Remove \\begin{figure}…\\end{figure} blocks entirely — emitted separately."""
    return re.sub(r"\\begin\{figure\}[\s\S]+?\\end\{figure\}", "", text)


def strip_table_inputs(text: str) -> str:
    return re.sub(r"\\input\s*\{Tables/[^}]+\}", "", text)


ACCENTS = {
    ("'", "a"): "á", ("'", "e"): "é", ("'", "i"): "í", ("'", "o"): "ó", ("'", "u"): "ú",
    ("'", "A"): "Á", ("'", "E"): "É", ("'", "I"): "Í", ("'", "O"): "Ó", ("'", "U"): "Ú",
    ("`", "a"): "à", ("`", "e"): "è", ("`", "i"): "ì", ("`", "o"): "ò", ("`", "u"): "ù",
    ('"', "a"): "ä", ('"', "e"): "ë", ('"', "i"): "ï", ('"', "o"): "ö", ('"', "u"): "ü",
    ('"', "A"): "Ä", ('"', "O"): "Ö", ('"', "U"): "Ü",
    ("^", "a"): "â", ("^", "e"): "ê", ("^", "i"): "î", ("^", "o"): "ô", ("^", "u"): "û",
    ("~", "n"): "ñ", ("~", "o"): "õ", ("~", "a"): "ã",
}
SPECIAL = {r"\\ss\b": "ß", r"\\o\b": "ø", r"\\O\b": "Ø", r"\\ae\b": "æ",
           r"\\AE\b": "Æ", r"\\aa\b": "å", r"\\AA\b": "Å"}


def fix_accents(text: str) -> str:
    """Translate common LaTeX accent macros to their Unicode equivalents."""
    def lookup(acc, letter):
        return ACCENTS.get((acc, letter), None)
    # Plain \'a, \"u, \^o, \~n
    text = re.sub(r"\\(['`\"^~])([A-Za-z])",
                  lambda m: lookup(m.group(1), m.group(2)) or m.group(),
                  text)
    # \'{a}, \"{u}, etc.
    text = re.sub(r"\\(['`\"^~])\{([A-Za-z])\}",
                  lambda m: lookup(m.group(1), m.group(2)) or m.group(),
                  text)
    # {\'a}, {\"u}, etc.
    text = re.sub(r"\{\\(['`\"^~])([A-Za-z])\}",
                  lambda m: lookup(m.group(1), m.group(2)) or m.group(),
                  text)
    for pat, repl in SPECIAL.items():
        text = re.sub(pat, repl, text)
    return text


def fix_math_commands(text: str) -> str:
    """Paper-specific math command substitutions (KaTeX-friendly form)."""
    # \z is defined in the preamble as \mbox{\boldmath$z$}. KaTeX doesn't see
    # the preamble — translate to \boldsymbol{z}, which it does understand.
    text = re.sub(r"\\z(?![A-Za-z])", r"\\boldsymbol{z}", text)
    return text


def strip_center_blocks(text: str) -> str:
    """\\begin{center}…\\end{center} → bare inner text (the wrapper is layout-only)."""
    return re.sub(r"\\begin\{center\}([\s\S]+?)\\end\{center\}",
                  lambda m: m.group(1).strip(),
                  text)


def with_math_masked(text: str, fn) -> str:
    """Apply fn to text with $...$ and $$...$$ blocks swapped for placeholders."""
    blocks: list[str] = []

    def mask(m):
        blocks.append(m.group(0))
        return f"\x00M{len(blocks)-1}\x00"

    # Order matters: $$…$$ before single $…$.
    masked = re.sub(r"\$\$[\s\S]+?\$\$", mask, text)
    masked = re.sub(r"(?<!\\)\$(?:[^\n$\\]|\\.)+?(?<!\\)\$", mask, masked)
    transformed = fn(masked)
    return re.sub(r"\x00M(\d+)\x00", lambda m: blocks[int(m.group(1))], transformed)


def convert_inline(text: str) -> str:
    """Inline LaTeX → Markdown for non-math content."""
    # Footnotes — extract and inline as parentheticals.
    def footnote_sub(arg: str) -> str:
        return f" (footnote: {arg.strip()})"
    text = replace_balanced(text, "footnote", footnote_sub)

    # Emphasis & strong
    text = replace_balanced(text, "textbf", lambda a: f"**{a}**")
    text = replace_balanced(text, "emph", lambda a: f"*{a}*")
    text = replace_balanced(text, "textit", lambda a: f"*{a}*")
    text = replace_balanced(text, "textsl", lambda a: f"*{a}*")
    text = replace_balanced(text, "texttt", lambda a: f"`{a}`")
    text = replace_balanced(text, "enquote", lambda a: f'"{a}"')

    # Links: \href{url}{text}  → [text](url)
    def href_sub(m):
        try:
            url_close = walk_balanced(m.string, m.end() - 1)
            url = m.string[m.end():url_close]
            # Following {text} block
            txt_open = m.string.find("{", url_close + 1)
            if txt_open == -1:
                return url
            txt_close = walk_balanced(m.string, txt_open)
            txt = m.string[txt_open + 1:txt_close]
            return f"[{txt}]({url})"
        except ValueError:
            return ""
    # \href doesn't slot neatly into replace_balanced (two args), do it manually
    # below — keep this lambda for a passthrough stripper as a safety net.

    out, i = [], 0
    pat = re.compile(r"\\href\s*\{")
    while True:
        m = pat.search(text, i)
        if not m:
            out.append(text[i:])
            break
        out.append(text[i:m.start()])
        try:
            url_close = walk_balanced(text, m.end() - 1)
            url = text[m.end():url_close]
            txt_open = text.find("{", url_close + 1)
            if txt_open < 0:
                out.append(url)
                i = url_close + 1
                continue
            txt_close = walk_balanced(text, txt_open)
            txt = text[txt_open + 1:txt_close]
            out.append(f"[{txt}]({url})")
            i = txt_close + 1
        except ValueError:
            out.append(text[m.start():m.end()])
            i = m.end()
    text = "".join(out)

    text = replace_balanced(text, "url", lambda a: a)

    # Paragraph headers: \paragraph{Title.}  →  **Title.**
    text = replace_balanced(text, "paragraph", lambda a: f"\n\n**{a.strip()}**")

    # Strip noise commands (no-arg).
    text = re.sub(
        r"\\(noindent|raggedright|centering|bigskip|medskip|smallskip|small|normalsize|"
        r"clearpage|pagebreak|maketitle|frenchspacing|widowpenalty\d*|doublespacing|"
        r"thispagestyle\{[^}]*\}|setcounter\{[^}]*\}\{[^}]*\}|setstretch\{[^}]*\}|"
        r"renewcommand\{[^}]*\}\{[^}]*\}|renewcommand\\[^{]+\{[^}]*\}|"
        r"bibliographystyle\{[^}]*\}|bibliography\{[^}]*\}|"
        r"begin\{spacing\}\{[^}]*\}|end\{spacing\}|"
        r"begin\{center\}|end\{center\}|"
        r"protect\\(?:small|raggedright|setstretch\{[^}]*\})|"
        r"date\{\}|tspace)\b",
        "",
        text,
    )

    # Escape-strip outside math only (inside math, `\%` etc. are required).
    def strip_escapes(s: str) -> str:
        s = s.replace(r"\%", "%").replace(r"\&", "&").replace(r"\_", "_")
        s = s.replace(r"\$", "$").replace("~", " ")
        return s
    text = with_math_masked(text, strip_escapes)
    # Em/en dashes are fine as-is in Markdown (`--` and `---`).

    return text


def convert_sections(text: str, in_appendix: bool) -> str:
    """LaTeX sectioning → Markdown headings (offset by 1 in the appendix)."""
    offset = 1 if in_appendix else 0
    base = {"section": 1, "subsection": 2, "subsubsection": 3}

    def section_sub(m: re.Match) -> str:
        cmd = m.group(1).rstrip("*")
        content, after = m.group(2), m.end()
        # Strip embedded \label{}
        content = re.sub(r"\\label\s*\{[^}]+\}", "", content).strip()
        level = base[cmd] + offset
        return "\n\n" + "#" * level + " " + content + "\n"

    out, i = [], 0
    pat = re.compile(r"\\(section|subsection|subsubsection)(\*?)\s*\{")
    while i < len(text):
        m = pat.search(text, i)
        if not m:
            out.append(text[i:])
            break
        out.append(text[i:m.start()])
        cmd = m.group(1)
        brace_idx = m.end() - 1
        close = walk_balanced(text, brace_idx)
        title = text[brace_idx + 1:close]
        title = re.sub(r"\\label\s*\{[^}]+\}", "", title).strip()
        level = base[cmd] + offset
        out.append("\n\n" + "#" * level + " " + title + "\n")
        i = close + 1
        # Also consume a standalone \label{…} that immediately follows.
        tail = text[i:i + 80]
        lab_m = re.match(r"\s*\\label\s*\{[^}]+\}", tail)
        if lab_m:
            i += lab_m.end()
    text = "".join(out)
    return text


# ---- per-file pipeline -------------------------------------------------------

def slice_body(text: str, in_appendix: bool) -> str:
    """Trim preamble/abstract front-matter; cut everything past the bibliography."""
    # Both files: body starts at the first real \section. For the main .tex
    # this skips the title/author/abstract block (the metadata re-emits the
    # abstract separately); for Appendix.tex this skips the centered title page.
    m = re.search(r"\\section\s*\{", text)
    if m:
        text = text[m.start():]
    end = re.search(r"\\bibliography\b", text)
    if end:
        text = text[:end.start()]
    return text


def whitespace(text: str) -> str:
    # Compress runs of blank lines, trim trailing space on each line.
    lines = [l.rstrip() for l in text.splitlines()]
    out, blanks = [], 0
    for l in lines:
        if not l.strip():
            blanks += 1
            if blanks <= 1:
                out.append("")
        else:
            blanks = 0
            out.append(l)
    return "\n".join(out).strip() + "\n"


def convert_file(path: Path, in_appendix: bool, refs: dict, fig: dict, tab: dict, sec: dict) -> str:
    text = path.read_text(encoding="utf-8")
    text = slice_body(text, in_appendix)
    text = strip_figures(text)
    text = strip_table_inputs(text)
    text = strip_center_blocks(text)
    text = convert_math_envs(text)
    text = fix_math_commands(text)
    text = convert_citations(text, refs)
    text = convert_refs(text, fig, tab, sec)
    text = convert_sections(text, in_appendix)
    text = convert_inline(text)
    text = fix_accents(text)
    text = whitespace(text)
    return text


# ---- placeholders ------------------------------------------------------------

def clean_placeholder_string(s: str, fig: dict, tab: dict, sec: dict) -> str:
    """Run a caption/description from metadata.json through the same ref-resolution
    and escape-stripping pipeline as the paper body, so the placeholder section
    of paper.md renders correctly under Markdown + KaTeX."""
    s = convert_refs(s, fig, tab, sec)
    s = with_math_masked(
        s,
        lambda t: t.replace(r"\%", "%").replace(r"\&", "&").replace(r"\_", "_"),
    )
    # Two refs concatenated by a period (e.g. "\\ref{sec:x}.\\ref{subsec:y}.")
    # resolve to "III.A." but stripping a missing one leaves "..". Collapse.
    s = re.sub(r"\.\s*\.", ".", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def figure_placeholders(metadata: dict, fig: dict, tab: dict, sec: dict) -> str:
    """One line per figure: `[FIGURE figN] short caption — description`."""
    lines = ["## Figures"]
    for f in metadata["figures"]:
        cap = clean_placeholder_string(f.get("caption_short", "") or "(no caption)", fig, tab, sec)
        desc = clean_placeholder_string(f.get("description", ""), fig, tab, sec)
        n_panels = len(f.get("files", []))
        panel_note = f" ({n_panels} sub-panels)" if n_panels > 1 else ""
        lines.append(f"\n**[FIGURE {f['id']}]** {cap}{panel_note}")
        if desc:
            lines.append(desc)
    return "\n".join(lines) + "\n"


def table_placeholders(metadata: dict, fig: dict, tab: dict, sec: dict) -> str:
    lines = ["## Tables"]
    for t in metadata["tables"]:
        cap = clean_placeholder_string(t.get("caption_short", "") or "(no caption)", fig, tab, sec)
        desc = clean_placeholder_string(t.get("description", ""), fig, tab, sec)
        lines.append(f"\n**[TABLE {t['id']}]** {cap}")
        if desc:
            lines.append(desc)
        body = t.get("body_latex", "")
        if body:
            # Keep the raw LaTeX inside a fenced block so Markdown renderers
            # treat it as code. The model reads it verbatim — Claude parses
            # tabular environments accurately, so this is the cheapest way
            # to make the actual numbers visible without a fragile MD-table
            # conversion.
            lines.append("\n```latex\n" + body + "\n```")
    return "\n".join(lines) + "\n"


# ---- main --------------------------------------------------------------------

def main() -> None:
    metadata = json.loads((BUNDLE_DIR / "metadata.json").read_text())
    refs_list = json.loads((BUNDLE_DIR / "references.json").read_text())
    refs = {r["key"]: r for r in refs_list}
    fig, tab, sec = build_lookups(metadata)

    main_md = convert_file(TEX, in_appendix=False, refs=refs, fig=fig, tab=tab, sec=sec)
    app_md = convert_file(APPENDIX_TEX, in_appendix=True, refs=refs, fig=fig, tab=tab, sec=sec)

    header = (
        f"# {metadata['title']}\n\n"
        f"_{' and '.join(a['name'] for a in metadata['authors'])}_\n\n"
        f"**{metadata['journal']}**, {metadata['year_issue']} "
        f"(published online {metadata['year_online']}). "
        f"DOI: [{metadata['doi']}](https://doi.org/{metadata['doi']}). "
        f"Replication: [Harvard Dataverse]"
        f"(https://doi.org/{metadata['dataverse_doi']}).\n\n"
        f"## Abstract\n\n{metadata['abstract']}\n"
    )

    paper = (
        header
        + "\n\n"
        + main_md
        + "\n\n---\n\n# Internet Appendix\n\n"
        + app_md
        + "\n\n---\n\n"
        + figure_placeholders(metadata, fig, tab, sec)
        + "\n\n"
        + table_placeholders(metadata, fig, tab, sec)
    )

    out = BUNDLE_DIR / "paper.md"
    out.write_text(paper, encoding="utf-8")
    print(f"wrote {out.relative_to(REPO)}")
    print(f"  size  : {len(paper):,} chars ({out.stat().st_size:,} bytes)")
    print(f"  lines : {paper.count(chr(10))}")
    # Quick sanity tally
    print(f"  remaining \\cite : {len(re.findall(r'\\\\cite', paper))}")
    print(f"  remaining \\ref  : {len(re.findall(r'\\\\ref', paper))}")
    print(f"  remaining \\begin: {len(re.findall(r'\\\\begin', paper))}")


if __name__ == "__main__":
    main()
