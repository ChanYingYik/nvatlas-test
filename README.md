# Nominal / Verb

An interactive English-Chinese corpus explorer for the Translation Technology
final project. It studies how English nominal meanings are realised as Chinese
verbs in 500 supplied subtitle sentence pairs.

## Features

- Keyword search and linked filters for category, verb position and human check.
- Interactive bilingual network, hierarchy (treemap), heatmap and data grid.
- Cross-view selection and URL-shareable filter state.
- English / Traditional Chinese interface switch.
- Filtered CSV export.
- Reproducible 50-entry quality-check sample with local result export.
- Learning report, codebook, AI use declaration and provenance notes.

## Local preview

The site is static and has no build dependencies. Serve the repository root:

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000>.

## Rebuild the browser data

The original supplied file is `NVAtlas-AI-Agent.csv`. To preserve its source text
and regenerate the analysis fields:

```bash
python3 scripts/build_corpus.py
```

This writes `data/corpus.json`. The script validates that there are exactly 500
non-empty rows and applies the coding rules published in `codebook.html`.

## Data status

The source, translation, English nominal and Chinese verb are preserved from the
supplied CSV. The OpenSubtitles 2024 en-zh_CN label is inferred from the course
example and sentence-ID format; it still needs confirmation against the original
download.

No row is marked as human checked in the published dataset. Complete the seeded
50-entry review in `review.html` before submission and incorporate the verified
results into `data/corpus.json`. This human check is intentionally not fabricated.

## GitHub Pages

The site is designed for GitHub Pages from the `main` branch and repository root.
Expected URL:

<https://chanyingyik.github.io/nvatlas-test/>
