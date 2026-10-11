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
const SunCalc = require('suncalc');

// ─── Config ─────────────────────────────────────────────────────────────────
// We run the pipeline with TWO boxes, decoupled on purpose:
//
//   BBOX_VENUES           — what the site actually covers. Venues are fetched
//                           and displayed over this wide box. Also the box the
//                           client map opens in (kept in sync with index.html).
//
//   BBOX_BUILDINGS_COMPUTE — buildings we fetch for the bake, slightly wider
//                           than BBOX_VENUES so shadows from buildings just
//                           outside the display area still land correctly on
//                           edge venues. Used only internally on the runner.
//
//   BBOX_BUILDINGS_DEPLOY — the central subset of buildings we ship in
//                           buildings.json. Cloudflare Pages rejects files
//                           over 25 MiB, so we only ship the dense inner
//                           Berlin tile. This is a FALLBACK-ONLY artifact: the
//                           fast path is windows-today.json (pre-computed from
//                           the full compute set) which covers every venue
//                           with accurate shadows regardless of this bbox.
//
// Expanded Apr 2026 from the old 52.47–52.55 × 13.35–13.49 box (~9×9km,
// inner Mitte only) to cover Charlottenburg, Wilmersdorf, Schöneberg,
// Neukölln South, Tempelhof, Pankow, Lichtenberg, upper Treptow-Köpenick.
const BBOX_VENUES = {
  south: 52.440, west: 13.240, north: 52.570, east: 13.570,
};
const BBOX_BUILDINGS_COMPUTE = {
  south: BBOX_VENUES.south - 0.010,
  west:  BBOX_VENUES.west  - 0.015,
  north: BBOX_VENUES.north + 0.010,
  east:  BBOX_VENUES.east  + 0.015,
};
const BBOX_BUILDINGS_DEPLOY = {
  south: 52.470, west: 13.350, north: 52.550, east: 13.490,
};

// Primary bbox reported in manifest.json — clients and dashboards that read
// manifest.bbox see the venue coverage (what the site shows), not the
// internal compute/deploy scoping.
const BBOX = BBOX_VENUES;

const ENDPOINTS = [
  'https://overpass-api.de/api/interpreter',
  'https://overpass.private.coffee/api/interpreter',
  'https://overpass.kumi.systems/api/interpreter',
];

const BUILDING_TILES_PER_SIDE = 7;   // 7×7 = 49 smaller tiles across the wider compute box
const PER_ATTEMPT_TIMEOUT_MS  = 120_000;
const MAX_ATTEMPTS_PER_QUERY  = 5;
const PAUSE_BETWEEN_QUERIES_MS = 2500;  // be nice to public endpoints

const OUT_DIR = path.resolve(__dirname, '..', 'data');

// ─── Utilities ──────────────────────────────────────────────────────────────
function bboxStr(b){ return `${b.south},${b.west},${b.north},${b.east}`; }
function sleep(ms){ return new Promise(r => setTimeout(r, ms)); }

function venueQuery(){
  const b = bboxStr(BBOX_VENUES);
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

function insideBbox(bbox, lat, lon){
  return lat >= bbox.south && lat <= bbox.north
      && lon >= bbox.west  && lon <= bbox.east;
}
function geometryCentroid(geom){
  if (!Array.isArray(geom) || !geom.length) return null;
  let clat = 0, clon = 0;
  for (const p of geom){ clat += p.lat; clon += p.lon; }
  return { lat: clat / geom.length, lon: clon / geom.length };
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
  console.log(`  compute bbox: ${bboxStr(BBOX_BUILDINGS_COMPUTE)}`);
  console.log(`  deploy bbox:  ${bboxStr(BBOX_BUILDINGS_DEPLOY)}`);
  const tiles = makeTiles(BBOX_BUILDINGS_COMPUTE, BUILDING_TILES_PER_SIDE);
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
  console.log(`  buildings (compute): ${ok}/${tiles.length} tiles, ${merged.length} unique buildings`);

  // Split: compute set keeps all buildings (used for windows-today.json accuracy),
  // deploy set is the central subset that ships in buildings.json. A building
  // is in the deploy set if its centroid falls inside BBOX_BUILDINGS_DEPLOY.
  const deployElements = [];
  for (const el of merged){
    const c = geometryCentroid(el.geometry);
    if (c && insideBbox(BBOX_BUILDINGS_DEPLOY, c.lat, c.lon)){
      deployElements.push(el);
    }
  }
  console.log(`  buildings (deploy):  ${deployElements.length} buildings in central subset`);

  return {
    elements:       merged,
    deployElements,
    _coverage:      { okTiles: ok, totalTiles: tiles.length },
  };
}

// ─── Sun windows (the big first-load win) ──────────────────────────────────
// Port of the client-side shadow math from index.html. We do the ray-cast
// once per night on a big GitHub Actions runner so every visitor skips it.
//
// The output `windows-today.json` contains a { venueId → [[startMs,endMs]…] }
// map. The client loads it in phase 1 (alongside venues) and can skip
// buildings.json entirely on the critical path — ~17 MB of bandwidth and
// several seconds of main-thread work per visitor, eliminated.

const CENTER = [52.520, 13.405];            // keep in sync with index.html
const SUN_WINDOW_STEP_MIN = 5;
const MAX_SHADOW_SEARCH_RADIUS = 500;       // metres
const METERS_PER_LEVEL = 3.0;

function toMeters(lat, lng){
  const latRad = CENTER[0] * Math.PI / 180;
  const x = (lng - CENTER[1]) * Math.cos(latRad) * 111320;
  const y = (lat - CENTER[0]) * 111320;
  return [x, y];
}
function parseHeightTags(t){
  if (t && t.height){
    const h = parseFloat(String(t.height).replace(',', '.'));
    if (!isNaN(h) && h > 0) return h;
  }
  if (t && t['building:levels']){
    const l = parseFloat(String(t['building:levels']).replace(',', '.'));
    if (!isNaN(l) && l > 0) return l * METERS_PER_LEVEL;
  }
  return 8; // default ~2-3 stories — matches client assumption
}
function preprocessBuildings(elements){
  const out = [];
  for (const el of elements){
    if (!el.geometry || el.geometry.length < 3) continue;
    const poly = el.geometry.map(g => toMeters(g.lat, g.lon));
    let cx=0, cy=0;
    for (const [x,y] of poly){ cx+=x; cy+=y; }
    cx /= poly.length; cy /= poly.length;
    let r=0;
    for (const [x,y] of poly){
      const d = Math.hypot(x-cx, y-cy);
      if (d>r) r=d;
    }
    out.push({ poly, heightM: parseHeightTags(el.tags), cx, cy, br: r });
  }
  return out;
}

// Spatial grid index. Without this, bakeWindows is O(venues × all_buildings)
// per time step: for our widened Berlin BBOX (~200k buildings × 7k venues ×
// 170 steps) that's 240B inner-loop iterations and blows past the 45-minute
// GitHub Actions timeout. With it, each venue only checks buildings in its
// ~600m neighborhood, cutting the hot path ~100×.
//
// Cells are keyed on the (x,y) meter grid around CENTER. We bucket by the
// centroid; a building can only cast a venue shadow if its centroid sits
// within MAX_SHADOW_SEARCH_RADIUS + br of the venue, so querying the 3-cell
// neighborhood (with GRID_CELL_M=200 and a max br ~100m) is enough.
const GRID_CELL_M = 200;
function cellKey(cx, cy){
  return ((cx / GRID_CELL_M) | 0) + ':' + ((cy / GRID_CELL_M) | 0);
}
function buildBuildingGrid(bldgs){
  const grid = new Map();
  for (const b of bldgs){
    const k = cellKey(b.cx, b.cy);
    let bucket = grid.get(k);
    if (!bucket){ bucket = []; grid.set(k, bucket); }
    bucket.push(b);
  }
  return grid;
}
// Return every building whose centroid is within `radiusM` of (x,y).
// Cheap superset — the isShaded inner loop still filters precisely.
function buildingsNearPoint(grid, x, y, radiusM){
  const out = [];
  const cells = Math.ceil(radiusM / GRID_CELL_M);
  const gx = (x / GRID_CELL_M) | 0;
  const gy = (y / GRID_CELL_M) | 0;
  for (let dx=-cells; dx<=cells; dx++){
    for (let dy=-cells; dy<=cells; dy++){
      const bucket = grid.get((gx+dx) + ':' + (gy+dy));
      if (bucket) for (const b of bucket) out.push(b);
    }
  }
  return out;
}
function rayFirstHit(ox, oy, dx, dy, poly){
  let minT = Infinity;
  for (let i=0; i<poly.length; i++){
    const ax=poly[i][0], ay=poly[i][1];
    const bx=poly[(i+1)%poly.length][0], by=poly[(i+1)%poly.length][1];
    const ex=bx-ax, ey=by-ay;
    const denom = dx*ey - dy*ex;
    if (Math.abs(denom) < 1e-9) continue;
    const t = ((ax-ox)*ey - (ay-oy)*ex)/denom;
    const s = ((ax-ox)*dy - (ay-oy)*dx)/denom;
    if (t > 1e-6 && s >= 0 && s <= 1 && t < minT) minT = t;
  }
  return minT === Infinity ? null : minT;
}
function pointInPoly(x, y, poly){
  let inside=false;
  for (let i=0, j=poly.length-1; i<poly.length; j=i++){
    const xi=poly[i][0], yi=poly[i][1];
    const xj=poly[j][0], yj=poly[j][1];
    const intersect = ((yi>y)!==(yj>y)) && (x < (xj-xi)*(y-yi)/(yj-yi) + xi);
    if (intersect) inside = !inside;
  }
  return inside;
}
function isShaded(xy, sunAz, sunAlt, bldgs){
  if (sunAlt <= 0) return true;
  const dx = -Math.sin(sunAz), dy = -Math.cos(sunAz);
  const tanAlt = Math.tan(sunAlt);
  const [ox, oy] = xy;
  for (const b of bldgs){
    const vx = b.cx - ox, vy = b.cy - oy;
    const proj = vx*dx + vy*dy;
    if (proj < -b.br) continue;
    const perp = Math.abs(vx*dy - vy*dx);
    if (perp > b.br + 2) continue;
    if (proj > MAX_SHADOW_SEARCH_RADIUS + b.br) continue;
    if (pointInPoly(ox, oy, b.poly)) continue;
    const t = rayFirstHit(ox, oy, dx, dy, b.poly);
    if (t == null) continue;
    if (t > MAX_SHADOW_SEARCH_RADIUS) continue;
    if (b.heightM / t > tanAlt) return true;
  }
  return false;
}

// Same dedupe key the browser uses in parseVenues, so baked window ids match
// whichever v.id the client keeps after dedupe.
function dedupeVenues(elements){
  const parsed = [];
  for (const el of elements || []){
    const lat = el.lat ?? el.center?.lat;
    const lng = el.lon ?? el.center?.lon;
    if (lat==null || lng==null) continue;
    const t = el.tags || {};
    if (t.outdoor_seating === 'no') continue;
    if (!t.name) continue;
    parsed.push({
      id: `${el.type}/${el.id}`,
      name: t.name,
      lat, lng,
    });
  }
  const seen = new Map();
  for (const v of parsed){
    const key = `${v.name.toLowerCase()}::${v.lat.toFixed(4)},${v.lng.toFixed(4)}`;
    if (!seen.has(key)) seen.set(key, v);
  }
  return [...seen.values()];
}

function berlinDateStr(d = new Date()){
  const parts = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Europe/Berlin',
    year:'numeric', month:'2-digit', day:'2-digit',
  }).formatToParts(d);
  const get = k => parts.find(p => p.type === k).value;
  return `${get('year')}-${get('month')}-${get('day')}`;
}

function bakeWindows(venuesJson, buildingsJson){
  console.log('▸ Baking sun windows for today…');
  const bldgs = preprocessBuildings(buildingsJson.elements || []);
  const venues = dedupeVenues(venuesJson.elements);
  console.log(`  ${venues.length} venues × ${bldgs.length} buildings`);

  // Build the spatial grid once. ~100ms for 200k buildings — trivially paid
  // back on the first 50 venues.
  const tGrid = Date.now();
  const grid = buildBuildingGrid(bldgs);
  // Query radius: shadow search radius + a generous building radius buffer.
  // A centroid up to this far from the venue might still have edges that
  // shadow the venue, so we include it in the candidate set.
  const QUERY_RADIUS_M = MAX_SHADOW_SEARCH_RADIUS + 150;
  console.log(`  spatial grid: ${grid.size} cells @ ${GRID_CELL_M}m ` +
              `built in ${Date.now()-tGrid}ms (query r=${QUERY_RADIUS_M}m)`);

  // Anchor on Berlin "today noon" so the same calendar day in Berlin is baked
  // regardless of when the runner kicks off (03:40 UTC or manual trigger at 15:00).
  const bakeDate = berlinDateStr();
  const anchor = new Date(bakeDate + 'T12:00:00+00:00');  // roughly Berlin mid-day
  const sunTimes = SunCalc.getTimes(anchor, CENTER[0], CENTER[1]);
  const start = sunTimes.sunrise.getTime();
  const end   = sunTimes.sunset.getTime();
  const step  = SUN_WINDOW_STEP_MIN * 60 * 1000;

  const windows = {};
  const t0 = Date.now();
  let localBuildingsSum = 0;
  for (let i=0; i<venues.length; i++){
    const v = venues[i];
    const xy = toMeters(v.lat, v.lng);
    // Per-venue candidate set — typically 100–2000 buildings instead of
    // the full 200k. Same set is reused across all ~170 time steps.
    const localBldgs = buildingsNearPoint(grid, xy[0], xy[1], QUERY_RADIUS_M);
    localBuildingsSum += localBldgs.length;
    const wins = [];
    let curStart = null;
    for (let t=start; t<=end; t+=step){
      const p = SunCalc.getPosition(new Date(t), v.lat, v.lng);
      const sunny = p.altitude > 0 && !isShaded(xy, p.azimuth, p.altitude, localBldgs);
      if (sunny && curStart === null) curStart = t;
      else if (!sunny && curStart !== null){
        wins.push([curStart, t - step/2]);
        curStart = null;
      }
    }
    if (curStart !== null) wins.push([curStart, end]);
    const totalMin = Math.round(wins.reduce((s,[a,b]) => s+(b-a)/60000, 0));
    windows[v.id] = { w: wins, m: totalMin };
    if ((i+1) % 250 === 0 || i+1 === venues.length){
      const pct = ((i+1)/venues.length*100).toFixed(0);
      const et  = ((Date.now()-t0)/1000).toFixed(0);
      const avgLocal = Math.round(localBuildingsSum / (i+1));
      console.log(`  windows: ${i+1}/${venues.length} (${pct}%, ${et}s, avg ${avgLocal} local bldgs/venue)`);
    }
  }

  return {
    bakeDate,                                // "2026-04-20" in Europe/Berlin
    bakedAt:  new Date().toISOString(),
    sunrise:  sunTimes.sunrise.toISOString(),
    sunset:   sunTimes.sunset.toISOString(),
    stepMin:  SUN_WINDOW_STEP_MIN,
    center:   CENTER,
    venueCount: venues.length,
    buildingCount: bldgs.length,
    windows,
  };
}

// ─── Horizon profiles (the "never goes stale" path) ────────────────────────
// For each venue we record how high the surrounding buildings reach, as an
// elevation angle, for every 1° of azimuth the sun can ever occupy in Berlin.
// Sun position is pure astronomy, so with this profile the browser can work
// out sun/shade for ANY date and time — no daily bake required. Buildings
// change on a scale of years; this file stays valid until they do.
//
// Encoding (keep in sync with index.html → decodeHorizon):
//   azimuth uses SunCalc's convention (degrees from south, west positive).
//   Bins are HZ_BIN_DEG wide, centred on HZ_AZ_MIN_DEG + i*HZ_BIN_DEG; Berlin's
//   sun stays inside about ±135° from south all year. Each bin holds the
//   obstruction elevation in HZ_STEP_DEG units, rounded UP (errs toward shade);
//   255 = blocked at any sun height.
//   A profile is run-length text: runs joined by ';', each run "<hex value>"
//   or "<hex value>*<hex count>". Open sky = "" (most compact, most common).
//   This text form gzips ~2× better than base64 bytes.
const HZ_AZ_MIN_DEG = -140;
const HZ_AZ_MAX_DEG = 140;
const HZ_BIN_DEG = 2;
const HZ_BINS = (HZ_AZ_MAX_DEG - HZ_AZ_MIN_DEG) / HZ_BIN_DEG + 1;   // 141
const HZ_STEP_DEG = 0.5;

// Highest obstruction tangent along azimuth `az` (radians, SunCalc convention).
// Same geometry as isShaded(), just returning max(height / distance) instead
// of comparing it to one sun altitude.
function horizonTan(xy, az, bldgs){
  const dx = -Math.sin(az), dy = -Math.cos(az);
  const [ox, oy] = xy;
  let best = 0;
  for (const b of bldgs){
    const vx = b.cx - ox, vy = b.cy - oy;
    const proj = vx*dx + vy*dy;
    if (proj < -b.br) continue;
    const perp = Math.abs(vx*dy - vy*dx);
    if (perp > b.br + 2) continue;
    if (proj > MAX_SHADOW_SEARCH_RADIUS + b.br) continue;
    if (pointInPoly(ox, oy, b.poly)) continue;
    const t = rayFirstHit(ox, oy, dx, dy, b.poly);
    if (t == null || t > MAX_SHADOW_SEARCH_RADIUS) continue;
    const tan = b.heightM / t;
    if (tan > best) best = tan;
  }
  return best;
}

function horizonProfile(xy, bldgs){
  const vals = new Array(HZ_BINS).fill(0);
  const half = HZ_BIN_DEG / 2;
  for (let i = 0; i < HZ_BINS; i++){
    const c = HZ_AZ_MIN_DEG + i * HZ_BIN_DEG;
    let tan = 0;
    // Sample across the bin and keep the highest obstruction.
    for (const f of [-0.5, 0, 0.5]){
      tan = Math.max(tan, horizonTan(xy, (c + f * half) * Math.PI / 180, bldgs));
    }
    if (tan <= 0) continue;
    const deg = Math.atan(tan) * 180 / Math.PI;
    vals[i] = Math.min(255, Math.ceil(deg / HZ_STEP_DEG));
    if (deg >= 254 * HZ_STEP_DEG) vals[i] = 255;
  }
  if (!vals.some(Boolean)) return '';
  const runs = [];
  for (let i = 0; i < vals.length;){
    let j = i;
    while (j < vals.length && vals[j] === vals[i]) j++;
    const n = j - i;
    runs.push(vals[i].toString(16) + (n > 1 ? '*' + n.toString(16) : ''));
    i = j;
  }
  return runs.join(';');
}

function bakeHorizons(venuesJson, buildingsJson){
  console.log('▸ Baking horizon profiles…');
  const bldgs = preprocessBuildings(buildingsJson.elements || []);
  const venues = dedupeVenues(venuesJson.elements);
  const grid = buildBuildingGrid(bldgs);
  const QUERY_RADIUS_M = MAX_SHADOW_SEARCH_RADIUS + 150;
  const profiles = {};
  const t0 = Date.now();
  for (let i = 0; i < venues.length; i++){
    const v = venues[i];
    const xy = toMeters(v.lat, v.lng);
    const local = buildingsNearPoint(grid, xy[0], xy[1], QUERY_RADIUS_M);
    profiles[v.id] = horizonProfile(xy, local);
    if ((i+1) % 500 === 0 || i+1 === venues.length){
      console.log(`  horizons: ${i+1}/${venues.length} (${((Date.now()-t0)/1000).toFixed(0)}s)`);
    }
  }
  return {
    v: 2,
    bakedAt: new Date().toISOString(),
    azMinDeg: HZ_AZ_MIN_DEG,
    binDeg: HZ_BIN_DEG,
    bins: HZ_BINS,
    stepDeg: HZ_STEP_DEG,
    venueCount: venues.length,
    buildingCount: bldgs.length,
    h: profiles,
  };
}

// ─── Shadow tiles (what the map draws) ──────────────────────────────────────
// The map renders real building shadows for the chosen time. It needs the same
// footprints + heights the horizons were computed from, so shadows on the map
// and sun/shade on the terrace dots always agree. Buildings are bucketed into
// z15 web-mercator tiles by centroid; the client loads the tiles around the
// viewport (plus one ring, for shadows cast in from neighbours).
//
// data/shadows/15/{x}/{y}.json = { b: [[heightM, lon0, lat0, dLon1, dLat1, …], …] }
//   coordinates are integers in 1e-5° (≈1 m), first vertex absolute relative
//   to the tile's west/north edge, the rest delta-encoded.
// data/shadows/index.json = { bakedAt, z, tiles: [[x, y], …] }
const SHADOW_Z = 15;
function bakeShadowTiles(elements){
  console.log('▸ Baking shadow tiles…');
  const n = 2 ** SHADOW_Z;
  const lon2x = lon => Math.floor((lon + 180) / 360 * n);
  const lat2y = lat => { const r = lat * Math.PI / 180; return Math.floor((1 - Math.log(Math.tan(r) + 1 / Math.cos(r)) / Math.PI) / 2 * n); };
  const x2lon = x => x / n * 360 - 180;
  const y2lat = y => { const k = Math.PI - 2 * Math.PI * y / n; return 180 / Math.PI * Math.atan(0.5 * (Math.exp(k) - Math.exp(-k))); };
  const tiles = new Map();
  for (const el of elements){
    const g = el.geometry;
    if (!g || g.length < 3) continue;
    let clat = 0, clon = 0;
    for (const p of g){ clat += p.lat; clon += p.lon; }
    clat /= g.length; clon /= g.length;
    const tx = lon2x(clon), ty = lat2y(clat), key = tx + '/' + ty;
    let t = tiles.get(key);
    if (!t){ t = { x: tx, y: ty, lon0: x2lon(tx), lat0: y2lat(ty), b: [] }; tiles.set(key, t); }
    const h = Math.round(parseHeightTags(el.tags) * 10) / 10;
    const out = [h];
    let px = 0, py = 0;
    const ring = g[0].lat === g[g.length-1].lat && g[0].lon === g[g.length-1].lon ? g.slice(0, -1) : g;
    ring.forEach((p, i) => {
      const ix = Math.round((p.lon - t.lon0) * 1e5), iy = Math.round((t.lat0 - p.lat) * 1e5);
      if (i === 0) out.push(ix, iy); else out.push(ix - px, iy - py);
      px = ix; py = iy;
    });
    t.b.push(out);
  }
  const dir = path.join(OUT_DIR, 'shadows');
  fs.rmSync(dir, { recursive: true, force: true });
  let bytes = 0;
  for (const t of tiles.values()){
    const d = path.join(dir, String(SHADOW_Z), String(t.x));
    fs.mkdirSync(d, { recursive: true });
    const body = JSON.stringify({ b: t.b });
    fs.writeFileSync(path.join(d, `${t.y}.json`), body);
    bytes += body.length;
  }
  fs.writeFileSync(path.join(dir, 'index.json'), JSON.stringify({
    bakedAt: new Date().toISOString(), z: SHADOW_Z,
    tiles: [...tiles.values()].map(t => [t.x, t.y]),
  }));
  console.log(`  shadow tiles: ${tiles.size} tiles, ${(bytes / 1048576).toFixed(1)} MB`);
  return tiles.size;
}

// ─── Rooftop matching ──────────────────────────────────────────────────────
// Hand-curated list of well-known Berlin rooftops/terraces/beer gardens
// (data/rooftops.json) gets matched to venues in the OSM dataset at bake time.
// Output data/rooftops-today.json = { bakeDate, ids: [venueId, …] } — tiny.
// Client sets v.isRooftop = true for matched ids and exposes a Rooftop chip.
//
// Matcher is deliberately conservative:
//   · 120 m search radius, name-fuzzy within that preferred
//   · fallback: one candidate within 40 m even without name match
// If something doesn't match it's logged, not a crash. Easy to tune over time.

function haversineMeters(lat1, lng1, lat2, lng2){
  const R = 6371000;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLng = (lng2 - lng1) * Math.PI / 180;
  const a = Math.sin(dLat/2)**2
          + Math.cos(lat1*Math.PI/180) * Math.cos(lat2*Math.PI/180)
          * Math.sin(dLng/2)**2;
  return 2 * R * Math.asin(Math.sqrt(a));
}
function normalizeName(s){
  return (s || '').toLowerCase().normalize('NFKD')
    .replace(/[^a-z0-9]+/g, '').trim();
}
function nameSimilar(a, b){
  const na = normalizeName(a), nb = normalizeName(b);
  if (!na || !nb) return false;
  return na === nb || na.includes(nb) || nb.includes(na);
}

// Supplemental fetch: pull named venues within 100 m of each curated rooftop,
// ignoring outdoor_seating. Famous rooftops like Klunkerkranich are effectively
// all outdoor and often aren't tagged outdoor_seating=yes, so the main query
// misses them. We merge only the ones that end up matching a curated rooftop
// back into venues — unmatched supplement venues are discarded so venues.json
// stays focused on outdoor-seating terraces.
function readCuratedRooftops(){
  const rooftopsPath = path.resolve(__dirname, '..', 'data', 'rooftops.json');
  if (!fs.existsSync(rooftopsPath)) return [];
  return JSON.parse(fs.readFileSync(rooftopsPath, 'utf8')).rooftops || [];
}
async function fetchVenueSupplement(){
  const curated = readCuratedRooftops();
  if (!curated.length) return { elements: [] };
  console.log(`▸ Fetching supplemental venues near ${curated.length} curated rooftops…`);
  const parts = curated.map(r =>
    `  nwr["amenity"~"^(bar|pub|cafe|restaurant|biergarten|ice_cream)$"](around:100,${r.lat},${r.lng});`
  ).join('\n');
  const query = `[out:json][timeout:60];\n(\n${parts}\n);\nout center tags;`;
  try {
    return await fetchOverpass(query, 'rooftop supplement');
  } catch(e){
    console.warn('  supplement fetch failed, continuing without it:', e.message);
    return { elements: [] };
  }
}

function bakeRooftops(venuesJson, supplementJson){
  console.log('▸ Matching curated rooftops…');
  const curated = readCuratedRooftops();
  if (!curated.length){
    console.log('  (no data/rooftops.json — skipping)');
    return {
      bakeDate: berlinDateStr(), bakedAt: new Date().toISOString(),
      curatedCount: 0, matchedCount: 0, ids: [], supplementAdded: [],
    };
  }

  // Build a merged pool: main venues ∪ supplement (by OSM id), so the matcher
  // can pick up rooftops that lack outdoor_seating=yes. We remember which ids
  // came only from supplement — those get merged into venues.json iff matched.
  const mainElements = venuesJson.elements || [];
  const suppElements = supplementJson?.elements || [];
  const mainIds = new Set(mainElements.map(el => `${el.type}/${el.id}`));
  const suppOnly = new Map(); // OSM id → supplement element (for post-match merge)
  const merged = [...mainElements];
  for (const el of suppElements){
    const id = `${el.type}/${el.id}`;
    if (mainIds.has(id)) continue;
    if (!el.tags || !el.tags.name) continue;
    suppOnly.set(id, el);
    merged.push(el);
  }
  console.log(`  main venues: ${mainElements.length}, supplemental candidates: ${suppOnly.size}`);

  const venues = dedupeVenues(merged);

  const NEAR_M_STRICT    = 40;
  const NEAR_M_WITH_NAME = 120;

  const matchedIds = new Set();
  const matchedElements = new Map();  // id → OSM element, for the client fallback block
  const matches = [];
  const unmatched = [];
  // Keep a quick lookup from id → original OSM element in the merged pool, so
  // once we pick a candidate we can grab its raw tags for rooftops-today.json.
  const mergedById = new Map(merged.map(el => [`${el.type}/${el.id}`, el]));
  for (const r of curated){
    const candidates = venues
      .map(v => ({ v, d: haversineMeters(r.lat, r.lng, v.lat, v.lng) }))
      .filter(c => c.d <= NEAR_M_WITH_NAME)
      .sort((a, b) => a.d - b.d);
    if (!candidates.length){
      unmatched.push(`${r.name} (no venues within ${NEAR_M_WITH_NAME}m)`);
      continue;
    }
    // 1) Preferred: any candidate whose name fuzzy-matches.
    let pick = candidates.find(c => nameSimilar(c.v.name, r.name));
    // 2) Fallback: exactly one candidate within a strict radius.
    if (!pick){
      const tight = candidates.filter(c => c.d <= NEAR_M_STRICT);
      if (tight.length === 1) pick = tight[0];
    }
    if (pick){
      if (!matchedIds.has(pick.v.id)){
        matchedIds.add(pick.v.id);
        const raw = mergedById.get(pick.v.id);
        if (raw) matchedElements.set(pick.v.id, raw);
        const tag = suppOnly.has(pick.v.id) ? ' [supp]' : '';
        matches.push(`${r.name} → ${pick.v.name} (${Math.round(pick.d)}m)${tag}`);
      } else {
        matches.push(`${r.name} → ${pick.v.name} (dup, already matched)`);
      }
    } else {
      const nearby = candidates.slice(0, 3)
        .map(c => `${c.v.name} ${Math.round(c.d)}m`).join(', ');
      unmatched.push(`${r.name} (near: ${nearby})`);
    }
  }

  // Promote matched supplement venues to first-class venues for venues.json.
  const supplementAdded = [];
  for (const [id, el] of suppOnly){
    if (matchedIds.has(id)) supplementAdded.push(el);
  }

  // Bundle the raw OSM elements for each matched rooftop INTO rooftops-today.json
  // itself. This is defence-in-depth: if the deployed venues.json ever drifts
  // out of sync with rooftops-today.json (cache staleness, partial deploy,
  // CDN edge mismatch), the client can synthesize the missing venue entries
  // from this payload instead of silently showing zero rooftops.
  const matchedVenues = [...matchedIds].map(id => {
    const el = matchedElements.get(id);
    if (!el) return null;
    return {
      type: el.type, id: el.id,
      lat: el.lat ?? el.center?.lat ?? null,
      lon: el.lon ?? el.center?.lon ?? null,
      tags: el.tags || {},
    };
  }).filter(Boolean);

  console.log(`  matched: ${matches.length}/${curated.length} curated rooftops`);
  for (const m of matches) console.log(`    ✓ ${m}`);
  if (unmatched.length){
    console.log('  unmatched (will not show in Rooftop filter):');
    for (const m of unmatched) console.log(`    · ${m}`);
  }
  if (supplementAdded.length){
    console.log(`  promoted ${supplementAdded.length} supplemental venues into venues.json`);
  }

  return {
    bakeDate:     berlinDateStr(),
    bakedAt:      new Date().toISOString(),
    curatedCount: curated.length,
    matchedCount: matchedIds.size,
    ids:          [...matchedIds],
    venues:       matchedVenues,   // self-sufficient fallback; see client loadRooftopsToday
    supplementAdded,
  };
}

// ─── Manifest ───────────────────────────────────────────────────────────────
// windowsBakedAt + bakeDate let the client detect stale bakes cheaply — it
// already loads manifest.json, so no extra round-trip. If bakeDate != today's
// Berlin date on page load, we warn loud in console so a silent cron failure
// is visible without inspecting data/ in git.
function buildManifest(venues, buildings, windowsToday, rooftopsToday){
  return {
    bakedAt: new Date().toISOString(),
    bakeDate:         windowsToday ? windowsToday.bakeDate : null,
    windowsBakedAt:   windowsToday ? windowsToday.bakedAt  : null,
    rooftopsBakedAt:  rooftopsToday ? rooftopsToday.bakedAt : null,
    bbox: BBOX_VENUES,
    bboxBuildingsDeploy:  BBOX_BUILDINGS_DEPLOY,
    bboxBuildingsCompute: BBOX_BUILDINGS_COMPUTE,
    venues: { count: (venues.elements || []).length },
    buildings: {
      count:        (buildings.elements       || []).length,
      deployCount:  (buildings.deployElements || []).length,
      tileCoverage: buildings._coverage || null,
    },
    version: 2,
  };
}

// ─── Main ───────────────────────────────────────────────────────────────────
module.exports = { bakeShadowTiles, bakeHorizons, bakeWindows, horizonProfile, preprocessBuildings, dedupeVenues, toMeters, isShaded, buildBuildingGrid, buildingsNearPoint, CENTER, HZ_AZ_MIN_DEG, HZ_BIN_DEG, HZ_BINS, HZ_STEP_DEG };
if (require.main === module) (async () => {
  fs.mkdirSync(OUT_DIR, { recursive: true });

  const venues     = await bakeVenues();
  const supplement = await fetchVenueSupplement();

  // ─── Light run (most days) ───────────────────────────────────────────────
  // Buildings change on a scale of years and horizons.json is valid for any
  // date, so the slow Overpass building fetch — the step that kept hitting
  // the 45-minute Actions timeout — only runs when horizons.json is older
  // than HORIZON_REFRESH_DAYS (or BAKE_FULL=1). Other days just refresh
  // venues + rooftops in a few minutes. New venues show up immediately but
  // stay uncoloured until the next full run computes their horizon.
  const HORIZON_REFRESH_DAYS = 30;
  const manifestPathEarly = path.join(OUT_DIR, 'manifest.json');
  let hzAgeDays = Infinity;
  try {
    const hz = JSON.parse(fs.readFileSync(path.join(OUT_DIR, 'horizons.json'), 'utf8'));
    hzAgeDays = (Date.now() - Date.parse(hz.bakedAt)) / 86400000;
  } catch {}
  const haveShadowTiles = fs.existsSync(path.join(OUT_DIR, 'shadows', 'index.json'));
  if (process.env.BAKE_FULL !== '1' && hzAgeDays < HORIZON_REFRESH_DAYS && haveShadowTiles){
    console.log(`▸ Light run: horizons.json is ${hzAgeDays.toFixed(1)} days old ` +
                `(< ${HORIZON_REFRESH_DAYS}) — skipping buildings + shadow bake`);
    const rooftopsLight = bakeRooftops(venues, supplement);
    if (rooftopsLight.supplementAdded && rooftopsLight.supplementAdded.length){
      venues.elements = [...(venues.elements || []), ...rooftopsLight.supplementAdded];
    }
    delete rooftopsLight.supplementAdded;
    let prev = {};
    try { prev = JSON.parse(fs.readFileSync(manifestPathEarly, 'utf8')); } catch {}
    const manifestLight = {
      ...prev,
      bakedAt: new Date().toISOString(),
      rooftopsBakedAt: rooftopsLight.bakedAt || new Date().toISOString(),
      venues: { count: (venues.elements || []).length },
      lastRun: 'light',
    };
    fs.writeFileSync(path.join(OUT_DIR, 'venues.json'), JSON.stringify(venues));
    fs.writeFileSync(path.join(OUT_DIR, 'rooftops-today.json'), JSON.stringify(rooftopsLight));
    fs.writeFileSync(manifestPathEarly, JSON.stringify(manifestLight, null, 2));
    console.log(`\n✓ Light bake: ${manifestLight.venues.count} venues, ` +
                `${rooftopsLight.matchedCount}/${rooftopsLight.curatedCount} rooftops matched`);
    return;
  }
  console.log(`▸ Full run: horizons.json age ${isFinite(hzAgeDays) ? hzAgeDays.toFixed(1) + ' days' : 'unknown'}`);

  const buildings  = await bakeBuildings();

  // Two distinct building sets live on from bakeBuildings():
  //   · buildingsCompute — full set across BBOX_BUILDINGS_COMPUTE. Used for
  //     accurate shadow calculation across every venue in BBOX_VENUES.
  //   · buildingsDeploy  — central subset inside BBOX_BUILDINGS_DEPLOY. Only
  //     this gets written to buildings.json (25 MiB Cloudflare Pages cap).
  const buildingsCompute = { elements: buildings.elements        || [] };
  const buildingsDeploy  = { elements: buildings.deployElements  || [] };

  // Match curated rooftops against main ∪ supplement; this also returns any
  // supplement venues that matched, which we promote into venues.json so the
  // client can show them + bake their sun windows.
  const rooftopsToday = bakeRooftops(venues, supplement);
  if (rooftopsToday.supplementAdded && rooftopsToday.supplementAdded.length){
    venues.elements = [...(venues.elements || []), ...rooftopsToday.supplementAdded];
  }
  // Don't persist `supplementAdded` in rooftops-today.json.
  delete rooftopsToday.supplementAdded;

  // Compute today's sun windows for every venue (incl. promoted rooftops)
  // against the FULL compute set — windows-today.json is the fast path and
  // must be accurate even for venues near the edge of BBOX_VENUES.
  const windowsToday = bakeWindows(venues, buildingsCompute);

  // Horizon profiles power the client's sun math for any date. Only replace
  // the committed file when building coverage is complete — a partial
  // Overpass run would otherwise mark shaded terraces as sunny. A missing
  // tile just means we keep last month's (still-valid) horizons.
  const cov = buildings._coverage || {};
  const horizonsPath = path.join(OUT_DIR, 'horizons.json');
  const coverageComplete = cov.okTiles && cov.okTiles === cov.totalTiles;
  if (coverageComplete || !fs.existsSync(horizonsPath)){
    const horizons = bakeHorizons(venues, buildingsCompute);
    fs.writeFileSync(horizonsPath, JSON.stringify(horizons));
    console.log(`  horizons.json: ${(fs.statSync(horizonsPath).size/1024).toFixed(0)} KB, ${horizons.venueCount} venues`);
  } else {
    console.warn(`  horizons.json kept as-is: building coverage ${cov.okTiles}/${cov.totalTiles}`);
  }
  // Same rule for the map's shadow tiles — they must match the horizons.
  if (coverageComplete || !haveShadowTiles){
    bakeShadowTiles(buildingsCompute.elements);
  }

  const manifest = buildManifest(venues, buildings, windowsToday, rooftopsToday);

  const venuesPath    = path.join(OUT_DIR, 'venues.json');
  const buildingsPath = path.join(OUT_DIR, 'buildings.json');
  const windowsPath   = path.join(OUT_DIR, 'windows-today.json');
  const rooftopsPath  = path.join(OUT_DIR, 'rooftops-today.json');
  const manifestPath  = path.join(OUT_DIR, 'manifest.json');

  fs.writeFileSync(venuesPath,    JSON.stringify(venues));
  fs.writeFileSync(buildingsPath, JSON.stringify(buildingsDeploy));
  fs.writeFileSync(windowsPath,   JSON.stringify(windowsToday));
  fs.writeFileSync(rooftopsPath,  JSON.stringify(rooftopsToday));
  fs.writeFileSync(manifestPath,  JSON.stringify(manifest, null, 2));

  // Loud failure if the deploy artifact would be rejected at the edge.
  // Cloudflare Pages blocks files >25 MiB; we stop the bake now rather than
  // push a broken manifest into a partial deploy.
  const CF_MAX = 25 * 1024 * 1024;
  const buildingsSize = fs.statSync(buildingsPath).size;
  if (buildingsSize > CF_MAX){
    throw new Error(
      `buildings.json is ${(buildingsSize/1024/1024).toFixed(2)} MiB — over the ` +
      `25 MiB Cloudflare Pages cap. Narrow BBOX_BUILDINGS_DEPLOY or add more ` +
      `aggressive slimming in slimBuildingElement().`
    );
  }

  const sizes = [
    ['venues.json',         fs.statSync(venuesPath).size],
    ['buildings.json',      fs.statSync(buildingsPath).size],
    ['windows-today.json',  fs.statSync(windowsPath).size],
    ['rooftops-today.json', fs.statSync(rooftopsPath).size],
    ['manifest.json',       fs.statSync(manifestPath).size],
  ];
  console.log('');
  console.log('✓ Baked.');
  for (const [name, bytes] of sizes){
    console.log(`  ${name}: ${(bytes/1024/1024).toFixed(2)} MB`);
  }
  console.log(`  manifest: ${manifest.venues.count} venues · ${manifest.buildings.count} buildings compute / ${manifest.buildings.deployCount} deploy · ${manifest.bakedAt}`);
  console.log(`  windows: baked for ${windowsToday.bakeDate} (Europe/Berlin), ${windowsToday.venueCount} venues`);
  console.log(`  rooftops: ${rooftopsToday.matchedCount}/${rooftopsToday.curatedCount} curated entries matched`);
})().catch(err => {
  console.error('\n✗ Bake failed:', err);
  process.exit(1);
});
