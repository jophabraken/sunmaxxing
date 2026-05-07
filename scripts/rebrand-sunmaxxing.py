#!/usr/bin/env python3
"""
Rebrand pass: 'Sonne Berlin' → 'Sunmaxxing'.

Strategy:
- Brand placement (og:site_name, JSON-LD name, footer, nav aria-labels, etc.):
  blanket replace "Sonne Berlin" → "Sunmaxxing".
- Visible wordmark in topbar / header (the stylized "sonne berlin" with the
  italic first word) gets a structural swap to "sun maxxing" so the same
  italic-first-word visual treatment carries over to the new brand.
- Lowercase "sonne berlin" inside <span class="sonne">sonne</span>
  <span>berlin</span> (or <span class="berlin">berlin</span>) wordmarks gets
  the same treatment.
- The homepage <title> gets a hand-crafted SEO descriptor lead.
- The homepage SEO footer blurb keeps "Sunmaxxing is..." (descriptive,
  changes the subject from brand-as-product to brand-as-app).

What this script does NOT touch:
- README.md and docs/ (internal — not user-facing SERP content)
- Python generators (handled separately so future regenerations stay clean)
- favicon.svg (handled separately if it has text)
- service-worker cache prefix `sonne-*` (internal — renaming would invalidate
  caches and force re-downloads; not worth the churn)
"""
import re
import sys
from pathlib import Path

ROOT = Path("/sessions/nice-inspiring-cerf/work")

# Files to process: all .html under work/, excluding docs and node_modules
HTML_FILES = sorted([
    p for p in ROOT.glob("**/*.html")
    if "node_modules" not in p.parts
    and "docs" not in p.parts
])

# Track diffs for reporting
changes = []  # list of (path, count, before_sample, after_sample)

# ---- WORDMARK STRUCTURAL SWAPS (do these first, before blanket replace) ----
# These handle the stylized lowercase wordmark "sonne berlin" with various
# span structures. We replace with "sun maxxing" using the same span scaffolding
# so the italic-first-word visual treatment carries to the new brand.

WORDMARK_PATTERNS = [
    # Pattern: <span class="sonne">sonne</span> <span>berlin</span>
    (
        r'<span class="sonne">sonne</span>\s*<span>berlin</span>',
        '<span class="sonne">sun</span><span>maxxing</span>'
    ),
    # Pattern: <span class="sonne">sonne</span> <span class="berlin">berlin</span>
    (
        r'<span class="sonne">sonne</span>\s*<span class="berlin">berlin</span>',
        '<span class="sonne">sun</span><span class="berlin">maxxing</span>'
    ),
    # Pattern: brand-text on the live map homepage:
    # <div class="brand-text">Sonne <em>Berlin</em></div>
    (
        r'<div class="brand-text">Sonne <em>Berlin</em></div>',
        '<div class="brand-text">sun<em>maxxing</em></div>'
    ),
]

# ---- BRAND-NAME BLANKET REPLACE ----
# After wordmarks are taken care of, every remaining "Sonne Berlin" is a
# brand-name placement (og:site_name, JSON-LD name, footer credit,
# title-tag suffix, body copy) and should become "Sunmaxxing".
BRAND_REPLACE = [
    # Footer credit phrasing
    ("Built by Sonne Berlin", "Built by Sunmaxxing"),
    # Generic
    ("Sonne Berlin", "Sunmaxxing"),
]

# ---- HOMEPAGE TITLE / META: hand-crafted SEO descriptor lead ----
# Only applied to the top-level homepage (work/index.html).
HOMEPAGE_OVERRIDES = [
    (
        "<title>Sonne Berlin — find the sunniest terrace, right now</title>",
        "<title>Sunmaxxing — Find the sun in Berlin | Sunniest terraces, right now</title>",
    ),
    # Note: some og/twitter title strings already get caught by the blanket
    # "Sonne Berlin" → "Sunmaxxing" replace above. Those are fine.
]

# Run pass --------------------------------------------------------------
for path in HTML_FILES:
    rel = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8")
    original = text
    file_changes = 0

    # 1. Wordmark structural swaps
    for pattern, replacement in WORDMARK_PATTERNS:
        new_text, n = re.subn(pattern, replacement, text)
        if n > 0:
            text = new_text
            file_changes += n

    # 2. Homepage-specific overrides
    if path == ROOT / "index.html":
        for old, new in HOMEPAGE_OVERRIDES:
            if old in text:
                text = text.replace(old, new)
                file_changes += 1

    # 3. Brand-name blanket replace
    for old, new in BRAND_REPLACE:
        count = text.count(old)
        if count > 0:
            text = text.replace(old, new)
            file_changes += count

    if text != original:
        path.write_text(text, encoding="utf-8")
        changes.append((str(rel), file_changes))

# Print report
print(f"\nRebrand complete. Updated {len(changes)} file(s).\n")
total = 0
for rel, n in changes:
    print(f"  {rel:<60} {n:>4} change(s)")
    total += n
print(f"\nTotal replacements: {total}")
