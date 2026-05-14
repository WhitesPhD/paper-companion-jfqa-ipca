#!/usr/bin/env python3
"""Bundle a curated subset of replication source into bundle/replication.md.

The curated set is the files that answer "how is X computed?" or "how is
the estimator implemented?" — the data pipeline + the IPCA library. Empirical
scripts (one per figure/table) are NOT in the curated set; they're recoverable
from the README's mapping, which is also included so the model knows what's
missing and can point the reader at the right script on Dataverse.

Reads:
  replication/Data/data_codes/data_chrs.py        (35 characteristic formulas)
  replication/Data/data_codes/data_cleaning.py    (sample filters)
  replication/Data/data_codes/data_builder.py     (panel assembly + FF merge)
  replication/Data/data_codes/data_fetch.py       (CryptoCompare ingest)
  replication/CODE/ipca_prop/ipca.py              (IPCA estimator — ALS loop)
  replication/README.md                           (script → output mapping)

Writes:
  bundle/replication.md
"""

from __future__ import annotations
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REPL = REPO / "replication"
BUNDLE = REPO / "bundle"
OUTPUT = BUNDLE / "replication.md"

# (relative path, code-fence language, one-line role description)
CURATED = [
    ("CODE/ipca_prop/ipca.py", "python",
     "The IPCA estimator. The alternating least squares loop that iterates "
     "over $\\Gamma$ and the latent factors $f_{t+1}$ lives here; use it to "
     "ground answers about the estimation mechanics."),
    ("Data/data_codes/data_chrs.py", "python",
     "Computes the 35 asset characteristics in Table 1 (and Appendix B). "
     "Use this to answer questions like \"how exactly is `max30` / `illiq` / "
     "`co-skew` computed?\" with the actual formula instead of a paraphrase."),
    ("Data/data_codes/data_cleaning.py", "python",
     "Sample filters: zero/negative price drops, return guards "
     "($-100\\%$ / $+150\\%$), ticker screens, winsorisation."),
    ("Data/data_codes/data_builder.py", "python",
     "Assembles the cleaned cross-sectional panel and merges Fama-French "
     "factors. Drives the order the characteristic functions run in."),
    ("Data/data_codes/data_fetch.py", "python",
     "Downloads OHLCV + social + blockchain metrics from CryptoCompare "
     "(and IntoTheBlock via CryptoCompare). Authoritative source for the "
     "raw-data step."),
    ("README.md", "markdown",
     "Maps every empirical script in `CODE/` (one per figure/table) to the "
     "output it produces. The empirical scripts themselves are not bundled; "
     "this README is enough to tell the reader which file to open on Dataverse."),
]

HEADER = """# Replication code (curated subset)

Foundational code from the paper's replication package on Harvard Dataverse.
Use these files to answer "how is X computed?" or "how is the estimator
implemented?" questions with the actual formula rather than a paraphrase.

The empirical scripts that reproduce each individual figure/table (one
`CODE/Figure_*.py` or `CODE/Table_*.py` per output) are not embedded — the
README at the bottom maps each one to its output, so you can still point the
reader at the right file on Dataverse when they ask.

---
"""


def main() -> None:
    BUNDLE.mkdir(exist_ok=True)
    parts: list[str] = [HEADER]
    total = 0
    missing: list[str] = []

    for relpath, lang, role in CURATED:
        src = REPL / relpath
        if not src.exists():
            missing.append(relpath)
            continue
        text = src.read_text(encoding="utf-8", errors="replace").rstrip()
        total += len(text)
        parts.append(
            f"\n## `replication/{relpath}`\n\n{role}\n\n```{lang}\n{text}\n```\n"
        )

    OUTPUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(REPO)}")
    print(f"  files       : {len(CURATED) - len(missing)} of {len(CURATED)}")
    print(f"  code        : {total:,} chars")
    print(f"  output size : {OUTPUT.stat().st_size:,} bytes")
    if missing:
        print(f"  MISSING ({len(missing)}):")
        for m in missing:
            print(f"    {m}")


if __name__ == "__main__":
    main()
