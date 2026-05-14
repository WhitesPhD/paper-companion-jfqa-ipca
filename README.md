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

scripts/              Build pipeline. `bash scripts/build.sh` regenerates the
                      whole bundle in the right order.

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
- **BYOK.** Your API key lives in `sessionStorage`, never leaves your browser,
  wipes when you close the tab.

The widget was adapted from the
[ECOM215 course chat](https://github.com/WhitesPhD/ECOM215/tree/main/chat) —
same UI shell and BYOK pattern, different problem (one paper in long context
vs. a chunked course corpus with RAG).

## Building the bundle locally

If you have the source materials (`manuscript/JFQA_IPCA.tex`,
`manuscript/Appendix.tex`, `manuscript/Figures/*`, `manuscript/Tables/*`, the
`biblibrary.bib`, and the `replication/` tree from Dataverse):

```bash
bash scripts/build.sh
```

That runs five scripts in order: `extract_metadata.py`, `extract_refs.py`,
`extract_code.py`, `tex_to_md.py`, `assemble_bundle.py`. Output lands in
`bundle/`. To preview before pushing:

```bash
python3 -m http.server 8000
# visit http://localhost:8000/chat/
```

## License

Code in this repo (the widget and build scripts): MIT.

The paper text and figures included under `bundle/` belong to the authors and
are posted under the open-access terms of the *Journal of Financial and
Quantitative Analysis*. The canonical version of the paper is at
<https://doi.org/10.1017/S0022109025102329>; the canonical replication
package is at <https://doi.org/10.7910/DVN/IQR5DH>.
