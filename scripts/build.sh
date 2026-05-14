#!/usr/bin/env bash
# Rebuild the entire bundle in the canonical order.
#
# Run this any time manuscript/, replication/, or one of the scripts changes.
# The five steps must run in this order:
#
#   1. extract_metadata.py   — parses the .tex and table sources into metadata.json
#   2. extract_refs.py       — pulls cited works out of biblibrary.bib → references.json
#   3. extract_code.py       — bundles the curated replication files → replication.md
#   4. tex_to_md.py          — produces paper.md from main .tex + Appendix.tex,
#                              resolving refs/citations against metadata + references.json
#   5. assemble_bundle.py    — copies PNGs to bundle/figures/<id>_<panel>.png and
#                              rewrites metadata.json so files[].file points to the
#                              bundled name. Must be LAST: re-running extract_metadata
#                              after this resets the names back to the manuscript form.

set -euo pipefail
cd "$(dirname "$0")/.."

python3 scripts/extract_metadata.py
python3 scripts/extract_refs.py
python3 scripts/extract_code.py
python3 scripts/tex_to_md.py
python3 scripts/assemble_bundle.py
