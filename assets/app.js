/* sunmaxxing — Golden Hour app (2026 redesign)
 *
 * Data (all same-origin, all static):
 *   data/venues.json      terraces (raw Overpass, refreshed daily)
 *   data/horizons.json    per-terrace building horizon → sun/shade for ANY time
 *   data/shadows/…        building footprints + heights, z15 tiles → map shadows
 *   data/rooftops-today.json  curated rooftop flags
 *   tiles/{z}/{x}/{y}.pbf  self-hosted basemap (Protomaps / OSM)
 * Weather: Open-Meteo (optional — the app works without it).
 *
 * Shadows on the map and sun/shade on the dots come from the same buildings,
 * so they always agree.
 */
(() => {
'use strict';

// ═════════════════════════════════════════════════════════════════════════
//  i18n
// ═════════════════════════════════════════════════════════════════════════
const STR = {
  en: {
    search_ph: 'Search a place in Berlin', now: 'Now', today: 'Today', tomorrow: 'Tomorrow',
    in_sun: n => n === 1 ? 'terrace in the sun<br>around here' : 'terraces in the sun<br>around here',
    next_sun: (n, cl) => `next sun · ${n} terraces<br>${cl ? 'once the clouds clear' : 'later today'}`,
    no_more: 'no more sun today', sunny_here: 'sunny here', next_sun_s: 'next sun', n_terraces: n => `${n} terraces`, first_sun_s: d => d === 1 ? 'first sun tomorrow' : 'first sun',
    first_tomorrow: (n, d) => `first sun ${d === 1 ? 'tomorrow' : 'that day'} · ${n} terraces<br>tap one to plan ahead`,
    until: t => `until ${t}`, left: d => `${d} left`, walk: m => `${m} min walk`, sun_at: (a, b) => `sun ${a}–${b}`,
    shade_reaches: (s, t) => `shade on ${s} at ${t}`, lights_up: (s, t) => `sun on ${s} from ${t}`,
    golden: (g, s) => `golden hour ${g} · sunset ${s}`, overcast: t => t ? `Overcast · clearing around ${t}` : 'Overcast for the rest of the day',
    after_sunset: (s, r) => `Sunset was ${s} · sunrise ${r}`,
    chip_sunny: 'Sunny now', chip_open: 'Open now', chip_bar: 'Bars', chip_cafe: 'Cafés', chip_rest: 'Restaurants', chip_ice: 'Ice cream', chip_roof: 'Rooftops', chip_fav: 'Saved',
    list_h: 'Around here', list_sub: n => `${n} terraces`, more: 'Show more', nothing: 'No terraces match here. Zoom out or clear a filter.',
    sun_until: t => `Sun until ${t}`, then_shade: (d, dir) => `${d} left · then shade from the buildings to the ${dir}`,
    sunny_cloudy: 'Sunny spot, cloudy sky', sunny_cloudy_sm: (t, c) => `Direct sun here until ${t}.${c ? ` Clouds forecast to clear ~${c}.` : ''}`,
    sun_again: t => `Sun again at ${t}`, sun_again_sm: d => `In shade right now · then ${d} of direct sun`,
    no_sun_more: 'No more sun today', had_sun: d => `It had ${d} of direct sun today.`, never: 'No direct sun on this day.', sunrise_at: t => `Sunrise ${t}.`,
    ribbon_lab: d => `Sun on this terrace · ${d}`, windows_n: n => n > 1 ? `${n} sun windows. ` : '', longest: (a, b, d) => `Longest: <b>${a}–${b}</b> (${d}).`,
    try_other: 'No direct sun, so try the other side of the street.', sunset: t => `Sunset ${t}.`,
    hours: 'Hours', open_now: 'Open now', closed_now: 'Closed now', website: 'Website', address: 'Address', directions: 'Directions',
    type: { restaurant: 'Restaurant', cafe: 'Café', bar: 'Bar', pub: 'Pub', biergarten: 'Beer garden', ice_cream: 'Ice cream' },
    dirs: ['north', 'north-east', 'east', 'south-east', 'south', 'south-west', 'west', 'north-west'],
    locating: 'Finding you…', loc_fail: 'Could not get your location', out_of_area: 'You’re outside the area we cover — showing central Berlin',
    rooftop: 'Rooftop', saved: 'Saved', share_copied: 'Link copied', weather_na: 'Weather unavailable',
    sr_cloud: c => `${c}% cloud`, search_none: 'Nothing found', snap_lab: t => `Sun & shade · ${t}`, photo: 'Photo',
  },
  de: {
    search_ph: 'Ort in Berlin suchen', now: 'Jetzt', today: 'Heute', tomorrow: 'Morgen',
    in_sun: n => n === 1 ? 'Terrasse in der Sonne<br>hier in der Nähe' : 'Terrassen in der Sonne<br>hier in der Nähe',
    next_sun: (n, cl) => `nächste Sonne · ${n} Terrassen<br>${cl ? 'sobald die Wolken weg sind' : 'später heute'}`,
    no_more: 'heute keine Sonne mehr', sunny_here: 'sonnig hier', next_sun_s: 'nächste Sonne', n_terraces: n => `${n} Terrassen`, first_sun_s: d => d === 1 ? 'erste Sonne morgen' : 'erste Sonne',
    first_tomorrow: (n, d) => `erste Sonne ${d === 1 ? 'morgen' : 'an dem Tag'} · ${n} Terrassen<br>antippen zum Vorplanen`,
    until: t => `bis ${t}`, left: d => `noch ${d}`, walk: m => `${m} Min. zu Fuß`, sun_at: (a, b) => `Sonne ${a}–${b}`,
    shade_reaches: (s, t) => `Schatten in der ${s} ab ${t}`, lights_up: (s, t) => `Sonne in der ${s} ab ${t}`,
    golden: (g, s) => `goldene Stunde ${g} · Untergang ${s}`, overcast: t => t ? `Bewölkt · klart gegen ${t} auf` : 'Bewölkt für den Rest des Tages',
    after_sunset: (s, r) => `Sonnenuntergang war ${s} · Aufgang ${r}`,
    chip_sunny: 'Jetzt sonnig', chip_open: 'Geöffnet', chip_bar: 'Bars', chip_cafe: 'Cafés', chip_rest: 'Restaurants', chip_ice: 'Eis', chip_roof: 'Dachterrassen', chip_fav: 'Gemerkt',
    list_h: 'Hier in der Nähe', list_sub: n => `${n} Terrassen`, more: 'Mehr anzeigen', nothing: 'Hier passt nichts. Rauszoomen oder Filter entfernen.',
    sun_until: t => `Sonne bis ${t}`, then_shade: (d, dir) => `noch ${d} · dann Schatten von den Häusern im ${dir}`,
    sunny_cloudy: 'Sonnenplatz, aber bewölkt', sunny_cloudy_sm: (t, c) => `Direkte Sonne hier bis ${t}.${c ? ` Aufklaren gegen ${c} erwartet.` : ''}`,
    sun_again: t => `Wieder Sonne um ${t}`, sun_again_sm: d => `Gerade im Schatten · dann ${d} direkte Sonne`,
    no_sun_more: 'Heute keine Sonne mehr', had_sun: d => `Heute ${d} direkte Sonne.`, never: 'An diesem Tag keine direkte Sonne.', sunrise_at: t => `Sonnenaufgang ${t}.`,
    ribbon_lab: d => `Sonne auf dieser Terrasse · ${d}`, windows_n: n => n > 1 ? `${n} Sonnenfenster. ` : '', longest: (a, b, d) => `Am längsten: <b>${a}–${b}</b> (${d}).`,
    try_other: 'Keine direkte Sonne – probier die andere Straßenseite.', sunset: t => `Sonnenuntergang ${t}.`,
    hours: 'Öffnungszeiten', open_now: 'Jetzt geöffnet', closed_now: 'Jetzt geschlossen', website: 'Website', address: 'Adresse', directions: 'Route',
    type: { restaurant: 'Restaurant', cafe: 'Café', bar: 'Bar', pub: 'Kneipe', biergarten: 'Biergarten', ice_cream: 'Eis' },
    dirs: ['Norden', 'Nordosten', 'Osten', 'Südosten', 'Süden', 'Südwesten', 'Westen', 'Nordwesten'],
    locating: 'Suche deinen Standort…', loc_fail: 'Standort nicht verfügbar', out_of_area: 'Du bist außerhalb unseres Gebiets – zeige die Innenstadt',
    rooftop: 'Dachterrasse', saved: 'Gemerkt', share_copied: 'Link kopiert', weather_na: 'Wetter nicht verfügbar',
    sr_cloud: c => `${c}% Wolken`, search_none: 'Nichts gefunden', snap_lab: t => `Sonne & Schatten · ${t}`, photo: 'Foto',
  },
};
const store = {
  get(k, d){ try { const v = localStorage.getItem('sm_' + k); return v == null ? d : JSON.parse(v); } catch { return d; } },
  set(k, v){ try { localStorage.setItem('sm_' + k, JSON.stringify(v)); } catch {} },
};
// /de/ is the German homepage (rewritten to this file); the URL wins, then a saved choice, then the browser.
let LANG = /^\/de(\/|$)/.test(location.pathname) ? 'de' : (store.get('lang', null) || (/^de\b/i.test(navigator.language || '') ? 'de' : 'en'));
const T = () => STR[LANG];
const $ = id => document.getElementById(id);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

// ═════════════════════════════════════════════════════════════════════════
//  Time (always Europe/Berlin)
// ═════════════════════════════════════════════════════════════════════════
const CENTER = [52.520, 13.405];
const fmtParts = new Intl.DateTimeFormat('en-CA', { timeZone: 'Europe/Berlin', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', hourCycle: 'h23' });
function berlin(d){ const o = {}; for (const p of fmtParts.formatToParts(d)) o[p.type] = +p.value || p.value; return o; }
function offsetMin(ms){ const p = berlin(new Date(ms)); return Math.round((Date.UTC(p.year, p.month - 1, p.day, p.hour, p.minute) - Math.floor(ms / 60000) * 60000) / 60000); }
// Berlin-midnight per day offset. Intl formatting is slow, so the date key is
// computed once and refreshed by the clock tick — never per call.
const dateKey = () => { const p = berlin(new Date()); return `${p.year}-${p.month}-${p.day}`; };
let DS_KEY = dateKey();
const DS = {};
function dayStart(off){
  if (DS[off] != null) return DS[off];
  const [y, mo, d] = DS_KEY.split('-').map(Number);
  const guess = Date.UTC(y, mo - 1, d + off, 0, 0);
  let ms = guess - offsetMin(guess) * 60000;
  ms = guess - offsetMin(ms) * 60000;                 // settle across DST edges
  return (DS[off] = ms);
}
function refreshDay(){
  const k = dateKey(); if (k === DS_KEY) return false;
  DS_KEY = k; for (const c of [DS, SUNT, WIN, CLD]) for (const x in c) delete c[x];
  return true;
}
const nowMin = () => (Date.now() - dayStart(0)) / 60000;
const fmt = m => { m = Math.round(m); const h = Math.floor(m / 60), mm = ((m % 60) + 60) % 60; return `${String(h).padStart(2, '0')}:${String(mm).padStart(2, '0')}`; };
const dur = m => { m = Math.max(0, Math.round(m)); const h = Math.floor(m / 60), mm = m % 60; return h ? `${h}h ${String(mm).padStart(2, '0')}m` : `${mm}m`; };
const ST = { day: 0, min: nowMin(), live: true, sel: null, filters: store.get('filters', { sunny: false, open: false, cat: null, roof: false, fav: false }), user: null };
const tMs = (min = ST.min, day = ST.day) => dayStart(day) + min * 60000;
const SUNT = {};
function sunTimes(day = ST.day){
  if (SUNT[day]) return SUNT[day];
  const t = SunCalc.getTimes(new Date(dayStart(day) + 12 * 3600e3), CENTER[0], CENTER[1]);
  const m = d => (d.getTime() - dayStart(day)) / 60000;
  return (SUNT[day] = { rise: m(t.sunrise), set: m(t.sunset), golden: m(t.goldenHour), noon: m(t.solarNoon) });
}
const sunPos = (min = ST.min, day = ST.day) => SunCalc.getPosition(new Date(tMs(min, day)), CENTER[0], CENTER[1]);
const dayLabel = d => d === 0 ? T().today : d === 1 ? T().tomorrow : new Date(dayStart(d) + 12 * 3600e3).toLocaleDateString(LANG === 'de' ? 'de-DE' : 'en-GB', { weekday: 'long', timeZone: 'Europe/Berlin' });

// ═════════════════════════════════════════════════════════════════════════
//  Weather (Open-Meteo, optional)
// ═════════════════════════════════════════════════════════════════════════
const WX = { cloud: new Map(), temp: new Map(), ok: false };
async function loadWeather(){
  try {
    const r = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${CENTER[0]}&longitude=${CENTER[1]}&hourly=cloud_cover,temperature_2m&forecast_days=3&timezone=UTC`);
    const j = await r.json();
    j.hourly.time.forEach((t, i) => { const ms = Date.parse(t + 'Z'); WX.cloud.set(ms, j.hourly.cloud_cover[i]); WX.temp.set(ms, j.hourly.temperature_2m[i]); });
    WX.ok = true; for (const k in CLD) delete CLD[k];
  } catch { WX.ok = false; }
}
const hourKey = ms => Math.floor(ms / 3600e3) * 3600e3;
const CLD = {};
function cloudArr(day){
  if (CLD[day]) return CLD[day];
  const a = new Array(26).fill(undefined);
  if (WX.ok) for (let h = 0; h < 26; h++) a[h] = WX.cloud.get(hourKey(dayStart(day) + h * 3600e3));
  return (CLD[day] = a);
}
const cloudAt = (min, day = ST.day) => cloudArr(day)[Math.max(0, Math.floor(min / 60))];
const tempAt = (min, day = ST.day) => WX.temp.get(hourKey(tMs(min, day)));
const isCloudy = (min, day = ST.day) => { const c = cloudAt(min, day); return c != null && c >= 60; };
function clearsAt(min, day = ST.day){ const st = sunTimes(day); for (let m = Math.ceil(min / 60) * 60; m < st.set; m += 60) if (!isCloudy(m, day)) return m; return null; }

// ═════════════════════════════════════════════════════════════════════════
//  Venues + sun windows
// ═════════════════════════════════════════════════════════════════════════
let VEN = [], HZ = null;
const P0 = (lat, lng) => [(lng + 180) / 360 * 256, (1 - Math.log(Math.tan(lat * Math.PI / 180) + 1 / Math.cos(lat * Math.PI / 180)) / Math.PI) / 2 * 256];
function parseVenues(j){
  const seen = new Map();
  for (const el of j.elements || []){
    const t = el.tags || {}, lat = el.lat ?? el.center?.lat, lng = el.lon ?? el.center?.lon;
    if (lat == null || lng == null || !t.name || t.outdoor_seating === 'no') continue;
    const key = `${t.name.toLowerCase()}::${lat.toFixed(4)},${lng.toFixed(4)}`;
    if (seen.has(key)) continue;
    const [x0, y0] = P0(lat, lng);
    seen.set(key, {
      id: `${el.type}/${el.id}`, name: t.name, lat, lng, x0, y0, a: t.amenity || '',
      cuisine: (t.cuisine || '').split(';')[0].replace(/_/g, ' '),
      street: t['addr:street'] || '', hn: t['addr:housenumber'] || '',
      hoursStr: t.opening_hours || '', web: t.website || t['contact:website'] || '', roof: false,
      img: t.image || '', commons: t.wikimedia_commons || '', wd: t.wikidata || '',
    });
  }
  return [...seen.values()];
}
function decodeHorizon(str, bins){
  const out = new Uint8Array(bins); if (!str) return out;
  let k = 0;
  for (const run of str.split(';')){ const s = run.indexOf('*'); const v = parseInt(s < 0 ? run : run.slice(0, s), 16), n = s < 0 ? 1 : parseInt(run.slice(s + 1), 16); out.fill(v, k, k + n); k += n; }
  return out;
}
const D64 = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-';
function decodeD64(str, bins){
  const out = new Uint8Array(bins); if (!str) return out;
  let prev = 0, k = 0;
  for (let i = 0; i < str.length && k < bins; ){
    const c = str[i];
    if (c === '_'){ prev = parseInt(str.substr(i + 1, 2), 16); i += 3; }
    else { prev += D64.indexOf(c) - 31; i++; }
    out[k++] = prev;
  }
  return out;
}
// Sun windows per venue for a day, in minutes after Berlin midnight. Cached.
const WIN = {};
function windows(day = ST.day){
  if (WIN[day]) return WIN[day];
  if (!VEN.length || !HZ) return [];          // not loaded yet — don't cache an empty result
  const st = sunTimes(day), step = 5, steps = [];
  if (HZ) for (let m = Math.ceil(st.rise / step) * step; m <= st.set; m += step){
    const p = sunPos(m, day), az = p.azimuth * 180 / Math.PI, alt = p.altitude * 180 / Math.PI;
    steps.push([m, Math.max(0, Math.min(HZ.bins - 1, Math.round((az - HZ.azMinDeg) / HZ.binDeg))), alt / HZ.stepDeg, alt > 0]);
  }
  const out = VEN.map(v => {
    if (!v.hz) return null;
    const w = []; let cur = null;
    for (const [m, bin, q, up] of steps){
      const h = v.hz[bin], sun = up && h !== 255 && q > h;
      if (sun && cur === null) cur = m;
      if (!sun && cur !== null){ w.push([cur, m]); cur = null; }
    }
    if (cur !== null) w.push([cur, st.set]);
    return w;
  });
  return (WIN[day] = out);
}
function vstate(v, min = ST.min, day = ST.day){
  const W = windows(day)[v.i];
  if (!W) return { known: false, W: [] };
  const win = W.find(([a, b]) => min >= a && min < b);
  const cl = isCloudy(min, day);
  let left = 0;
  if (win) for (let m = min; m < win[1]; m += 5) if (!isCloudy(m, day)) left += 5;
  const next = W.find(([a]) => a > min);
  return { known: true, W, win, geo: !!win, sunny: !!win && !cl, cloudy: cl, left, next };
}
// opening hours (library loads deferred)
// The opening-hours parser (+ its i18next dependency, ~290 KB) is only loaded
// when something needs it: a terrace page with hours, or the "Open now" chip.
let hoursLoading = null;
function ensureHours(){
  if (window.opening_hours || hoursLoading) return hoursLoading;
  const add = src => new Promise((res, rej) => { const s = document.createElement('script'); s.src = src; s.onload = res; s.onerror = rej; document.head.appendChild(s); });
  hoursLoading = add('/vendor/i18next.min.js').then(() => add('/vendor/opening_hours.min.js')).then(() => render()).catch(() => { hoursLoading = null; });
  return hoursLoading;
}
function isOpen(v, ms){
  if (!v.hoursStr) return null;
  if (!window.opening_hours){ ensureHours(); return null; }
  try { if (v.oh === undefined) v.oh = new opening_hours(v.hoursStr, { lat: v.lat, lon: v.lng, address: { country_code: 'de', state: 'Berlin' } }); return v.oh ? v.oh.getState(new Date(ms)) : null; }
  catch { v.oh = null; return null; }
}
const typeOf = v => (T().type[v.a] || v.a || '').replace(/^./, c => c.toUpperCase());
const catOf = v => v.a === 'cafe' ? 'cafe' : v.a === 'ice_cream' ? 'ice' : v.a === 'restaurant' ? 'rest' : 'bar';

// ═════════════════════════════════════════════════════════════════════════
//  Map
// ═════════════════════════════════════════════════════════════════════════
const BOUNDS = L.latLngBounds([52.40, 13.17], [52.61, 13.64]);
const map = L.map('map', { zoomControl: false, attributionControl: true, minZoom: 11, maxZoom: 19, zoomSnap: 0.25, maxBounds: BOUNDS.pad(0.3), maxBoundsViscosity: 0.8, preferCanvas: true })
  .setView(...(() => {
    const m = location.hash.match(/^#(\d+(?:\.\d+)?)\/(\d+\.\d+)\/(\d+\.\d+)/);       // #zoom/lat/lng
    if (m) return [[+m[2], +m[3]], +m[1]];
    const v = store.get('view', null);
    return v ? [v.c, v.z] : [[52.5205, 13.4095], 15.5];
  })());
map.attributionControl.setPrefix(false);
map.createPane('shadowPane').style.zIndex = 250;
map.createPane('venuePane').style.zIndex = 450;

const GOLD = {
  background: '#F2EBDF', earth: '#F2EBDF', park_a: '#DCE4C4', park_b: '#D2DEB8', wood_a: '#D7E1C2', wood_b: '#CDDAB4', scrub_a: '#DDE4C8', scrub_b: '#D5DEBE',
  hospital: '#EDE4D6', industrial: '#EAE3D6', school: '#EDE4D6', pedestrian: '#EFE6D6', glacier: '#F4EFE6', sand: '#EDE3CF', beach: '#EDE3CF', aerodrome: '#E9E2D4', runway: '#E2D9C8',
  zoo: '#DCE4C4', military: '#E9E2D4', water: '#B7D2DE', pier: '#E3D7C3', buildings: '#E6DBC9',
  other: '#FBF6EC', minor_service: '#FBF6EC', minor_a: '#FFFDF8', minor_b: '#FFFDF8', link: '#FFFDF8', major: '#FFFDF8', highway: '#FFF4DC', railway: '#CFC3AE', boundaries: '#C9BCA6',
  roads_label_minor: '#9A8C75', roads_label_minor_halo: '#F7F1E6', roads_label_major: '#8A7C66', roads_label_major_halo: '#F7F1E6',
  subplace_label: '#9A8C75', subplace_label_halo: '#F2EBDF', city_label: '#5C5446', city_label_halo: '#F2EBDF', address_label: '#B3A68E', address_label_halo: '#F2EBDF',
};
// Protomaps "light" flavor (copied from @protomaps/basemaps 5.x) — base for our golden palette.
const LIGHT = {"background":"#cccccc","earth":"#e2dfda","park_a":"#cfddd5","park_b":"#9cd3b4","hospital":"#e4dad9","industrial":"#d1dde1","school":"#e4ded7","wood_a":"#d0ded0","wood_b":"#a0d9a0","pedestrian":"#e3e0d4","scrub_a":"#cedcd7","scrub_b":"#99d2bb","glacier":"#e7e7e7","sand":"#e2e0d7","beach":"#e8e4d0","aerodrome":"#dadbdf","runway":"#e9e9ed","water":"#80deea","zoo":"#c6dcdc","military":"#dcdcdc","tunnel_other_casing":"#e0e0e0","tunnel_minor_casing":"#e0e0e0","tunnel_link_casing":"#e0e0e0","tunnel_major_casing":"#e0e0e0","tunnel_highway_casing":"#e0e0e0","tunnel_other":"#d5d5d5","tunnel_minor":"#d5d5d5","tunnel_link":"#d5d5d5","tunnel_major":"#d5d5d5","tunnel_highway":"#d5d5d5","pier":"#e0e0e0","buildings":"#cccccc","minor_service_casing":"#e0e0e0","minor_casing":"#e0e0e0","link_casing":"#e0e0e0","major_casing_late":"#e0e0e0","highway_casing_late":"#e0e0e0","other":"#ebebeb","minor_service":"#ebebeb","minor_a":"#ebebeb","minor_b":"#ffffff","link":"#ffffff","major_casing_early":"#e0e0e0","major":"#ffffff","highway_casing_early":"#e0e0e0","highway":"#ffffff","railway":"#a7b1b3","boundaries":"#adadad","bridges_other_casing":"#e0e0e0","bridges_minor_casing":"#e0e0e0","bridges_link_casing":"#e0e0e0","bridges_major_casing":"#e0e0e0","bridges_highway_casing":"#e0e0e0","bridges_other":"#ebebeb","bridges_minor":"#ffffff","bridges_link":"#ffffff","bridges_major":"#f5f5f5","bridges_highway":"#ffffff","roads_label_minor":"#91888b","roads_label_minor_halo":"#ffffff","roads_label_major":"#938a8d","roads_label_major_halo":"#ffffff","ocean_label":"#728dd4","subplace_label":"#8f8f8f","subplace_label_halo":"#e0e0e0","city_label":"#5c5c5c","city_label_halo":"#e0e0e0","state_label":"#b3b3b3","state_label_halo":"#e0e0e0","country_label":"#a3a3a3","address_label":"#91888b","address_label_halo":"#ffffff","pois":{"blue":"#1A8CBD","green":"#20834D","lapis":"#315BCF","pink":"#EF56BA","red":"#F2567A","slategray":"#6A5B8F","tangerine":"#CB6704","turquoise":"#00C3D4"},"landcover":{"grassland":"rgba(210, 239, 207, 1)","barren":"rgba(255, 243, 215, 1)","urban_area":"rgba(230, 230, 230, 1)","farmland":"rgba(216, 239, 210, 1)","glacier":"rgba(255, 255, 255, 1)","scrub":"rgba(234, 239, 210, 1)","forest":"rgba(196, 231, 210, 1)"}};
let basemap = null;
function addBasemap(){
  if (basemap || !window.protomapsL) return;
  const F = JSON.parse(JSON.stringify(LIGHT));
  for (const k of Object.keys(F)){
    if (/casing/.test(k)) F[k] = '#E5D9C5';
    else if (/^tunnel_/.test(k)) F[k] = '#EFE7D9';
    else if (/^bridges_/.test(k)) F[k] = '#FFFDF8';
  }
  Object.assign(F, GOLD);
  if (F.pois) for (const k of Object.keys(F.pois)) F.pois[k] = '#A8987C';
  basemap = protomapsL.leafletLayer({ url: '/tiles/{z}/{x}/{y}.pbf', maxDataZoom: 14,
    paintRules: protomapsL.paintRules(F),
    // Shop/POI icons + labels are the costliest part of the basemap and compete with our own dots — skip them.
    labelRules: protomapsL.labelRules(F, LANG).filter(r => r.dataLayer !== 'pois'),
    backgroundColor: F.background, updateWhenZooming: false, keepBuffer: 1,
    attribution: '© <a href="https://openstreetmap.org/copyright">OpenStreetMap</a> · <a href="https://protomaps.com">Protomaps</a> · <a href="https://open-meteo.com">Open-Meteo</a>' }).addTo(map);
}
window.__basemapReady = addBasemap;
addBasemap();

// Generic full-viewport canvas overlay.
const CanvasLayer = L.Layer.extend({
  initialize(pane, draw){ this._pane = pane; this._drawFn = draw; },
  onAdd(m){
    this._c = L.DomUtil.create('canvas', 'cv'); this._c.style.position = 'absolute'; this._c.style.pointerEvents = 'none';
    m.getPane(this._pane).appendChild(this._c);
    m.on('move resize', this.redraw, this);
    m.on('zoomstart', () => { this._c.style.visibility = 'hidden'; });
    m.on('zoomend', () => { this._c.style.visibility = ''; this.redraw(); });
    this.redraw();
  },
  redraw(){ if (this._raf) return; this._raf = requestAnimationFrame(() => { this._raf = 0; this._render(); }); },
  _render(){
    const m = this._map; if (!m) return;
    const size = m.getSize(), dpr = Math.min(2, window.devicePixelRatio || 1), tl = m.containerPointToLayerPoint([0, 0]);
    L.DomUtil.setPosition(this._c, tl);
    if (this._c.width !== size.x * dpr || this._c.height !== size.y * dpr){ this._c.width = size.x * dpr; this._c.height = size.y * dpr; this._c.style.width = size.x + 'px'; this._c.style.height = size.y + 'px'; }
    const ctx = this._c.getContext('2d'); ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, size.x, size.y);
    const z = m.getZoom(), S = 2 ** z, o = m.getPixelOrigin();
    this._drawFn(ctx, { S, ox: o.x + tl.x, oy: o.y + tl.y, W: size.x, H: size.y, z });
  },
});

// ─── Shadows ───────────────────────────────────────────────────────────────
const SH = { index: null, tiles: new Map(), z: 15 };
async function loadShadowIndex(){
  try { const r = await fetch('/data/shadows/index.json', { cache: 'no-cache' }); const j = await r.json(); SH.index = new Set(j.tiles.map(([x, y]) => x + '/' + y)); SH.z = j.z || 15; }
  catch { SH.index = new Set(); }
}
function loadShadowTile(key){
  if (SH.tiles.has(key)) return SH.tiles.get(key);
  SH.tiles.set(key, null);
  const [tx, ty] = key.split('/').map(Number), n = 2 ** SH.z;
  // Tile origin on the 1e-5° grid (matches scripts/bake-data.js → bakeShadowTiles)
  const k = Math.PI - 2 * Math.PI * ty / n, lon0 = Math.round((tx / n * 360 - 180) * 1e5) / 1e5, lat0 = Math.round(180 / Math.PI * Math.atan(0.5 * (Math.exp(k) - Math.exp(-k))) * 1e5) / 1e5;
  fetch(`/data/shadows/${SH.z}/${tx}/${ty}.json`).then(r => r.json()).then(j => {
    const blds = [];
    for (const b of j.b){
      const h = b[0], np = (b.length - 1) / 2, pts = new Float64Array(np * 2);
      let ix = 0, iy = 0, minx = Infinity, miny = Infinity, maxx = -Infinity, maxy = -Infinity;
      for (let i = 0; i < np; i++){
        ix += b[1 + 2 * i]; iy += b[2 + 2 * i];
        const [x, y] = P0(lat0 - iy / 1e5, lon0 + ix / 1e5);
        pts[2 * i] = x; pts[2 * i + 1] = y;
        if (x < minx) minx = x; if (x > maxx) maxx = x; if (y < miny) miny = y; if (y > maxy) maxy = y;
      }
      blds.push({ h, pts, minx, miny, maxx, maxy });
    }
    SH.tiles.set(key, { blds, pxPerM: 256 / (2 * Math.PI * 6378137 * Math.cos(lat0 * Math.PI / 180)) });
    shadowLayer.redraw(); paintSnaps(document);
  }).catch(() => {});
  return null;
}
const SHADOW_MIN_Z = 15;
// Shadows are drawn per 256-px tile (Leaflet GridLayer): panning only paints
// tiles that scroll into view, zoom animates like any tile layer, and a time
// change repaints just the tiles on screen — each touching only the buildings
// that can reach it.
function sunScene(){
  const p = sunPos(), alt = p.altitude, altDeg = alt * 180 / Math.PI, cl = isCloudy(ST.min);
  return { p, alt, altDeg, cl, up: alt > 0.01 && !cl, tanA: Math.tan(Math.max(alt, 0.03)), ux: Math.sin(p.azimuth), uy: -Math.cos(p.azimuth) };
}
function paintShadowTile(c, coords, sc){
  const dpr = c._dpr, ctx = c.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, 256, 256);
  const { alt, altDeg, cl, up, tanA, ux, uy } = sc;
  if (alt <= 0){ ctx.fillStyle = 'rgba(28,30,70,.36)'; ctx.fillRect(0, 0, 256, 256); }
  else if (cl){ ctx.fillStyle = 'rgba(120,125,140,.12)'; ctx.fillRect(0, 0, 256, 256); }
  else if (altDeg < 18){ ctx.fillStyle = `rgba(255,150,40,${(.12 * (1 - altDeg / 18)).toFixed(3)})`; ctx.fillRect(0, 0, 256, 256); }
  if (coords.z < SHADOW_MIN_Z || !SH.index) return;
  const S = 2 ** coords.z, ox = coords.x * 256, oy = coords.y * 256;
  const X = x => x * S - ox, Y = y => y * S - oy;
  // Data tiles (z15) that can cast shade into this tile: tile bounds + max shadow reach.
  const n = 2 ** SH.z, reachPx = up ? Math.min(400, 60 / tanA) * 256 / (2 * Math.PI * 6378137 * 0.6) * S : 0;
  const t0 = v => Math.floor(v / S / 256 * n);
  // Projected footprints for this tile are cached on the canvas (they don't
  // change with time), so a time change only recomputes the shadow sweep.
  const reachMax = Math.min(400, 60 / 0.0524) * 256 / (2 * Math.PI * 6378137 * 0.6) * S;   // reach at 3° sun
  if (!c._geo || c._geoZ !== coords.z + '/' + coords.x + '/' + coords.y || c._geoN !== SH.tiles.size){
    const geo = [];
    for (let tx = t0(ox - reachMax); tx <= t0(ox + 256 + reachMax); tx++) for (let ty = t0(oy - reachMax); ty <= t0(oy + 256 + reachMax); ty++){
      const key = tx + '/' + ty; if (!SH.index.has(key)) continue;
      const t = SH.tiles.get(key); if (!t){ loadShadowTile(key); continue; }
      for (const b of t.blds){
        const bx0 = X(b.minx), bx1 = X(b.maxx), by0 = Y(b.miny), by1 = Y(b.maxy);
        const reach = Math.min(400, b.h / 0.0524) * t.pxPerM * S;
        if (bx1 < -reach || bx0 > 256 + reach || by1 < -reach || by0 > 256 + reach) continue;
        const np = b.pts.length / 2, P = new Float64Array(np * 2);
        for (let i = 0; i < np; i++){ P[2 * i] = X(b.pts[2 * i]); P[2 * i + 1] = Y(b.pts[2 * i + 1]); }
        let area = 0; for (let i = 0, j = np - 1; i < np; j = i++) area += P[2 * j] * P[2 * i + 1] - P[2 * i] * P[2 * j + 1];
        geo.push({ P, np, h: b.h, ppm: t.pxPerM * S, bx0, bx1, by0, by1, sgn: area > 0 ? 1 : -1, onTile: !(bx1 < 0 || bx0 > 256 || by1 < 0 || by0 > 256) });
      }
    }
    c._geo = geo; c._geoZ = coords.z + '/' + coords.x + '/' + coords.y; c._geoN = SH.tiles.size;
  }
  const shadows = new Path2D(), roofs = new Path2D();
  let any = false;
  for (const g of c._geo){
    const { P, np } = g;
    if (g.onTile) ringPath(roofs, P, false);
    if (!up) continue;
    const L = Math.min(400, g.h / tanA) * g.ppm, dx = ux * L, dy = uy * L;
    if (Math.max(g.bx1, g.bx1 + dx) < 0 || Math.min(g.bx0, g.bx0 + dx) > 256 || Math.max(g.by1, g.by1 + dy) < 0 || Math.min(g.by0, g.by0 + dy) > 256) continue;
    any = true;
    const Q = new Float64Array(np * 2);
    for (let i = 0; i < np; i++){ Q[2 * i] = P[2 * i] + dx; Q[2 * i + 1] = P[2 * i + 1] + dy; }
    ringPath(shadows, Q, true);
    for (let i = 0; i < np; i++){
      const j = (i + 1) % np, ex = P[2 * j] - P[2 * i], ey = P[2 * j + 1] - P[2 * i + 1];
      if ((ey * dx - ex * dy) * g.sgn < 0) continue;
      ringPath(shadows, [P[2 * i], P[2 * i + 1], P[2 * j], P[2 * j + 1], Q[2 * j], Q[2 * j + 1], Q[2 * i], Q[2 * i + 1]], true);
    }
  }
  if (any){ ctx.save(); ctx.globalAlpha = 0.27 * Math.min(1, altDeg / 4); ctx.fillStyle = '#3E3462'; ctx.fill(shadows, 'nonzero'); ctx.restore(); }
  ctx.fillStyle = alt <= 0 ? '#CFC6B8' : '#E6DBC9'; ctx.fill(roofs);
  if (coords.z >= 16 && !ST.dragging){ ctx.strokeStyle = 'rgba(160,140,110,.35)'; ctx.lineWidth = .6; ctx.stroke(roofs); }
  if (alt <= 0){ ctx.fillStyle = 'rgba(28,30,70,.18)'; ctx.fill(roofs); }
}
const ShadowGrid = L.GridLayer.extend({
  options: { pane: 'shadowPane', tileSize: 256, keepBuffer: 1, updateWhenZooming: false },
  createTile(coords){
    const c = document.createElement('canvas'), dpr = Math.min(2, window.devicePixelRatio || 1);
    c._dpr = dpr; c.width = c.height = 256 * dpr;
    paintShadowTile(c, coords, sunScene());
    return c;
  },
  repaint(){
    if (!this._map) return;
    const sc = sunScene();
    for (const k in this._tiles){ const t = this._tiles[k]; if (t.current) paintShadowTile(t.el, t.coords, sc); }
  },
});
const shadowLayer = new ShadowGrid().addTo(map);
let shadowRepaintQueued = false;
let shadowLast = 0, shadowTrail = 0;
// While the sun is being dragged, shadows repaint ~8×/s (the dial, time and
// dots still follow every frame); a final full-quality repaint follows release.
shadowLayer.redraw = () => {
  if (shadowRepaintQueued) return;
  const wait = ST.dragging ? Math.max(0, 120 - (performance.now() - shadowLast)) : 0;
  shadowRepaintQueued = true;
  clearTimeout(shadowTrail);
  shadowTrail = setTimeout(() => requestAnimationFrame(() => { shadowRepaintQueued = false; shadowLast = performance.now(); shadowLayer.repaint(); }), wait);
};

// ─── Sun snapshots ─────────────────────────────────────────────────────────
// A small aerial view of each terrace's block with its real building shadows
// at the chosen time — our "photo" for every place. Same buildings + heights
// as the map and the sun/shade dots.
let VBY = new Map();
function ringPath(path, P, reverseIfCW){
  let a = 0; for (let i = 0, j = P.length - 2; i < P.length; j = i, i += 2) a += P[j] * P[i + 1] - P[i] * P[j + 1];
  if ((a > 0) === reverseIfCW){ path.moveTo(P[P.length - 2], P[P.length - 1]); for (let i = P.length - 4; i >= 0; i -= 2) path.lineTo(P[i], P[i + 1]); }
  else { path.moveTo(P[0], P[1]); for (let i = 2; i < P.length; i += 2) path.lineTo(P[i], P[i + 1]); }
  path.closePath();
}
// Buildings around a terrace, cached once their data tiles are loaded
// (a snapshot then touches ~100 buildings instead of ~6,000).
function nearBuildings(v, radiusM){
  const key = radiusM > 300 ? '_nearL' : '_nearS';
  if (v[key]) return v[key];
  if (!SH.index) return [];
  const mPer0 = 2 * Math.PI * 6378137 * Math.cos(v.lat * Math.PI / 180) / 256, r0 = radiusM / mPer0;
  const n = 2 ** SH.z, tx0 = Math.floor((v.x0 - r0) / 256 * n), tx1 = Math.floor((v.x0 + r0) / 256 * n), ty0 = Math.floor((v.y0 - r0) / 256 * n), ty1 = Math.floor((v.y0 + r0) / 256 * n);
  const out = []; let complete = true;
  for (let tx = tx0; tx <= tx1; tx++) for (let ty = ty0; ty <= ty1; ty++){
    const k = tx + '/' + ty; if (!SH.index.has(k)) continue;
    const t = SH.tiles.get(k); if (!t){ loadShadowTile(k); complete = false; continue; }
    for (const b of t.blds) if (b.maxx > v.x0 - r0 && b.minx < v.x0 + r0 && b.maxy > v.y0 - r0 && b.miny < v.y0 + r0) out.push([b, t.pxPerM]);
  }
  if (complete) v[key] = out;
  return out;
}
function snapTiles(v){
  if (!SH.index) return [];
  const n = 2 ** SH.z, tx = Math.floor(v.x0 / 256 * n), ty = Math.floor(v.y0 / 256 * n), out = [];
  for (let dx = -1; dx <= 1; dx++) for (let dy = -1; dy <= 1; dy++){
    const k = (tx + dx) + '/' + (ty + dy);
    if (SH.index.has(k)){ const t = loadShadowTile(k); if (t) out.push(t); }
  }
  return out;
}
function paintSnap(cv){
  const v = VBY.get(cv.dataset.snap); if (!v) return;
  const day = cv.dataset.day ? +cv.dataset.day : ST.day, min = cv.dataset.min ? +cv.dataset.min : ST.min, z = +(cv.dataset.z || 16.4);
  const r = cv.getBoundingClientRect(), W = Math.round(r.width), H = Math.round(r.height);
  if (!W || !H) return;
  const dpr = Math.min(2, window.devicePixelRatio || 1);
  if (cv.width !== W * dpr || cv.height !== H * dpr){ cv.width = W * dpr; cv.height = H * dpr; }
  const ctx = cv.getContext('2d'); ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  const S = 2 ** z, ox = v.x0 * S - W / 2, oy = v.y0 * S - H / 2, X = x => x * S - ox, Y = y => y * S - oy;
  const p = sunPos(min, day), alt = p.altitude, altDeg = alt * 180 / Math.PI, cl = isCloudy(min, day), up = alt > 0.01 && !cl;
  ctx.fillStyle = '#F2EBDF'; ctx.fillRect(0, 0, W, H);
  const tanA = Math.tan(Math.max(alt, 0.03)), ux = Math.sin(p.azimuth), uy = -Math.cos(p.azimuth);
  const shadows = new Path2D(), roofs = new Path2D();
  for (const [b, ppm] of nearBuildings(v, W > 200 ? 650 : 280)){
    const L = up ? Math.min(400, b.h / tanA) * ppm * S : 0;
    const bx0 = X(b.minx), bx1 = X(b.maxx), by0 = Y(b.miny), by1 = Y(b.maxy);
    if (bx1 < -L - 2 || bx0 > W + L + 2 || by1 < -L - 2 || by0 > H + L + 2) continue;
    const np = b.pts.length / 2, P = new Float64Array(np * 2);
    for (let i = 0; i < np; i++){ P[2 * i] = X(b.pts[2 * i]); P[2 * i + 1] = Y(b.pts[2 * i + 1]); }
    ringPath(roofs, P, false);
    if (!up) continue;
    const dx = ux * L, dy = uy * L, Q = new Float64Array(np * 2);
    let area = 0; for (let i = 0, j = np - 1; i < np; j = i++) area += P[2 * j] * P[2 * i + 1] - P[2 * i] * P[2 * j + 1];
    for (let i = 0; i < np; i++){ Q[2 * i] = P[2 * i] + dx; Q[2 * i + 1] = P[2 * i + 1] + dy; }
    ringPath(shadows, Q, true);
    const sgn = area > 0 ? 1 : -1;
    for (let i = 0; i < np; i++){
      const j = (i + 1) % np, ex = P[2 * j] - P[2 * i], ey = P[2 * j + 1] - P[2 * i + 1];
      if ((ey * dx - ex * dy) * sgn < 0) continue;
      ringPath(shadows, [P[2 * i], P[2 * i + 1], P[2 * j], P[2 * j + 1], Q[2 * j], Q[2 * j + 1], Q[2 * i], Q[2 * i + 1]], true);
    }
  }
  if (up){ ctx.globalAlpha = .3 * Math.min(1, altDeg / 4); ctx.fillStyle = '#3E3462'; ctx.fill(shadows); ctx.globalAlpha = 1; }
  ctx.fillStyle = alt <= 0 ? '#CFC6B8' : '#E6DBC9'; ctx.fill(roofs);
  ctx.strokeStyle = 'rgba(150,130,100,.45)'; ctx.lineWidth = .7; ctx.stroke(roofs);
  if (alt <= 0){ ctx.fillStyle = 'rgba(28,30,70,.38)'; ctx.fillRect(0, 0, W, H); }
  else if (cl){ ctx.fillStyle = 'rgba(120,125,140,.16)'; ctx.fillRect(0, 0, W, H); }
  else if (altDeg < 18){ ctx.fillStyle = `rgba(255,150,40,${(.12 * (1 - altDeg / 18)).toFixed(3)})`; ctx.fillRect(0, 0, W, H); }
  // the terrace
  const s = vstate(v, min, day), cx = W / 2, cy = H / 2, big = W > 120;
  if (s.sunny){ const R = big ? 22 : 15; ctx.drawImage(GLOW, cx - R, cy - R, R * 2, R * 2); ctx.fillStyle = '#FFB000'; ctx.strokeStyle = '#fff'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(cx, cy, big ? 7 : 5, 0, 7); ctx.fill(); ctx.stroke(); }
  else { ctx.fillStyle = '#FFFDF8'; ctx.strokeStyle = s.geo && s.cloudy ? '#C8A65A' : '#6F6790'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(cx, cy, big ? 6 : 4.5, 0, 7); ctx.fill(); ctx.stroke(); }
  // where the light comes from
  if (alt > 0){
    const sx = -Math.sin(p.azimuth), sy = Math.cos(p.azimuth), rx = W / 2 - (big ? 16 : 10), ry = H / 2 - (big ? 16 : 10);
    const k = 1 / Math.max(Math.abs(sx) / rx, Math.abs(sy) / ry), gx = cx + sx * k, gy = cy + sy * k;
    if (cl){ ctx.fillStyle = '#F4F1EA'; ctx.strokeStyle = '#B9B19E'; ctx.lineWidth = 1; ctx.beginPath(); ctx.arc(gx, gy, big ? 8 : 5.5, 0, 7); ctx.fill(); ctx.stroke(); }
    else { ctx.drawImage(GLOW, gx - 14, gy - 14, 28, 28); ctx.fillStyle = '#FFC23A'; ctx.strokeStyle = '#fff'; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.arc(gx, gy, big ? 7 : 5, 0, 7); ctx.fill(); ctx.stroke(); }
  }
}
function paintSnaps(root){ if (!root) return; root.querySelectorAll('canvas.snap').forEach(paintSnap); }
const snapHTML = (v, cls = '', extra = '') => `<canvas class="snap ${cls}" data-snap="${esc(v.id)}" ${extra} aria-hidden="true"></canvas>`;

// ─── Real photos (open-licence only) ───────────────────────────────────────
// ~1% of terraces have a Wikimedia Commons / Wikidata photo in OpenStreetMap.
// Shown on the terrace page with author + licence, as the licence requires.
const PHOTO = new Map();
function photoFor(v){
  if (PHOTO.has(v.id)) return PHOTO.get(v.id);
  const commonsInfo = async file => {
    const title = 'File:' + file.replace(/^File:/i, '').trim();
    const j = await (await fetch(`https://commons.wikimedia.org/w/api.php?action=query&format=json&origin=*&prop=imageinfo&iiprop=url|extmetadata&iiurlwidth=900&titles=${encodeURIComponent(title)}`)).json();
    const page = Object.values(j.query?.pages || {})[0], ii = page?.imageinfo?.[0];
    if (!ii || !ii.thumburl) return null;
    const md = ii.extmetadata || {}, strip = h => (h || '').replace(/<[^>]*>/g, '').trim();
    return { src: ii.thumburl, href: ii.descriptionurl, credit: [strip(md.Artist?.value), md.LicenseShortName?.value].filter(Boolean).join(' · ') || 'Wikimedia Commons' };
  };
  const pr = (async () => {
    try {
      if (v.commons && /^File:/i.test(v.commons)) return await commonsInfo(v.commons);
      const m = v.img.match(/commons\.wikimedia\.org\/wiki\/(File:[^?#]+)/i);
      if (m) return await commonsInfo(decodeURIComponent(m[1]));
      if (v.wd && /^Q\d+$/.test(v.wd)){
        const j = await (await fetch(`https://www.wikidata.org/wiki/Special:EntityData/${v.wd}.json`)).json();
        const f = j.entities?.[v.wd]?.claims?.P18?.[0]?.mainsnak?.datavalue?.value;
        if (f) return await commonsInfo(f);
      }
      if (/^https:\/\/.+\.(jpe?g|png|webp)(\?.*)?$/i.test(v.img)){ const h = new URL(v.img).hostname; return { src: v.img, href: v.img, credit: h }; }
    } catch {}
    return null;
  })();
  PHOTO.set(v.id, pr);
  return pr;
}
const hasPhotoTags = v => !!(v.commons || v.wd || v.img);

// ─── Venue dots ────────────────────────────────────────────────────────────
let VIS = [];          // visible (filtered) venues with state, for hit-testing
const GLOW = (() => { const c = document.createElement('canvas'), r = 24; c.width = c.height = r * 2; const g = c.getContext('2d'), gr = g.createRadialGradient(r, r, 0, r, r, r); gr.addColorStop(0, 'rgba(255,190,40,.5)'); gr.addColorStop(1, 'rgba(255,190,40,0)'); g.fillStyle = gr; g.fillRect(0, 0, r * 2, r * 2); return c; })();
const venueLayer = new CanvasLayer('venuePane', (ctx, v) => {
  const glow = v.z >= 14, r = v.z >= 16 ? 7 : v.z >= 14 ? 6 : 4.2;
  const list = [];
  for (const ven of FILTERED){
    const x = ven.x0 * v.S - v.ox, y = ven.y0 * v.S - v.oy;
    if (x < -20 || y < -20 || x > v.W + 20 || y > v.H + 20) continue;
    list.push([ven, x, y, ST.sel === ven ? 2 : ven._s.sunny ? 1 : 0]);
  }
  list.sort((a, b) => a[3] - b[3]);
  VIS = list;
  for (const [ven, x, y, rank] of list){
    const s = ven._s;
    if (rank === 2) continue;
    if (s.sunny){
      if (glow){ const R = r * 2.6; ctx.drawImage(GLOW, x - R, y - R, R * 2, R * 2); }
      ctx.fillStyle = '#FFB000'; ctx.strokeStyle = '#fff'; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.fill(); ctx.stroke();
    } else if (s.geo && s.cloudy){
      ctx.fillStyle = '#FFFDF8'; ctx.strokeStyle = '#C8A65A'; ctx.lineWidth = 1.6; ctx.beginPath(); ctx.arc(x, y, r * .7, 0, 7); ctx.fill(); ctx.stroke();
    } else {
      ctx.fillStyle = 'rgba(255,253,248,.92)'; ctx.strokeStyle = s.known ? '#8E86A6' : '#C2BAAA'; ctx.lineWidth = 1.4; ctx.beginPath(); ctx.arc(x, y, r * .58, 0, 7); ctx.fill(); ctx.stroke();
    }
  }
  if (ST.user){
    const [ux0, uy0] = P0(ST.user[0], ST.user[1]), x = ux0 * v.S - v.ox, y = uy0 * v.S - v.oy;
    ctx.fillStyle = 'rgba(47,123,255,.14)'; ctx.beginPath(); ctx.arc(x, y, 18, 0, 7); ctx.fill();
    ctx.fillStyle = '#2F7BFF'; ctx.strokeStyle = '#fff'; ctx.lineWidth = 2.5; ctx.beginPath(); ctx.arc(x, y, 6.5, 0, 7); ctx.fill(); ctx.stroke();
  }
  const sel = list.find(e => e[3] === 2);
  if (sel){
    const [ven, x, y] = sel, s = ven._s;
    ctx.fillStyle = s.sunny ? '#FFB000' : '#FFFDF8'; ctx.strokeStyle = s.sunny ? '#fff' : '#211C14'; ctx.lineWidth = 3;
    ctx.beginPath(); ctx.arc(x, y, 10, 0, 7); ctx.fill(); ctx.stroke();
    ctx.font = '400 16px "Iowan Old Style",Palatino,Georgia,serif'; ctx.textBaseline = 'middle';
    ctx.strokeStyle = 'rgba(255,252,246,.95)'; ctx.lineWidth = 4; ctx.strokeText(ven.name, x + 16, y); ctx.fillStyle = '#211C14'; ctx.fillText(ven.name, x + 16, y);
  }
});
venueLayer.addTo(map);
map.on('click', e => {
  const pt = e.containerPoint; let best = null, bd = 22 * 22;
  for (const [ven, x, y] of VIS){ const d = (x - pt.x) ** 2 + (y - pt.y) ** 2; if (d < bd){ bd = d; best = ven; } }
  if (best) openDetail(best);
});

// ═════════════════════════════════════════════════════════════════════════
//  State → views
// ═════════════════════════════════════════════════════════════════════════
let FILTERED = [];
const refPoint = () => ST.user || [map.getCenter().lat, map.getCenter().lng];
const distM = (v, ref) => { const dx = (v.lng - ref[1]) * 111320 * Math.cos(ref[0] * Math.PI / 180), dy = (v.lat - ref[0]) * 111320; return Math.hypot(dx, dy); };
const walkMin = d => Math.max(1, Math.round(d * 1.3 / 80));
const FAV = new Set(store.get('favs', []));
function applyFilters(){
  const f = ST.filters, t = tMs();
  FILTERED = VEN.filter(v => {
    if (f.cat && catOf(v) !== f.cat) return false;
    if (f.roof && !v.roof) return false;
    if (f.fav && !FAV.has(v.id)) return false;
    if (f.sunny && !v._s.sunny) return false;
    if (f.open && isOpen(v, t) === false) return false;
    return true;
  });
}
function computeStates(){ for (const v of VEN) v._s = vstate(v); }
let renderQueued = false;
function render(){
  if (renderQueued) return; renderQueued = true;
  requestAnimationFrame(() => {
    renderQueued = false;
    computeStates(); applyFilters();
    shadowLayer.redraw(); venueLayer.redraw();
    renderDial(); renderTop(); renderChips(); renderSheet(ST.dragging);
    if (ST.sel) renderDetail();
  });
}

// ─── Top bar ───────────────────────────────────────────────────────────────
function renderTop(){
  $('search-open').querySelector('span').textContent = T().search_ph;
  $('lang-toggle').textContent = LANG === 'de' ? 'EN' : 'DE';
  const st = sunTimes(), night = ST.min < st.rise || ST.min > st.set, c = cloudAt(ST.min), tp = tempAt(ST.min);
  $('wx-chip').innerHTML = WX.ok && tp != null ? `${Math.round(tp)}° ${night ? '☾' : c >= 60 ? '☁' : c >= 30 ? '⛅' : '☀'}` : (night ? '☾' : '☀');
  $('wx-chip').title = WX.ok && c != null ? T().sr_cloud(Math.round(c)) : T().weather_na;
}
const CHIPS = [['sunny', 'chip_sunny'], ['open', 'chip_open'], ['cat:bar', 'chip_bar'], ['cat:cafe', 'chip_cafe'], ['cat:rest', 'chip_rest'], ['cat:ice', 'chip_ice'], ['roof', 'chip_roof'], ['fav', 'chip_fav']];
function renderChips(){
  const f = ST.filters, nSun = VEN.filter(v => v._s.sunny && inView(v)).length;
  $('chips').innerHTML = CHIPS.filter(([k]) => k !== 'fav' || FAV.size).map(([k, label]) => {
    const on = k.startsWith('cat:') ? f.cat === k.slice(4) : !!f[k];
    return `<button class="chip ${on ? 'on' : ''}" data-chip="${k}">${k === 'sunny' ? '<span class="dot"></span>' : ''}${T()[label]}${k === 'sunny' ? ` <span class="n">${nSun}</span>` : ''}</button>`;
  }).join('');
}
$('chips').addEventListener('click', e => {
  const b = e.target.closest('[data-chip]'); if (!b) return;
  const k = b.dataset.chip, f = ST.filters;
  if (k.startsWith('cat:')){ const c = k.slice(4); f.cat = f.cat === c ? null : c; } else f[k] = !f[k];
  store.set('filters', f); render();
});

// ─── Sun dial ──────────────────────────────────────────────────────────────
function renderDial(){
  const svg = $('dial-svg'), W = svg.getBoundingClientRect().width || 360, st = sunTimes();
  const cx = W / 2, base = 106, rx = Math.min(W / 2 - 34, 250), ry = 64;
  const u = Math.max(0, Math.min(1, (ST.min - st.rise) / (st.set - st.rise)));
  const th = Math.PI * (1 - u), kx = cx + rx * Math.cos(th), ky = base - ry * Math.sin(th);
  const night = ST.min < st.rise || ST.min > st.set, cl = isCloudy(ST.min);
  const arc = (a0, a1) => `M${cx + rx * Math.cos(a0)},${base - ry * Math.sin(a0)} A${rx},${ry} 0 0 1 ${cx + rx * Math.cos(a1)},${base - ry * Math.sin(a1)}`;
  const mono = 'font-family="ui-monospace,SF Mono,Menlo,monospace" font-size="10" fill="#7C6F58"';
  svg.innerHTML = `
    <defs><radialGradient id="sg"><stop offset="0" stop-color="#FFF6CF"/><stop offset=".55" stop-color="${cl ? '#E9E4D6' : '#FFC23A'}"/><stop offset="1" stop-color="${cl ? '#CFC8B6' : '#FF9E00'}"/></radialGradient></defs>
    <rect class="dial-hit" x="0" y="32" width="${W}" height="96" fill="transparent"/>
    <path d="${arc(Math.PI, 0)}" fill="none" stroke="#211C14" stroke-opacity=".3" stroke-width="1.5" stroke-dasharray="2 5" pointer-events="none"/>
    ${night ? '' : `<path d="${arc(Math.PI, th)}" fill="none" stroke="${cl ? '#A9A08C' : '#E89A00'}" stroke-width="2.5" stroke-linecap="round" pointer-events="none"/>`}
    <line x1="16" x2="${W - 16}" y1="${base}" y2="${base}" stroke="#211C14" stroke-opacity=".15" pointer-events="none"/>
    <text x="${cx - rx}" y="${base + 14}" ${mono} text-anchor="middle">↑ ${fmt(st.rise)}</text>
    <text x="${cx + rx}" y="${base + 14}" ${mono} text-anchor="middle">${fmt(st.set)} ↓</text>
    <g class="knob" transform="translate(${kx},${ky})">
      <circle r="26" fill="transparent"/>
      ${night ? `<circle r="11" fill="#D9DCEF" stroke="#fff" stroke-width="2"/><circle r="9" cx="5" cy="-3" fill="#3A3E66"/>`
              : `<circle r="24" fill="${cl ? '#CFC8B6' : '#FFC23A'}" opacity=".22"/><circle r="14" fill="url(#sg)" stroke="#fff" stroke-width="2.5"/>`}
      ${cl && !night ? '<path d="M-14,6 a7,7 0 0 1 6,-9 a9,9 0 0 1 17,1 a6,6 0 0 1 2,12 h-22 a5,5 0 0 1 -3,-4z" fill="#F4F1EA" stroke="#C9C1AE"/>' : ''}
    </g>`;
  $('dial-time').textContent = fmt(ST.min);
  $('now-btn').classList.toggle('hidden', ST.live);
  $('now-btn').textContent = T().now;
  $('dial-days').innerHTML = [0, 1, 2].map(d => `<button data-day="${d}" class="${d === ST.day ? 'on' : ''}">${esc(dayLabel(d))}</button>`).join('');
  $('dial-range').value = Math.round(ST.min);
  svg._geom = { cx, rx, st };
}
function dialToMin(clientX){
  const svg = $('dial-svg'), g = svg._geom, r = svg.getBoundingClientRect();
  const x = clientX - r.left, uu = Math.max(0, Math.min(1, (x - (g.cx - g.rx)) / (2 * g.rx)));
  const u = 1 - Math.acos(2 * uu - 1) / Math.PI;     // x = cx + rx·cos(θ), θ = π(1−u)
  return Math.round((g.st.rise + u * (g.st.set - g.st.rise)) / 5) * 5;
}
function setTime(min, day = ST.day){
  ST.day = day; ST.min = Math.max(0, Math.min(1439, min));
  ST.live = day === 0 && Math.abs(ST.min - nowMin()) < 3;
  render();
}
(() => {
  const svg = $('dial-svg'); let dragging = false;
  svg.addEventListener('pointerdown', e => {
    if (!e.target.closest('.knob') && !e.target.closest('.dial-hit')) return;
    dragging = true; ST.dragging = true; svg.setPointerCapture(e.pointerId); setTime(dialToMin(e.clientX)); e.preventDefault();
  });
  svg.addEventListener('pointermove', e => { if (dragging) setTime(dialToMin(e.clientX)); });
  const end = () => { if (!dragging) return; dragging = false; ST.dragging = false; render(); };
  svg.addEventListener('pointerup', end); svg.addEventListener('pointercancel', end);
  $('dial-days').addEventListener('click', e => { const b = e.target.closest('[data-day]'); if (!b) return; const d = +b.dataset.day; setTime(d === 0 ? nowMin() : (ST.day === 0 ? Math.max(ST.min, sunTimes(d).rise + 120) : ST.min), d); });
  $('now-btn').addEventListener('click', () => setTime(nowMin(), 0));
  $('dial-range').addEventListener('input', e => setTime(+e.target.value));
})();

// ─── Sheet: summary, cards, list ───────────────────────────────────────────
let LIST_N = 40, LIST_DIRTY = true;
const inView = v => { const b = map.getBounds(); return b.contains([v.lat, v.lng]); };
function streetInsight(vs){
  const st = sunTimes(), by = {};
  for (const v of vs) if (v.street && v._s.known) (by[v.street] ||= []).push(v);
  const streets = Object.entries(by).filter(([, a]) => a.length >= 5).sort((a, b) => b[1].length - a[1].length).slice(0, 4);
  const W = windows();
  const frac = (a, m) => a.filter(v => (W[v.i] || []).some(([s, e]) => m >= s && m < e)).length / a.length;
  const short = s => s.replace(/straße$/i, 'str.').replace(/strasse$/i, 'str.');
  for (const [name, a] of streets){
    if (frac(a, ST.min) < .34) continue;
    for (let m = ST.min + 5; m <= st.set; m += 5) if (frac(a, m) < .34) return T().shade_reaches(short(name), fmt(m));
  }
  if (streets[0]){ const [name, a] = streets[0]; for (let m = ST.min + 5; m <= st.set; m += 5) if (frac(a, m) >= .5) return T().lights_up(short(name), fmt(m)); }
  return ST.min < st.golden ? T().golden(fmt(st.golden), fmt(st.set)) : '';
}
function stripHTML(W, day = ST.day, nowMark = true){
  const st = sunTimes(day), a0 = Math.floor(st.rise / 60) * 60, a1 = Math.ceil(st.set / 60) * 60, span = a1 - a0, P = m => (Math.max(a0, Math.min(a1, m)) - a0) / span * 100;
  let h = (W || []).map(([a, b]) => `<i style="left:${P(a).toFixed(2)}%;width:${(P(b) - P(a)).toFixed(2)}%"></i>`).join('');
  if (WX.ok) for (let m = a0; m < a1; m += 60) if (isCloudy(m, day)) h += `<i class="cl" style="left:${P(m).toFixed(2)}%;width:${(60 / span * 100).toFixed(2)}%"></i>`;
  if (nowMark && ST.min >= a0 && ST.min <= a1) h += `<div class="now" style="left:${P(ST.min).toFixed(2)}%"></div>`;
  return { h, a0, a1 };
}
function rowHTML(v, ref){
  const s = v._s, d = distM(v, ref);
  const tag = s.sunny ? `☀ ${T().until(fmt(s.win[1]))}` : s.geo && s.cloudy ? `☁ ${T().until(fmt(s.win[1]))}` : s.next ? (isCloudy(s.next[0]) ? '☁ ' : '') + T().sun_at(fmt(s.next[0]), fmt(s.next[1])) : '';
  return `<button class="row" data-id="${esc(v.id)}">${snapHTML(v, 'sm')}<div class="row-main"><div class="row-top"><span class="nm">${esc(v.name)}</span><span class="tag ${s.sunny ? '' : 'off'}">${tag}</span></div>
    <div class="meta">${esc(typeOf(v))}${v.street ? ' · ' + esc(v.street) : ''} · ${T().walk(walkMin(d))}</div>
    ${s.known ? `<div class="strip">${stripHTML(s.W).h}</div>` : ''}</div></button>`;
}
function renderSheet(skipList){
  const ref = refPoint(), st = sunTimes(), t = T();
  const vis = FILTERED.filter(inView);
  const sunny = vis.filter(v => v._s.sunny);
  const cl = isCloudy(ST.min);
  let sum, cards;
  if (sunny.length){
    const ins = skipList ? ($('summary').querySelector('.ins')?.textContent || '') : streetInsight(vis);
    sum = `<div class="sum"><span class="n">${sunny.length}</span><span class="t">${t.sunny_here}</span><span class="ins">${ins ? '· ' + esc(ins) : ''}</span></div>`;
    cards = sunny.map(v => [v, distM(v, ref)]).sort((a, b) => a[1] - b[1]).slice(0, 12).map(([v, d]) =>
      `<button class="card" data-id="${esc(v.id)}">${snapHTML(v)}<div class="ct"><div class="nm">${esc(v.name)}</div><div class="ty">${esc(typeOf(v))}${v.roof ? ' · ' + t.rooftop : ''}</div><div class="st">${t.until(fmt(v._s.win[1]))}</div><div class="wk">${walkMin(d)} min · ${t.left(dur(v._s.left))}</div></div></button>`);
  } else {
    // Next sun: earliest upcoming cloud-free sunny minute among visible terraces
    let best = null;
    for (const v of vis){ for (const [a, b] of v._s.W){ if (b <= ST.min) continue; for (let m = Math.max(a, Math.ceil(ST.min / 5) * 5 + 5); m < b; m += 5){ if (!isCloudy(m)){ if (!best || m < best.m) best = { m }; break; } } } }
    const night = ST.min < st.rise || ST.min > st.set;
    const sub = cl ? t.overcast(clearsAt(ST.min) != null ? fmt(clearsAt(ST.min)) : null) : night ? t.after_sunset(fmt(st.set), fmt(st.rise)) : '';
    if (best){
      const later = vis.filter(v => v._s.W.some(([, b]) => b > best.m));
      sum = `<div class="sum"><span class="n">${fmt(best.m)}</span><span class="t">${t.next_sun_s}</span><span class="ins">· ${esc(sub || t.n_terraces(later.length))}</span></div>`;
      cards = later.map(v => [v, distM(v, ref)]).sort((a, b) => a[1] - b[1]).slice(0, 12).map(([v, d]) => {
        const w = v._s.W.find(([, b]) => b > best.m);
        const at = Math.max(w[0], best.m) + 10;
        return `<button class="card off" data-id="${esc(v.id)}">${snapHTML(v, '', `data-min="${at}"`)}<div class="ct"><div class="nm">${esc(v.name)}</div><div class="ty">${esc(typeOf(v))}</div><div class="st">${t.sun_at(fmt(Math.max(w[0], best.m)), fmt(w[1]))}</div><div class="wk">${t.walk(walkMin(d))}</div></div></button>`;
      });
    } else if (ST.day < 2){
      // Nothing left today → show tomorrow's first sun (geometry; clouds shown on the strip)
      const d1 = ST.day + 1, W1 = windows(d1);
      const tom = vis.map(v => [v, (W1[v.i] || []).find(([a, b]) => b - a >= 30), distM(v, ref)]).filter(e => e[1]);
      const first = tom.reduce((m, e) => Math.min(m, e[1][0]), Infinity);
      sum = `<div class="sum"><span class="n">${isFinite(first) ? fmt(first) : '—'}</span><span class="t">${t.first_sun_s(d1)}</span><span class="ins">${sub ? '· ' + esc(sub) : ''}</span></div>`;
      cards = tom.sort((a, b) => (a[1][0] - b[1][0]) || (a[2] - b[2])).slice(0, 12).map(([v, w, d]) =>
        `<button class="card off" data-id="${esc(v.id)}" data-day="${d1}" data-min="${w[0]}">${snapHTML(v, '', `data-day="${d1}" data-min="${w[0] + 10}"`)}<div class="ct"><div class="nm">${esc(v.name)}</div><div class="ty">${esc(typeOf(v))}</div><div class="st">${t.sun_at(fmt(w[0]), fmt(w[1]))}</div><div class="wk">${t.walk(walkMin(d))}</div></div></button>`);
    } else {
      sum = `<div class="sum"><span class="n">☾</span><span class="t">${t.no_more}</span><span class="ins">${sub ? '· ' + esc(sub) : ''}</span></div>`;
      cards = [];
    }
  }
  $('summary').innerHTML = sum;
  if (skipList) return;
  $('cards').innerHTML = cards.join('');
  paintSnaps($('cards'));
  // The list (40 rows + snapshots) is only built when it can be seen.
  if (innerWidth < 900 && $('sheet').dataset.state !== 'full'){ LIST_DIRTY = true; return; }
  LIST_DIRTY = false;
  // Full list: sunny first (closest first), then upcoming sun, then the rest
  const rank = v => v._s.sunny ? 0 : v._s.next ? 1 : 2;
  const rows = vis.map(v => [v, distM(v, ref)]).sort((a, b) => (rank(a[0]) - rank(b[0])) || (a[1] - b[1]));
  $('list').innerHTML = rows.length
    ? `<div class="list-h"><b>${t.list_h}</b><span>${t.list_sub(rows.length)}</span></div>` + rows.slice(0, LIST_N).map(([v]) => rowHTML(v, ref)).join('') + (rows.length > LIST_N ? `<button class="more" id="more">${t.more}</button>` : '')
    : `<div class="empty">${t.nothing}</div>`;
  paintSnaps($('list'));
}
$('sheet').addEventListener('click', e => {
  if (e.target.id === 'more'){ LIST_N += 60; renderSheet(); return; }
  const b = e.target.closest('[data-id]'); if (!b) return;
  const v = VEN.find(x => x.id === b.dataset.id); if (!v) return;
  if (b.dataset.day){ ST.day = +b.dataset.day; ST.min = +b.dataset.min + 10; ST.live = false; }
  openDetail(v);
});
// Sheet drag (mobile)
(() => {
  const sh = $('sheet'), grab = $('sheet-grab'); let y0 = null, st0;
  const set = s => { sh.dataset.state = s; document.body.dataset.sheet = s; if (s === 'full' && LIST_DIRTY) renderSheet(); };
  grab.addEventListener('click', () => set(sh.dataset.state === 'full' ? 'peek' : 'full'));
  grab.addEventListener('pointerdown', e => { y0 = e.clientY; st0 = sh.dataset.state; grab.setPointerCapture(e.pointerId); });
  grab.addEventListener('pointerup', e => { if (y0 == null) return; const dy = e.clientY - y0; y0 = null; if (Math.abs(dy) > 30) set(dy < 0 ? 'full' : 'peek'); });
  $('summary').addEventListener('click', () => { if (innerWidth < 900) set(sh.dataset.state === 'peek' ? 'full' : 'peek'); });
})();

// ─── Terrace page ──────────────────────────────────────────────────────────
function compass(az){ const deg = (az * 180 / Math.PI + 180 + 360) % 360; return T().dirs[Math.round(deg / 45) % 8]; }
function openDetail(v){
  ST.sel = v;
  $('detail').classList.add('open'); $('detail').setAttribute('aria-hidden', 'false');
  document.body.dataset.detail = '1';
  const z = Math.max(map.getZoom(), 16.5);
  const target = map.project([v.lat, v.lng], z);
  if (innerWidth < 900) target.y += map.getSize().y * 0.22;      // keep the terrace visible above the panel
  map.flyTo(map.unproject(target, z), z, { duration: .6 });
  history.replaceState(null, '', '?v=' + encodeURIComponent(v.id) + location.hash);
  render();
}
function closeDetail(){
  ST.sel = null; $('detail').classList.remove('open'); $('detail').setAttribute('aria-hidden', 'true'); delete document.body.dataset.detail;
  history.replaceState(null, '', location.pathname + location.hash); render();
}
$('detail-back').addEventListener('click', closeDetail);
function renderDetail(){
  const v = ST.sel, s = v._s, st = sunTimes(), t = T(), ref = refPoint();
  let state;
  if (!s.known) state = `<div class="d-state off"><div class="big">—</div><div class="sm">${LANG === 'de' ? 'Neu hier – Sonnendaten kommen mit dem nächsten Update.' : 'New here — sun data arrives with the next monthly update.'}</div></div>`;
  else if (s.sunny) state = `<div class="d-state"><div class="big">${t.sun_until(fmt(s.win[1]))}</div><div class="sm">${t.then_shade(dur(s.left), compass(sunPos(s.win[1]).azimuth))}</div></div>`;
  else if (s.geo && s.cloudy){ const c = clearsAt(ST.min); state = `<div class="d-state off"><div class="big">${t.sunny_cloudy}</div><div class="sm">${t.sunny_cloudy_sm(fmt(s.win[1]), c != null && c < s.win[1] ? fmt(c) : null)}</div></div>`; }
  else if (s.next) state = `<div class="d-state off"><div class="big">${t.sun_again(fmt(s.next[0]))}</div><div class="sm">${t.sun_again_sm(dur(s.next[1] - s.next[0]))}</div></div>`;
  else { const tot = s.W.reduce((a, [x, y]) => a + y - x, 0); state = `<div class="d-state off"><div class="big">${t.no_sun_more}</div><div class="sm">${tot ? t.had_sun(dur(tot)) : t.never} ${t.sunrise_at(fmt(sunTimes(ST.day + 1 <= 2 ? ST.day + 1 : ST.day).rise))}</div></div>`; }
  const strip = stripHTML(s.W);
  const ticks = []; const stepH = (strip.a1 - strip.a0) > 12 * 60 ? 240 : 180; for (let m = strip.a0; m <= strip.a1; m += stepH) ticks.push(`<span>${fmt(m)}</span>`);
  const longest = s.W.slice().sort((a, b) => (b[1] - b[0]) - (a[1] - a[0]))[0];
  const open = isOpen(v, tMs());
  const addr = [v.street, v.hn].filter(Boolean).join(' ');
  const facts = [];
  if (v.hoursStr) facts.push(`<div><span>${t.hours}</span><span>${open === true ? `<b style="color:#2E7D32">${t.open_now}</b> · ` : open === false ? `<b style="color:#B3261E">${t.closed_now}</b> · ` : ''}${esc(v.hoursStr)}</span></div>`);
  if (addr) facts.push(`<div><span>${t.address}</span><span>${esc(addr)}</span></div>`);
  if (v.web) facts.push(`<div><span>${t.website}</span><span><a href="${esc(/^https?:/.test(v.web) ? v.web : 'https://' + v.web)}" target="_blank" rel="noopener">${esc(v.web.replace(/^https?:\/\/(www\.)?/, '').replace(/\/$/, ''))}</a></span></div>`);
  $('detail-body').innerHTML = `
    <button class="d-fav ${FAV.has(v.id) ? 'on' : ''}" id="d-fav" aria-label="${t.saved}">${FAV.has(v.id) ? '★' : '☆'}</button>
    <div class="d-hero" id="d-hero">${snapHTML(v, 'hero', 'data-z="17.3"')}<span class="d-hero-lab">${esc(t.snap_lab(fmt(ST.min)))}</span></div>
    <h2 class="d-name">${esc(v.name)}</h2>
    <div class="d-meta">${esc(typeOf(v))}${v.cuisine ? ' · ' + esc(v.cuisine) : ''}${v.roof ? ' · ' + t.rooftop : ''} · ${t.walk(walkMin(distM(v, ref)))}</div>
    ${state}
    ${s.known ? `<div class="d-lab">${esc(t.ribbon_lab(dayLabel(ST.day)))}</div><div class="ribbon">${strip.h}</div><div class="axis">${ticks.join('')}</div>
    <div class="d-best">${longest ? t.windows_n(s.W.length) + t.longest(fmt(longest[0]), fmt(longest[1]), dur(longest[1] - longest[0])) : t.try_other} ${t.sunset(fmt(st.set))}</div>` : ''}
    <div class="d-facts">${facts.join('')}</div>
    <div class="d-cta"><a class="go" href="https://www.google.com/maps/dir/?api=1&destination=${v.lat},${v.lng}" target="_blank" rel="noopener">${t.directions} · ${walkMin(distM(v, ref))} min</a><button class="sh" id="d-share" aria-label="Share">↗</button></div>`;
  paintSnaps($('detail-body'));
  if (hasPhotoTags(v)) photoFor(v).then(ph => {
    if (!ph || ST.sel !== v) return;
    const hero = $('d-hero'); if (!hero || hero.dataset.photo) return;
    hero.dataset.photo = '1';
    hero.insertAdjacentHTML('afterbegin', `<img class="d-photo" src="${esc(ph.src)}" alt="${esc(v.name)}" loading="lazy">`);
    hero.querySelector('canvas.snap').classList.add('inset'); paintSnaps(hero);
    hero.insertAdjacentHTML('beforeend', `<a class="d-credit" href="${esc(ph.href)}" target="_blank" rel="noopener">${esc(T().photo)}: ${esc(ph.credit)}</a>`);
  });
}
$('detail').addEventListener('click', async e => {
  const v = ST.sel; if (!v) return;
  if (e.target.closest('#d-fav')){ FAV.has(v.id) ? FAV.delete(v.id) : FAV.add(v.id); store.set('favs', [...FAV]); render(); }
  if (e.target.closest('#d-share')){
    const url = `${location.origin}${location.pathname}?v=${encodeURIComponent(v.id)}`;
    try { if (navigator.share) await navigator.share({ title: v.name, url }); else { await navigator.clipboard.writeText(url); toast(T().share_copied); } } catch {}
  }
});

// ─── Search ────────────────────────────────────────────────────────────────
const norm = s => (s || '').toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '');
function openSearch(){ $('search').classList.add('open'); $('search').setAttribute('aria-hidden', 'false'); $('search-input').placeholder = T().search_ph; setTimeout(() => $('search-input').focus(), 60); renderSearch(); }
function closeSearch(){ $('search').classList.remove('open'); $('search').setAttribute('aria-hidden', 'true'); $('search-input').blur(); }
function renderSearch(){
  const q = norm($('search-input').value.trim()), ref = refPoint();
  if (!q){ $('search-results').innerHTML = ''; return; }
  const hits = VEN.filter(v => norm(v.name).includes(q) || norm(v.street).includes(q) || norm(v.cuisine).includes(q))
    .map(v => [v, (norm(v.name).startsWith(q) ? 0 : 1), distM(v, ref)]).sort((a, b) => a[1] - b[1] || a[2] - b[2]).slice(0, 40);
  $('search-results').innerHTML = hits.length ? hits.map(([v]) => rowHTML(v, ref)).join('') : `<div class="empty">${T().search_none}</div>`;
  paintSnaps($('search-results'));
}
$('search-open').addEventListener('click', openSearch);
$('search-close').addEventListener('click', closeSearch);
$('search-input').addEventListener('input', renderSearch);
$('search-results').addEventListener('click', e => { const b = e.target.closest('[data-id]'); if (!b) return; const v = VEN.find(x => x.id === b.dataset.id); closeSearch(); if (v) openDetail(v); });

// ─── Misc controls ─────────────────────────────────────────────────────────
function toast(msg){ const el = $('toast'); el.textContent = msg; el.classList.add('show'); clearTimeout(el._t); el._t = setTimeout(() => el.classList.remove('show'), 2600); }
$('lang-toggle').addEventListener('click', () => {
  LANG = LANG === 'de' ? 'en' : 'de'; store.set('lang', LANG); document.documentElement.lang = LANG;
  if (location.pathname === '/' || /^\/de\/?$/.test(location.pathname)) history.replaceState(null, '', (LANG === 'de' ? '/de/' : '/') + location.search + location.hash);
  render();
});
$('locate').addEventListener('click', () => {
  if (ST.user){ ST.user = null; $('locate').classList.remove('on'); render(); return; }
  if (!navigator.geolocation){ toast(T().loc_fail); return; }
  toast(T().locating);
  navigator.geolocation.getCurrentPosition(p => {
    const ll = [p.coords.latitude, p.coords.longitude];
    if (!BOUNDS.contains(ll)){ toast(T().out_of_area); return; }
    ST.user = ll; $('locate').classList.add('on'); map.flyTo(ll, Math.max(map.getZoom(), 16), { duration: .6 }); render();
  }, () => toast(T().loc_fail), { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 });
});
map.on('moveend', () => { store.set('view', { c: [map.getCenter().lat, map.getCenter().lng], z: map.getZoom() }); render(); });
window.__hoursReady = () => render();
window.__sm = { ST, setTime, openDetail, closeDetail, render, VEN: () => VEN, map,
  bench(n = 20){ const out = {}; const t = (k, f) => { const a = performance.now(); f(); out[k] = (out[k] || 0) + performance.now() - a; };
    for (let i = 0; i < n; i++){ ST.min += 5; t('states', computeStates); t('filters', applyFilters); t('shadows', () => shadowLayer.repaint()); t('dots', () => venueLayer._render()); t('dial', renderDial); t('chips', renderChips); t('sheet', () => renderSheet(true)); }
    for (const k in out) out[k] = +(out[k] / n).toFixed(1); return out; } };   // handy for debugging in the console
document.addEventListener('keydown', e => { if (e.key === 'Escape'){ if ($('search').classList.contains('open')) closeSearch(); else if (ST.sel) closeDetail(); } });
// Live clock
setInterval(() => {
  const rolled = refreshDay();
  if (ST.live || rolled){ if (ST.live) ST.min = nowMin(); render(); }
}, 30000);

// ═════════════════════════════════════════════════════════════════════════
//  Boot
// ═════════════════════════════════════════════════════════════════════════
(async () => {
  document.documentElement.lang = LANG;
  document.body.dataset.sheet = 'peek';
  const [pj] = await Promise.all([window.__places || fetch('/data/places.json').then(r => r.ok ? r.json() : null).catch(() => null), loadShadowIndex()]);
  if (pj && pj.p && pj.hz){
    // places.json: one compact file with terrace positions + horizon profiles
    HZ = pj.hz;
    VEN = pj.p.map(([id, name, lat, lng, a, cuisine, street, hn, hours, web, roof, img, commons, wd, hz]) => {
      const [x0, y0] = P0(lat, lng);
      return { id, name, lat, lng, x0, y0, a, cuisine: (cuisine || '').split(';')[0].replace(/_/g, ' '), street, hn, hoursStr: hours, web,
        roof: !!roof, img, commons, wd, hz: hz == null ? null : decodeD64(hz, HZ.bins) };
    });
  } else {
    // Legacy files (until the data job has produced places.json)
    const [vj, hz, rt] = await Promise.all([
      fetch('/data/venues.json').then(r => r.json()),
      fetch('/data/horizons.json').then(r => r.ok ? r.json() : null).catch(() => null),
      fetch('/data/rooftops-today.json').then(r => r.ok ? r.json() : null).catch(() => null),
    ]);
    VEN = parseVenues(vj);
    const roofs = new Set(rt?.ids || []);
    HZ = hz;
    VEN.forEach(v => { v.roof = roofs.has(v.id); v.hz = HZ && v.id in HZ.h ? decodeHorizon(HZ.h[v.id], HZ.bins) : null; });
  }
  VEN.forEach((v, i) => { v.i = i; });
  for (const k in WIN) delete WIN[k];
  VBY = new Map(VEN.map(v => [v.id, v]));
  render();
  $('loading').classList.add('done');
  loadWeather().then(render);
  const params = new URLSearchParams(location.search);
  const q = params.get('v');
  if (q){ const v = VEN.find(x => x.id === q); if (v) openDetail(v); }
  if (params.get('q')){ openSearch(); $('search-input').value = params.get('q'); renderSearch(); }   // sitelinks search box
})().catch(err => { console.error(err); $('loading').innerHTML = '<p style="padding:24px;text-align:center">Could not load Berlin’s terraces. Please reload.</p>'; });
})();
