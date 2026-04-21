"""
Render the Open Graph share card for sunmaxxing.com.

Output: og-image.png (1200x630, the FB/X/LinkedIn/Telegram/WhatsApp standard).
The preview is the single most important visual asset for a share-driven
product — 3–10x more click-through vs. unbranded link previews — so we spend
real care on it.

Design intent: warm sunset gradient that evokes an afternoon terrace; product
name in a confident display serif italic; tagline in a clean sans; the domain
small and self-effacing. One decorative sun in the corner, not the whole card.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

W, H = 1200, 630
OUT  = os.path.join(os.path.dirname(__file__), '..', 'og-image.png')

# Palette — lifted from the site's :root CSS vars so the card sits in-brand.
SUN         = (245, 166,  35)  # --sun
SUN_BRIGHT  = (255, 182,  39)  # --sun-bright
SUN_BG      = (255, 244, 214)  # --sun-bg
CORAL       = (255, 107,  87)  # --coral
BG_WARM     = (251, 247, 239)  # --bg
INK         = ( 22,  24,  34)  # --text
INK_SOFT    = (107, 114, 128)  # --muted

FONT_DIR = '/usr/share/fonts/truetype/google-fonts'
F_SERIF_ITALIC = os.path.join(FONT_DIR, 'Lora-Italic-Variable.ttf')
F_BOLD         = os.path.join(FONT_DIR, 'Poppins-Bold.ttf')
F_MEDIUM       = os.path.join(FONT_DIR, 'Poppins-Medium.ttf')
F_REGULAR      = os.path.join(FONT_DIR, 'Poppins-Regular.ttf')

img = Image.new('RGB', (W, H), BG_WARM)
d   = ImageDraw.Draw(img)

# Diagonal sunset gradient (warm white → sun orange), painted as horizontal
# strips with per-pixel alpha blending so it reads like real sunset light.
def lerp(a, b, t): return tuple(int(a[i] + (b[i]-a[i])*t) for i in range(3))
for y in range(H):
    # Vertical fade, plus a soft warm push toward the right-bottom.
    t = y / H
    col = lerp(BG_WARM, (255, 227, 178), t ** 1.4)
    d.line([(0, y), (W, y)], fill=col)

# Radial sun glow, top-right — built as a separate alpha layer and composited
# so we get a soft photographic bloom instead of a hard disc.
glow = Image.new('RGBA', (W, H), (0,0,0,0))
gd   = ImageDraw.Draw(glow)
cx, cy, rmax = 1050, 180, 420
for r in range(rmax, 0, -6):
    a = int(180 * (1 - r/rmax) ** 2.4)
    gd.ellipse((cx-r, cy-r, cx+r, cy+r), fill=(*SUN_BRIGHT, a))
glow = glow.filter(ImageFilter.GaussianBlur(radius=14))
img = Image.alpha_composite(img.convert('RGBA'), glow).convert('RGB')
d = ImageDraw.Draw(img)

# Crisp solid sun disc inside the glow.
d.ellipse((cx-95, cy-95, cx+95, cy+95), fill=SUN_BRIGHT)
# Subtle ring halo for a more editorial feel.
for r, a in [(130, 55), (170, 32), (210, 18)]:
    d.ellipse((cx-r, cy-r, cx+r, cy+r), outline=(*SUN, a), width=2)

# Berlin-silhouette accent in the bottom-right: Fernsehturm + rooflines. A
# short geometric evocation, not a literal skyline — keeps it readable at
# share-preview thumbnail sizes (where most people actually see this).
base_y = H - 90
def rect(x, y, w, h, col): d.rectangle((x, y, x+w, y+h), fill=col)
DARK = (47, 38, 25)  # warm near-black that sits in the sunset palette
# Left cluster of rooftop-bar buildings
rect(720, base_y-55, 90, 55, DARK)
rect(815, base_y-40, 70, 40, DARK)
rect(890, base_y-80, 55, 80, DARK)
rect(950, base_y-48, 45, 48, DARK)
# Fernsehturm (simplified)
rect(1018, base_y-170, 8, 170, DARK)                       # mast
d.ellipse((1003, base_y-200, 1041, base_y-162), fill=DARK) # ball
rect(1007, base_y-165, 30, 165, DARK)                      # shaft stub
# Right cluster
rect(1055, base_y-60, 50, 60, DARK)
rect(1110, base_y-35, 70, 35, DARK)
# Horizon strip pulls the skyline together
d.rectangle((0, base_y, W, H), fill=DARK)

# ─── Typography ────────────────────────────────────────────────────────────
# Wordmark: serif italic "sonne" + bold sans "berlin" — matches the H1 in the
# site itself ("Sonne *Berlin*") so the share card and the landing page feel
# like the same object.
PAD_L = 70
y = 160

font_sonne   = ImageFont.truetype(F_SERIF_ITALIC, 150)
font_berlin  = ImageFont.truetype(F_BOLD, 140)

w_sonne, _ = d.textbbox((0,0), 'sonne', font=font_sonne)[2:]
d.text((PAD_L, y), 'sonne', font=font_sonne, fill=INK)
d.text((PAD_L + w_sonne + 18, y+6), 'berlin', font=font_berlin, fill=INK)

# Tagline — short, product-value-first, keyword-rich but not stuffy.
font_tag = ImageFont.truetype(F_MEDIUM, 44)
d.text((PAD_L, y + 190), 'Find the sunniest terrace in Berlin,', font=font_tag, fill=INK)
d.text((PAD_L, y + 246), 'right now.',                           font=font_tag, fill=INK)

# Sun-pill accent next to the domain — mirrors the site's yellow accent and
# gives people a visual cue that there IS a sun element, not just text.
pill_x, pill_y = PAD_L, H - 90
pill_w, pill_h = 240, 48
d.rounded_rectangle((pill_x, pill_y, pill_x+pill_w, pill_y+pill_h),
                    radius=24, fill=SUN_BRIGHT)
font_url = ImageFont.truetype(F_BOLD, 22)
d.text((pill_x + 22, pill_y + 11), 'sunmaxxing.com', font=font_url, fill=INK)

# Quiet trust signal — anchors the brand in reality. "Live Berlin weather
# + shadow tracking" is the actual product diff vs. a generic list site.
font_meta = ImageFont.truetype(F_REGULAR, 18)
d.text((pill_x + pill_w + 16, pill_y + 16),
       'live weather + shadow tracking',
       font=font_meta, fill=INK_SOFT)

img.save(OUT, 'PNG', optimize=True)
print(f'Wrote {OUT} — {os.path.getsize(OUT)} bytes')
