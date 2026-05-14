# Paper companion — *Mispricing and Risk Compensation in Cryptocurrency Returns*

A BYOK (bring-your-own-key) chat widget that helps readers of [Babiak &
Bianchi, *JFQA* 2026](https://doi.org/10.1017/S0022109025102329) understand
the paper. Paste an Anthropic or OpenAI key, ask a question. The widget loads
the full paper text, the cited references, the table data, and a curated
subset of the replication code into the model's context every turn, so answers
stay grounded in the paper rather than the model's training data.

→ **Live:** <https://whitesphd.github.io/paper-companion-jfqa-ipca/chat/>

## What's in this repo

```
chat/index.html       The widget. Single static page; loads marked.js + KaTeX
                      from CDN; fetches the bundle below at boot.

bundle/               What the widget loads at runtime.
  paper.md              Clean Markdown of the full paper, with [FIGURE figN]
                        / [TABLE tabN] placeholders. Sections are anchored,
                        math survives as LaTeX, table bodies are embedded as
                        fenced LaTeX so the model sees the actual numbers.
  metadata.json         Structured registry: title, authors, sections,
                        figures (id, label, sub-panel files, caption), tables,
                        characteristic-group map.
  references.json       Cited works only (extracted from biblibrary.bib).
  replication.md        Curated subset of the replication package: the data
                        pipeline (data_chrs.py, data_cleaning.py, …) and the
                        IPCA estimator library (ipca.py).
  figures/*.png         Every figure panel, renamed under stable IDs
                        (fig5.png, appfig6_c.png, …).
  manifest.json         Per-file size + sha256, for cache-busting.

scripts/              Build pipeline. Five Python scripts that read the
                      manuscript and replication trees and write `bundle/`.
                      Run via `bash scripts/build.sh`.

eval/questions.md     20 reader questions across 4 audience tiers
                      (journalist, practitioner, MSc, PhD) for accuracy checks.
```

The original LaTeX (`manuscript/`) and full replication tree (`replication/`)
are not in this repo — the .tex source lives with the authors and the
replication package is on
[Harvard Dataverse](https://doi.org/10.7910/DVN/IQR5DH).

## Design choices

- **Long-context, not RAG.** The full paper goes into the system prompt every
  turn. Anthropic prompt caching keeps per-turn cost reasonable after the
  first call.
- **Multimodal, on request.** Naming a figure ("Show me Figure 5", "Appendix
  Figure 6c") attaches the PNG(s) to that turn's API request — the model
  describes what's actually in the image rather than paraphrasing the caption.
- **BYOK.** The API key lives in `sessionStorage`, never leaves the browser,
  wipes when the tab closes.

## Adapting this for another paper

To build a similar companion for a different paper, clone this repo as a
template and replace the per-paper pieces:

1. **Drop your sources beside the existing folders.** You'll need a
   `manuscript/` with the main `.tex`, an `Appendix.tex`, `Figures/`,
   `Tables/`, and `biblibrary.bib`; and a `replication/` tree from your
   data/code archive.

2. **Edit `scripts/extract_metadata.py`** — update the hard-coded title,
   authors, journal, DOI, and any paper-specific structures (this repo
   carries a `characteristic_groups` map for the IPCA factor families; your
   paper will have its own).

3. **Edit `scripts/extract_code.py`** — change the inclusion list to point
   at the replication files you want bundled into `replication.md`.

4. **Edit `chat/index.html`** — update the page title, the header subtitle,
   the system-prompt audience and instructions, and the welcome message.

5. **Run the pipeline:**

   ```bash
   bash scripts/build.sh
   ```

   This runs `extract_metadata.py`, `extract_refs.py`, `extract_code.py`,
   `tex_to_md.py`, `assemble_bundle.py` in order. Output lands in `bundle/`.

6. **Push to a GitHub Pages-enabled repo** and point Pages at the `main`
   branch. The live URL serves `chat/index.html` directly.

## License

Code in this repo (the widget and build scripts): MIT.

The paper text and figures included under `bundle/` belong to the authors and
are posted under the open-access terms of the *Journal of Financial and
Quantitative Analysis*. The canonical version of the paper is at
<https://doi.org/10.1017/S0022109025102329>; the canonical replication
package is at <https://doi.org/10.7910/DVN/IQR5DH>.
