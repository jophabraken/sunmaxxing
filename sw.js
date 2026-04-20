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
 * - /data/*.json       → stale-while-revalidate (serve cached instantly, fetch fresh in bg)
 * - Same-origin static → cache-first
 * - Cross-origin       → pass through (Overpass, OSM tiles, Wikidata, weather API)
 */

const SW_VERSION   = 'sonne-sw-v1';
const SHELL_CACHE  = 'sonne-shell-v1';
const DATA_CACHE   = 'sonne-data-v1';
const STATIC_CACHE = 'sonne-static-v1';
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

  // Nightly-baked data → stale-while-revalidate
  if (url.pathname.startsWith('/data/')){
    event.respondWith(staleWhileRevalidate(req, DATA_CACHE));
    return;
  }

  // Everything else (SVG/JSON from /assets/, etc.) → cache-first
  event.respondWith(cacheFirst(req, STATIC_CACHE));
});

async function networkFirst(req, cacheName){
  const cache = await caches.open(cacheName);
  try {
    const fresh = await fetch(req);
    if (fresh && fresh.ok) cache.put(req, fresh.clone());
    return fresh;
  } catch (e) {
    const cached = await cache.match(req);
    if (cached) return cached;
    throw e;
  }
}

async function staleWhileRevalidate(req, cacheName){
  const cache = await caches.open(cacheName);
  const cached = await cache.match(req);
  const fresh = fetch(req).then(res => {
    if (res && res.ok) cache.put(req, res.clone());
    return res;
  }).catch(() => cached);
  // Return cached immediately if we have it; otherwise wait for network.
  return cached || fresh;
}

async function cacheFirst(req, cacheName){
  const cache = await caches.open(cacheName);
  const cached = await cache.match(req);
  if (cached) return cached;
  const fresh = await fetch(req);
  if (fresh && fresh.ok) cache.put(req, fresh.clone());
  return fresh;
}
