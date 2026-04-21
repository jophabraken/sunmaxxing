"""
Render apple-touch-icon.png — the 180x180 PNG iOS uses for Home Screen
bookmarks and some Android launchers. Same sun glyph as favicon.svg, but
rasterized so iOS doesn't cache a fallback Safari compass over our brand.
"""
from PIL import Image, ImageDraw
import math, os

SIZE = 180
R_BG = SIZE // 2
CENTER = (SIZE // 2, SIZE // 2)

SUN_BG      = (255, 244, 214)
SUN_BRIGHT  = (255, 182,  39)
SUN         = (245, 166,  35)

img = Image.new('RGBA', (SIZE, SIZE), (0,0,0,0))
d   = ImageDraw.Draw(img)

# Rounded-square backdrop — iOS masks to squircle anyway, so fill edge-to-edge.
d.ellipse((0, 0, SIZE-1, SIZE-1), fill=SUN_BG)

# 8 sun rays at 45° increments, drawn as rounded rectangles.
cx, cy = CENTER
inner_r, outer_r = 56, 74
for i in range(8):
    theta = math.radians(i * 45)
    x1, y1 = cx + math.cos(theta) * inner_r, cy + math.sin(theta) * inner_r
    x2, y2 = cx + math.cos(theta) * outer_r, cy + math.sin(theta) * outer_r
    d.line([(x1, y1), (x2, y2)], fill=SUN, width=9)

# Sun disc.
r = 35
d.ellipse((cx-r, cy-r, cx+r, cy+r), fill=SUN_BRIGHT, outline=SUN, width=3)

out = os.path.join(os.path.dirname(__file__), '..', 'apple-touch-icon.png')
img.save(out, 'PNG', optimize=True)
print(f'Wrote {out} — {os.path.getsize(out)} bytes')
