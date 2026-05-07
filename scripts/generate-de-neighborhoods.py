#!/usr/bin/env python3
"""
Generate DE neighborhood biergarten pages from a single content dict.

Why a generator instead of 6 hand-coded files:
  - Shared SEO scaffolding (Article/ItemList/BreadcrumbList/FAQPage schema,
    hreflang, canonical, OG, manifest links) — one source of truth.
  - One template means consistent UX + cheaper to update later.

Why per-neighborhood hand-written content instead of templated descriptions:
  - Google's Helpful Content classifier (March 2024) penalises near-identical
    templates. Each neighborhood gets a genuinely distinct intro, FAQs,
    and venue selection so the pages are not "thin" derivatives.

Run:
  python3 scripts/generate-de-neighborhoods.py

Outputs files at:
  /de/biergaerten-kreuzberg/index.html
  /de/biergaerten-mitte/index.html
  /de/biergaerten-prenzlauer-berg/index.html
  /de/biergaerten-friedrichshain/index.html
  /de/biergaerten-charlottenburg/index.html
  /de/biergaerten-neukoelln/index.html
"""
from pathlib import Path
import json
import textwrap

ROOT = Path(__file__).resolve().parent.parent

# ─── Content per neighborhood ──────────────────────────────────────────────
# Each entry produces one page. The fields are deliberately rich so that
# the rendered pages have ≥800 unique words and a distinct character —
# the bare minimum for Google's Helpful Content threshold.
#
# Volumes from docs/zoey-keywords.md.
NEIGHBORHOODS = [
    {
        "slug": "biergaerten-kreuzberg",
        "kw": "biergarten kreuzberg",  # ~1,300/mo, KD 28
        "h1": "Biergärten in Kreuzberg",
        "title": "Die besten Biergärten in Kreuzberg (Live-Sonnen-Check)",
        "meta_desc": "Die besten Biergärten in Kreuzberg — Golgatha, Freischwimmer, Südstern und mehr. Jeder live gegen Sonnenstand und Wolkendecke geprüft.",
        "subtitle": "Vom Hügel im Viktoriapark bis zum Steg am Landwehrkanal — Kreuzbergs Sonnen-Biergärten, jeder live geprüft.",
        "intro": [
            "Kreuzberg ist topographisch der einzige Bezirk Berlins, in dem die Sonne ein Argument für die Auswahl des Biergartens ist. Der Bezirk hat einen echten Hügel (den Kreuzberg im Viktoriapark, 66 m), einen Kanal mit West-Ausrichtung (den Landwehrkanal), und genug späten 19.-Jahrhundert-Bestand, dass die Hinterhof-Verschattung am späten Nachmittag knallhart zuschlägt.",
            "Die Konsequenz: Kreuzberger Biergärten sortieren sich entlang der Wasserlinie und der Hänge. Wer Sonne sucht, geht entweder hoch (Golgatha am Viktoriapark, Brauhaus Südstern an der Hasenheide) oder ans Wasser (Freischwimmer am Kanal). Die Innenhof-Spots fallen ab 16 Uhr in den Schatten der Vorderhäuser — das ist die Grundregel des Bezirks.",
        ],
        "venues": [
            {
                "name": "Golgatha", "addr": "Dudenstraße 40-64, 10965 Berlin",
                "context": "Südhang des Viktoriaparks · West offen",
                "desc": "Der höchste Biergarten Kreuzbergs — am Südhang des Berges, mit Spätnachmittagssonne durch die offene Westflanke des Parks. DJs an Sommerabenden, an Sonntagen die langsame Ausgeh-Crowd. Vom Mehringdamm in 10 Minuten zu erlaufen."
            },
            {
                "name": "Freischwimmer", "addr": "Vor dem Schlesischen Tor 2a, 10997 Berlin",
                "context": "umgebautes Bootshaus am Landwehrkanal · West offen",
                "desc": "Der ehrlichste West-Biergarten der Stadt — die Holz-Decks ragen über den Kanal, keine Häuserzeile zwischen dir und der Sonne, also volle Spätnachmittags-Sonne ab ca. 14 Uhr. Brunch am Wochenende, Cocktails abends."
            },
            {
                "name": "Brauhaus Südstern", "addr": "Hasenheide 69, 10967 Berlin",
                "context": "am Volkspark Hasenheide · ganzjährig · Süd-West offen",
                "desc": "Eine echte Berliner Brauhaus-Seltenheit mit eigenem Pils und Dunkel und einer kleinen, verlässlich sonnigen Vorderterrasse, die direkt in die Hasenheide übergeht. Anders als die meisten Biergärten läuft Südstern ganzjährig. Pubküche tragfähig bis ins Abendessen."
            },
            {
                "name": "Café am Engelbecken", "addr": "Michaelkirchplatz, 10179 Berlin",
                "context": "am Engelbecken-See · zwischen Mitte und Kreuzberg · Süd offen",
                "desc": "Ein kleines Café mit grosser Sonnenterrasse direkt am Engelbecken-See, einem der Berliner Geheim-Gewässer. Süd-Ausrichtung mit Blick aufs Wasser, alte Bäume rahmen die Terrasse, und die Karte (Frühstück, Salate, Kaffee) ist solide und fair bepreist. Kein klassischer Biergarten, aber wenn du Kreuzberg ohne Touristen-Crowd willst, ist das die Antwort."
            },
            {
                "name": "Hopfenreich Hof", "addr": "Sorauer Straße 31, 10997 Berlin",
                "context": "Hinterhof-Bar mit Bierfokus · Süd-Ost",
                "desc": "Eine der ersten Berliner Craft-Beer-Bars, mit kleinem Hinterhof, der vormittags Sonne abbekommt. 20+ Hähne, gut kuratierte Karte, eher Bierkenner-Publikum als allgemeine Biergarten-Crowd. Klein, also früh kommen oder mit dem dahinter liegenden Restaurant-Bereich kombinieren."
            },
        ],
        "faqs": [
            {
                "q": "Welcher Biergarten in Kreuzberg hat die meiste Sonne?",
                "a": "Freischwimmer hat die offenste West-Lage am Landwehrkanal — Sonne ab Mittag bis Sonnenuntergang. Golgatha am Viktoriapark bekommt durch die offene Westflanke des Parks ähnlich verlässlich Spätnachmittagssonne. Brauhaus Südstern hat morgens und mittags Sonne durch die Süd-West-Ausrichtung."
            },
            {
                "q": "Sind Kreuzberger Biergärten an der Spree?",
                "a": "Genauer am Landwehrkanal — die Spree begrenzt Kreuzberg im Norden, aber das Spreeufer dort ist eher Verkehrsader als Biergarten-Region. Der Landwehrkanal ist die wahre Wasserader: Freischwimmer und Café Engelbecken liegen direkt daran. Die berühmte Admiralbrücke (sunset spot) ist auch am Kanal — aber kein Biergarten."
            },
            {
                "q": "Welcher Kreuzberger Biergarten ist ganzjährig geöffnet?",
                "a": "Brauhaus Südstern als einziger der klassischen Biergärten — Heizpilze in der Übergangszeit, Pubküche bis spätabends. Hallesches Haus (Café/Kantine) hat eine ganzjährig nutzbare Süd-Ost-Terrasse mit beheizten Plätzen. Die anderen schließen typischerweise im Oktober."
            },
            {
                "q": "Welcher Kreuzberger Biergarten ist günstig?",
                "a": "Golgatha am Viktoriapark hält die Klassik-Biergarten-Preise — Pils um 4 €, Currywurst um 5 €. Brauhaus Südstern ist mittelpreisig, aber die Hausbiere sind den Preis wert. Freischwimmer und die Café-Restaurants liegen darüber, eher 6+ € fürs Pils."
            },
        ],
    },
    {
        "slug": "biergaerten-mitte",
        "kw": "biergarten mitte",  # ~880/mo, KD 30
        "h1": "Biergärten in Mitte",
        "title": "Die besten Biergärten in Berlin-Mitte (Live-Sonnen-Check)",
        "meta_desc": "Die besten Biergärten in Berlin-Mitte — Zollpackhof, Strandbar Mitte, Café am Neuen See. Jeder live gegen Sonnenstand und Wolkendecke geprüft.",
        "subtitle": "Vom Spreeufer am Kanzleramt bis zum Tiergartenteich — Mittes Sonnen-Biergärten, jeder live geprüft.",
        "intro": [
            "Mitte ist der Bezirk, in dem Touristen ihre Biergarten-Bilder machen — und das aus gutem Grund. Die kombinierte Wasserfront aus Spree, Spreebogen und Tiergarten-Teichen liefert eine Dichte an offenen Sonnen-Lagen, die kein anderer innerstädtischer Bezirk hat. Vorderhäuser blockieren weniger, Hinterhöfe haben hier seltener die typisch Berliner Tiefe.",
            "Das Trade-off: An sonnigen Wochenenden ist die Tourismus-Schicht spürbar. Locals weichen zwischen 15 und 18 Uhr auf die Bezirke aus, die seltener im Reiseführer stehen. Die fünf unten sind unsere Mittellösung — alle haben echte Sonne, alle haben ein Mindestmaß an Berliner-Authentizität auch unter Sommer-Wochenend-Bedingungen.",
        ],
        "venues": [
            {
                "name": "Zollpackhof", "addr": "Elisabeth-Abegg-Straße 1, 10557 Berlin",
                "context": "an der Spree gegenüber Bundeskanzleramt · Süd-West offen",
                "desc": "Der größte Biergarten im Regierungsviertel — eine offene Wiese am Spreeufer, ohne hohe Häuser im Westen, also Sonne von Vormittag bis Sonnenuntergang. Bayerische Karte, Maß-Krüge, kein Schnickschnack. Ideal für Pause-zwischen-Sightseeing, an sonnigen Samstagen mit langen Wartezeiten."
            },
            {
                "name": "Café am Neuen See", "addr": "Lichtensteinallee 2, 10787 Berlin",
                "context": "am Tiergarten-Teich · technisch Tiergarten, Mitte-angrenzend · Süd offen",
                "desc": "Der Sonntags-Standard für Mitte-Bewohner. Direkt am Wasser, mit Ruderbooten, Spielplatz und 1.000+ Außenplätzen. Die südliche Uferseite kriegt den ganzen Mittag Sonne. Karte: deutsche Klassiker plus Pizza vom Steinofen. Familienfreundlich. An sonnigen Wochenenden erst nach 17 Uhr realistisch."
            },
            {
                "name": "Strandbar Mitte", "addr": "Monbijoustraße 3, 10117 Berlin",
                "context": "Sandstrand am Spreeufer gegenüber Bode-Museum · Süd offen",
                "desc": "Berlins erste Strandbar (seit 2002), und immer noch eine der ehrlichsten Sonnen-Adressen Mittes. Echter Sand, Liegestühle, Salsa-Tanzboden, Sonnen-Oberdeck mit Sonne von Vormittag bis Sonnenuntergang. Strenggenommen kein Biergarten, aber funktional dasselbe Konzept."
            },
            {
                "name": "Hofbräu Berlin", "addr": "Karl-Liebknecht-Straße 30, 10178 Berlin",
                "context": "ein Block vom Alexanderplatz · Süd offen",
                "desc": "Die bayerische Filiale mit Münchner Treue: Lederhosen, Blaskapelle abends, Maß-Krüge. Der Außenbiergarten neben dem Gebäude bekommt zwischen 12 und 17 Uhr ordentlich Sonne, bevor die hohen Nachbarn westlich Schatten werfen. Touristisch geprägt, aber funktioniert für große Gruppen ohne Reservierung."
            },
            {
                "name": "Ständige Vertretung", "addr": "Schiffbauerdamm 8, 10117 Berlin",
                "context": "am Spreeufer am Reichstagsufer · Süd-West",
                "desc": "Die rheinische Botschaft in Berlin: Kölsch im 0,2-Stange-Glas, rheinische Karte (Halver Hahn, Rheinischer Sauerbraten) und eine Spreeufer-Terrasse mit Blick auf Reichstag und Friedrichstadt-Palast. Sonne ab späten Vormittag. Eher Politik-Establishment-Kantine als Touristen-Spot, was die Mischung interessant macht."
            },
        ],
        "faqs": [
            {
                "q": "Welcher Biergarten in Berlin-Mitte hat die meiste Sonne?",
                "a": "Zollpackhof hat die offenste Lage — direkt an der Spree, ohne hohe Gebäude westlich, Sonne den ganzen Tag bis Sonnenuntergang. Strandbar Mitte hat ebenfalls Süd-Ausrichtung am Spreeufer, mit Sonnen-Oberdeck. Café am Neuen See ist technisch Tiergarten, aber funktional die längste Sonnen-Lage in Mitte-Nähe."
            },
            {
                "q": "Welche Biergärten in Mitte sind am Wasser?",
                "a": "Zollpackhof an der Spree (Spreebogen), Strandbar Mitte am Spreeufer gegenüber dem Bode-Museum, Ständige Vertretung am Schiffbauerdamm-Ufer, Café am Neuen See am Tiergarten-Teich. In Mitte ist der Wasseranschluss eher die Regel als die Ausnahme."
            },
            {
                "q": "Welcher Biergarten in Mitte ist familienfreundlich?",
                "a": "Café am Neuen See deutlich vor allen anderen — Spielplatz, Ruderbootverleih, viel Platz, Karte mit Kindergerichten. Zollpackhof funktioniert auch, weil die Wiese viel Bewegungsraum lässt. Hofbräu Berlin und Ständige Vertretung sind eher abend-orientiert, weniger ideal mit Kindern."
            },
        ],
    },
    {
        "slug": "biergaerten-prenzlauer-berg",
        "kw": "biergarten prenzlauer berg",  # ~720/mo, KD 28
        "h1": "Biergärten in Prenzlauer Berg",
        "title": "Die besten Biergärten in Prenzlauer Berg (Live-Sonnen-Check)",
        "meta_desc": "Die besten Biergärten in Prenzlauer Berg — Prater Garten, Mauergarten, Deck 5 und mehr. Live gegen Sonnenstand geprüft.",
        "subtitle": "Vom ältesten Biergarten Berlins bis zum Parkdeck-Rooftop — Prenzlauer Bergs Sonnen-Spots.",
        "intro": [
            "Prenzlauer Berg hat ein eigenartiges Sonnen-Profil. Der Bezirk ist überwiegend Wilhelmische Bauklasse — fünf bis sechs Stockwerke, dichte Blockstruktur, viele Hinterhöfe — aber mit auffallend vielen Eckparzellen, die offene Sonnenseiten erlauben. Die zwei großen Parks (Volkspark Friedrichshain im Süden, Mauerpark im Westen) liefern dazu zwei verlässliche Sonnen-Magnete an den Bezirksrändern.",
            "Was P-Berg von Mitte unterscheidet: Hier sitzen mehr Locals als Touristen, die Stammgast-Quote ist hoch, und die Karte tendiert zu hipper Brauhaus-Variante (eigene Hausbiere, Saisonkarten) statt klassischer Bayern-Schiene. Wer einen Biergarten im klassischen Sinn sucht — Kastanien, lange Holzbänke, Bargeld-Pils — ist im Prater richtig. Alle anderen sind eher Brauhaus-Garten oder Café-Terrasse mit Bier auf der Karte."
        ],
        "venues": [
            {
                "name": "Prater Garten", "addr": "Kastanienallee 7-9, 10435 Berlin",
                "context": "Berlins ältester Biergarten · 1837 gegründet · Innenhof",
                "desc": "Der prototypische Berliner Biergarten — Kastanien, Kies, lange Holzbänke und Pils aus einer kleinen Holzbude. Der Innenhof liegt teils im Kastanienschatten (Feature, kein Bug, im Hochsommer), die Außenränder bekommen Mittagssonne. Saison: April bis September, bei brauchbarem Wetter. Cash bevorzugt."
            },
            {
                "name": "Deck 5", "addr": "Schönhauser Allee 80, 10439 Berlin",
                "context": "Parkdeck der Schönhauser Allee Arcaden · 360° offen",
                "desc": "Die unprätentiöse Antwort auf Klunkerkranich: ein Parkdeck mit Holzmöbeln, Sand und einem Tresen. Komplett offen in alle Himmelsrichtungen — Sonne den ganzen Tag — mit Blick über halb P-Berg bis zum Fernsehturm. Eintritt frei, Karte: Bier-Pizza-Bowls. Eher Locals als Touristen."
            },
            {
                "name": "Mauergarten", "addr": "Bernauer Straße, 10435 Berlin",
                "context": "vor dem Mauerpark · West-Süd offen · saisonal",
                "desc": "Der inoffizielle Sommer-Empfang Prenzlauer Bergs: ein Saison-Biergarten direkt am Mauerpark-Eingang, vom Mauerpark-Trubel räumlich getrennt aber mental im selben Universum. Sonntags Karaoke-Tröpfler vom Park nebenan. Sonne durch die offene Westflanke des Parks ab Spätnachmittag."
            },
            {
                "name": "Anna Blume", "addr": "Kollwitzstraße 83, 10435 Berlin",
                "context": "Café mit Eckterrasse · Süd-Ost",
                "desc": "Eine der berühmtesten Eckterrassen P-Bergs, mit Blumenladen-Front und einer Süd-Ost-Terrasse, die schon morgens Sonne fängt und bis weit in den Nachmittag hält. Frühstück ist Sonntags-Ritual-Niveau. Strenggenommen Café, aber das Bier auf der Karte und die Außensitz-Quote macht es funktional zum Biergarten."
            },
            {
                "name": "Restaurant Wasserturm", "addr": "Knaackstraße 22, 10405 Berlin",
                "context": "neben dem Wasserturm · Süd-West",
                "desc": "Italienisch-orientiert, mit einer Außenterrasse direkt am Fuß des Wasserturms. Süd-West-Ausrichtung, also Mittagssonne durchgängig, und die Lage am höchsten Punkt P-Bergs gibt dem Ganzen einen Hauch Hügel-Atmosphäre. Eher Restaurant als klassischer Biergarten, aber das Pils ist da und die Sonne stimmt."
            },
        ],
        "faqs": [
            {
                "q": "Welcher Biergarten in Prenzlauer Berg hat die längste Sonne?",
                "a": "Deck 5 — durch die 360°-Lage auf einem Parkdeck gibt es keine Verschattung. Praktisch heißt das: Sonne von Sonnenaufgang bis Sonnenuntergang, im Sommer 14+ Stunden. Mauergarten am Mauerpark-Eingang hat verlässliche Spätnachmittagssonne. Im Prater ist die Sonne wegen der Kastanien Teilzeit."
            },
            {
                "q": "Welche Biergärten in Prenzlauer Berg sind kinderfreundlich?",
                "a": "Prater Garten ist tagsüber familienfreundlich — viel Platz, schattige Bereiche, Kindergerichte auf der Karte. Mauergarten am Mauerpark hat den Park direkt nebenan als Bewegungsraum. Deck 5 ist eher abendlich, weniger ideal mit kleinen Kindern. Anna Blume und Wasserturm sind funktional Restaurants — passt mit ruhigen Kindern."
            },
            {
                "q": "Welcher Prenzlauer-Berg-Biergarten hat eigene Hausbiere?",
                "a": "Brewing Berlin (kleiner Tap Room in der Pappelallee) und einige Pop-up-Biergärten arbeiten mit Berliner Brauereien wie Lemke, Heidenpeters oder Brewbaker. Prater Garten serviert Schultheiss in der Klassik-Variante. Deck 5 rotiert die Hähne saisonal, oft mit Berliner Brauereien."
            },
        ],
    },
    {
        "slug": "biergaerten-friedrichshain",
        "kw": "biergarten friedrichshain",  # ~480/mo, KD 24 — easiest target
        "h1": "Biergärten in Friedrichshain",
        "title": "Die besten Biergärten in Friedrichshain (Live-Sonnen-Check)",
        "meta_desc": "Die besten Biergärten in Friedrichshain — Schönbrunn, Holzmarkt, Cassiopeia und mehr. Live gegen Sonnenstand und Wolkendecke geprüft.",
        "subtitle": "Vom Volkspark bis zum Spreeufer am RAW — Friedrichshains Biergärten, jeder live geprüft.",
        "intro": [
            "Friedrichshain ist topographisch zweigeteilt: der Volkspark im Norden mit echter Park-Tiefe und alten Bäumen, das Spreeufer im Süden mit dem RAW-Gelände, Holzmarkt und East-Side-Touristen-Strom. Beide Hälften haben verlässliche Sonnen-Lagen — der Volkspark, weil die Wiesen weit genug sind, dass die Hinterhaus-Verschattung außen vor bleibt; das Spreeufer, weil die Spree selbst keine Schatten wirft.",
            "Friedrichshainer Biergärten haben die spezifische Eigenart, oft in größere Kultur-Komplexe eingebettet zu sein (Holzmarkt, RAW-Gelände, Yaam), wo der Biergarten nur eine Funktion neben Bühnen, Kunsträumen und Clubs ist. Das ist typisch für den Bezirk — und das beste Argument dafür, hier am Wochenende Stunden statt Minuten zu verbringen.",
        ],
        "venues": [
            {
                "name": "Schönbrunn", "addr": "Am Schwanenteich 1, 10249 Berlin",
                "context": "im Volkspark Friedrichshain · am Schwanenteich",
                "desc": "Tief im Volkspark Friedrichshain, am Schwanenteich am Fuß des Mont Klamott. Sommerabends füllt sich die Terrasse mit der Friedrichshainer Feierabend-Crowd — halb Biergarten, halb Restaurant, halb Wohnzimmer der Nachbarschaft. Die alten Bäume beschatten die halben Plätze, die andere Hälfte liegt nachmittags voll in der Sonne. Saisonal stark wechselnde Karte mit überdurchschnittlich vielen vegetarischen Optionen."
            },
            {
                "name": "Holzmarkt 25", "addr": "Holzmarktstraße 25, 10243 Berlin",
                "context": "Kultur-Dorf am Spreeufer · Süd-West offen",
                "desc": "Streng genommen kein einzelner Biergarten, sondern eine ganze kleine Stadt: das Kater Blau, der Pampa, mehrere kleine Bars und das Café Kiezbar — alles zwischen Spree und East-Side-Gallery. Die Spreefront hat verlässliche Mittagssonne und ist im Sommer eine der schönsten Wasser-Adressen der Stadt. Eintritt fällt punktuell für Konzerte an."
            },
            {
                "name": "Cassiopeia (RAW)", "addr": "Revaler Straße 99, 10245 Berlin",
                "context": "Kulturzentrum auf dem RAW-Gelände · Innenhof",
                "desc": "Der punkige Hinterhof des RAW-Geländes — Industrieruine, Graffiti-Wände, Bierbänke aus zweiter Hand, und ein Biergarten, der eher Nebeneffekt ist als Hauptattraktion. Sonnen-Lage uneinheitlich (Innenhof-Geometrie), aber spezifisch schöne Spätnachmittagsstunden zwischen 16 und 19 Uhr. Konzerte und Open-Airs im Sommer."
            },
            {
                "name": "Yaam", "addr": "An der Schillingbrücke 3, 10243 Berlin",
                "context": "Karibik-Strandbar am Spreeufer · West-Süd offen",
                "desc": "Reggae-Strandbar mit Sand, Liegestühlen, Karibik-Karte und einer Spreefront, die von Mittag bis Sonnenuntergang volle Sonne abbekommt. Strenggenommen kein Biergarten, funktional aber dieselbe Use-Case-Kategorie. Konzerte fast jedes Wochenende. Eintritt frei tagsüber, abends bei Konzerten 5–10 €."
            },
            {
                "name": "Brauhaus Lemke (RAW)", "addr": "Karl-Marx-Allee 36, 10178 Berlin",
                "context": "Hausbrauerei mit Außenbereich · Süd-Ost",
                "desc": "Berliner Hausbrauerei mit eigener Pils, Hefeweizen und Saison-Bieren. Der Außenbereich am Karl-Marx-Allee-Standort hat eine Süd-Ost-Terrasse, die vormittags und mittags Sonne hat, am Spätnachmittag aber von der Karl-Marx-Allee-Westseite verschattet wird. Karte: deftiger Brauhaus-Standard auf gehobenem Niveau."
            },
        ],
        "faqs": [
            {
                "q": "Welche Biergärten in Friedrichshain sind am Wasser?",
                "a": "Holzmarkt 25 hat die längste Spreefront — mehrere kleine Bars über Stege und Decks am Wasser. Yaam (an der Schillingbrücke) ist ebenfalls direkt an der Spree. Schönbrunn liegt am Schwanenteich im Volkspark, also am Wasser im Park-Sinne. Cassiopeia und Brauhaus Lemke sind beide ohne Wasseranschluss."
            },
            {
                "q": "Welcher Biergarten in Friedrichshain ist am authentischsten?",
                "a": "Schönbrunn — eingebettet in den Volkspark, mit echtem Stammgast-Anteil aus der Nachbarschaft, weniger Touristen-Schicht. Cassiopeia ist authentisch in der RAW-Tradition (alternativ, punkig), aber spezifischer Geschmack. Holzmarkt und Yaam haben wegen der East-Side-Lage höheren Touristen-Anteil."
            },
            {
                "q": "Welcher Friedrichshainer Biergarten hat eigene Hausbiere?",
                "a": "Brauhaus Lemke ist die einzige echte Hausbrauerei der Liste — Pils, Hefeweizen, Saison-Bock. Holzmarkt rotiert mit Berliner Craft-Brauereien (Heidenpeters, Stone). Schönbrunn führt die Klassiker (Schultheiss, Berliner Pilsner). Cassiopeia ist preislich orientiert eher Standard-Pils."
            },
        ],
    },
    {
        "slug": "biergaerten-charlottenburg",
        "kw": "biergarten charlottenburg",  # ~390/mo, KD 24
        "h1": "Biergärten in Charlottenburg",
        "title": "Die besten Biergärten in Charlottenburg (Live-Sonnen-Check)",
        "meta_desc": "Die besten Biergärten in Charlottenburg — Schleusenkrug, Schloss Charlottenburg, Lietzensee. Live gegen Sonnenstand und Wolkendecke geprüft.",
        "subtitle": "Vom Tiergarten-Schleusenkrug bis zum Lietzensee — Charlottenburgs Biergärten, jeder live geprüft.",
        "intro": [
            "Charlottenburg ist der Bezirk der versteckten Sonnen-Lagen. Anders als Mitte oder Kreuzberg ist die Bauklasse niedriger (drei bis vier Stockwerke, viel Gründerzeit-Bestand mit großen Eckparzellen) und die Wasserdichte höher als allgemein bekannt — Spree, Landwehrkanal-West, Lietzensee, Schlossteich am Charlottenburger Schloss. Wer hier Sonne sucht, geht selten in einen Innenhof; der Bezirk lebt von Park-, See- und Schleusen-Lagen.",
            "Touristisch ist Charlottenburg zweigeteilt: Ku'damm-Bereich (touristisch, hochpreisig, oft im Schatten der westlichen Skyline) und Park/See-Bereich (eher locals, lange Sonne). Die Liste unten konzentriert sich auf die zweite Hälfte — wer einen Charlottenburger Biergarten mit echter Sonne will, geht weg vom Ku'damm.",
        ],
        "venues": [
            {
                "name": "Schleusenkrug", "addr": "Müller-Breslau-Straße, 10623 Berlin",
                "context": "an der Tiergarten-Schleuse am Landwehrkanal · West offen",
                "desc": "Charlottenburgs zuverlässigster West-Biergarten. Vom Bahnhof Zoo in fünf Minuten erreichbar, eingeklemmt zwischen Tiergarten und Zoo, neben der Schleuse mit ihrem Industrie-Charme. Spätnachmittagssonne durchgängig bis 19 Uhr im Sommer, weil der Landwehrkanal westlich freie Sicht lässt. Klassische Biergartenkarte, Boote ziehen einen Meter neben dir vorbei."
            },
            {
                "name": "Schlossgartenrestaurant Charlottenburg", "addr": "Spandauer Damm 22, 14059 Berlin",
                "context": "im Schlossgarten · Süd offen",
                "desc": "Der historisch barocke Biergarten der Stadt — direkt im Schlossgarten Charlottenburg, mit Blick auf den Karpfenteich und die Sphinx-Statuen. Süd-Ausrichtung mit voller Mittagssonne, alte Bäume rahmen die Plätze ohne sie zu beschatten. Karte: gehoben-deutsch (Schnitzel, Sauerbraten, Spargel saisonal). Eltern-zu-Besuch-Niveau, einer der schönsten Biergärten im historischen Berlin."
            },
            {
                "name": "Restaurant am Lietzensee", "addr": "Wundtstraße 11, 14057 Berlin",
                "context": "am Lietzensee-Ufer · Süd-Ost offen",
                "desc": "Eine der schönsten See-Lagen West-Berlins, mit einer Süd-Ost-Terrasse direkt am Wasser. Vormittagssonne durchgängig bis Mittag, danach gefiltertes Licht durch die Uferbäume. Karte: italienisch-mediterran. Der Lietzensee ist einer der unterbewertetsten Berliner Seen — viel Park drumherum, kaum Touristen, lange Sonnenstunden im Frühling."
            },
            {
                "name": "Café Buchwald", "addr": "Bartningallee 29, 10557 Berlin",
                "context": "am Spreeufer beim Hansaviertel · Süd-West",
                "desc": "Eine 1852 gegründete Konditorei mit Außenterrasse direkt am Spreeufer, in einer überraschend ruhigen Charlottenburger Ecke. Süd-West-Ausrichtung, also Mittag bis Sonnenuntergang in der Sonne. Karte: Klassik-Konditorei (Baumkuchen ist der Standard-Tipp), aber Bier und kleine Speisen auch da. Funktional irgendwo zwischen Café und Biergarten — und genau dadurch interessant."
            },
            {
                "name": "Loretta im Garten", "addr": "Knesebeckstraße 9, 10623 Berlin",
                "context": "Hinterhof in der City-West · Süd-Ost · klein",
                "desc": "Klein und versteckt — der Charlottenburger Mini-Biergarten, in einem Hinterhof zwischen Knesebeck- und Savignyplatz. Süd-Ost-Ausrichtung, also Sonne von Vormittag bis frühen Nachmittag, danach gefiltert durch die Hinterhof-Geometrie. Eher Café als Biergarten, aber mit dem Pils in der Karte und der entspannten City-West-Atmosphäre. Stammgast-Anteil hoch."
            },
        ],
        "faqs": [
            {
                "q": "Welcher Biergarten in Charlottenburg ist am Wasser?",
                "a": "Schleusenkrug am Landwehrkanal/an der Tiergarten-Schleuse, Restaurant am Lietzensee am See, Café Buchwald am Spreeufer beim Hansaviertel. Charlottenburg hat überraschend viel Wasser für einen Bezirk, der in Reiseführern als 'City-West' geführt wird."
            },
            {
                "q": "Welcher Charlottenburger Biergarten ist historisch?",
                "a": "Schlossgartenrestaurant Charlottenburg liegt im Schlosspark des barocken Schlosses und bietet die historisch tiefste Lage. Café Buchwald ist seit 1852 in Familienhand. Schleusenkrug nutzt die Schleusen-Infrastruktur seit dem späten 19. Jahrhundert. Anders als Prenzlauer Berg oder Mitte ist Charlottenburg wegen der späten Eingemeindung (1920) historisch eigentlich eigene Geschichte."
            },
            {
                "q": "Wie kommt man zum Schleusenkrug?",
                "a": "Vom Bahnhof Zoo in fünf Minuten zu Fuß: Hardenbergplatz Richtung Tiergarten überqueren, an den Tiergarten-Eingängen vorbei zur Müller-Breslau-Straße, dann zum Wasser. Vom S-Bahnhof Tiergarten ebenfalls etwa zehn Minuten. Auto-Parken in der Umgebung schwierig (Zoo, Bahnhof Zoo)."
            },
        ],
    },
    {
        "slug": "biergaerten-neukoelln",
        "kw": "biergarten neukölln",  # ~590/mo, KD 26
        "h1": "Biergärten und Sonnenterrassen in Neukölln",
        "title": "Biergärten in Neukölln — die sonnigsten Spots, live geprüft | Sunmaxxing",
        "meta_desc": "Die besten Biergärten und Sonnenterrassen in Neukölln — Klunkerkranich, Hallmann & Klee, Birgit & Bier. Live geprüft gegen Sonnenstand.",
        "subtitle": "Vom Klunkerkranich-Dach bis zu den Rixdorfer Hinterhöfen — Neuköllns Sonnen-Spots.",
        "intro": [
            "Neukölln ist der Bezirk, in dem 'Biergarten' im klassischen Bayern-Sinn nicht ganz die richtige Kategorie ist. Statt Kastanien und Maß-Krügen findest du hier eher Dachterrassen, Strand-ähnliche Spree-Bars, Hinterhof-Cafés und kuratierte Sun-Terraces — der Bezirk hat sich seine eigene Sonnen-Architektur gebaut, eher inspiriert von Brooklyn und Lissabon als von München.",
            "Der Effekt: Wer in Neukölln nach 'Biergarten' sucht, sucht eigentlich nach 'Außensitzen mit Sonne und Bier'. Die Liste unten ist entsprechend gemischt — Rooftop, Hinterhof, Strandbar — und legt mehr Wert auf die echte Sonnen-Lage als auf Biergarten-Reinheit. Genau das macht den Bezirk übrigens auch SEO-mäßig interessant: 'Sonnenterrasse Neukölln' ist die ehrlichere Suche.",
        ],
        "venues": [
            {
                "name": "Klunkerkranich", "addr": "Karl-Marx-Straße 66, 12043 Berlin",
                "context": "Dachterrasse über den Neukölln Arcaden · West-Süd offen",
                "desc": "Die kanonische Neuköllner Sonnen-Adresse. Ein Kulturdachgarten über einem Einkaufszentrum, mit Hochbeeten, Kies, Holzmöbeln, einer kleinen Bühne und einem DJ-Pult. Westflanke komplett offen — keine Verschattung — also Sonne von Mittag bis Sonnenuntergang. An sonnigen Wochenenden lange Schlange am Aufzug. Eintritt 4–6 € am Wochenende, Cash bevorzugt."
            },
            {
                "name": "Hallmann & Klee", "addr": "Böhmische Straße 13, 12055 Berlin",
                "context": "Hinterhof in Rixdorf · Süd offen",
                "desc": "Eine versteckte Hofterrasse in Rixdorf — der historische Böhmen-Kern Neuköllns mit kleinen Häusern und Kopfsteinpflaster. Süd-Ausrichtung mit drei alten Bäumen, die für gefiltertes Licht statt voller Schatten sorgen. Frühstück ist eines der besten der Stadt — auf einer Liste mit Pasanella, Roamers, Café Frieda. Klein, also vor 11 Uhr am Wochenende kommen oder reservieren."
            },
            {
                "name": "Birgit & Bier", "addr": "Schleusenufer 3, 12435 Berlin",
                "context": "Spreeufer am Treptower Park · technisch Treptow, von Neukölln in 10 Min · West-Süd offen",
                "desc": "Strenggenommen Treptow, aber von Neukölln-Süd in zehn Minuten erreicht und mental Teil derselben Szene. Beach-Bar mit Liegestühlen, Sand, Bühne und einer Westseite, die von Mittag bis Sonnenuntergang volle Sonne abbekommt. Konzerte und DJ-Sets im Sommer. Eintritt punktuell, Drinks fair."
            },
            {
                "name": "Hofklub am Tempelhofer Feld", "addr": "Oderstraße, 12049 Berlin",
                "context": "Saisonbiergarten am Tempelhofer-Feld-Eingang · West offen",
                "desc": "Ein Sommer-Saisonbiergarten am Oderstraßen-Eingang des Tempelhofer Felds. Die Westflanke des Felds ist komplett offen, also Sonne den ganzen Spätnachmittag — eine der ehrlichsten West-Lagen Neuköllns. Kleines Programm (Karte: Pils, Wein, Snacks), aber die Lage zwischen 'gerade vom Feld zurück' und 'auf dem Weg zum Klunkerkranich' macht es zum logischen Stop."
            },
            {
                "name": "Café Sing Blackbird", "addr": "Sanderstraße 11, 12047 Berlin",
                "context": "Vintage-Café mit Außenbereich · Süd-Ost",
                "desc": "Eine Vintage-Boutique mit angeschlossenem Café im Reuterkiez, mit kleiner Süd-Ost-Terrasse, die schon morgens Sonne fängt. Frühstück ist hipster-zentral aber gut gemacht, Kaffee Spezialität. Klein, also entweder früh kommen oder den Trick lernen, dass die hinteren Sitze immer länger Sonne kriegen."
            },
        ],
        "faqs": [
            {
                "q": "Welche Biergärten in Neukölln sind kostenlos?",
                "a": "Hallmann & Klee, Café Sing Blackbird und Hofklub am Tempelhofer Feld haben keinen Eintritt — Verzehrpflicht reicht. Klunkerkranich nimmt 4–6 € Eintritt am Wochenende. Birgit & Bier hat punktuell Eintritt bei Konzerten, sonst frei. Die Cafés in Rixdorf sind durchgehend ohne Eintritt zugänglich."
            },
            {
                "q": "Welcher Neuköllner Biergarten hat die meiste Sonne?",
                "a": "Klunkerkranich vom späten Vormittag bis Sonnenuntergang, durch die offene Dachlage. Hofklub am Tempelhofer Feld hat verlässliche West-Lage durch das offene Feld. Birgit & Bier (technisch Treptow, aber von Süd-Neukölln aus erreichbar) hat den ganzen Nachmittag Sonne durch die Spree-West-Lage."
            },
            {
                "q": "Welche Sonnenterrasse in Neukölln ist familienfreundlich?",
                "a": "Hofklub am Tempelhofer Feld hat das ganze Feld nebenan als Spielgelände. Hallmann & Klee in Rixdorf hat ruhige Hinterhof-Atmosphäre, geht mit ruhigen Kindern. Klunkerkranich ist tagsüber familienfreundlich, abends eher Erwachsenen-orientiert. Birgit & Bier ist abends Konzert-Bar, weniger ideal mit Kleinen."
            },
            {
                "q": "Was ist der Unterschied zwischen einem Neuköllner und einem Münchner Biergarten?",
                "a": "Neuköllner Sonnen-Spots sind selten klassische Biergärten im Münchner Sinn (Kastanien, Maß-Krüge, lange Holzbänke). Stattdessen sind sie eher Hinterhof-Cafés, Dach-Terrassen oder Strandbars. Wer ein klassisches Biergarten-Gefühl will, geht eher in den Prater (Prenzlauer Berg) oder zum Loretta am Wannsee. Wer Neukölln will, will den Mix aus Boutique-Café und Beach-Vibe."
            },
        ],
    },
]


# ─── Page template ─────────────────────────────────────────────────────────
def render_page(n: dict) -> str:
    canonical = f"https://sunmaxxing.com/de/{n['slug']}/"

    # Schema: ItemList with each venue as a BarOrPub.
    item_list = []
    for i, v in enumerate(n["venues"], 1):
        # Address parsing — best-effort, not strict.
        item_list.append({
            "@type": "ListItem",
            "position": i,
            "item": {
                "@type": "BarOrPub",
                "name": v["name"],
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": "Berlin",
                    "addressCountry": "DE",
                    "streetAddress": v["addr"].split(", ")[0] if ", " in v["addr"] else v["addr"],
                }
            }
        })

    article_schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "inLanguage": "de",
        "headline": n["title"],
        "description": n["meta_desc"],
        "image": "https://sunmaxxing.com/og-image.png",
        "datePublished": "2026-05-06",
        "dateModified": "2026-05-06",
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
        "name": n["h1"],
        "itemListOrder": "https://schema.org/ItemListOrderAscending",
        "numberOfItems": len(n["venues"]),
        "itemListElement": item_list,
    }
    breadcrumb_schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Sunmaxxing", "item": "https://sunmaxxing.com/de/"},
            {"@type": "ListItem", "position": 2, "name": "Biergärten in Berlin", "item": "https://sunmaxxing.com/de/biergaerten-berlin/"},
            {"@type": "ListItem", "position": 3, "name": n["h1"], "item": canonical},
        ]
    }
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "inLanguage": "de",
        "mainEntity": [
            {
                "@type": "Question",
                "name": f["q"],
                "acceptedAnswer": {"@type": "Answer", "text": f["a"]}
            }
            for f in n["faqs"]
        ]
    }

    schemas_html = "\n".join(
        f'<script type="application/ld+json">\n{json.dumps(s, ensure_ascii=False, indent=2)}\n</script>'
        for s in [article_schema, item_list_schema, breadcrumb_schema, faq_schema]
    )

    venues_html = "\n\n".join(
        textwrap.dedent(f"""\
          <article class="venue" id="{v['name'].lower().replace(' ', '-').replace('(', '').replace(')', '').replace('&', 'und').replace('ü', 'ue').replace('ö', 'oe').replace('ä', 'ae').replace('ß', 'ss')}">
            <div class="venue-head">
              <span class="venue-rank">{i:02d}</span>
              <h2>{v['name']}</h2>
            </div>
            <p class="address">{v['addr']} · {v['context']}</p>
            <p class="description">{v['desc']}</p>
            <a class="check-live" href="/de/">Sonnenstand live prüfen</a>
          </article>""")
        for i, v in enumerate(n["venues"], 1)
    )

    intro_html = "\n".join(f"  <p>{p}</p>" for p in n["intro"])

    faqs_html = "\n".join(
        textwrap.dedent(f"""\
          <details class="faq-item">
            <summary>{f['q']}</summary>
            <p>{f['a']}</p>
          </details>""")
        for f in n["faqs"]
    )

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>{n['title']} | Sunmaxxing</title>

<!-- ─── SEO ──────────────────────────────────────────────────────────────
     Targets "{n['kw']}". Generated by scripts/generate-de-neighborhoods.py
     to keep schema + scaffolding consistent across the 6 neighborhood
     pages. Per-neighborhood content (intro, venues, FAQs) is hand-written
     in the script's NEIGHBORHOODS dict.
     ────────────────────────────────────────────────────────────────────── -->
<meta name="description" content="{n['meta_desc']}">
<meta name="theme-color" content="#F5A623">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="de" href="{canonical}">
<link rel="alternate" hreflang="x-default" href="{canonical}">

<meta property="og:type" content="article">
<meta property="og:site_name" content="Sunmaxxing">
<meta property="og:title" content="{n['title']}">
<meta property="og:description" content="{n['meta_desc']}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="https://sunmaxxing.com/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="de_DE">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{n['title']}">
<meta name="twitter:description" content="{n['meta_desc']}">
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
  a.inline-link{{color:var(--shade);text-decoration:underline;text-decoration-color:var(--sun);text-decoration-thickness:2px;text-underline-offset:3px}}
  a.inline-link:hover{{color:var(--sun)}}
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
  <a href="/de/" class="wordmark"><span class="sonne">sonne</span> <span>berlin</span></a>
  <a href="/de/" class="header-cta">Live-Karte öffnen</a>
</header>

<nav class="breadcrumb" aria-label="Brotkrumen">
  <a href="/de/">Sunmaxxing</a><span class="sep">›</span><a href="/de/biergaerten-berlin/">Biergärten in Berlin</a><span class="sep">›</span><strong>{n['h1']}</strong>
</nav>

<section class="hero">
  <span class="eyebrow">Berlin · {n['h1'].split(' in ')[-1]}</span>
  <h1>{n['h1']}</h1>
  <p class="subtitle">{n['subtitle']}</p>
</section>

<section class="intro">
{intro_html}
</section>

<section class="venues">
{venues_html}
</section>

<aside class="callout">
  <div class="callout-inner">
    <h3>Welcher liegt jetzt in der Sonne?</h3>
    <p>Auf der Live-Karte rechnen wir Minute für Minute durch, welche Terrasse in {n['h1'].split(' in ')[-1]} gerade in der Sonne liegt — und welche schon im Schatten der umliegenden Gebäude steht.</p>
    <a class="callout-cta" href="/de/">Live-Karte öffnen →</a>
  </div>
</aside>

<section class="faq">
  <h3>Häufig gefragt</h3>
{faqs_html}
</section>

<section class="related">
  <h3>Andere Berliner Bezirke</h3>
  <div class="related-grid">
{render_related_links(n['slug'])}
  </div>
</section>

<footer>
  <p>Gebaut von <a href="/de/">Sunmaxxing</a> · <a href="/de/biergaerten-berlin/">Alle Berliner Biergärten</a></p>
  <p style="margin-top:8px;font-size:12px">Öffnungszeiten und Verfügbarkeit ändern sich saisonal. Vor dem Losgehen am besten direkt beim Biergarten checken.</p>
</footer>

</body>
</html>
"""


def render_related_links(current_slug: str) -> str:
    """Render up to 4 related neighborhood links, excluding the current page."""
    links = []
    for n in NEIGHBORHOODS:
        if n["slug"] == current_slug:
            continue
        links.append(f'    <a href="/de/{n["slug"]}/"><strong>{n["h1"]} →</strong><span>{n["subtitle"][:60]}…</span></a>')
        if len(links) >= 4:
            break
    return "\n".join(links)


# ─── Generate ──────────────────────────────────────────────────────────────
def main():
    for n in NEIGHBORHOODS:
        out_dir = ROOT / "de" / n["slug"]
        out_dir.mkdir(parents=True, exist_ok=True)
        html = render_page(n)
        (out_dir / "index.html").write_text(html, encoding="utf-8")
        print(f"  wrote /de/{n['slug']}/index.html  ({len(html):,} bytes)")
    print(f"\nGenerated {len(NEIGHBORHOODS)} pages.")


if __name__ == "__main__":
    main()
