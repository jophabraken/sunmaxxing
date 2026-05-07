# sunmaxxing.com — Sunmaxxing

Find the sunny terrace in Berlin, right now. Live sun-math over OpenStreetMap
venues and building footprints.

## What makes a user's cold start fast

On a fresh visit, the app needs two datasets: the list of outdoor terraces
(~2,400 venues) and building footprints for the shadow math (~40k buildings).
Pulling those from OSM's public Overpass API on every page load is slow and
flaky — Overpass is under heavy load and frequently returns 429 / 503 / timeouts.

So this repo ships **pre-baked static JSON** alongside `index.html`:

```
data/
  venues.json      (~1 MB)
  buildings.json   (~8–15 MB)
  manifest.json
```

The app fetches those first. They're served from Cloudflare's CDN, usually in
well under a second. If the files are missing (e.g., the bake has never run)
or the app is running on a domain that doesn't have them yet, `index.html`
falls back to querying Overpass directly — it still works, just slower.

A GitHub Actions workflow (`.github/workflows/bake-data.yml`) rebakes the JSON
every night. Cloudflare Pages, watching this repo, redeploys automatically on
each `main` push.

## Repo layout

```
index.html                       the whole app, single file
data/*.json                      static OSM bundles (regenerated nightly)
scripts/bake-data.js             the baker — fetches Overpass, writes data/
.github/workflows/bake-data.yml  nightly cron that runs the baker
deploy/                          ignore this in the repo; legacy drag-drop bundle
```

## First-time setup (one-off)

The site is currently deployed via Cloudflare Pages drag-and-drop. To unlock
nightly auto-rebakes, move it onto a git-backed Pages project:

1. **Create a GitHub repo** and push this folder to `main`.
2. **Cloudflare Pages → sunmaxxing → Settings → Builds & deployments →
   Connect to Git.** Pick the new repo and the `main` branch. Build command:
   *(leave empty — it's a static site)*. Build output directory: `/`.
3. **GitHub repo → Settings → Actions → General → Workflow permissions:
   "Read and write permissions"**. Save. This lets the workflow push the
   refreshed `data/` files back to `main`.
4. **Bake once to seed the data.** Either:
   - Locally: `node scripts/bake-data.js` (needs Node 18+), then commit the
     resulting `data/` folder and push.
   - Or: GitHub → Actions → "Bake OSM data nightly" → **Run workflow**.
     It'll take 5–10 minutes.

After that, every night at 03:40 UTC the workflow pulls fresh data, commits
it, and Cloudflare auto-deploys the new bundle. Users always see data less
than 24 hours old.

## Running the baker locally

```bash
node scripts/bake-data.js
```

Requires Node 18+ (for global `fetch`). No npm install needed — uses only
Node's standard library.

Output: `data/venues.json`, `data/buildings.json`, `data/manifest.json`.

The baker is deliberately patient: it queries Overpass serially with pauses
between calls, retries failed tiles, and can take 5–10 minutes. That's fine —
it's not on any user's critical path.

## How the app decides static vs. live

Inside `index.html`:

```js
async function loadVenuesData(){
  try {
    const r = await fetch('data/venues.json');
    if (r.ok) return await r.json();       // ← fast path
  } catch {}
  return await overpass(venueQuery(), …);  // ← fallback: live Overpass
}
```

Same pattern for buildings. The static and live paths return the same JSON
shape (raw Overpass response), so the parsing code in the browser is identical.

If you ever want to force the fallback path for testing, rename `data/` to
something else temporarily.

## Progressive rendering

Even if both static files take a moment, the map and all venue markers render
as soon as `venues.json` arrives. The markers start as neutral dots; they
color in (sunny / shaded / cloudy) as the shadow math completes in the
background — users never stare at a blank loader.

## Changing the map area

The bbox lives in two places and must be kept in sync:

```js
// index.html
const BBOX = { south: 52.488, west: 13.350, north: 52.550, east: 13.470 };
```

```js
// scripts/bake-data.js
const BBOX = { south: 52.488, west: 13.350, north: 52.550, east: 13.470 };
```

Bigger bbox → bigger `buildings.json`. 60×60 km starts to get unwieldy
(>50 MB). If you want to cover more than central Berlin, consider switching
to Cloudflare R2 for the static bundle.
