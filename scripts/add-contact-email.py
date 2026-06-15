#!/usr/bin/env python3
"""
Add jophabraken@gmail.com contact link to all listicle/neighborhood page footers.

Patterns:
- EN pages: '<p>Built by <a href="/">Sunmaxxing</a> · ...</p>' → append '· <a href="mailto:jophabraken@gmail.com">Contact</a>'
- DE pages: '<p>Gebaut von <a href="/de/">Sunmaxxing</a> · ...</p>' → append '· <a href="mailto:jophabraken@gmail.com">Kontakt</a>'

Homepage (index.html) is handled separately because it uses a different
seo-footer structure (link list + blurb), and gets a dedicated Contact
section in the SEO content.
"""
import re
from pathlib import Path

ROOT = Path("/sessions/nice-inspiring-cerf/work")

EN_PATTERN = re.compile(
    r'(<p>Built by <a href="/">Sunmaxxing</a>[^<]*<a[^>]*>[^<]*</a>)\s*</p>',
    re.IGNORECASE
)
DE_PATTERN = re.compile(
    r'(<p>Gebaut von <a href="/de/">Sunmaxxing</a>[^<]*<a[^>]*>[^<]*</a>)\s*</p>',
    re.IGNORECASE
)

EN_REPLACEMENT = r'\1 · <a href="mailto:jophabraken@gmail.com">Contact</a></p>'
DE_REPLACEMENT = r'\1 · <a href="mailto:jophabraken@gmail.com">Kontakt</a></p>'

changes = []
for path in sorted(ROOT.glob("**/*.html")):
    # Skip homepage — handled separately
    if path == ROOT / "index.html":
        continue
    if "node_modules" in path.parts:
        continue
    text = path.read_text(encoding="utf-8")
    original = text

    # Skip if already has the contact link
    if 'mailto:jophabraken@gmail.com' in text:
        continue

    new_text, en_n = EN_PATTERN.subn(EN_REPLACEMENT, text)
    text = new_text
    new_text, de_n = DE_PATTERN.subn(DE_REPLACEMENT, text)
    text = new_text

    if text != original:
        path.write_text(text, encoding="utf-8")
        changes.append((str(path.relative_to(ROOT)), en_n + de_n))

print(f"Added contact link to {len(changes)} files:\n")
for rel, n in changes:
    print(f"  {rel}")
