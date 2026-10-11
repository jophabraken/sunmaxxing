#!/usr/bin/env node
// Explode a PMTiles archive into static /{z}/{x}/{y}.pbf files (uncompressed
// MVT). Static tiles need no HTTP range requests — Cloudflare Pages answers a
// range request on an uncached file with the full body, which breaks PMTiles
// for the first visitor at every edge location.
//   node scripts/pmtiles-to-zxy.js tiles/berlin.pmtiles tiles
const fs = require('node:fs');
const path = require('node:path');
const zlib = require('node:zlib');
const { PMTiles } = require('pmtiles');

class FileSource {
  constructor(p){ this.fd = fs.openSync(p, 'r'); this.p = p; }
  getKey(){ return this.p; }
  async getBytes(offset, length){
    const b = Buffer.alloc(length);
    fs.readSync(this.fd, b, 0, length, offset);
    return { data: b.buffer.slice(b.byteOffset, b.byteOffset + length) };
  }
}

(async () => {
  const [src, outDir] = process.argv.slice(2);
  const pm = new PMTiles(new FileSource(src));
  const h = await pm.getHeader();
  const lon2x = (lon, z) => Math.floor((lon + 180) / 360 * 2 ** z);
  const lat2y = (lat, z) => { const r = lat * Math.PI / 180; return Math.floor((1 - Math.log(Math.tan(r) + 1 / Math.cos(r)) / Math.PI) / 2 * 2 ** z); };
  let n = 0, bytes = 0;
  for (let z = h.minZoom; z <= h.maxZoom; z++){
    for (let x = lon2x(h.minLon, z); x <= lon2x(h.maxLon, z); x++){
      for (let y = lat2y(h.maxLat, z); y <= lat2y(h.minLat, z); y++){
        const t = await pm.getZxy(z, x, y);
        if (!t) continue;
        let data = Buffer.from(t.data);
        if (data[0] === 0x1f && data[1] === 0x8b) data = zlib.gunzipSync(data);
        const dir = path.join(outDir, String(z), String(x));
        fs.mkdirSync(dir, { recursive: true });
        fs.writeFileSync(path.join(dir, `${y}.pbf`), data);
        n++; bytes += data.length;
      }
    }
  }
  console.log(`wrote ${n} tiles, ${(bytes / 1048576).toFixed(1)} MB, z${h.minZoom}–${h.maxZoom}`);
})().catch(e => { console.error(e); process.exit(1); });
