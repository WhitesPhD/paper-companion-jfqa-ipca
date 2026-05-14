#!/usr/bin/env python3
"""Materialise the figure PNGs into bundle/figures/ under their stable IDs,
and rewrite bundle/metadata.json so the chat widget can look up each panel
by name without knowing the original filename.

Reads:
  bundle/metadata.json           (figure registry — must already exist)
  manuscript/Figures/*.png       (source PNGs)

Writes:
  bundle/figures/<id>.png        (single-panel)
  bundle/figures/<id>_a.png ...  (multi-panel)
  bundle/metadata.json           (in place — files[].file now points to the bundled name)
  bundle/manifest.json           (per-file size + checksum; lets the widget
                                  verify the bundle on load and helps future
                                  cache-busting)
"""

from __future__ import annotations
import hashlib
import json
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANUSCRIPT = REPO / "manuscript"
FIGURES_SRC = MANUSCRIPT / "Figures"
BUNDLE_DIR = REPO / "bundle"
FIGURES_DST = BUNDLE_DIR / "figures"


def panel_name(fig_id: str, panel_idx: int, n_panels: int) -> str:
    if n_panels == 1:
        return f"{fig_id}.png"
    letter = chr(ord("a") + panel_idx)
    return f"{fig_id}_{letter}.png"


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    meta_path = BUNDLE_DIR / "metadata.json"
    if not meta_path.exists():
        raise SystemExit("run scripts/extract_metadata.py first")
    metadata = json.loads(meta_path.read_text())

    FIGURES_DST.mkdir(parents=True, exist_ok=True)
    manifest: list[dict] = []
    missing: list[str] = []
    copied = 0

    for fig in metadata["figures"]:
        files = fig.get("files", [])
        for i, panel in enumerate(files):
            src = FIGURES_SRC / panel["file"]
            if not src.exists():
                missing.append(panel["file"])
                continue
            new_name = panel_name(fig["id"], i, len(files))
            dst = FIGURES_DST / new_name
            shutil.copy2(src, dst)
            copied += 1
            panel["original_file"] = panel.pop("file")
            panel["file"] = new_name
            manifest.append({
                "figure_id": fig["id"],
                "panel": chr(ord("a") + i) if len(files) > 1 else "",
                "file": new_name,
                "original_file": panel["original_file"],
                "bytes": dst.stat().st_size,
                "sha256": sha256_of(dst),
            })

    meta_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (BUNDLE_DIR / "manifest.json").write_text(
        json.dumps({"figures": manifest}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    total_bytes = sum(m["bytes"] for m in manifest)
    print(f"copied {copied} panel files to {FIGURES_DST.relative_to(REPO)}")
    print(f"  total size : {total_bytes:,} bytes ({total_bytes / 1024 / 1024:.1f} MB)")
    print(f"  figures    : {len(metadata['figures'])} entries / {len(manifest)} panels")
    if missing:
        print(f"  MISSING SOURCE PNGS ({len(missing)}):")
        for m in missing:
            print(f"    {m}")


if __name__ == "__main__":
    main()
