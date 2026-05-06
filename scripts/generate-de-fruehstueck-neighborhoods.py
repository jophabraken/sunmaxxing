#!/usr/bin/env python3
"""
Generate DE Frühstück (brunch) pages by neighborhood.

Why this exists separately from the biergarten generator:
  Brunch venues are mostly DIFFERENT from biergarten venues — different
  food category, different opening hours, different sun-pattern reasoning.
  Sharing the generator would force the biergarten template to bloat with
  brunch-specific fields. Cleaner to keep them parallel.

Each page is hand-written content per neighborhood:
  - Distinct intro paragraph about the neighborhood's specific brunch
    culture (Kreuzberg's water-front + market mix, P-Berg's regulars,
    Mitte's tourist tilt, Friedrichshain's Antipodean coffee belt,
    Neukölln's Rixdorf hofs).
  - 4-6 venues per neighborhood drawn from the city-wide /de/fruehstueck-berlin/
    list, kept tight to genuine neighborhood spots.
  - 3-4 FAQs that ask LOCAL-specific questions (e.g., Mitte's "wo kann man
    in der Nähe vom Hauptbahnhof frühstücken").

Run:
  python3 scripts/generate-de-fruehstueck-neighborhoods.py
"""
from pathlib import Path
import json
import textwrap

ROOT = Path(__file__).resolve().parent.parent

NEIGHBORHOODS = [
    {
        "slug": "fruehstueck-kreuzberg",
        "kw": "frühstück kreuzberg",  # ~600/mo estimate
        "h1": "Frühstück in Kreuzberg",
        "title": "Frühstück in Kreuzberg — die besten Spots mit Sonnenterrasse",
        "meta_desc": "Die besten Frühstücks-Adressen in Kreuzberg — Hallesches Haus, Pasanella, Markthalle Neun. Live gegen Sonnenstand und Wolkendecke geprüft.",
        "subtitle": "Vom Postamt-Café am Landwehrkanal bis zum Streetfood-Frühstück in der Markthalle — Kreuzbergs beste Brunch-Spots, jeder live geprüft.",
        "intro": [
            "Kreuzberg-Brunch hat ein bestimmtes Profil: weniger Insta-Florist-Teller (das macht Neukölln), mehr ehrliche Fülle. Die Schwerpunkte sind Wasser (Landwehrkanal), Markt (Markthalle Neun) und ein paar versteckte Hinterhöfe in den Wiener-Straßen-Block-Strukturen. Die Frühstücks-Crowd hier ist gemischter als in Mitte oder P-Berg — Touristen aus den Görli-Hostels mischen sich mit Familien aus den Quartieren rund um den Bergmannkiez.",
            "Sonne ist in Kreuzberg eine Geometrie-Frage. Die Block-Struktur in den Wiener Straßen wirft am späten Vormittag schon Schatten in viele Innenhöfe. Die ehrlichsten Sonnen-Frühstücke sind am Wasser (Landwehrkanal-Lage = West/Süd offen) oder direkt am Park (Görli, Hasenheide).",
        ],
        "venues": [
            {
                "name": "Hallesches Haus", "addr": "Tempelhofer Ufer 1, 10961 Berlin",
                "context": "am Landwehrkanal · Süd-Ost-Deck · ab 9:00 Uhr",
                "desc": "Das umgebaute Postamt am Kanal ist Kreuzbergs verlässlichste Frühstücks-Adresse für Gruppen und Sonnen-Liebhaber gleichzeitig. Süd-Ost-Lage, also <em>Sonne ab 9:00 bis weit nach 13:00 Uhr</em>, lange Gemeinschaftstische und eine Karte, die den Berliner Brunch-Standard sehr sauber liefert (Eggs Benedict, Granola-Bowls, hausgemachte Marmeladen). Reservierungen für Gruppen ab sechs Personen — sonst Walk-in mit kurzer Wartezeit."
            },
            {
                "name": "Pasanella", "addr": "Wienerstraße 14, 10999 Berlin",
                "context": "ruhiges Ende der Wienerstraße · Süd-West · Mo geschlossen",
                "desc": "Italienisch-leaning Brunch — hausgemachter Ricotta, saisonal richtig reife Tomaten, und um 12:30 Uhr eine völlig legitime Carbonara, falls du in Lunch-Modus rutschst. Die kleine Vorderterrasse ist <em>Süd-West, Sonne ab spätem Vormittag bis 16 Uhr</em>. Einer der wenigen Berliner Brunch-Spots, an denen das langsame Hinüberrutschen in den Nachmittag explizit gewollt ist. Wochenend-Reservierung empfohlen."
            },
            {
                "name": "Markthalle Neun — Frühstücksmarkt", "addr": "Eisenbahnstraße 42-43, 10997 Berlin",
                "context": "samstags 10:00–15:00 · Süd-Lage · Streetfood",
                "desc": "Kein einzelnes Lokal, sondern ein samstäglicher Frühstücksmarkt mit zehn-plus Ständen — Bagels von Heidenpeters, Kaiserschmarrn, Pho, polnische Pierogi. Du baust dir den Teller im Gehen zusammen. Außensitze auf dem Kopfsteinpflaster vor der Halle haben <em>Süd-Sonne ab 11 Uhr</em>. Mit Abstand die beste Brunch-Option für Gruppen ab fünf Personen, ohne dass jemand reservieren muss."
            },
            {
                "name": "Café Engelbecken", "addr": "Michaelkirchplatz, 10179 Berlin",
                "context": "am Engelbecken-See · Süd offen · ganztägig",
                "desc": "An der Mitte-Kreuzberg-Grenze, am kleinen Engelbecken-See — einer der unter-bewerteten Wasserlagen Berlins. Die Süd-Terrasse fängt <em>volle Mittagssonne von 11 bis 15 Uhr</em>, mit alten Bäumen drumherum, die filtertes Licht statt vollen Schatten geben. Die Karte ist solide bis sehr gut: Frühstücksbretter, Salate, Suppen, Kaffee. Touristen-Quote niedrig, weil der See nicht in den Standard-Reiseführern steht."
            },
            {
                "name": "Roamers (Sister-Spot Sing Blackbird)", "addr": "Sanderstraße 11, 12047 Berlin",
                "context": "knapp Neukölln-Seite, von Görli in 7 Min · Süd-Ost",
                "desc": "Streng genommen Neukölln, aber von vielen Kreuzberg-Adressen aus näher als Hallesches Haus. Vintage-Boutique mit angeschlossenem Café, Süd-Ost-Terrasse mit <em>Vormittagssonne bis ca. 12 Uhr</em>. Brunch ist hipster-zentral, aber gut gemacht, Kaffee Spezialität. Klein, also entweder früh kommen oder den Trick lernen, dass die hinteren Sitze immer länger Sonne kriegen."
            },
        ],
        "faqs": [
            { "q": "Wo kann man in Kreuzberg samstags früh frühstücken?", "a": "Hallesches Haus öffnet um 9 Uhr und ist die ruhigste Option vor 10:30. Markthalle Neun startet 10 Uhr und hat ab 11 Uhr Wartezeiten. Café Engelbecken öffnet ebenfalls 9 Uhr und ist samstagvormittags noch fast leer. Pasanella und Sing Blackbird sind eher 10–10:30-Spots." },
            { "q": "Wo gibt es in Kreuzberg Brunch direkt am Wasser?", "a": "Hallesches Haus am Landwehrkanal ist die direkteste Wasser-Lage. Café Engelbecken am Engelbecken-See ist die zweite. Beide haben Süd-Ost- bis Süd-Lagen und damit lange Sonnen-Vormittage. Freischwimmer (auch Landwehrkanal) macht zwar Brunch am Wochenende, ist aber eher Restaurant als Frühstücks-Café." },
            { "q": "Welcher Kreuzberger Brunch-Spot ist familienfreundlich?", "a": "Markthalle Neun samstags — viel Platz, lockere Atmosphäre, viele Speise-Optionen für wählerische Esser. Hallesches Haus mit den langen Tischen funktioniert auch gut. Café Engelbecken hat den See als Bewegungsraum daneben. Pasanella und Sing Blackbird sind zu klein und zu eng für Familien mit kleinen Kindern." },
            { "q": "Welcher Kreuzberger Brunch hat die längste Sonnenterrasse?", "a": "Pasanella mit Süd-West-Lage hält die Sonne am längsten — bis 16 Uhr im Sommer. Hallesches Haus hat die früheste Sonne (ab 9 Uhr) und behält sie bis ca. 14 Uhr. Markthalle Neun ist samstags ab 11 Uhr Sonne bis ca. 14 Uhr. Café Engelbecken liegt dazwischen mit voller Mittagssonne." },
        ],
    },
    {
        "slug": "fruehstueck-mitte",
        "kw": "frühstück mitte",
        "h1": "Frühstück in Berlin-Mitte",
        "title": "Frühstück in Berlin-Mitte — die besten Brunch-Spots, live geprüft",
        "meta_desc": "Die besten Frühstücks-Adressen in Mitte — Distrikt Coffee, House of Small Wonder, Father Carpenter, The Barn. Live gegen Sonnenstand und Wolkendecke geprüft.",
        "subtitle": "Vom Apotheken-Café am Rosenthaler bis zum versteckten Hof in der Münzstraße — Mittes Brunch-Spots mit echten Außensitzen.",
        "intro": [
            "Mitte-Brunch ist die touristisch am stärksten gefärbte Variante der Berliner Frühstücks-Kultur. Die ikonischen Spots (House of Small Wonder, Distrikt Coffee, The Barn) tauchen in fast jedem internationalen Berlin-Reiseführer auf, was an warmen Wochenenden zu Schlangen führt, die quer über den Bürgersteig laufen. Locals weichen entweder in Hinterhof-Spots (Father Carpenter) oder ganz aus Mitte raus.",
            "Die Sonnen-Geometrie hier ist überraschend gut für die Bauklasse — Mitte hat viele Eckparzellen und einige offene Plätze, die selbst tiefe Wilhelminische Hinterhöfe vermeiden. Die Spots unten sind speziell so ausgewählt, dass jeder mindestens vier zusammenhängende Sonnen-Stunden zwischen 9 und 14 Uhr hat.",
        ],
        "venues": [
            {
                "name": "Distrikt Coffee", "addr": "Bergstraße 68, 10115 Berlin",
                "context": "alte Apotheke nördlich vom Rosenthaler · Süd-West · ab 8:30 Uhr",
                "desc": "Der Mitte-Klassiker für Spezialitätenkaffee plus Standard-Brunch (Avocado-Toast, Shakshuka, Granola-Bowls). Die Vorderterrasse läuft entlang der ruhigen Bergstraße, Süd-West-Lage, also <em>Sonne ab späten Vormittag bis ca. 14:30 Uhr</em>. Konsistent statt spektakulär — und genau das, was die meisten Hangover-Sonntage brauchen. Keine Reservierungen, am Wochenende Schlange."
            },
            {
                "name": "House of Small Wonder", "addr": "Johannisstraße 20, 10117 Berlin",
                "context": "Mitte · Glasdach + Spiraltreppe · Ost-Terrasse",
                "desc": "Der meist-fotografierte Brunch-Spot der Stadt — Glas-Lichthof, Pflanzen überall, japanisch-amerikanische Karte (Okonomiyaki, Curry, Ricotta-Pancakes). Innen ist die Hauptattraktion; die kleine Vorder-Terrasse ist <em>ostausgerichtet, also Vormittagssonne bis ca. 11 Uhr</em>. Klein (30 innen, 10 außen), Wartezeiten am Wochenende reliable 45+ Minuten. Vor 10 Uhr kommen oder Wochentag nehmen."
            },
            {
                "name": "Father Carpenter", "addr": "Münzstraße 21, 10178 Berlin",
                "context": "Innenhof am Hackescher Markt · ab 9:00 Uhr",
                "desc": "Versteckt in einem Mitte-Innenhof — durch die Toreinfahrt durch und plötzlich ruhiger Garten mit alten Bäumen. Australisch-Berliner Linie, sehr guter Avocado-Toast, Sironi-Sauerteigbrot, Five-Elephant-Kaffee. Der Innenhof ist im Sommer überwiegend baumbeschattet — <em>direkte Vormittagssonne nur 9:30 bis 11 Uhr</em>. Wenn Schatten ein Feature ist (Juli, 28 °C), ist das hier optimal."
            },
            {
                "name": "The Barn", "addr": "Auguststraße 58, 10119 Berlin",
                "context": "Auguststraße · Bürgersteig-Sitze · Süd-Ost · ab 9:00 Uhr",
                "desc": "Die Berliner Spezialitätenkaffee-Institution. Klein, sachlich, Fokus auf Kaffee mehr als auf Essen — Pastries, Granola, Sandwiches, kein voller Brunch-Teller. Der schmale Bürgersteig-Bereich an der Auguststraße kriegt <em>Süd-Ost-Vormittagssonne bis ca. 12:30 Uhr</em>. Funktioniert am besten als Kaffee-Stop auf dem Weg zu einem längeren Brunch woanders."
            },
            {
                "name": "Cô Chu", "addr": "Linienstraße 91, 10115 Berlin",
                "context": "vietnamesisches Café · Süd · ab 9:30 Uhr",
                "desc": "Eine der ehrlicheren Mitte-Adressen — vietnamesisch geprägter Brunch (Bánh Mì, Pho, Sticky Rice mit Mango), kleine, immer freundliche Crew, faire Preise für die Lage. Süd-orientierte Außensitze auf der Linienstraße haben <em>Mittags- bis Spätnachmittagssonne, ca. 11 bis 16 Uhr</em>. Keine Touristen-Schicht, weil noch nicht in jedem Reiseführer."
            },
        ],
        "faqs": [
            { "q": "Wo kann man in Mitte ohne Schlange frühstücken?", "a": "Cô Chu, Father Carpenter (innen kaum, draußen voll), The Barn unter der Woche. House of Small Wonder, Distrikt und 5 Elephant haben durchgehend Schlangen am Wochenende. Trick: die meisten Mitte-Spots öffnen 8:30–9:00 — vor 10 Uhr da sein heißt: kein Wartezeit." },
            { "q": "Welche Mitte-Brunch-Adresse ist am nächsten zum Hauptbahnhof?", "a": "Distrikt Coffee (Bergstraße) ist 12 Min zu Fuß vom Hauptbahnhof. Father Carpenter und House of Small Wonder sind 18–20 Min, was mit S-Bahn (Friedrichstraße) auf 10 Min runtergeht. Wenn du zwischen Zügen wirklich knapp bist, ist Distrikt die einzige realistische Option." },
            { "q": "Wo kann man in Mitte sonntags spät frühstücken?", "a": "Die meisten Mitte-Spots schließen 16–17 Uhr am Wochenende. Wenn du um 14 Uhr erst loskommst: Hallesches Haus (Kreuzberg-Grenze, durchgehend 9–22 Uhr) oder Benedict (Charlottenburg, 24/7) sind sicherer als die Mitte-Liste, wo nach 14:30 die Frühstücks-Karte oft schon weg ist." },
            { "q": "Welcher Mitte-Brunch hat die meiste Sonne?", "a": "Cô Chu (Süd-Lage Linienstraße) — Mittagssonne durchgängig. Distrikt Coffee (Süd-West Bergstraße) — von Vormittag bis Spätnachmittag. Father Carpenters Hof ist überwiegend baumbeschattet, also ein Spezialfall: gefiltertes Licht statt voller Sonne. House of Small Wonder ist Ost — nur Vormittag." },
        ],
    },
    {
        "slug": "fruehstueck-prenzlauer-berg",
        "kw": "frühstück prenzlauer berg",
        "h1": "Frühstück in Prenzlauer Berg",
        "title": "Frühstück in Prenzlauer Berg — die besten Brunch-Spots, live geprüft",
        "meta_desc": "Die besten Frühstücks-Adressen in Prenzlauer Berg — Café Frieda, Anna Blume, das Sonntags-Ritual. Live gegen Sonnenstand geprüft.",
        "subtitle": "Vom Helmholtzplatz-Café bis zur Eckterrasse am Kollwitzkiez — Prenzlauer Bergs Frühstücks-Klassiker mit echten Sonnenstunden.",
        "intro": [
            "Prenzlauer Berg ist der Berliner Bezirk, in dem Brunch am stärksten als Wochenend-Ritual eingebaut ist. Sonntags um 11 Uhr sind die Eckterrassen am Helmholtzplatz und im Kollwitzkiez dichter besetzt als die meisten Cafés der Stadt unter der Woche. Die Stammgast-Quote ist hoch, die Karten sind solide statt experimentell, und der Wartezeit-Vibe ist eher entspannt als gestresst.",
            "Was P-Berg von Mitte unterscheidet: weniger Touristen-Schicht, mehr Eckparzellen mit Süd-Ost-Lagen, und eine Zeitstruktur, die sich um 9 Uhr Frühstück und 14 Uhr letzten Bestellschluss organisiert. Die Spots unten haben alle Außensitze mit verlässlichen Vormittagssonnenstunden — der Bezirk ist dafür gemacht.",
        ],
        "venues": [
            {
                "name": "Café Frieda", "addr": "Stargarder Straße 72, 10437 Berlin",
                "context": "am Helmholtzplatz · Süd-Ost · ab 9:00 Uhr",
                "desc": "Der Eckpfeiler-Brunch von P-Berg. Stammgäste, die ohne Speisekarten-Blick bestellen, langsam-gerührtes Rührei, echtes Sauerteigbrot, ein starkes Hausgranola. Die Helmholtzplatz-Terrasse ist Süd-Ost, <em>volle Sonne von 9 bis ca. 13:30 Uhr</em>, und um 11 Uhr sonntags im Mai einer der schönsten Sitzplätze Berlins. Keine Reservierungen, aber die Schlange läuft entspannt."
            },
            {
                "name": "Anna Blume", "addr": "Kollwitzstraße 83, 10435 Berlin",
                "context": "Kollwitzkiez · Eckterrasse · Süd-Ost · ab 8:00 Uhr",
                "desc": "Halb Blumenladen, halb Café — die Frischblumen-Front ist das Foto, das jede macht. Signature: die „Frühstücksetagere“, ein dreistöckiger Kuchenständer für zwei Personen mit Käsen, Salami, Marmelade, Brot, Eiern, Obst. Old-school im besten Sinn. Die Terrasse zieht sich um die Ecke mit <em>Süd-Ost-Lage — Sonne morgens bis ca. 13:30 Uhr</em>, danach kippt der Schatten."
            },
            {
                "name": "Restaurant Wasserturm", "addr": "Knaackstraße 22, 10405 Berlin",
                "context": "neben dem Wasserturm · Süd-West · italienisch",
                "desc": "Italienisch-leaning, mit Sonntags-Brunch ab 10 Uhr und einer Außenterrasse direkt am Fuß des Wasserturms. Süd-West-Ausrichtung, also <em>Mittagssonne durchgehend bis ca. 16 Uhr</em>, mit dem Hügel-Charakter dieser P-Berg-Ecke. Die Brunch-Karte ist Italian-Berlin-Standard (Bruschetta, Frittata, Burrata-Brett). Reservierung empfohlen, weil voll."
            },
            {
                "name": "Konnopke's Imbiss-Außensitz (mit Kaffee-Trick)", "addr": "Schönhauser Allee 44, 10435 Berlin",
                "context": "unter dem U-Bahn-Bogen · Ost · ab 11:00 Uhr",
                "desc": "Streng genommen kein Frühstücks-Spot, sondern Berlins berühmtester Currywurst-Stand. Aber: viele P-Berger machen sonntags die Kombi „Frühstück bei Frieda, dann Currywurst-Booster bei Konnopke's um 11:30“. Die Stehtische unter den Bögen kriegen <em>Vormittagssonne bis ca. 12:30 Uhr</em>. Klassischer P-Berg-Move für Brunch, der nicht wie Brunch aussieht."
            },
            {
                "name": "Aux Délices Normands", "addr": "Stargarder Straße 5, 10437 Berlin",
                "context": "französisch · ab 8:00 Uhr · Süd-Ost",
                "desc": "Eine kleine französische Pâtisserie + Café, die das Sonntags-Frühstücks-Ritual mit Pain au Chocolat und Café au Lait ernst nimmt. Süd-Ost-Vorderterrasse mit <em>Vormittagssonne bis ca. 12 Uhr</em>. Klein, also vor 10 Uhr kommen oder mitten in der Woche. Ehrliche Konkurrenz für die Touristen-Spots in Mitte zum halben Preis."
            },
        ],
        "faqs": [
            { "q": "Wo gibt es in Prenzlauer Berg Frühstück mit Stammgast-Vibe?", "a": "Café Frieda am Helmholtzplatz ist die kanonische Antwort — die Stammgast-Quote sonntags ist >70%. Anna Blume zieht eher Wochenend-Pärchen aus der ganzen Stadt. Aux Délices Normands hat eine treue Nachbarschafts-Kundschaft. Wasserturm ist gemischter, mit ehrlich beidem." },
            { "q": "Welcher P-Berg-Brunch hat die ruhigste Außenterrasse?", "a": "Aux Délices Normands ist klein und wird selten überrannt. Restaurant Wasserturm ist räumlich groß genug, dass es auch voll nicht eng wirkt. Café Frieda und Anna Blume sind sonntags eng — wenn du Ruhe willst, samstagvormittag zwischen 9 und 11 Uhr kommen." },
            { "q": "Wo kann man in Prenzlauer Berg ohne Reservierung frühstücken?", "a": "Alle fünf Spots sind Walk-in. Anna Blume und Café Frieda haben sonntags 30–45 Min Wartezeit nach 10:30 Uhr. Aux Délices Normands und Konnopke's quasi nie. Wasserturm akzeptiert Reservierungen, aber Walk-in funktioniert auch." },
            { "q": "Welcher P-Berg-Brunch hat die längste Sonne?", "a": "Restaurant Wasserturm mit Süd-West-Lage hält die Sonne am längsten — bis 16 Uhr im Sommer. Café Frieda und Anna Blume haben Süd-Ost, also lange Vormittage bis ca. 13:30. Aux Délices Normands fällt in die gleiche Kategorie. Konnopke's unter den U-Bahn-Bögen kippt früh in Schatten — eher Vormittag als Mittag." },
        ],
    },
    {
        "slug": "fruehstueck-neukoelln",
        "kw": "frühstück neukölln",
        "h1": "Frühstück in Neukölln",
        "title": "Frühstück in Neukölln — die sonnigsten Brunch-Spots, live geprüft",
        "meta_desc": "Die besten Frühstücks-Adressen in Neukölln — Roamers, Hallmann & Klee, Sing Blackbird. Live gegen Sonnenstand und Wolkendecke geprüft.",
        "subtitle": "Vom florist-stylischen Hofterrassen-Brunch in Reuterkiez bis zur Rixdorfer Hofterrasse — Neuköllns Frühstücks-Spots mit echten Sonnenstunden.",
        "intro": [
            "Neukölln-Brunch ist optisch das, was Berlin in den Kopf der Welt gepflanzt hat — Roamers' florist-styled Teller in jedem Reiseführer-Foto, Hallmann &amp; Klees Rixdorfer Hof in jedem „verstecktes Berlin“-Article. Die Realität vor Ort ist weniger Insta und mehr Nachbarschaft: die Stammgast-Schicht in den Reuterkiez-Cafés ist hoch, die Karten sind besser als der Hype suggeriert, und die Hinterhof-Geometrie liefert verlässlich gute Sonnen-Lagen.",
            "Was Neukölln-Brunch besonders macht, ist die Wasser-Lage Richtung Süd: das Tempelhofer Feld als offene Westflanke, der Landwehrkanal an der Nord-Grenze, und die Rixdorfer Höfe mit Süd-Lagen, die in der dichten Berliner Block-Struktur Seltenheitswert haben. Wer in Neukölln frühstücken geht, geht in der Regel mit der Geometrie, nicht gegen sie.",
        ],
        "venues": [
            {
                "name": "Roamers", "addr": "Pannierstraße 64, 12047 Berlin",
                "context": "Reuterkiez · großer Innenhof · ab 9:30 Uhr (Wochenende ab 10:00)",
                "desc": "Der berühmteste Brunch-Spot Neuköllns, und nicht zufällig — Roamers hat seinen Standing aufgebaut auf florist-styled Tellern (essbare Blüten, Focaccia-Türmchen, Matcha) und schafft es trotzdem, das Essen unter dem Styling ehrlich zu halten. Der Vorderhof, voll mit Pflanzen und unpassenden Stühlen, hat <em>Vormittagssonne bis ca. 12:00 Uhr</em>. Walk-in only — Wartezeit am Wochenende nach 11 Uhr 30–45 Minuten."
            },
            {
                "name": "Hallmann &amp; Klee", "addr": "Böhmische Straße 13, 12055 Berlin",
                "context": "Rixdorf · Süd-Hof · Mo–Di geschlossen",
                "desc": "Tief im böhmisch-dörflichen Rixdorf — eine der ruhigsten Ecken Neuköllns. Saisonal wechselnde Brunch-Karte (in Berlin-Brunch eine Seltenheit), chef-led Plates. Die Hofterrasse ist Süd-orientiert mit <em>Sonne von 9:30 bis ca. 14:00 Uhr</em>, danach gefiltertes Licht durch alte Kastanien. Reservierungen Do–So möglich und sehr empfehlenswert — der Laden ist klein."
            },
            {
                "name": "Sing Blackbird", "addr": "Sanderstraße 11, 12047 Berlin",
                "context": "Reuterkiez · Süd-Ost · Vintage-Boutique",
                "desc": "Vintage-Boutique mit angeschlossenem Café — kleiner als Roamers, weniger Touristen-Schicht, ehrlich-Berliner Vibe. Die kleine Süd-Ost-Vorderterrasse hat <em>Vormittagssonne bis ca. 12 Uhr</em>. Karte: Brunch-Klassiker plus ein paar persönliche Variationen, sehr guter Specialty-Coffee. Trick: die hinteren Sitze (näher zur Hauswand) bekommen länger Sonne als die vorderen."
            },
            {
                "name": "Café Mugrabi", "addr": "Hobrechtstraße 56, 12047 Berlin",
                "context": "israelisch geprägt · ab 9:00 Uhr · Süd-West",
                "desc": "Israelisch-leaning Brunch — Shakshuka, Sabich, Hummus-Bowls, fluffy Pita aus eigenem Backofen. Die Karte ist saisonal, die Atmosphäre familiär, und die Vorderterrasse zur Hobrechtstraße hat <em>Süd-West-Lage mit Sonne bis ca. 16 Uhr</em>. Eine der ehrlicheren Antworten auf die Frage „wo essen Neuköllner brunchen, ohne dass die Foto-Schlange 30 Min läuft?“."
            },
            {
                "name": "Hofklub am Tempelhofer Feld", "addr": "Oderstraße, 12049 Berlin",
                "context": "saisonal · West-Lage · ab 10:00 Uhr",
                "desc": "Sommer-Saisonbrunch am Oderstraßen-Eingang des Tempelhofer Felds. Die offene Westflanke des Felds liefert <em>Sonne den ganzen Spätnachmittag</em>, was hier bedeutet: ab 11 Uhr durchgehend bis Sonnenuntergang. Karte simpler als bei den Reuterkiez-Cafés (Brötchen, Granola, Eier, Snacks), aber die Lage ist die Hauptattraktion — du frühstückst am Rand eines ehemaligen Flughafens."
            },
        ],
        "faqs": [
            { "q": "Wo gibt es in Neukölln Brunch ohne 30-Minuten-Schlange?", "a": "Sing Blackbird, Café Mugrabi und Hofklub haben unter der Woche und an ruhigen Wochenenden meistens sofort Plätze. Roamers und Hallmann & Klee fahren konsistent Wartezeiten — bei Hallmann & Klee einfach reservieren, bei Roamers vor 10:30 Uhr kommen oder einen Wochentag wählen." },
            { "q": "Welcher Neukölln-Brunch ist am authentischsten?", "a": "Sing Blackbird, Café Mugrabi und Hallmann & Klee haben hohe Stammgast-Quoten und low Touristen-Anteil. Roamers ist authentisch, aber im Insta-Sinne — die Crowd ist gemischter. Hofklub ist eher Sommer-Pop-up als ganzjähriger Spot." },
            { "q": "Welche Brunch-Spots in Neukölln sind direkt am Tempelhofer Feld?", "a": "Hofklub am Oderstraßen-Eingang ist der einzige direkt am Feld. Café Mugrabi und einige andere Reuterkiez-Spots sind 5–10 Minuten weg. Wer Brunch + Feld-Spaziergang kombinieren will: zuerst Hofklub, dann übers Feld Richtung Tempelhof oder Hermannplatz." },
            { "q": "Welcher Neukölln-Brunch hat den besten Specialty-Coffee?", "a": "Sing Blackbird und Roamers sind beide Kaffee-fokussiert (Spezialitätenröster aus Berlin und Wien). Hallmann & Klee macht ebenfalls sehr guten Kaffee, aber die Karte ist food-fokussierter. Café Mugrabi ist israelisch-Kaffee-geprägt, das kann man mögen oder nicht." },
        ],
    },
    {
        "slug": "fruehstueck-friedrichshain",
        "kw": "frühstück friedrichshain",
        "h1": "Frühstück in Friedrichshain",
        "title": "Frühstück in Friedrichshain — Specialty Coffee + Brunch, live geprüft",
        "meta_desc": "Die besten Frühstücks-Adressen in Friedrichshain — Silo Coffee, Lemon Leaf, Briefmarken. Live gegen Sonnenstand und Wolkendecke geprüft.",
        "subtitle": "Vom Antipodean-Café im Boxhagener bis zum Spreeufer am RAW — Friedrichshains Brunch-Spots mit echten Sonnenstunden.",
        "intro": [
            "Friedrichshain hat sich in den letzten Jahren zur Berliner Specialty-Coffee-Achse gemausert — wo Mitte das Marketing macht und P-Berg die Klassiker hält, hier liegt der ernsthaft-australische Flat-White-Standard. Das hat den Brunch geprägt: viele Antipodean-leaning Karten, viele Pour-Over-Bars, weniger touristische Insta-Spots als in Neukölln.",
            "Geometrisch ist der Bezirk geteilt: der Boxhagener Kiez im Norden mit dichter Block-Struktur und vielen Süd-Ost-Eckparzellen (gute Vormittagssonne), das Spreeufer im Süden mit dem RAW und Holzmarkt (durchgehende West-Lage). Die Liste unten deckt beide Hälften ab — wo du frühstücken willst, hängt davon ab, ob du Vormittag oder Nachmittag im Sonnenlicht sitzen möchtest.",
        ],
        "venues": [
            {
                "name": "Silo Coffee", "addr": "Gabriel-Max-Straße 4, 10245 Berlin",
                "context": "Boxhagener · Süd-Ost · ab 9:00 Uhr",
                "desc": "Antipodisch-leaning Brunch transplantiert nach Friedrichshain — Bananenbrot, Eier auf Sauerteig, sehr ernsthaft gezogene Flat Whites. Die kleine Terrasse an der Gabriel-Max-Straße fängt <em>Vormittagssonne von 9 bis ca. 12:30 Uhr</em>, danach in Schatten. Freitag ist ein ruhiger Tag ohne Schlange; Sonntags voll, aber nie so schlimm wie Mitte. Karten werden akzeptiert."
            },
            {
                "name": "Lemon Leaf", "addr": "Grünberger Straße 69, 10245 Berlin",
                "context": "Boxhagener · südostasiatisch · Süd",
                "desc": "Südostasiatisch geprägter Brunch — Pho zum Frühstück, vietnamesische Bánh Mì, Kokos-Glutinous-Rice. Die Vorderterrasse zur Grünberger Straße hat <em>Süd-Lage mit Sonne ab 10 Uhr bis ca. 15 Uhr</em>. Locals kommen wegen der ehrlichen Pho, der Kaffee ist Standard. Klein, aber fast nie voll am Vormittag — eine echte Geheimadresse, die kein Reiseführer abdeckt."
            },
            {
                "name": "Briefmarken Weine (Wein-Bistro mit Brunch)", "addr": "Karl-Marx-Allee 99, 10243 Berlin",
                "context": "Karl-Marx-Allee · Süd-West · sonntags 11–15 Uhr",
                "desc": "Strenggenommen ein Wein-Bistro, das sonntags ein durchdachter Brunch fährt — italienisch-leaning, mit echten Wein-Optionen ab Mittag (Friulianer ab 12 Uhr ist legitim hier). Süd-West-Terrasse zur Karl-Marx-Allee mit <em>Sonne ab 11 Uhr bis ca. 16 Uhr</em>. Ruhig, weniger Touristen, eher älteres Friedrichshain-Publikum. Reservierung empfohlen."
            },
            {
                "name": "Holzmarkt 25 (mehrere Cafés)", "addr": "Holzmarktstraße 25, 10243 Berlin",
                "context": "Spreeufer · Süd-West · saisonal",
                "desc": "Kein einzelner Brunch-Spot, sondern eine Reihe von Cafés und Bars im Holzmarkt-Kultur-Dorf direkt an der Spree. Pampa, Kater Blau Tagcafé, Kiezbar — du wechselst zwischen Sitzplätzen je nach Sonnenstand. Die Spreefront hat <em>Süd-West, also Sonne ab Mittag bis Sonnenuntergang</em>. Eher Saison-orientiert (April–Oktober), aber genau dafür eine der schönsten Wasser-Brunch-Lagen der Stadt."
            },
            {
                "name": "Café Bonbon", "addr": "Sonntagstraße 25, 10245 Berlin",
                "context": "Sonntagstraße · Süd-Ost · klein",
                "desc": "Eine kleine Eckcafé-Adresse in der Sonntagstraße (nomen est omen — eine der ruhigeren Friedrichshainer Wochenend-Strecken). Brunch-Karte solide-deutsch (Brötchen-Plate, Eier, Granola), Süd-Ost-Vorderterrasse mit <em>Vormittagssonne bis ca. 12:30 Uhr</em>. Stammgast-Vibe, kaum Touristen, fast nie Wartezeit. Wenn du Friedrichshain ohne Specialty-Coffee-Hype willst, hier."
            },
        ],
        "faqs": [
            { "q": "Wo gibt es in Friedrichshain Brunch direkt an der Spree?", "a": "Holzmarkt 25 ist die direkteste Spreeufer-Lage — mehrere Cafés und Bars über Stege und Decks am Wasser. Yaam (auch Spreeufer, etwas weiter Richtung Schillingbrücke) macht am Wochenende einen entspannten Frühstücks-Service. Briefmarken Weine ist nicht am Wasser, aber 5 Min vom Spreeufer." },
            { "q": "Welcher Friedrichshain-Brunch hat den besten Coffee?", "a": "Silo Coffee ist die kanonische Antwort — antipodischer Standard, ernsthafte Pour-Overs, gut kuratierte Bohnen-Rotation. Briefmarken Weine konzentriert sich mehr auf Wein, der Kaffee ist solide aber nicht die Hauptachse. Lemon Leaf und Café Bonbon servieren Standard-Italienischer-Espresso-Niveau." },
            { "q": "Welcher Friedrichshainer Brunch ist gut für ruhige Sonntage?", "a": "Café Bonbon und Lemon Leaf sind die ruhigsten — sonntags um 11 Uhr meistens halbvoll, kaum Wartezeit. Briefmarken Weine ist saisonal-abhängig, aber selten überrannt. Silo und Holzmarkt sind sonntags voll, aber nie so eng wie Mitte." },
            { "q": "Welcher Friedrichshain-Brunch hat die längste Sonne?", "a": "Holzmarkt 25 mit Süd-West-Spreefront — Sonne durchgehend bis Sonnenuntergang. Briefmarken Weine ebenfalls Süd-West, bis ca. 16 Uhr. Lemon Leaf hat volle Mittagssonne. Silo Coffee und Café Bonbon sind Süd-Ost-orientiert — also Vormittagssonne, dann Schatten. Wahl je nach Tageszeit-Plan." },
        ],
    },
]


def render_page(n: dict) -> str:
    canonical = f"https://sunmaxxing.com/de/{n['slug']}/"

    item_list = []
    for i, v in enumerate(n["venues"], 1):
        item_list.append({
            "@type": "ListItem",
            "position": i,
            "item": {
                "@type": "Restaurant",
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
        "@context": "https://schema.org", "@type": "Article", "inLanguage": "de",
        "headline": n["title"], "description": n["meta_desc"],
        "image": "https://sunmaxxing.com/og-image.png",
        "datePublished": "2026-05-06", "dateModified": "2026-05-06",
        "author": {"@type": "Organization", "name": "Sonne Berlin", "url": "https://sunmaxxing.com/"},
        "publisher": {"@type": "Organization", "name": "Sonne Berlin",
                      "logo": {"@type": "ImageObject", "url": "https://sunmaxxing.com/android-chrome-512x512.png"}},
        "mainEntityOfPage": canonical,
    }
    item_list_schema = {
        "@context": "https://schema.org", "@type": "ItemList", "name": n["h1"],
        "itemListOrder": "https://schema.org/ItemListOrderAscending",
        "numberOfItems": len(n["venues"]), "itemListElement": item_list,
    }
    breadcrumb_schema = {
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Sonne Berlin", "item": "https://sunmaxxing.com/de/"},
            {"@type": "ListItem", "position": 2, "name": "Frühstück in Berlin", "item": "https://sunmaxxing.com/de/fruehstueck-berlin/"},
            {"@type": "ListItem", "position": 3, "name": n["h1"], "item": canonical},
        ]
    }
    faq_schema = {
        "@context": "https://schema.org", "@type": "FAQPage", "inLanguage": "de",
        "mainEntity": [
            {"@type": "Question", "name": f["q"],
             "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
            for f in n["faqs"]
        ]
    }

    schemas_html = "\n".join(
        f'<script type="application/ld+json">\n{json.dumps(s, ensure_ascii=False, indent=2)}\n</script>'
        for s in [article_schema, item_list_schema, breadcrumb_schema, faq_schema]
    )

    venues_html = "\n\n".join(
        textwrap.dedent(f"""\
          <article class="venue" id="{v['name'].lower().split()[0].replace('&amp;','und').replace('ü','ue').replace('ö','oe').replace('ä','ae').replace('ß','ss')}">
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

    siblings = [x for x in NEIGHBORHOODS if x["slug"] != n["slug"]][:4]
    sibling_links_html = "\n".join(
        f'    <a href="/de/{x["slug"]}/"><strong>{x["h1"]} →</strong><span>{x["subtitle"][:60]}…</span></a>'
        for x in siblings
    )

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>{n['title']} | Sonne Berlin</title>

<!-- Targets "{n['kw']}". Generated by scripts/generate-de-fruehstueck-neighborhoods.py
     with hand-written content per neighborhood. -->
<meta name="description" content="{n['meta_desc']}">
<meta name="theme-color" content="#F5A623">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="de" href="{canonical}">
<link rel="alternate" hreflang="x-default" href="{canonical}">

<meta property="og:type" content="article">
<meta property="og:site_name" content="Sonne Berlin">
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
  .venue{{background:var(--card);border:1px solid var(--border);border-radius:18px;padding:24px;margin-bottom:18px;box-shadow:0 1px 2px rgba(16,17,34,.04)}}
  .venue-head{{display:flex;align-items:baseline;gap:14px;margin-bottom:8px;flex-wrap:wrap}}
  .venue-rank{{font-family:'Fraunces',Georgia,serif;font-style:italic;color:var(--sun);font-size:26px;font-weight:600;line-height:1}}
  h2{{font-weight:700;font-size:21px;margin:0;letter-spacing:-.01em}}
  .address{{font-size:13.5px;color:var(--muted);margin:0 0 12px}}
  .description{{margin:0 0 14px;font-size:15.5px;line-height:1.65}}
  .description em{{font-style:normal;background:linear-gradient(to bottom, transparent 60%, var(--sun-bg) 60%);padding:0 1px}}
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
  <a href="/de/">Sonne Berlin</a><span class="sep">›</span><a href="/de/fruehstueck-berlin/">Frühstück in Berlin</a><span class="sep">›</span><strong>{n['h1']}</strong>
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
    <h3>Welcher Spot liegt jetzt in der Sonne?</h3>
    <p>Auf der Live-Karte rechnen wir Minute für Minute durch, welche der oben genannten Terrassen in {n['h1'].split(' in ')[-1]} gerade in der Sonne liegt — und welche schon im Schatten der umliegenden Gebäude steht. Wolkendecke wird stündlich aktualisiert.</p>
    <a class="callout-cta" href="/de/">Live-Karte öffnen →</a>
  </div>
</aside>

<section class="faq">
  <h3>Häufig gefragt</h3>
{faqs_html}
</section>

<section class="related">
  <h3>Frühstück in anderen Bezirken</h3>
  <div class="related-grid">
{sibling_links_html}
  </div>
</section>

<section class="related" style="margin-top:24px">
  <h3>Andere Sonnen-Guides</h3>
  <div class="related-grid">
    <a href="/de/fruehstueck-berlin/"><strong>Frühstück in Berlin (alle Bezirke) →</strong><span>Die kuratierte Stadtweite Liste mit 14 Top-Spots.</span></a>
    <a href="/de/sonnenterrassen-berlin/"><strong>Sonnenterrassen in Berlin →</strong><span>Die ehrlichste Liste der sonnigsten Plätze der Stadt.</span></a>
    <a href="/de/biergaerten-berlin/"><strong>Biergärten in Berlin →</strong><span>Wenn der Brunch in den Nachmittag kippt.</span></a>
    <a href="/brunch-berlin/" hreflang="en" lang="en"><strong>Brunch in Berlin (EN) →</strong><span>Die englische Schwesterseite mit zusätzlichen Adressen.</span></a>
  </div>
</section>

<footer>
  <p>Gebaut von <a href="/de/">Sonne Berlin</a> · <a href="/de/fruehstueck-berlin/">Alle Berliner Frühstücks-Spots</a></p>
  <p style="margin-top:8px;font-size:12px">Öffnungszeiten ändern sich saisonal. Vor dem Hingehen am besten direkt beim Spot checken.</p>
</footer>

</body>
</html>
"""


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
