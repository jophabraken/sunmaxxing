/* Service Worker for sunmaxxing.com
 *
 * Goals
 * - Make repeat loads feel instant by serving cached data + shell immediately.
 * - Never ship stale app code: HTML is network-first.
 * - Never block the user when the network is flaky: everything falls back to
 *   the cached copy.
 *
 * Strategies
 * - Navigation / HTML  → network-first, cache fallback
 * - /data/*.json       → network-first (3 s timeout), cache fallback. v1 used
 *                        stale-while-revalidate here, which served returning
 *                        visitors weeks-old sun data and pushed them onto the
 *                        slow path. Data is small now; fresh beats instant.
 * - /tiles/*, Range    → pass through (PMTiles uses HTTP range requests,
 *                        which the Cache API can't store)
 * - Same-origin static → cache-first
 * - Cross-origin       → pass through (Wikidata, weather API)
 */

// Bumped from 'sonne-*' to 'sunmaxxing-*' on the brand consolidation. The
// activate handler deletes any cache not in KEEP, so the old 'sonne-*' caches
// auto-evict on first SW activate after this deploy.
// v2: bumping these names evicts every v1 cache (incl. stale sun data) on
// activate.
const SW_VERSION   = 'sunmaxxing-sw-v2';
const SHELL_CACHE  = 'sunmaxxing-shell-v2';
const DATA_CACHE   = 'sunmaxxing-data-v2';
const STATIC_CACHE = 'sunmaxxing-static-v2';
const KEEP = new Set([SHELL_CACHE, DATA_CACHE, STATIC_CACHE]);

self.addEventListener('install', () => {
  // Activate immediately so the fix reaches users on next load
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(k => !KEEP.has(k)).map(k => caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  if (req.method !== 'GET') return;

  const url = new URL(req.url);

  // Cross-origin: don't touch it. Browser/HTTP cache handles OSM tiles etc.
  if (url.origin !== self.location.origin) return;

  // Navigation → network-first
  if (req.mode === 'navigate' || req.destination === 'document'){
    event.respondWith(networkFirst(req, SHELL_CACHE));
    return;
  }

  // Range requests (basemap tiles) can't be cached by the Cache API.
  if (req.headers.has('range') || url.pathname.startsWith('/tiles/')) return;

  // Baked data → network-first with a short timeout, cached copy as fallback.
  if (url.pathname.startsWith('/data/')){
    event.respondWith(networkFirst(req, DATA_CACHE, 3000));
    return;
  }

  // Everything else (SVG/JSON from /assets/, etc.) → cache-first
  event.respondWith(cacheFirst(req, STATIC_CACHE));
});

async function networkFirst(req, cacheName, timeoutMs){
  const cache = await caches.open(cacheName);
  try {
    const net = fetch(req);
    const fresh = timeoutMs
      ? await Promise.race([net, new Promise((_, rej) => setTimeout(() => rej(new Error('timeout')), timeoutMs))])
      : await net;
    if (fresh && fresh.status === 200) cache.put(req, fresh.clone()).catch(() => {});
    return fresh;
  } catch (e) {
    const cached = await cache.match(req);
    if (cached) return cached;
    throw e;
  }
}

async function cacheFirst(req, cacheName){
  const cache = await caches.open(cacheName);
  const cached = await cache.match(req);
  if (cached) return cached;
  const fresh = await fetch(req);
  if (fresh && fresh.status === 200) cache.put(req, fresh.clone()).catch(() => {});
  return fresh;
}
