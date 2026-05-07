# ZOEY — Listicle template

Reference template for new `/best-X-berlin/` style pages. Match the conventions used in `/best-rooftops-berlin/index.html` and `/best-beer-gardens-berlin/index.html` — do not reinvent.

## Directory

Every listicle lives at `/<slug>/index.html`. DE variants at `/de/<slug>/index.html`.

## File structure (follow exactly)

```
1. <!DOCTYPE html> + <head>
   - <title> must include "(Live-Tracked for Sun)" or a variant. Keep brand "Sunmaxxing" at the end.
   - <meta name="description"> — 150-160 chars. Must include the primary keyword and a sun-angle hook.
   - <link rel="canonical">
   - OG + Twitter meta (reuse the exact structure from beer-gardens page)
   - 4 JSON-LD blocks: Article, ItemList (BarOrPub), BreadcrumbList, FAQPage
   - hreflang pair: <link rel="alternate" hreflang="en" href="..."> + <link rel="alternate" hreflang="de" href="...">
   - <link rel="alternate" hreflang="x-default" href="https://sunmaxxing.com/"> (EN page points to root)

2. Inline <style> — reuse the shared styles. If the page needs anything custom, keep it scoped.

3. <body>
   - <header> with back-to-app link
   - <article>
     - <h1>
     - Intro paragraph (2-3 sentences, mentions sun + Berlin + the specific category)
     - Live-app CTA block ("See the real-time sun map →" linking to /)
     - Numbered list (1 through N) — each venue is an <h2> with:
       · the name
       · address + neighborhood as <address>
       · 50-100 word blurb (ZOEY's voice — see rules below)
       · "Sun profile" line — afternoon/morning/west-facing/covered
     - FAQ section (matches the FAQPage JSON-LD entries 1:1)
   - <footer> with brand + links back to app

4. No external JS. No analytics beyond the Cloudflare snippet already in the main app — don't add it here.
```

## Content rules (ZOEY's voice)

- **Specific > generic.** "Chestnut trees start shading the east side at 5pm" beats "great for sunny afternoons."
- **Cross-check every claim against our live data** before publishing. If the page says "Zollpackhof catches afternoon sun," the live map at `state.selectedTimeMs = 15:00 UTC+2` should agree.
- **No superlatives without substance.** "The best" needs a reason tied to sun, location, or a specific feature — not vibes.
- **Never bury the sun-angle hook.** Every blurb should answer "when does this place have sun?" in the first 2 sentences.
- **Never invent facts.** If you don't know the opening hours, leave them out — don't guess.
- **Word count:** ~80-120 words per venue. 10 venues = ~1,000 words. Plus ~150-word intro + 4-5 FAQ entries = ~1,500-1,800 words total. This is the sweet spot.
- **Internal links:** Every listicle should have at least 3 internal links to other listicles in the cluster, plus 1 to the live map, plus 1 to the DE/EN hreflang pair.

## DE voice rules (specific to German pages)

- Use "Du" form, not "Sie." We are a consumer-facing summer site, not a law firm.
- Berlin-specific German is fine and preferred — "Biergarten" (not "Bierlokal"), "Draußensitzen" (not "Außengastronomie").
- Don't translate place names or dish names that Berliners keep in English or loan-words. "Rooftop Bar" stays "Rooftop Bar" in German.
- Do not auto-translate the EN page. Write fresh for DE, using the same venue list and facts, but restructured for what a DE resident would ask (lean more toward practical: opening hours, reservations, BVG access).

## JSON-LD rules

- Article.datePublished: the date ZOEY ships it (real date, not placeholder).
- Article.dateModified: update every time ZOEY refreshes the page.
- ItemList: one BarOrPub (or Restaurant/CafeOrCoffeeShop depending on category) per venue, with proper address schema.
- FAQPage: 4-6 questions that real searchers ask. Copy the question patterns from Google's "People Also Ask" for the target keyword.
- BreadcrumbList: always 2 items — "Sunmaxxing" → page title.

## Pre-publish checklist

Before committing the new page, ZOEY must verify:
- [ ] Title contains primary keyword
- [ ] Meta description 150-160 chars, contains primary keyword
- [ ] Canonical URL matches the URL it'll live at
- [ ] hreflang pair points to the correct DE/EN counterpart (or x-default if the pair isn't shipped yet)
- [ ] All 4 JSON-LD blocks validate (no trailing commas, valid @type)
- [ ] Every venue mentioned also exists in the live `state.venues` data (name-match, not strict ID-match — these are curated venues)
- [ ] Every venue blurb has a sun-angle sentence
- [ ] At least 3 internal links to other listicles in the cluster
- [ ] FAQ JSON-LD questions match the FAQ section headings 1:1
- [ ] Page weight stays under 50KB HTML (we aim for fast Core Web Vitals)

## After-publish checklist

- [ ] Append row to `/docs/zoey-content-calendar.md` "Shipped log" table
- [ ] Mark keyword row in `/docs/zoey-keywords.md` as `shipped` with today's date
- [ ] Commit with message: `seo: ship /<slug>/ — target "<primary keyword>" (vol ~N, KD N)`
- [ ] Note in today's brief which page went live and why
- [ ] Add internal link TO this new page from at least 1 existing listicle in the same cluster
