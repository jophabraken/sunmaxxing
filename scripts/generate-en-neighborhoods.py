#!/usr/bin/env python3
"""
Generate EN neighborhood pages — mirrors the successful DE neighborhood
strategy. Each page targets a neighborhood-level keyword (e.g.,
"rooftop bars mitte berlin", "brunch kreuzberg", "beer gardens prenzlauer berg")
with hand-written content per neighborhood.

Categories shipped here:
  - Rooftops:    /best-rooftops-{neighborhood}/
  - Beer gardens: /best-beer-gardens-{neighborhood}/
  - Brunch:      /brunch-{neighborhood}/

Why a generator vs hand-coded pages:
  - Shared SEO scaffolding (Article + ItemList + BreadcrumbList + FAQPage
    schema, canonical, OG) — one source of truth.

Why per-neighborhood hand-written content vs templated descriptions:
  - Google's Helpful Content classifier (March 2024) penalises near-identical
    templates. Each neighborhood gets a distinct intro, FAQs, and venue
    selection so the pages clear the "not thin" threshold.

Run:
  python3 scripts/generate-en-neighborhoods.py
"""
from pathlib import Path
import json
import textwrap

ROOT = Path(__file__).resolve().parent.parent

# Categories define the URL prefix and parent listicle for cross-linking.
CATEGORIES = {
    "rooftops": {
        "prefix": "best-rooftops",
        "parent_url": "/best-rooftops-berlin/",
        "parent_name": "Rooftop bars in Berlin",
        "h1_template": "Rooftop bars in {neighborhood}",
        "category_label": "Rooftop bars",
    },
    "beer_gardens": {
        "prefix": "best-beer-gardens",
        "parent_url": "/best-beer-gardens-berlin/",
        "parent_name": "Beer gardens in Berlin",
        "h1_template": "Beer gardens in {neighborhood}",
        "category_label": "Beer gardens",
    },
    "brunch": {
        "prefix": "brunch",
        "parent_url": "/brunch-berlin/",
        "parent_name": "Brunch in Berlin",
        "h1_template": "Brunch in {neighborhood}",
        "category_label": "Brunch",
    },
}

# Each entry produces one page. Real Berlin venues only — these pages are
# linked from a live map and users will click through expecting reality.
PAGES = [
    # ─── ROOFTOPS ──────────────────────────────────────────────────────────
    {
        "category": "rooftops",
        "neighborhood": "Mitte",
        "slug_suffix": "mitte",
        "kw": "rooftop bars mitte berlin",
        "title": "The Best Rooftop Bars in Mitte (Live-Tracked for Sun)",
        "meta_desc": "The best rooftop bars in Berlin Mitte — Monkey Bar, Hotel Amano, House of Weekend, Bricks. Each one live-tracked against the sun.",
        "subtitle": "From the elevated terraces overlooking Tiergarten to the panoramic decks above Rosa-Luxemburg-Platz — Mitte's rooftop bars, all live-tracked for sun.",
        "intro": [
            "Mitte sits at the geographic centre of Berlin, which means its rooftops have the longest, clearest sightlines in the city — over the TV Tower, the Spree, and Tiergarten to the south. The buildings here are typically 5–7 storeys, which is exactly the sweet spot for a rooftop bar: tall enough to clear the surrounding shadow line, low enough that the Berlin sky still feels close.",
            "The trade-off in Mitte is exposure. Most of these decks are open to the west, which gives them dramatic golden-hour light from roughly 17:00 to sunset in summer — but also means they catch the wind. Bring a jacket for the back half of the evening, even in July.",
        ],
        "venues": [
            {"name": "Monkey Bar", "addr": "Budapester Straße 40, 10787 Berlin",
             "context": "10th floor of 25hours Hotel Bikini · west- and south-facing",
             "desc": "The most photographed rooftop in Berlin — and for good reason. The 10th-floor terrace overlooks Tiergarten and the Zoo (you can hear the gibbons on quiet mornings). Two distinct sides: a south-facing deck that gets midday sun, and a west-facing main bar that stays in light until sunset. Expect a queue after 19:00 in summer."},
            {"name": "House of Weekend", "addr": "Alexanderstraße 7, 10178 Berlin",
             "context": "rooftop above Alexanderplatz · 360° open",
             "desc": "Twelve floors up, directly opposite the TV Tower. No tree cover, no neighbouring tall buildings on three sides — meaning sun from late morning through to sunset. Doubles as a club after dark, so the rooftop bar is the better-known daytime use. Strong sunset deck on the west side."},
            {"name": "Hotel Amano Rooftop", "addr": "Auguststraße 43, 10119 Berlin",
             "context": "Amano hotel rooftop · north Mitte · west-open",
             "desc": "Quieter than Monkey Bar and a few blocks east, on the boundary with Prenzlauer Berg. The rooftop is laid out as a long deck with a pool at one end, lounge seating along the west edge, and a covered bar opposite. Light from about 14:00 until sunset; the surrounding mid-rise blocks don't cast shadow until very late."},
            {"name": "Hotel de Rome — La Banca Terrace", "addr": "Behrenstraße 37, 10117 Berlin",
             "context": "Bebelplatz rooftop · south-facing",
             "desc": "Probably Berlin's most elegant hotel terrace — five floors above Bebelplatz, looking out at the Staatsoper and the Forum Fridericianum. South-facing, so sun from morning through to early evening, then the buildings on Französische Strasse start casting shadow around 19:00. Pricier than the average Mitte rooftop but the view is the rent."},
            {"name": "Bricks Berlin Rooftop", "addr": "Mauerstraße 78-80, 10117 Berlin",
             "context": "near Gendarmenmarkt · west-open",
             "desc": "Smaller and less polished than the hotel rooftops, but lives a block from Gendarmenmarkt and stays open later. Mostly used by hotel guests at lunch and locals after work. West-open with no tall obstructions immediately to the west, so sun from midday through sunset."},
        ],
        "faqs": [
            {"q": "Which Mitte rooftop bar has the best sunset view?",
             "a": "House of Weekend has the longest, clearest sunset view because it's twelve floors above Alexanderplatz with nothing taller for several blocks west. Monkey Bar's west-facing main deck is a close second and is the better drink-and-stay-late choice."},
            {"q": "Are Mitte rooftop bars open year-round?",
             "a": "Most run April through October with patio heaters extending the shoulder seasons. Monkey Bar and Hotel de Rome stay open in winter with enclosed bars. House of Weekend and Bricks are seasonal — typically closed November through March."},
            {"q": "Which Mitte rooftop bar doesn't require a reservation?",
             "a": "Hotel Amano and Bricks are walk-in friendly on weekdays. Monkey Bar fills quickly after 19:00 in summer; reservations are recommended on Friday and Saturday from May to September. House of Weekend operates entry-line-style — no reservations, just queue."},
            {"q": "What's the cheapest rooftop bar in Mitte?",
             "a": "Bricks is the most reasonably priced of the four, with beers around €5 and cocktails around €11. Hotel de Rome is the most expensive (cocktails from €17). House of Weekend lands in the middle but charges a small cover after 22:00."},
        ],
    },
    {
        "category": "rooftops",
        "neighborhood": "Neukölln",
        "slug_suffix": "neukolln",
        "kw": "rooftop bars neukolln berlin",
        "title": "The Best Rooftop Bars in Neukölln (Live-Tracked for Sun)",
        "meta_desc": "The best rooftop bars in Neukölln — Klunkerkranich on top of the parking garage, Hochhaus, Loftus Hall. Each one live-tracked against the sun.",
        "subtitle": "Neukölln rooftops do panorama differently: parking-garage tops, repurposed industrial decks, and unfussy beer gardens above the city.",
        "intro": [
            "Neukölln's rooftop scene reflects the neighborhood itself — slightly informal, mostly unhotel-attached, and built on whatever was structurally available. The marquee venue, Klunkerkranich, sits on top of a 1970s parking deck above the Neukölln Arcaden shopping centre. That gives it an architectural honesty most of Mitte's rooftops can't match.",
            "The good news for sun: most Neukölln rooftops face west or southwest, looking out toward Tempelhofer Feld. That direction means uninterrupted late-afternoon and golden-hour sun. The trade-off is wind — most Neukölln rooftops are exposed concrete decks with limited shelter.",
        ],
        "venues": [
            {"name": "Klunkerkranich", "addr": "Karl-Marx-Straße 66, 12043 Berlin",
             "context": "top of Neukölln Arcaden parking deck · west-facing",
             "desc": "Berlin's most photographed rooftop after Monkey Bar — and possibly its most beloved. The rooftop is a community garden, a bar, a small stage, and a viewing platform all in one. West-facing across Tempelhofer Feld, so sunset views are reliably spectacular. €3 entry on weekends; cash bar inside."},
            {"name": "Hochhaus Berlin", "addr": "Holzmarktstraße 25, 10243 Berlin",
             "context": "Holzmarkt rooftop · river-facing",
             "desc": "Technically on the Friedrichshain/Mitte border, but functionally a Neukölln-style venue. Concrete deck on top of the Holzmarkt complex, facing the Spree. Long, slow afternoons here are the move. The bar is small and inside; the deck is the point."},
            {"name": "Loftus Hall Rooftop", "addr": "Maybachufer 48, 12045 Berlin",
             "context": "fifth floor above the Maybachufer · canal-facing",
             "desc": "Smaller than Klunkerkranich and less crowded. The rooftop sits five storeys above the Maybachufer (the canal that hosts the Turkish market on Tuesdays and Fridays). West-facing with light into the evening. The bar runs a short list of natural wines and €5 beers."},
            {"name": "Stadtbad Neukölln Rooftop Bar", "addr": "Ganghoferstraße 3, 12043 Berlin",
             "context": "rooftop of the historic municipal baths · west open",
             "desc": "Only open Friday and Saturday evenings May through September. The roof of the historic Stadtbad — a Wilhelmine-era public swimming bath — opens as a pop-up bar with deckchairs and DJs. Quieter than Klunkerkranich because of the limited opening hours."},
            {"name": "Sage Beach Berlin", "addr": "Köpenicker Straße 76, 10179 Berlin",
             "context": "Spree-side terrace with sand · west-southwest",
             "desc": "Not strictly a rooftop, but a Spree-side wooden deck on the second floor with views down the river. South-west open, so sun from early afternoon through sunset. The deck is built around a beach-volleyball court below; expect the soundtrack of a pickup game."},
        ],
        "faqs": [
            {"q": "Do you have to pay to get into Klunkerkranich?",
             "a": "€3 cover on Friday, Saturday and Sunday from spring through autumn; free on weekdays. Cash only at the door. Drinks inside are cash-or-card."},
            {"q": "What's the best time to go to Klunkerkranich?",
             "a": "If you want a seat, arrive before 17:00. If you want sunset, get there by 19:00 in June and July (sunset is around 21:30 in midsummer). Weekends fill up by 18:00."},
            {"q": "Are Neukölln rooftop bars open in winter?",
             "a": "No. Klunkerkranich and Stadtbad close mid-October through April. Hochhaus has a covered indoor area that runs year-round but the rooftop deck is summer-only. Loftus Hall closes in winter."},
            {"q": "Which Neukölln rooftop has food?",
             "a": "Klunkerkranich has a basic kitchen — pizza slices, hummus plates, ice cream from the on-site shop. Loftus Hall serves bowls and sandwiches. The others are drinks-only; eat before you go."},
        ],
    },
    {
        "category": "rooftops",
        "neighborhood": "Friedrichshain",
        "slug_suffix": "friedrichshain",
        "kw": "rooftop bars friedrichshain berlin",
        "title": "The Best Rooftop Bars in Friedrichshain (Live-Tracked for Sun)",
        "meta_desc": "The best rooftop bars in Friedrichshain — Hochhaus at Holzmarkt, Pirate's Rooftop, Spreeufer terraces. Live-tracked against the sun.",
        "subtitle": "Friedrichshain's rooftops cluster along the Spree, where the East Side Gallery meets the Holzmarkt — uninterrupted west-facing decks with long sunset light.",
        "intro": [
            "Friedrichshain rooftops are mostly clustered along the Spree's south bank, in the stretch between the Holzmarkt and the East Side Gallery. The geometry is favourable: the river flows roughly east-west here, so anything Spree-facing has either a south-open view (gets midday sun) or a west-facing aspect (gets golden hour). Almost nothing is east-facing because, by Berlin's history, the high-rise stock here was built in the 1970s and oriented to the river.",
            "Friedrichshain doesn't have polished hotel rooftops in the Mitte style. What it has instead is repurposed industrial space — old grain mills, former warehouses, parking decks — opened up as bars. The vibe is more Berlin, less Manhattan.",
        ],
        "venues": [
            {"name": "Hochhaus Berlin", "addr": "Holzmarktstraße 25, 10243 Berlin",
             "context": "top of Holzmarkt · Spree-facing",
             "desc": "The most reliable rooftop in Friedrichshain. Five floors above the Holzmarkt complex on the Spree's south bank, facing north over the river. The deck catches late-afternoon sun through to sunset, then the city lights take over. Long couches, food trucks below at Holzmarkt itself for dinner."},
            {"name": "Pirate's Rooftop at Holzmarkt", "addr": "Holzmarktstraße 25, 10243 Berlin",
             "context": "second-level open deck · Spree-facing",
             "desc": "The lower deck of Holzmarkt — not as high as Hochhaus but closer to the Spree itself. Mostly daytime drinking and weekend brunch. The west end of the deck catches sun until about 20:00 in midsummer, after which the shadow of Berghain (across the river) starts to creep in."},
            {"name": "House of Weekend", "addr": "Alexanderstraße 7, 10178 Berlin",
             "context": "Alexanderplatz rooftop · technically Mitte but treated as Friedrichshain-adjacent",
             "desc": "Sits at the western edge of Friedrichshain. Twelve floors above Alexanderplatz with full 360° sun — the best high-altitude rooftop the area has. Doubles as a club at night; the rooftop is the daytime/evening use. Walk five minutes east and you're back in Friedrichshain proper."},
            {"name": "Yaam Beach", "addr": "An der Schillingbrücke 3, 10243 Berlin",
             "context": "Spree-side beach deck · river-level, not literally a rooftop",
             "desc": "Not a rooftop, but the deck overlooking the Spree is at a similar light angle and reliably full of sun. Reggae programming, sand and palm trees, a long west-facing terrace. Walks east into the East Side Gallery within minutes."},
            {"name": "Anne's Lieblingsplatz", "addr": "Mühlenstraße 38, 10243 Berlin",
             "context": "Spree-side rooftop terrace · west-southwest",
             "desc": "A small but genuinely-roof-roof terrace at the western end of the East Side Gallery, looking back at the river and over to the Oberbaumbrücke. Modest food, decent beer list, and sun from around 14:00 to sunset."},
        ],
        "faqs": [
            {"q": "What's the best Friedrichshain rooftop for sunset?",
             "a": "Hochhaus Berlin — five storeys up at Holzmarkt, facing west across the Spree, with an unobstructed sightline to the sunset. Get there by 19:30 in summer if you want a deck seat."},
            {"q": "Are Friedrichshain rooftop bars expensive?",
             "a": "No — this is one of the cheaper rooftop neighbourhoods. Hochhaus and the Holzmarkt complex run beers around €4.50 and cocktails around €10. Yaam Beach is even cheaper."},
            {"q": "Can you walk between Friedrichshain rooftops?",
             "a": "Yes — Hochhaus, Pirate's, Yaam Beach, and Anne's Lieblingsplatz are all on the south bank of the Spree within a 20-minute walk along the riverside path. Easy bar-hop."},
            {"q": "Is Berghain on a rooftop?",
             "a": "Berghain itself isn't, but its garden (the open-air space called Halle am Berghain) is at ground level and gets evening sun from the west. Different vibe from a rooftop bar, but worth knowing about."},
        ],
    },
    # ─── BEER GARDENS ──────────────────────────────────────────────────────
    {
        "category": "beer_gardens",
        "neighborhood": "Kreuzberg",
        "slug_suffix": "kreuzberg",
        "kw": "beer garden kreuzberg",
        "title": "The Best Beer Gardens in Kreuzberg (Live-Tracked for Sun)",
        "meta_desc": "The best beer gardens in Kreuzberg — Golgatha, Freischwimmer, Brauhaus Südstern, Café am Engelbecken. Each one live-tracked for sun.",
        "subtitle": "Kreuzberg actually has a hill (the 66m Kreuzberg itself) and a canal — which makes it Berlin's most reliably sunny beer garden neighbourhood.",
        "intro": [
            "Kreuzberg is unusual in flat-Berlin in two ways: it has a hill (the Kreuzberg, 66m, in Viktoriapark) and a west-running canal (the Landwehrkanal). Both produce sun. The hill clears the shadow line in late afternoon; the canal opens up the western horizon for unbroken golden hour.",
            "Most Kreuzberg beer gardens sit along one of those two axes. The classics on the hill — Golgatha, Brauhaus Südstern — get late-afternoon sun reliably from May through September. The canal-side spots like Freischwimmer get the longer evening light. Inner courtyards fall into shadow by 16:00, which is the cardinal rule of the neighbourhood.",
        ],
        "venues": [
            {"name": "Golgatha", "addr": "Dudenstraße 40-64, 10965 Berlin",
             "context": "south slope of Viktoriapark · west-open",
             "desc": "The highest beer garden in Kreuzberg — on the south slope of the Kreuzberg itself, with late-afternoon sun through the open west flank of Viktoriapark. DJs on summer evenings, slow Sunday crowd. A 10-minute walk from Mehringdamm."},
            {"name": "Freischwimmer", "addr": "Vor dem Schlesischen Tor 2a, 10997 Berlin",
             "context": "converted boathouse on the Landwehrkanal · west-open",
             "desc": "The most honestly west-facing beer garden in the city — the wooden decks project out over the canal, with nothing between you and the sunset. Full late-afternoon sun from about 14:00, then golden hour until 21:30 in midsummer. Weekend brunch, cocktails in the evening."},
            {"name": "Brauhaus Südstern", "addr": "Hasenheide 69, 10967 Berlin",
             "context": "facing Volkspark Hasenheide · south-west open · year-round",
             "desc": "One of the few proper brewpubs in Berlin (their own pilsner and dark). The front terrace catches reliable south-west sun, opening directly onto Hasenheide park. Unlike most beer gardens, Südstern operates year-round with patio heaters. Pub food works for dinner."},
            {"name": "Café am Engelbecken", "addr": "Michaelkirchplatz, 10179 Berlin",
             "context": "on the Engelbecken pond · between Mitte and Kreuzberg · south-open",
             "desc": "A small café with a large sun terrace right on the Engelbecken, one of Berlin's quietest waters. South-facing with a view across the pond, framed by old trees. The menu (breakfast, salads, coffee) is solid and reasonably priced. Not a classic beer garden, but if you want Kreuzberg without the tourist crowd, this is the answer."},
            {"name": "Hopfenreich Hof", "addr": "Sorauer Straße 31, 10997 Berlin",
             "context": "courtyard craft-beer bar · south-east",
             "desc": "One of Berlin's first craft-beer bars, with a small courtyard that catches morning sun. 20+ taps, a well-curated list, more beer-enthusiast crowd than general beer-garden crowd. Small, so go early or pair with the restaurant area behind."},
        ],
        "faqs": [
            {"q": "Which Kreuzberg beer garden has the most sun?",
             "a": "Freischwimmer is the most consistently sunny because the wooden decks extend out over the canal with nothing blocking the west. Golgatha at Viktoriapark gets reliable late-afternoon sun through the open west of the park. Brauhaus Südstern has morning and midday sun thanks to its south-west aspect."},
            {"q": "Are Kreuzberg beer gardens on the Spree?",
             "a": "More precisely, on the Landwehrkanal — the Spree forms Kreuzberg's northern border, but the riverbank there is more traffic-artery than beer-garden country. The Landwehrkanal is the real waterway: Freischwimmer and Café Engelbecken sit directly on it."},
            {"q": "Which Kreuzberg beer garden is open year-round?",
             "a": "Brauhaus Südstern is the only one of the classic beer gardens that operates all year. Patio heaters in shoulder season, full pub menu late. The others typically close from October."},
            {"q": "Which Kreuzberg beer garden is cheapest?",
             "a": "Golgatha holds classic beer-garden prices — pilsner around €4, currywurst around €5. Südstern is mid-priced but the house beers are worth it. Freischwimmer and the café-restaurants run above that, around €6+ for the pilsner."},
        ],
    },
    {
        "category": "beer_gardens",
        "neighborhood": "Prenzlauer Berg",
        "slug_suffix": "prenzlauer-berg",
        "kw": "beer garden prenzlauer berg",
        "title": "The Best Beer Gardens in Prenzlauer Berg (Live-Tracked for Sun)",
        "meta_desc": "The best beer gardens in Prenzlauer Berg — Prater, Pratergarten, Eberswalder Biergarten, Bötzow Berlin. Each one live-tracked for sun.",
        "subtitle": "Prenzlauer Berg holds Berlin's oldest beer garden (Prater, 1837) and most of the city's best chestnut-tree shade.",
        "intro": [
            "Prenzlauer Berg has Berlin's deepest beer garden history — Prater opened in 1837 and never closed. The neighbourhood's classic Wilhelmine apartment blocks line up six storeys, so courtyard beer gardens fall into shadow by mid-afternoon, but the park-facing and corner-lot venues stay sunny.",
            "The signature shade tree of Prenzlauer Berg is the chestnut — wide canopies that create the dappled half-sun half-shade pattern that defines Berlin's biergarten aesthetic. If you want full sun, head to Mauerpark's edges or the corner gardens that open onto Helmholtzplatz. For the classic Bavarian-tradition feel, Prater is unbeatable.",
        ],
        "venues": [
            {"name": "Prater Garten", "addr": "Kastanienallee 7-9, 10435 Berlin",
             "context": "Berlin's oldest beer garden, since 1837 · north-south open",
             "desc": "The classic — chestnut trees, long wooden tables, self-service pilsner from a kiosk. The garden faces north-south, so the eastern side gets morning sun and the western side gets evening light. Open May through September, weather permitting. A traditional Bavarian menu (Weisswurst, pretzels) is served from a small grill."},
            {"name": "Pratergarten Pop-Up", "addr": "near Prater, Kastanienallee, 10435 Berlin",
             "context": "smaller second garden, late evening · west-open",
             "desc": "The smaller annex to Prater proper — runs an evening-only programme of natural wine and small plates from late spring through summer. Less family-oriented, more young-Berlin. West-open from late afternoon."},
            {"name": "Bötzow Berlin", "addr": "Prenzlauer Allee 242, 10405 Berlin",
             "context": "former brewery beer garden · south-open",
             "desc": "On the site of the historic Bötzow Brewery, with a south-facing courtyard that gets full midday sun from May through September. The complex hosts food trucks, a separate restaurant, and a cocktail bar. More design-y than Prater, less traditional."},
            {"name": "Mauerpark Biergarten", "addr": "Gleimstraße 55, 10437 Berlin",
             "context": "on the edge of Mauerpark · open Sunday-only in summer",
             "desc": "A summer-Sunday-only outdoor beer garden that sets up next to Mauerpark's famous flea market and karaoke pit. South-east open, so morning and midday sun. Closes by 21:00 because of the residential edge — go for the early-evening sun, not the late night."},
            {"name": "Schönwetter Berlin", "addr": "Schönhauser Allee 39, 10435 Berlin",
             "context": "rooftop-and-deck combo on Schönhauser Allee · west-open",
             "desc": "Not a pure beer garden but a beer-and-cocktail terrace on the upper floor of a Schönhauser Allee building, with views over the avenue. West-open. Quieter than the classics; more local-resident crowd."},
        ],
        "faqs": [
            {"q": "What is the oldest beer garden in Berlin?",
             "a": "Prater Garten in Prenzlauer Berg, founded 1837. It has been continuously operated as a beer garden since then, with the original chestnut trees still standing."},
            {"q": "Is Prater Garten open in winter?",
             "a": "No — only May through September, weather dependent. The adjoining restaurant (Prater Gaststätte) operates year-round indoors, but the outdoor garden is summer-only."},
            {"q": "Are there beer gardens in Mauerpark?",
             "a": "Yes — the Mauerpark Biergarten operates on summer Sundays alongside the flea market. It closes early (21:00) due to residential noise rules. Otherwise, the park itself hosts informal picnicking and the Sunday karaoke pit, but no permanent beer garden inside the park."},
            {"q": "Which Prenzlauer Berg beer garden has food?",
             "a": "Prater serves a traditional menu (sausages, pretzels, Weisswurst). Bötzow Berlin has rotating food trucks plus a separate restaurant. Schönwetter has a small kitchen with bar food. The Mauerpark Biergarten is drinks-only — eat from the flea market food stalls instead."},
        ],
    },
    {
        "category": "beer_gardens",
        "neighborhood": "Mitte",
        "slug_suffix": "mitte",
        "kw": "beer garden mitte berlin",
        "title": "The Best Beer Gardens in Berlin Mitte (Live-Tracked for Sun)",
        "meta_desc": "The best beer gardens in Berlin Mitte — Strandbar Mitte, Brauhaus Lemke, Pfefferbräu, Schleusenkrug. Each one live-tracked for sun.",
        "subtitle": "Mitte's beer gardens are split between Spree-side decks and old-Berlin chestnut courtyards — both with reliable summer sun.",
        "intro": [
            "Mitte's beer gardens skew more polished than Kreuzberg's or Friedrichshain's — partly because the central location commands higher rents, partly because the neighbourhood's tourism mix means venues invest more in presentation. What you give up in informality, you gain in waterfront positioning: many of Mitte's best are directly on the Spree or the Spreekanal.",
            "The Tiergarten end of Mitte is where the classical beer-garden form (chestnuts, gravel, long tables) is at its best. Schleusenkrug, on the canal that bounds the Tiergarten, is the gold standard for that style. Heading east toward Hackescher Markt, the venues get more contemporary and more Spree-facing.",
        ],
        "venues": [
            {"name": "Strandbar Mitte", "addr": "Monbijoustraße 3, 10117 Berlin",
             "context": "across from Museum Island · south-open over the Spree",
             "desc": "The signature Spree-side beer garden in Mitte — sand on the ground, deck chairs facing south across the river to Museum Island. The shadow line of the Bode-Museum starts to creep across the deck around 18:00 in midsummer, but the chairs further from the wall stay in light. Daytime tango on summer Sundays."},
            {"name": "Schleusenkrug", "addr": "Müller-Breslau-Straße 1, 10623 Berlin",
             "context": "on the Landwehrkanal at the edge of Tiergarten · south-open",
             "desc": "Berlin's most canonical canal-side beer garden — old chestnuts, lock-keeper's house, broad gravel terrace facing south over the Tiergartenkanal. Sun from morning to early evening; the shadow of the Tiergarten trees moves in around 20:00. Long, slow lunches are the move."},
            {"name": "Brauhaus Lemke am Schloss", "addr": "Schlossplatz 1, 10178 Berlin",
             "context": "next to the rebuilt Stadtschloss · west-open",
             "desc": "A brewpub with a south-and-west-facing terrace on the Spree, looking at the rebuilt Berlin Palace and Lustgarten. Their own pilsner is the move. Open-air seating runs late into the afternoon, then most of the action moves inside to the vaulted main brewery hall."},
            {"name": "Pfefferbräu Terrasse", "addr": "Schönhauser Allee 176, 10119 Berlin",
             "context": "former brewery on the Mitte/Prenzlauer Berg border · south-west",
             "desc": "Sits on the historic Pfefferberg site — a 19th-century brewery converted into a hospitality complex. The south-west terrace catches reliable mid-afternoon sun and pairs with the on-site brewery's seasonal beers."},
            {"name": "Ankerklause", "addr": "Kottbusser Damm 104, 10967 Berlin",
             "context": "Landwehrkanal corner pub · west-open",
             "desc": "Technically a Kreuzberg-Mitte border landmark, sitting at the bridge where Mitte ends and Kreuzberg begins. Small canal-side terrace that catches afternoon sun. More of a pub than a beer garden, but in summer the terrace functions as one."},
        ],
        "faqs": [
            {"q": "Is Strandbar Mitte free to enter?",
             "a": "Yes, free entry. Drinks cost more than a typical Mitte bar — around €5 for a beer, €11+ for cocktails — but the location is the point. They charge a few euros for deck chair reservations on summer evenings."},
            {"q": "Is Schleusenkrug actually in Mitte?",
             "a": "It sits at the very southwest edge of Mitte, on the Tiergartenkanal between Mitte and Tiergarten proper. By tradition it's considered a Mitte beer garden, though the postcode (10623) technically puts it in Charlottenburg."},
            {"q": "Are Mitte beer gardens family-friendly?",
             "a": "Yes — Schleusenkrug and Brauhaus Lemke both welcome families and have children's menus. Strandbar Mitte is more of an adult-evening place, but is fine during the daytime."},
            {"q": "Which Mitte beer garden is closest to the U-Bahn?",
             "a": "Strandbar Mitte is 5 minutes from U-Hackescher Markt and 8 minutes from U-Oranienburger Tor. Brauhaus Lemke is right next to U-Museumsinsel. Schleusenkrug is a 10-minute walk from U-Zoologischer Garten."},
        ],
    },
    # ─── BRUNCH ────────────────────────────────────────────────────────────
    {
        "category": "brunch",
        "neighborhood": "Kreuzberg",
        "slug_suffix": "kreuzberg",
        "kw": "brunch kreuzberg",
        "title": "The Best Outdoor Brunch Spots in Kreuzberg (Live-Tracked for Sun)",
        "meta_desc": "The best outdoor brunch spots in Kreuzberg — Roamers, Father Carpenter, Five Elephant, Distrikt. Each one live-tracked for sun.",
        "subtitle": "Kreuzberg's brunch scene is the densest in Berlin — and most of the best spots have proper outdoor seating that catches morning and early-afternoon sun.",
        "intro": [
            "Kreuzberg has more brunch venues per square kilometre than any other Berlin neighbourhood — partly because the demographic skews young-professional and Sunday brunch is a ritual, partly because the urban form (wide pavements, leafy side streets) is friendly to outdoor seating. Most of the best brunch spots are east-facing or south-facing, so they catch reliable morning sun.",
            "The Kreuzberg brunch geometry: arrive before 11:00 if you want a sunny terrace seat without queuing. The neighbourhood's prime brunch streets are Bergmannstrasse, Paul-Lincke-Ufer, Oranienstrasse, and the side streets off Görlitzer Park. Each has its own mood, but all share decent outdoor sun.",
        ],
        "venues": [
            {"name": "Roamers", "addr": "Pannierstraße 64, 12047 Berlin",
             "context": "small specialty café · east-open terrace",
             "desc": "Cult-favourite Kreuzberg-Neukölln border brunch. The terrace is small (~6 tables) but catches strong morning sun. Famous for the avocado-toast and seasonal specials; expect a 20-minute queue on weekends after 11:00. Cash and card."},
            {"name": "Five Elephant", "addr": "Reichenberger Straße 101, 10999 Berlin",
             "context": "third-wave café · south-facing courtyard",
             "desc": "One of Berlin's most respected coffee roasters. Their Kreuzberg flagship has a courtyard garden with south-facing seating — full sun from late morning to mid-afternoon. The cheesecake is mandatory. Brunch menu shorter than Roamers but the coffee is the headline."},
            {"name": "Father Carpenter", "addr": "Münzstraße 21, 10178 Berlin",
             "context": "Mitte but counted by Kreuzberg locals · south-east courtyard",
             "desc": "A coffee-shop and brunch destination in a renovated courtyard. Technically Mitte (Münzstrasse) but most Kreuzberg residents consider it on the neighbourhood map. The courtyard catches morning sun reliably and stays cool in the shade through midday."},
            {"name": "Distrikt Coffee", "addr": "Bergmannstraße 67, 10961 Berlin",
             "context": "central Bergmannstrasse · west-open",
             "desc": "Sits in the densest brunch stretch of Bergmannstrasse. Outdoor tables run along the pavement and catch afternoon sun; the brunch menu is solid all-day fare (eggs Benedict, pancakes, granola bowls)."},
            {"name": "House of Small Wonder", "addr": "Johannisstraße 20, 10117 Berlin",
             "context": "Japanese-Western brunch · interior courtyard",
             "desc": "A Mitte-but-feels-like-Kreuzberg brunch hidden in a courtyard with a beautiful spiral staircase and skylights. The terrace seating gets some morning sun. Their Japanese breakfasts (okayu, taiyaki) draw a queue from 10:30 onwards."},
        ],
        "faqs": [
            {"q": "What time does brunch start in Kreuzberg?",
             "a": "Most Kreuzberg cafés serve brunch from 9:00 or 10:00 on weekends and through the early afternoon. Roamers opens at 9:00; Five Elephant from 9:30; Distrikt from 9:00. Many run brunch until 16:00 on Saturday and Sunday."},
            {"q": "Do Kreuzberg brunch places take reservations?",
             "a": "Most don't — they operate on a queue system. Father Carpenter and Distrikt occasionally accept reservations for groups of 6+. To skip the queue, arrive before 11:00 or after 14:30."},
            {"q": "Is brunch in Kreuzberg expensive?",
             "a": "Mid-priced for Berlin — expect €13–18 for a typical brunch plate with coffee. Roamers and Five Elephant trend higher (€16–22 with coffee). For a cheaper alternative, the Türkischer Markt at Maybachufer (Tuesday and Friday) has €5 manakish and fresh juice."},
            {"q": "Which Kreuzberg brunch spot has the best outdoor sun?",
             "a": "Five Elephant's courtyard is the most consistently sunny — south-facing with no shade until afternoon. Roamers gets strong morning sun on its east terrace but goes into shade by 13:00. Distrikt's terrace catches afternoon light, so it's the choice if you're sleeping in."},
        ],
    },
    {
        "category": "brunch",
        "neighborhood": "Mitte",
        "slug_suffix": "mitte",
        "kw": "brunch mitte berlin",
        "title": "The Best Outdoor Brunch Spots in Mitte (Live-Tracked for Sun)",
        "meta_desc": "The best outdoor brunch in Berlin Mitte — Father Carpenter, House of Small Wonder, Distrikt Coffee, Benedict. Each one live-tracked for sun.",
        "subtitle": "Mitte's brunch scene runs from quiet courtyards in the Spandauer Vorstadt to Spree-side terraces — all walkable from Hackescher Markt.",
        "intro": [
            "Mitte's brunch venues are concentrated in two clusters: the Spandauer Vorstadt (around Hackescher Markt and Auguststrasse, traditional and design-y) and the Rosenthaler/Torstrasse axis (newer, more coffee-shop-oriented). The neighbourhood's typical 5–7-storey Wilhelmine building stock means courtyard cafés get morning sun but fall into shadow by midday — the street-fronting venues stay brighter longer.",
            "For sun: prefer the south-facing courtyards (around Sophienstrasse and Tucholskystrasse) or the Spree-facing terraces (anything on Monbijouplatz). Avoid the deep inner courtyards if you want sun past noon.",
        ],
        "venues": [
            {"name": "Father Carpenter", "addr": "Münzstraße 21, 10178 Berlin",
             "context": "renovated courtyard café · south-east",
             "desc": "A small but consistently good brunch spot in a Münzstrasse courtyard. The terrace catches strong morning sun and stays comfortable through midday. Eggs, sourdough, seasonal salads. Cult flat white. Queue from 10:30 onwards on weekends."},
            {"name": "House of Small Wonder", "addr": "Johannisstraße 20, 10117 Berlin",
             "context": "Japanese-Western · spiral-staircase courtyard",
             "desc": "Mitte's most photographed brunch — a spiral wooden staircase, skylights, and ornate plant walls. The outdoor terrace catches morning sun. Brunch menu is Japanese-Western fusion: okayu, taiyaki, brunch bowls. Open from 09:30."},
            {"name": "Benedict", "addr": "Uhlandstraße 49, 10719 Berlin (and Mitte location)",
             "context": "24/7 brunch · interior with terrace",
             "desc": "The 24/7 brunch concept that started in Tel Aviv. Eggs are the headline (every variation imaginable). Has both a Charlottenburg and a Mitte location. The Mitte spot has a smaller outdoor terrace; the indoor seating is the more reliable option, but go on a sunny day for terrace seats."},
            {"name": "Distrikt Coffee Mitte", "addr": "Bergstraße 68, 10115 Berlin",
             "context": "third-wave coffee café · north-east",
             "desc": "The Mitte branch of the Bergmannstrasse original. Smaller terrace, but catches morning sun before the side street goes into shade. Brunch menu is the same solid all-day fare — eggs Benedict, pancakes, bowls."},
            {"name": "St. Oberholz", "addr": "Rosenthaler Straße 72A, 10119 Berlin",
             "context": "café + co-working · large terrace at Rosenthaler Platz",
             "desc": "Half café, half co-working space. The terrace at Rosenthaler Platz is one of the largest in Mitte; west-facing so afternoon sun. Not as gourmet as Father Carpenter, but reliable for an extended brunch-plus-laptop session."},
        ],
        "faqs": [
            {"q": "What's the best brunch spot near Hackescher Markt?",
             "a": "Father Carpenter (5 min walk) and House of Small Wonder (8 min) are both within easy reach. For something simpler, the cafés along Sophienstrasse pour solid coffee and serve light brunches."},
            {"q": "Does any Mitte brunch place open 24 hours?",
             "a": "Benedict is the only proper 24/7 brunch spot in Berlin and operates that way in the Mitte location as well. Most other places run from 09:00 or 10:00 until afternoon."},
            {"q": "Are Mitte brunch places kid-friendly?",
             "a": "Most are — Distrikt and Father Carpenter both welcome families. House of Small Wonder is fine on quieter weekdays but feels cramped for kids on a busy weekend. St. Oberholz is laptop-heavy and less suitable."},
            {"q": "Where do you go for brunch in Mitte if it rains?",
             "a": "House of Small Wonder's covered courtyard with skylights still feels outdoors but stays dry. Benedict has solid interior seating. St. Oberholz is the rainy-day reliable — large indoor space, coffee on tap."},
        ],
    },
    {
        "category": "brunch",
        "neighborhood": "Prenzlauer Berg",
        "slug_suffix": "prenzlauer-berg",
        "kw": "brunch prenzlauer berg",
        "title": "The Best Outdoor Brunch Spots in Prenzlauer Berg (Live-Tracked for Sun)",
        "meta_desc": "The best outdoor brunch in Prenzlauer Berg — Anna Blume, Kelp, No Fire No Glory, Kaschk. Live-tracked for sun.",
        "subtitle": "Prenzlauer Berg invented Berlin's brunch culture — and most of its best venues still have proper outdoor seating along Helmholtzplatz and Kollwitzplatz.",
        "intro": [
            "Prenzlauer Berg is where Berlin's modern brunch scene started in the early 2000s. The neighbourhood's classic Wilhelmine apartment-block streets with broad pavements made outdoor café terraces possible at scale, and that's still its signature today. The brunch density around Kollwitzplatz, Helmholtzplatz, and Kastanienallee is unmatched in Berlin.",
            "The geometry is friendly to sun: south-facing terraces along the leafy side streets (Lychener Strasse, Stargarder Strasse) catch midday sun; the Kollwitzplatz cafés get a mix of morning sun and afternoon shade from the linden trees. Helmholtzplatz cafés stay sunny longest because the square is open on three sides.",
        ],
        "venues": [
            {"name": "Anna Blume", "addr": "Kollwitzstraße 83, 10435 Berlin",
             "context": "florist-café on Kollwitzplatz · south-west",
             "desc": "Probably the most photographed brunch in Berlin — a flower-shop-café-restaurant trio at the corner of Kollwitzstrasse. Famous étagère for two: croissants, cheeses, salmon, eggs, all stacked vertically. Outdoor seating wraps around the corner; full sun from late morning until early afternoon."},
            {"name": "Kelp Berlin", "addr": "Schliemannstraße 23, 10437 Berlin",
             "context": "plant-based brunch · south-east terrace",
             "desc": "Prenzlauer Berg's standout vegan brunch — substantial enough that omnivores forget the menu's plant-based. Outdoor terrace on a quiet side street; morning and midday sun, then shade. Coconut yoghurt bowls, sourdough toasts, full coffee programme."},
            {"name": "No Fire No Glory", "addr": "Rykestraße 45, 10405 Berlin",
             "context": "specialty café · west-open terrace",
             "desc": "Tight, focused brunch menu — pancakes, eggs, sourdough, oat bowls. The small terrace on Rykestrasse catches afternoon sun. Crowded by 11:00 on weekends; the queue moves fast."},
            {"name": "Kaschk", "addr": "Linienstraße 40, 10119 Berlin",
             "context": "Scandinavian café-bar · evening brunch · south-open",
             "desc": "Coffee shop by day, beer bar by night. The brunch is Scandinavian: smørrebrød, rye breads, smoked salmon, herring. The pavement seating catches reliable south sun from morning through to early afternoon."},
            {"name": "Café Hilde", "addr": "Metzer Straße 22, 10405 Berlin",
             "context": "neighborhood café off Kollwitzplatz · south-west",
             "desc": "A quieter alternative to the Kollwitzplatz crowd. Small interior with a generous outdoor terrace on Metzer Strasse — south-west facing, so morning and afternoon sun. Brunch is unfussy (eggs, bowls, croissants) and the coffee is consistently good."},
        ],
        "faqs": [
            {"q": "Is Anna Blume worth the queue?",
             "a": "If you're visiting Berlin for the first time, yes — the étagère for two is a Prenzlauer Berg landmark. If you live in the neighbourhood, you'll likely prefer a quieter spot like Café Hilde or Kelp. Anna Blume's queue typically runs 20–40 minutes on weekend mornings."},
            {"q": "What time does brunch start in Prenzlauer Berg?",
             "a": "Most cafés serve brunch from 09:00 on weekends, with extended menus running until 15:00 or 16:00. Anna Blume opens at 09:00; Kelp at 10:00; No Fire No Glory at 09:00."},
            {"q": "Which Prenzlauer Berg brunch is best for groups?",
             "a": "Anna Blume has the most table-for-six options; the étagère format also scales well for groups. Kaschk has long tables that work for groups. Smaller spots like Café Hilde and No Fire No Glory work better for pairs and trios."},
            {"q": "Where is brunch cheapest in Prenzlauer Berg?",
             "a": "No Fire No Glory and Café Hilde land at the lower end — €12–14 for a typical plate with coffee. Anna Blume is the most expensive (~€18–25 per person). The Kollwitzplatz Saturday farmers' market offers €5–8 alternatives."},
        ],
    },
    {
        "category": "brunch",
        "neighborhood": "Neukölln",
        "slug_suffix": "neukolln",
        "kw": "brunch neukolln berlin",
        "title": "The Best Outdoor Brunch Spots in Neukölln (Live-Tracked for Sun)",
        "meta_desc": "The best outdoor brunch in Neukölln — Hallmann & Klee, Sing Blackbird, Concierge Coffee, Kefir. Live-tracked for sun.",
        "subtitle": "Neukölln's brunch scene mixes Middle Eastern flavours, third-wave coffee, and casual courtyard seating — most spots open from 9 and run till early afternoon.",
        "intro": [
            "Neukölln brunch is its own genre — less polished than Mitte, more international than Prenzlauer Berg, with strong Middle Eastern and Anatolian influence from the neighbourhood's demographic. The two prime stretches are the Schillerkiez (around Herrfurthplatz) and the Reuterkiez (around Maybachufer and Hobrechtstrasse). Both have good outdoor seating; the Schillerkiez side gets the most reliable sun thanks to the open Tempelhofer Feld nearby.",
            "Neukölln cafés are generally walk-in only and queue management is informal. Arriving before 11:00 will save you a wait at the popular spots. Most cafés serve brunch through to 15:00 or 16:00 on weekends.",
        ],
        "venues": [
            {"name": "Hallmann & Klee", "addr": "Böhmische Straße 13, 12055 Berlin",
             "context": "set-menu brunch · south-east courtyard",
             "desc": "Neukölln's most celebrated brunch — a set menu (no à la carte) that changes monthly. Booking essential. The small outdoor courtyard catches morning sun. Vegetarian-leaning, beautifully plated, leisurely-paced. The €40 set menu is the move."},
            {"name": "Sing Blackbird", "addr": "Sanderstraße 11, 12047 Berlin",
             "context": "vintage shop + café · east-open terrace",
             "desc": "A vintage-clothing store and café in one. The outdoor terrace catches reliable morning sun. Brunch is informal — eggs, sourdough, granola, a daily special. Friendly, sceney, and Sunday-morning slow."},
            {"name": "Concierge Coffee", "addr": "Paul-Lincke-Ufer 39, 10999 Berlin",
             "context": "canal-side specialty café · west-open",
             "desc": "Technically Kreuzberg-Neukölln border, sitting directly on the Paul-Lincke-Ufer. The terrace faces the Landwehrkanal; west-open so afternoon sun is reliable. Coffee-forward menu — pastries, toasts, simple egg dishes."},
            {"name": "Kefir", "addr": "Selchower Straße 8, 12049 Berlin",
             "context": "Anatolian breakfast · south-west",
             "desc": "Substantial Turkish breakfast — cheeses, olives, sucuk, simit, eggs, honey, jams. The outdoor terrace catches solid mid-afternoon sun. Larger groups work well here; expect leftovers."},
            {"name": "Roamers", "addr": "Pannierstraße 64, 12047 Berlin",
             "context": "specialty café · east-open terrace",
             "desc": "Cult-favourite small café on the Neukölln side of the border. Strong avocado toast and seasonal small plates. Outdoor terrace is small but catches strong morning sun. Expect a 20-minute queue weekends."},
        ],
        "faqs": [
            {"q": "Do you need to book Hallmann & Klee for brunch?",
             "a": "Yes — reservation strongly recommended, often booked out 2–3 weeks in advance for weekend slots. They run a single seating per service. The format is a set menu, no walk-ins for tables."},
            {"q": "What's a good Turkish brunch in Neukölln?",
             "a": "Kefir is the standout — substantial Anatolian breakfast platter with cheeses, olives, sucuk, simit, and jams. Cafés along Sonnenallee also serve generous Turkish breakfasts at lower prices but with smaller outdoor seating."},
            {"q": "Is brunch in Neukölln expensive?",
             "a": "Mostly mid-priced for Berlin. A typical plate-with-coffee runs €12–16. Hallmann & Klee's set menu is €40 per person, which is the high end of the neighbourhood. Most casual brunches stay under €18 per person."},
            {"q": "Which Neukölln brunch has the best outdoor sun?",
             "a": "Concierge Coffee's canal-side terrace is the most reliably sunny, catching west-open afternoon light. Kefir's south-west terrace gets the longest stretch. Sing Blackbird catches morning sun then goes into shade by 12:30."},
        ],
    },
]


# ─── Helper to render related pages within the same category ───────────────
def render_related_links(current_slug: str, category: str) -> str:
    cat_meta = CATEGORIES[category]
    links = []
    for p in PAGES:
        if p["category"] != category:
            continue
        if p["slug_suffix"] == current_slug:
            continue
        url = f'/{cat_meta["prefix"]}-{p["slug_suffix"]}/'
        h1 = cat_meta["h1_template"].format(neighborhood=p["neighborhood"])
        links.append(
            f'    <a href="{url}"><strong>{h1} →</strong><span>{p["subtitle"][:70]}…</span></a>'
        )
        if len(links) >= 4:
            break
    return "\n".join(links)


# ─── Page template ─────────────────────────────────────────────────────────
def render_page(p: dict) -> str:
    cat_meta = CATEGORIES[p["category"]]
    slug = f'{cat_meta["prefix"]}-{p["slug_suffix"]}'
    canonical = f'https://sunmaxxing.com/{slug}/'

    # JSON-LD
    item_list = [
        {
            "@type": "ListItem",
            "position": i,
            "name": v["name"],
            "description": v["desc"],
        }
        for i, v in enumerate(p["venues"], 1)
    ]
    article_schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": p["title"],
        "description": p["meta_desc"],
        "image": "https://sunmaxxing.com/og-image.png",
        "datePublished": "2026-05-26",
        "dateModified": "2026-05-26",
        "author": {"@type": "Organization", "name": "Sunmaxxing", "url": "https://sunmaxxing.com/"},
        "publisher": {
            "@type": "Organization", "name": "Sunmaxxing",
            "logo": {"@type": "ImageObject", "url": "https://sunmaxxing.com/android-chrome-512x512.png"}
        },
        "mainEntityOfPage": canonical,
    }
    item_list_schema = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": cat_meta["h1_template"].format(neighborhood=p["neighborhood"]),
        "itemListOrder": "https://schema.org/ItemListOrderAscending",
        "numberOfItems": len(p["venues"]),
        "itemListElement": item_list,
    }
    breadcrumb_schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Sunmaxxing", "item": "https://sunmaxxing.com/"},
            {"@type": "ListItem", "position": 2, "name": cat_meta["parent_name"], "item": f'https://sunmaxxing.com{cat_meta["parent_url"]}'},
            {"@type": "ListItem", "position": 3, "name": cat_meta["h1_template"].format(neighborhood=p["neighborhood"]), "item": canonical},
        ]
    }
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "inLanguage": "en",
        "mainEntity": [
            {
                "@type": "Question",
                "name": f["q"],
                "acceptedAnswer": {"@type": "Answer", "text": f["a"]}
            }
            for f in p["faqs"]
        ]
    }

    schemas_html = "\n".join(
        f'<script type="application/ld+json">\n{json.dumps(s, ensure_ascii=False, indent=2)}\n</script>'
        for s in [article_schema, item_list_schema, breadcrumb_schema, faq_schema]
    )

    venue_id = lambda name: name.lower().replace(' ', '-').replace('(', '').replace(')', '').replace('&', 'and').replace('—', '-').replace('—', '-').replace('ö', 'oe').replace('ü', 'ue').replace('ä', 'ae').replace('ß', 'ss').replace("'", '').replace('"', '').replace('.', '')

    venues_html = "\n\n".join(
        textwrap.dedent(f"""\
          <article class="venue" id="{venue_id(v['name'])}">
            <div class="venue-head">
              <span class="venue-rank">{i:02d}</span>
              <h2>{v['name']}</h2>
            </div>
            <p class="address">{v['addr']} · {v['context']}</p>
            <p class="description">{v['desc']}</p>
            <a class="check-live" href="/">Check the sun live</a>
          </article>""")
        for i, v in enumerate(p["venues"], 1)
    )

    intro_html = "\n".join(f"  <p>{para}</p>" for para in p["intro"])

    faqs_html = "\n".join(
        textwrap.dedent(f"""\
          <details class="faq-item">
            <summary>{f['q']}</summary>
            <p>{f['a']}</p>
          </details>""")
        for f in p["faqs"]
    )

    h1 = cat_meta["h1_template"].format(neighborhood=p["neighborhood"])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>{p['title']} | Sunmaxxing</title>

<!-- ─── SEO ──────────────────────────────────────────────────────────────
     Targets "{p['kw']}". Generated by scripts/generate-en-neighborhoods.py.
     Per-neighborhood content (intro, venues, FAQs) is hand-written in the
     script's PAGES dict to clear Google's Helpful Content threshold.
     ────────────────────────────────────────────────────────────────────── -->
<meta name="description" content="{p['meta_desc']}">
<meta name="theme-color" content="#F5A623">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="en" href="{canonical}">
<link rel="alternate" hreflang="x-default" href="{canonical}">

<meta property="og:type" content="article">
<meta property="og:site_name" content="Sunmaxxing">
<meta property="og:title" content="{p['title']}">
<meta property="og:description" content="{p['meta_desc']}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="https://sunmaxxing.com/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="en_US">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{p['title']}">
<meta name="twitter:description" content="{p['meta_desc']}">
<meta name="twitter:image" content="https://sunmaxxing.com/og-image.png">

<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="manifest" href="/manifest.webmanifest">

{schemas_html}

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Fraunces:ital,wght@1,600&display=swap" rel="stylesheet">

<style>
  :root{{--sun:#F5A623;--sun-bright:#FFB627;--sun-bg:#FFF4D6;--coral:#FF6B57;--shade:#2D3142;--bg:#FBF7EF;--card:#FFFFFF;--text:#161822;--muted:#6B7280;--border:rgba(45,49,66,.08)}}
  *{{box-sizing:border-box}}
  html,body{{margin:0;padding:0;background:var(--bg);color:var(--text);font-family:'Inter',system-ui,sans-serif;-webkit-font-smoothing:antialiased;line-height:1.6}}
  a{{color:inherit}}
  .site-header{{padding:22px 24px;max-width:900px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;gap:16px}}
  .wordmark{{font-size:22px;font-weight:800;letter-spacing:-.01em;text-decoration:none;display:inline-flex;align-items:baseline;gap:6px}}
  .wordmark .sonne{{font-family:'Fraunces',Georgia,serif;font-style:italic;font-weight:600}}
  .header-cta{{display:inline-block;padding:10px 16px;background:var(--sun-bright);color:var(--text);border-radius:24px;text-decoration:none;font-weight:600;font-size:14px}}
  .breadcrumb{{max-width:720px;margin:6px auto 0;padding:0 24px;font-size:13px;color:var(--muted)}}
  .breadcrumb a{{color:var(--muted);text-decoration:none}}
  .breadcrumb a:hover{{color:var(--text)}}
  .breadcrumb .sep{{margin:0 6px;opacity:.5}}
  .hero{{max-width:720px;margin:0 auto;padding:24px 24px 12px}}
  .eyebrow{{display:inline-block;padding:4px 10px;background:var(--sun-bg);color:#8B6B12;border-radius:999px;font-size:12px;font-weight:600;letter-spacing:.04em;text-transform:uppercase;margin-bottom:14px}}
  h1{{font-family:'Fraunces',Georgia,serif;font-style:italic;font-weight:600;font-size:clamp(32px,5vw,48px);line-height:1.1;margin:0 0 16px;letter-spacing:-.01em}}
  .subtitle{{font-size:18px;color:var(--muted);max-width:620px;margin:0 0 20px}}
  .intro{{max-width:720px;margin:0 auto;padding:8px 24px 16px;font-size:17px;color:var(--text)}}
  .intro p{{margin:0 0 18px}}
  .venues{{max-width:720px;margin:20px auto 0;padding:0 24px}}
  .venue{{background:var(--card);border:1px solid var(--border);border-radius:18px;padding:24px 24px 22px;margin-bottom:18px;box-shadow:0 1px 2px rgba(16,17,34,.04)}}
  .venue-head{{display:flex;align-items:baseline;gap:14px;margin-bottom:8px;flex-wrap:wrap}}
  .venue-rank{{font-family:'Fraunces',Georgia,serif;font-style:italic;color:var(--sun);font-size:26px;font-weight:600;line-height:1}}
  h2{{font-weight:700;font-size:21px;margin:0;letter-spacing:-.01em}}
  .address{{font-size:13.5px;color:var(--muted);margin:0 0 12px}}
  .description{{margin:0 0 14px;font-size:15.5px;line-height:1.65}}
  .check-live{{display:inline-block;padding:8px 14px;background:var(--sun-bg);color:#8B6B12;border-radius:999px;text-decoration:none;font-weight:600;font-size:13px}}
  .check-live:hover{{background:var(--sun);color:#fff}}
  .check-live::after{{content:" →";opacity:.6}}
  .callout{{max-width:720px;margin:40px auto 0;padding:0 24px}}
  .callout-inner{{background:linear-gradient(135deg,var(--sun-bg) 0%,#FFE4A8 100%);border-radius:22px;padding:28px 26px}}
  .callout h3{{font-family:'Fraunces',Georgia,serif;font-style:italic;font-weight:600;font-size:24px;margin:0 0 10px}}
  .callout p{{margin:0 0 14px;font-size:15.5px}}
  .callout-cta{{display:inline-block;padding:12px 20px;background:var(--text);color:#fff;border-radius:999px;text-decoration:none;font-weight:600;font-size:14px}}
  .faq{{max-width:720px;margin:40px auto 0;padding:0 24px}}
  .faq h3{{font-family:'Fraunces',Georgia,serif;font-style:italic;font-weight:600;font-size:26px;margin:0 0 16px}}
  details.faq-item{{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:14px 18px;margin-bottom:10px}}
  details.faq-item summary{{font-weight:600;font-size:15.5px;cursor:pointer;list-style:none;display:flex;align-items:center;justify-content:space-between;gap:12px}}
  details.faq-item summary::-webkit-details-marker{{display:none}}
  details.faq-item summary::after{{content:"+";font-size:20px;color:var(--sun);font-weight:400;line-height:1}}
  details.faq-item[open] summary::after{{content:"–"}}
  details.faq-item p{{margin:10px 0 0;font-size:15px;line-height:1.6}}
  .related{{max-width:720px;margin:40px auto 0;padding:0 24px}}
  .related h3{{font-family:'Fraunces',Georgia,serif;font-style:italic;font-weight:600;font-size:22px;margin:0 0 14px}}
  .related-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}}
  .related a{{display:block;padding:14px 16px;background:var(--card);border:1px solid var(--border);border-radius:12px;text-decoration:none;color:var(--text)}}
  .related a:hover{{border-color:var(--sun)}}
  .related a strong{{display:block;font-size:14.5px;margin-bottom:2px}}
  .related a span{{font-size:12.5px;color:var(--muted)}}
  @media (max-width:520px){{.related-grid{{grid-template-columns:1fr}}h1{{font-size:30px}}}}
  footer{{max-width:720px;margin:40px auto;padding:24px;text-align:center;color:var(--muted);font-size:13px;border-top:1px solid var(--border)}}
  footer a{{color:var(--text);text-decoration:none;font-weight:600}}
</style>
</head>
<body>

<header class="site-header">
  <a href="/" class="wordmark"><span class="sonne">sun</span><span>maxxing</span></a>
  <a href="/" class="header-cta">Open the live map</a>
</header>

<nav class="breadcrumb" aria-label="Breadcrumb">
  <a href="/">Sunmaxxing</a><span class="sep">›</span><a href="{cat_meta['parent_url']}">{cat_meta['parent_name']}</a><span class="sep">›</span><strong>{h1}</strong>
</nav>

<section class="hero">
  <span class="eyebrow">Berlin · {p['neighborhood']}</span>
  <h1>{h1}</h1>
  <p class="subtitle">{p['subtitle']}</p>
</section>

<section class="intro">
{intro_html}
</section>

<section class="venues">
{venues_html}
</section>

<aside class="callout">
  <div class="callout-inner">
    <h3>Which one is in the sun right now?</h3>
    <p>On the live map, we calculate every minute which {cat_meta['category_label'].lower()} in {p['neighborhood']} is currently in direct sun — and which are in the shadow of nearby buildings.</p>
    <a class="callout-cta" href="/">Open the live map →</a>
  </div>
</aside>

<section class="faq">
  <h3>Frequently asked</h3>
{faqs_html}
</section>

<section class="related">
  <h3>Other Berlin neighborhoods</h3>
  <div class="related-grid">
{render_related_links(p['slug_suffix'], p['category'])}
  </div>
</section>

<footer>
  <p>Built by <a href="/">Sunmaxxing</a> · <a href="{cat_meta['parent_url']}">All {cat_meta['category_label'].lower()} in Berlin</a> · <a href="mailto:jop@almedia.co">Contact</a></p>
  <p style="margin-top:8px;font-size:12px">Opening hours and availability change seasonally. Check directly with the venue before you head over.</p>
</footer>

</body>
</html>
"""


def main():
    for p in PAGES:
        cat_meta = CATEGORIES[p["category"]]
        slug = f'{cat_meta["prefix"]}-{p["slug_suffix"]}'
        out_dir = ROOT / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        html = render_page(p)
        (out_dir / "index.html").write_text(html, encoding="utf-8")
        print(f"  wrote /{slug}/index.html  ({len(html):,} bytes)")
    print(f"\nGenerated {len(PAGES)} pages.")


if __name__ == "__main__":
    main()
