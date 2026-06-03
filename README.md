# Paper companion — *Mispricing and Risk Compensation in Cryptocurrency Returns*

A BYOK (bring-your-own-key) chat widget that helps readers of [Babiak &
Bianchi, *JFQA* 2026](https://doi.org/10.1017/S0022109025102329) understand
the paper. Paste an Anthropic or OpenAI key, ask a question. The widget loads
the full paper text, the cited references, and the table data into the
model's context every turn — and the curated replication code on demand,
behind an opt-in sidebar toggle — so answers stay grounded in the paper
rather than the model's training data.

→ **Embedded:** opens as a modal from the publication page at
  <https://www.whitesphd.com/publications/pub1/>

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
                        IPCA estimator library (ipca.py). Loaded into the
                        model's context only when the reader ticks "Include
                        replication code" in the sidebar — keeps the default
                        prompt small enough to fit Tier 1 rate limits.
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

- **Long-context, not RAG.** The full paper text plus a structured metadata
  index and the cited references go into the system prompt every turn
  (≈45k tokens). Anthropic prompt caching keeps per-turn cost low after the
  first call.
- **Replication code is opt-in.** A sidebar toggle ("Include replication
  code") attaches the curated source on the next call (~50k extra tokens).
  Off by default so the cached prefix fits a Tier 1 Anthropic key on Haiku
  4.5 (50k input tokens/min). The widget retries once on a 429, surfacing
  the wait time and pointing the reader at the toggle or a tier upgrade.
- **Multimodal, on request.** Naming a figure ("Show me Figure 5", "Appendix
  Figure 6c") attaches the PNG(s) to that turn's API request — the model
  describes what's actually in the image rather than paraphrasing the caption.
- **Grounded definitions.** A "Definitional questions" block in the system
  prompt tells the model to quote the paper's exact definition of a concept
  with a section/table cite, and not to enumerate sibling characteristics
  from the same group as alternative measures of the same construct.
- **BYOK.** The API key lives in `sessionStorage`, never leaves the browser,
  wipes when the tab closes.

## Security and privacy

BYOK by design. The widget makes API calls directly from the reader's browser
to the provider the reader chose (Anthropic or OpenAI), with the reader's own
API key.

- The API key lives only in the tab's `sessionStorage`. It is never sent to
  any server other than the chosen provider's API endpoint, and is wiped when
  the tab closes.
- There is no telemetry, analytics, or logging in the widget.
- The Anthropic call uses the `anthropic-dangerous-direct-browser-access`
  header — Anthropic's deliberately-named opt-in for BYOK browser apps. It
  does not transmit any extra data.
- The widget's source is one auditable static HTML file (`chat/index.html`);
  the bundle it loads is the handful of files in `bundle/`.

If you embed this widget on your own site by iframing the GitHub Pages URL
from this repo, you are trusting the maintainer not to push a future commit
that logs keys. For defensive deployment, fork the repo, point GitHub Pages
at your fork, and iframe your fork's URL.

## Adapting this for another paper

### Before you start

You are responsible for verifying that (a) your paper's publication terms
permit redistributing the full text and figures — Creative Commons
Attribution licences do; many subscription-journal accepted-manuscript
policies do not cover the typeset version — and (b) anything you bundle from
your replication package is yours to redistribute (some replication trees
depend on data feeds with terms that don't permit re-distribution, e.g.
proprietary market data).

### Steps

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

## Embedding on a host page

The widget can be opened in-page from a host site (project page, paper
landing page, etc.) via a small modal that lazy-loads the standalone
URL into an iframe on first open. The pattern used at
<https://www.whitesphd.com/publications/pub1/> is a single block of
HTML/CSS/JS dropped into the page markup — a button labelled "Ask the
paper", a hidden overlay containing the iframe, and ~25 lines of JS for
open/close handlers (×, outside-click, Escape). Two prerequisites:

- The widget's static URL must be reachable (GitHub Pages enabled, repo
  public or on a paid plan).
- The host site must allow raw HTML in its content (for Hugo, set
  `markup.goldmark.renderer.unsafe: true` in the site config).

The iframe stays mounted between opens so chat state and the API key
in `sessionStorage` persist within a single page visit.

## Use of this repository

### What forks are encouraged to do

Clone this repo as a template, swap `bundle/` for your own paper's materials,
edit `chat/index.html` for your paper's title and audience, and ship a
companion widget for your own work. See "Adapting this for another paper"
above for the workflow.

### What you may not do

- Host the Babiak–Bianchi paper materials (`bundle/paper.md`,
  `bundle/figures/`, `bundle/replication.md`) without the CC BY 4.0
  attribution intact, or in a way that suggests authorship by anyone other
  than Mykola Babiak and Daniele Bianchi.
- Modify the paper text or figures and present the modified version as the
  original — CC BY 4.0 requires you to indicate that changes were made.
- Use the paper materials in a way that implies endorsement by the authors
  of a derivative product, service, or claim.

The widget code in `chat/`, `scripts/`, and `eval/` is MIT-licensed and you
may modify and redistribute it freely; legitimate forks rebundle a different
paper, they don't strip the attribution and re-host this one.

## License

Code in this repo — the widget (`chat/index.html`), the build scripts under
`scripts/`, and the reader-eval set under `eval/` — is released under the
**MIT License**.

The paper materials reproduced in `bundle/` — the full paper text
(`paper.md`), the figure panels (`figures/`), and the curated replication
excerpts (`replication.md`) — come from:

> Babiak, M., and Bianchi, D. "Mispricing and Risk Compensation in
> Cryptocurrency Returns." *Journal of Financial and Quantitative Analysis*,
> 2026. <https://doi.org/10.1017/S0022109025102329>

published as Open Access under the **[Creative Commons Attribution 4.0
International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)**
licence. Re-use, redistribution, and adaptation are permitted with
attribution. The canonical replication package is at
<https://doi.org/10.7910/DVN/IQR5DH>.
