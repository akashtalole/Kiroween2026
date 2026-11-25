# Night Shift site

A static, no-build site (HTML, CSS, vanilla JS) in the style of the Kiro Reinvent Labs pages: JSON catalogs in `data/`, markdown rendered in the browser, and a clickable architecture diagram.

| Path | Purpose |
|---|---|
| `index.html` | home: hero, interactive architecture, categories, feature experiments, labs, timeline |
| `ideas.html` | filterable idea bank from `data/ideas.json` |
| `labs.html`, `lab.html` | build labs from `data/labs.json` and `content/labs/*.md` |
| `doc.html` | renders the repo's markdown docs (copied at build time) |
| `assets/` | `site.css`, `site.js` (chrome, theme, markdown), `arch.js` (diagram) |

## Preview locally

```bash
bash site/preview.sh _site
python3 -m http.server -d _site 8000   # open http://localhost:8000
```

## Deploy

`.github/workflows/pages.yml` assembles the site and publishes it with GitHub Pages. One-time setup: repository **Settings → Pages → Source: GitHub Actions**. Expected URL: `https://akashtalole.github.io/Kiroween2026/`.

External scripts (pinned): `marked@12.0.2` from cdnjs and `mermaid@10.9.1` from jsDelivr. If they fail to load, pages fall back to showing raw markdown.
