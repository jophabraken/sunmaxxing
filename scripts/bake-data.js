#!/usr/bin/env node
/**
 * bake-data.js — pull Berlin venues + buildings from Overpass and write
 * static JSON bundles that the app serves from the CDN. Run nightly via
 * GitHub Actions (see .github/workflows/bake-data.yml).
 *
 * Philosophy: this script is patient, not user-facing. It can take 5-10
 * minutes if Overpass is slow or rate-limited — that's fine. Every user
 * on sunmaxxing.com wins that time back.
 *
 * Usage:
 *   node scripts/bake-data.js
 *
 * Output:
 *   data/venues.json
 *   data/buildings.json
 *   data/manifest.json
 *
 * Requires: Node 18+ (for global fetch).
 */

const fs = require('node:fs');
const path = require('node:path');

// ─── Config ─────────────────────────────────────────────────────────────────
// Keep this in sync with the BBOX constant in index.html.
const BBOX = { south: 52.488, west: 13.350, north: 52.550, east: 13.470 };

const ENDPOINTS = [
  'https://overpass-api.de/api/interpreter',
  'https://overpass.private.coffee/api/interpreter',
  'https://overpass.kumi.systems/api/interpreter',
];

const BUILDING_TILES_PER_SIDE = 4;   // 4×4 = 16 smaller tiles for gentler load
const PER_ATTEMPT_TIMEOUT_MS  = 120_000;
const MAX_ATTEMPTS_PER_QUERY  = 5;
const PAUSE_BETWEEN_QUERIES_MS = 2500;  // be nice to public endpoints

const OUT_DIR = path.resolve(__dirname, '..', 'data');

// ─── Utilities ──────────────────────────────────────────────────────────────
function bboxStr(b){ return `${b.south},${b.west},${b.north},${b.east}`; }
function sleep(ms){ return new Promise(r => setTimeout(r, ms)); }

function venueQuery(){
  const b = bboxStr(BBOX);
  return `
    [out:json][timeout:120];
    (
      node["amenity"~"^(bar|pub|cafe|restaurant|biergarten|ice_cream)$"]["outdoor_seating"="yes"](${b});
      way ["amenity"~"^(bar|pub|cafe|restaurant|biergarten|ice_cream)$"]["outdoor_seating"="yes"](${b});
      node["amenity"="biergarten"](${b});
      way ["amenity"="biergarten"](${b});
    );
    out center tags;
  `;
}

function buildingTileQuery(tileBbox){
  return `[out:json][timeout:180];(way["building"](${bboxStr(tileBbox)}););out geom;`;
}

async function fetchOverpassOnce(endpoint, query, attempt){
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), PER_ATTEMPT_TIMEOUT_MS);
  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'sunmaxxing-baker/1.0 (https://sunmaxxing.com)',
      },
      body: 'data=' + encodeURIComponent(query),
      signal: ctrl.signal,
    });
    clearTimeout(timer);
    if (!res.ok) throw new Error('HTTP ' + res.status + ' from ' + endpoint);
    return await res.json();
  } finally {
    clearTimeout(timer);
  }
}

async function fetchOverpass(query, label){
  let lastErr;
  for (let attempt = 1; attempt <= MAX_ATTEMPTS_PER_QUERY; attempt++){
    for (const endpoint of ENDPOINTS){
      try {
        process.stdout.write(`  ${label}: attempt ${attempt} @ ${new URL(endpoint).host} …`);
        const t0 = Date.now();
        const j = await fetchOverpassOnce(endpoint, query, attempt);
        const took = ((Date.now() - t0)/1000).toFixed(1);
        const n = (j?.elements?.length ?? 0);
        process.stdout.write(` ok (${n} elements, ${took}s)\n`);
        return j;
      } catch (e) {
        lastErr = e;
        process.stdout.write(` fail (${e.message})\n`);
        await sleep(PAUSE_BETWEEN_QUERIES_MS);
      }
    }
    // Backoff between rounds
    const backoff = 5000 * attempt;
    console.log(`  (waiting ${backoff/1000}s before retry round ${attempt + 1})`);
    await sleep(backoff);
  }
  throw lastErr || new Error('All Overpass attempts failed for ' + label);
}

// ─── Venues ─────────────────────────────────────────────────────────────────
async function bakeVenues(){
  console.log('▸ Baking venues…');
  const json = await fetchOverpass(venueQuery(), 'venues');
  // We write the raw Overpass response so the browser's parseVenues() can
  // consume it unchanged — static and live paths use identical parsers.
  return json;
}

// ─── Buildings (tiled) ──────────────────────────────────────────────────────
function makeTiles(bbox, n){
  const dLat = (bbox.north - bbox.south) / n;
  const dLng = (bbox.east  - bbox.west ) / n;
  const tiles = [];
  for (let i = 0; i < n; i++){
    for (let j = 0; j < n; j++){
      const s = bbox.south + i * dLat;
      const north = (i === n - 1) ? bbox.north : s + dLat;
      const w = bbox.west + j * dLng;
      const east  = (j === n - 1) ? bbox.east : w + dLng;
      tiles.push({ south: s, west: w, north, east });
    }
  }
  return tiles;
}

// Cloudflare Pages rejects any file >25 MiB, and raw OSM data for central
// Berlin comes in around 27 MiB. Two cheap, lossless-enough shrinks:
//
//   1. Round geometry coords to 5 decimals (≈1.1 m at 52°N — finer than the
//      shadow-precision the app needs, and way finer than the rendered pixels).
//   2. Drop tags we don't use in the client. Buildings only need footprint
//      and heights; names, addresses, and OSM bookkeeping just bloat the bundle.
//
// Together these typically cut 35–45% off the file size.
const COORD_DECIMALS = 5;
const KEEP_BUILDING_TAGS = new Set([
  'building',
  'building:levels',
  'building:min_level',
  'min_level',
  'height',
  'min_height',
  'roof:shape',
  'roof:height',
  'roof:levels',
]);

function roundCoord(v){
  return +v.toFixed(COORD_DECIMALS);
}

function slimBuildingElement(el){
  // Shape: { id, type, geometry: [{lat, lon}, …], tags: {...}, bounds, nodes }
  // The client only reads `geometry` + a handful of `tags`. Everything else
  // (nodes array, bounds, osm bookkeeping) is safe to drop.
  const out = { id: el.id, type: el.type };
  if (Array.isArray(el.geometry)){
    out.geometry = el.geometry.map(p => ({
      lat: roundCoord(p.lat),
      lon: roundCoord(p.lon),
    }));
  }
  if (el.tags){
    const t = {};
    for (const k of Object.keys(el.tags)){
      if (KEEP_BUILDING_TAGS.has(k)) t[k] = el.tags[k];
    }
    if (Object.keys(t).length) out.tags = t;
  }
  return out;
}

async function bakeBuildings(){
  console.log('▸ Baking buildings…');
  const tiles = makeTiles(BBOX, BUILDING_TILES_PER_SIDE);
  const seen = new Set();
  const merged = [];
  let ok = 0, failed = 0;

  for (let i = 0; i < tiles.length; i++){
    const tile = tiles[i];
    const label = `buildings tile ${i+1}/${tiles.length}`;
    try {
      const j = await fetchOverpass(buildingTileQuery(tile), label);
      for (const el of (j.elements || [])){
        if (!seen.has(el.id)){
          seen.add(el.id);
          merged.push(slimBuildingElement(el));
        }
      }
      ok++;
    } catch (e) {
      console.warn(`  !! ${label} failed: ${e.message}`);
      failed++;
    }
    // Serial, not parallel — be nice to Overpass operators.
    await sleep(PAUSE_BETWEEN_QUERIES_MS);
  }

  if (failed > 0 && ok === 0){
    throw new Error('All building tiles failed');
  }
  console.log(`  buildings: ${ok}/${tiles.length} tiles, ${merged.length} unique buildings`);

  return { elements: merged, _coverage: { okTiles: ok, totalTiles: tiles.length } };
}

// ─── Manifest ───────────────────────────────────────────────────────────────
function buildManifest(venues, buildings){
  return {
    bakedAt: new Date().toISOString(),
    bbox: BBOX,
    venues: { count: (venues.elements || []).length },
    buildings: {
      count: (buildings.elements || []).length,
      tileCoverage: buildings._coverage || null,
    },
    version: 1,
  };
}

// ─── Main ───────────────────────────────────────────────────────────────────
(async () => {
  fs.mkdirSync(OUT_DIR, { recursive: true });

  const venues    = await bakeVenues();
  const buildings = await bakeBuildings();

  // Don't persist the internal coverage flag in the JSON the browser reads.
  const buildingsOut = { elements: buildings.elements || [] };

  const manifest = buildManifest(venues, buildings);

  const venuesPath    = path.join(OUT_DIR, 'venues.json');
  const buildingsPath = path.join(OUT_DIR, 'buildings.json');
  const manifestPath  = path.join(OUT_DIR, 'manifest.json');

  fs.writeFileSync(venuesPath,    JSON.stringify(venues));
  fs.writeFileSync(buildingsPath, JSON.stringify(buildingsOut));
  fs.writeFileSync(manifestPath,  JSON.stringify(manifest, null, 2));

  const sizes = [
    ['venues.json',    fs.statSync(venuesPath).size],
    ['buildings.json', fs.statSync(buildingsPath).size],
    ['manifest.json',  fs.statSync(manifestPath).size],
  ];
  console.log('');
  console.log('✓ Baked.');
  for (const [name, bytes] of sizes){
    console.log(`  ${name}: ${(bytes/1024/1024).toFixed(2)} MB`);
  }
  console.log(`  manifest: ${manifest.venues.count} venues · ${manifest.buildings.count} buildings · ${manifest.bakedAt}`);
})().catch(err => {
  console.error('\n✗ Bake failed:', err);
  process.exit(1);
});
