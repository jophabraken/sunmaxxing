#!/usr/bin/env bash
# Build tiles/berlin.pmtiles — a self-hosted Protomaps (OpenStreetMap) vector
# basemap covering the site's venue bbox. One-off: the result is committed and
# served by Cloudflare Pages; rebuild only if you want fresher street data.
#
# Needs the `pmtiles` CLI:  brew install pmtiles   (macOS)
#                           or https://github.com/protomaps/go-pmtiles/releases
#
# Cloudflare Pages caps files at 25 MiB, so we try maxzoom 15 → 14 → 13 and
# keep the first that fits; index.html's maxDataZoom is updated to match
# (the renderer overzooms vector tiles past that, so the map stays sharp).
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
BBOX="13.17,52.40,13.64,52.61"   # venue bbox (data/manifest.json → bbox) + margin
LIMIT=$((24 * 1024 * 1024))

command -v pmtiles >/dev/null || { echo "pmtiles CLI not found — run: brew install pmtiles"; exit 1; }

# Newest Protomaps daily planet build (they keep the last few days).
SRC=""
for i in $(seq 0 20); do
  if date -v-1d >/dev/null 2>&1; then d=$(date -u -v-"${i}"d +%Y%m%d)    # macOS
  else d=$(date -u -d "-$i day" +%Y%m%d); fi                             # Linux
  if curl -sfI "https://build.protomaps.com/$d.pmtiles" >/dev/null; then
    SRC="https://build.protomaps.com/$d.pmtiles"; break
  fi
done
[ -n "$SRC" ] || { echo "No Protomaps daily build found"; exit 1; }
echo "source: $SRC"

mkdir -p "$REPO/tiles"
for z in 15 14 13; do
  rm -f "$REPO/tiles/berlin.pmtiles"
  pmtiles extract "$SRC" "$REPO/tiles/berlin.pmtiles" --bbox="$BBOX" --maxzoom=$z
  size=$(wc -c < "$REPO/tiles/berlin.pmtiles" | tr -d ' ')
  echo "maxzoom $z → $size bytes"
  if [ "$size" -le "$LIMIT" ]; then
    perl -pi -e "s/maxDataZoom: \d+,/maxDataZoom: $z,/" "$REPO/index.html"
    printf '{"source":"%s","maxzoom":%s,"bbox":"%s","bytes":%s,"builtAt":"%s"}\n' \
      "$SRC" "$z" "$BBOX" "$size" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$REPO/tiles/meta.json"
    echo "✓ tiles/berlin.pmtiles ready (maxzoom $z)"
    exit 0
  fi
done
echo "Basemap extract too large even at maxzoom 13"; exit 1
