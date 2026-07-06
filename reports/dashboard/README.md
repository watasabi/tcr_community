Dashboard scaffold (isolated)

This folder describes how to create an isolated static dashboard using modern JS stacks (Bun / Vite + React) and deploy to GitHub Pages. The dashboard should live separately from the data exploration and app code: keep sources under `reports/dashboard/` and the generated build under `reports/dashboard/dist/` (which you can add to .gitignore or deploy directly).

Quick steps (Bun)

1. From `reports/dashboard/` run:

```bash
# create a Vite React app (when using bun >= 1.0)
cd reports/dashboard
bun create vite ./ --template react
# install deps
bun install
# dev
bun dev
# build
bun build
```

2. The build output will be in `dist/` by default. Serve locally with any static server:

```bash
bunx serve dist
# or
python3 -m http.server --directory dist 8000
```

3. Deploy to GitHub Pages:

- Option A (manual): push `dist/` contents to `gh-pages` branch.
- Option B (GitHub Action): add a workflow to build and deploy `reports/dashboard/dist` to gh-pages.

Notes

- Keep `reports/dashboard/` self-contained. Do NOT import or move exploration notebooks or CSV readers there; the dashboard should consume the generated `reports/profile_report.html` data or a small JSON export produced by `generate_profile_report.py`.
- If you want, I can scaffold a minimal Vite+React app here and wire a small endpoint that reads `reports/association_results.csv` (exported as JSON) and shows interactive charts. Tell me and I'll scaffold it.
