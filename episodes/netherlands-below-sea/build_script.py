"""Builds script.json for netherlands-below-sea.  python build_script.py

Same production logic as episodes/green-sahara (hand-placed shots, painted regions, a photo or map frame at most
twice, push-ins that stay above Sentinel's 2-degree limit). The narration lives in drafts/narration.md (one
"Pnn:" line per paragraph, "## Title (mood)" per chapter); every sentence comes from research.md.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent.parent / "pipeline"))
from schema import Paragraph  # noqa: E402


def near(lon, lat, span):
    return {"lon": lon, "lat": lat, "span": span}


def place(name, lon, lat, label=None, kind="city"):
    return {"name": name, "lon": lon, "lat": lat, "kind": kind, "label": label if label is not None else name}


def m(at, *steps, text=None, cut=True):
    s = {"type": "map", "at": at, "map": {"steps": list(steps)}}
    if cut:
        s["map"]["cut"] = True
    if text:
        s["on_screen_text"] = text
    return s


_uses: dict = {}


def fresh(view):
    """Wide views come back with new content; frame each use a little differently so no map frame is seen twice."""
    if view["span"] <= 2.5:
        return view
    key = (view["lon"], view["lat"], view["span"])
    k = _uses.get(key, 0)
    _uses[key] = k + 1
    if k == 0:
        return view
    dx, dy = [(0.05, 0.02), (-0.05, -0.02), (0.03, -0.04), (-0.03, 0.04), (0.07, 0.0), (-0.07, 0.0), (0.0, 0.05), (0.0, -0.05)][(k - 1) % 8]
    zoom = [0.9, 1.1, 0.82, 1.18, 0.95, 0.86, 1.06, 0.78][(k - 1) % 8] * (0.97 ** ((k - 1) // 8))
    return {"lon": round(view["lon"] + dx * view["span"], 3), "lat": round(view["lat"] + dy * view["span"], 3), "span": round(view["span"] * zoom, 3)}


def v(view, at=None, **kw):
    d = {"view": fresh(view), **kw}
    if at is not None:
        d["at"] = at
    return d


SAT_MIN_SPAN = 0.08  # storyboard 2026-11-19: 0.035-0.06 views were soft (10 m Sentinel pixels blown up 5-7x)


def sat(at, lon, lat, span, label=None, **kw):
    """One close satellite view of a named spot (Sentinel-2 below 2 degrees, the basemap above)."""
    return m(at, v(near(lon, lat, max(span, SAT_MIN_SPAN)), **kw), text=label)


def paint(at, *names, view=None, **kw):
    return m(at, v(view or NL, highlight=list(names), **kw))


def photo(at, name, text=None):
    d = {"type": "photo", "at": at, "photo": name}
    if text:
        d["on_screen_text"] = text
    return d


def stat(at, value, label, source):
    return {"type": "stat", "at": at, "stat": {"value": value, "label": label, "source": source}}


def chart(at, title, unit, data, source, reveal=None, highlight=0):
    c = {"type": "bar", "title": title, "unit": unit, "data": data, "source": source, "highlight": highlight}
    if reveal:
        c["reveal"] = reveal
    return {"type": "chart", "at": at, "chart": c}


TEXT = {}
HEADS = []
for line in (HERE / "drafts" / "narration.md").read_text(encoding="utf-8").splitlines():
    if line.startswith("## "):
        mt = re.match(r"## (?:\d+\. |Hook: )?(.+?) \((\w+)\)", line)
        HEADS.append((mt.group(1), mt.group(2)))
    mp = re.match(r"(P\w+)(?: \([^)]*\))?: (.+)", line)
    if mp:
        TEXT[mp.group(1)] = mp.group(2).strip()


def P(key, *shots, ask=None):
    d = {"text": TEXT[key], "shots": list(shots)}
    if ask:
        d["ask"] = {"at": ask[0], "text": ask[1]}
    return d


# Views (span in degrees of longitude; painted views stay above 2.5 so Sentinel never patches them)
NL = {"lon": 5.4, "lat": 52.2, "span": 4.6}
NLW = {"lon": 4.6, "lat": 52.15, "span": 3.0}
NORTHSEA = {"lon": 3.0, "lat": 53.5, "span": 16}
SW = {"lon": 4.1, "lat": 51.7, "span": 2.8}
ZZ = {"lon": 5.4, "lat": 52.75, "span": 2.8}
NORTH = {"lon": 6.0, "lat": 53.25, "span": 3.0}
RIVERS = {"lon": 5.6, "lat": 51.9, "span": 3.2}
LOW = "file:belowsea.geojson@red"

SUM = "2024-06-01/2024-08-31"
SPR = "2024-03-15/2024-05-15"

PBL = "PBL Netherlands Environmental Assessment Agency, 2010"
ERK = "Erkens et al., Hydrogeology Journal 2016"
WSM = "Watersnoodmuseum"
RWS = "Rijkswaterstaat"

PH_TERP = "File:Geefsweer - wierde (noorden).jpg"
PH_TURF_ART = "File:Landschap met vissers en turfstekende boeren in het laagveen, SK-A-4946.jpg"
PH_PEAT_MEADOW = "File:Panoramic view peat meadows at Wijkergouw Schellingwoude with reflected horses at 29 October 2015 - panoramio.jpg"
PH_POLDER_FOG = "File:Fog in the polder 29-12-16 (31847866241).jpg"
PH_PALACE = "File:The Royal Palace on the Dam of Amsterdam on 25 November 2015.jpg"
PH_CANALS = "File:Amsterdam Canal Houses (52556779860).jpg"
PH_BEEMSTER_MAP = "File:Beemster 1658 (26226452006).jpg"
PH_BEEMSTER = "File:Lovely bulbbfields mid April at polder Beemster North Holland - panoramio.jpg"
PH_LEEGHWATER = "File:Portret van de waterbouwkundige Jan Adriaanszoon Leeghwater, RP-P-1905-3793.jpg"
PH_LEEGH_WORK = "File:Molenmaker Jan Adriaanszoon Leeghwater aan het werk, RP-P-1906-966.jpg"
PH_KINDERDIJK = "File:Some of the group of Windmills for waterworks at Kinderdijk. World Heritage these mills - panoramio.jpg"
PH_KINDERDIJK_OLD = "File:Molens bij Kinderdijk, Bestanddeelnr 901-4769.jpg"
PH_CRUQUIUS = "File:Cruquius Gemaal.jpg"
PH_CRUQUIUS_IN = "File:Gemaal De Cruquius (20082148438).jpg"
PH_HMEER_MAP = "File:Verkaveling van den Haarlemmermeer polder, Objectnr PV PV71366.jpg"
PH_RINGVAART = "File:Union ENI 03031748 Ringvaart Haarlemmermeer polder.jpg"
PH_POLDERBAAN = "File:Schiphol, Polderbaan, Antonov (7168694249).jpg"
PH_DORT = "File:Cuyp, Aelbert - The large Dort.jpg"
PH_LELY_PLAN = "File:Ontwerp Afsluiting Zuiderzee en Droogmaking Cornelis Lely 1891-1892.jpg"
PH_LELY_STATUE = "File:Cornelis Lely - Afsluitdijk (32896245132) (2).jpg"
PH_AFSLUIT = "File:Afsluitdijk - wind turbines.jpg"
PH_FLEVO_DRY = "File:Polder oostelijk Flevoland is aan het droogvallen, Bestanddeelnr 909-4895.jpg"
PH_FLEVO_WORK = "File:Werkzaamheden in de polder Oostelijk Flevoland, Bestanddeelnr 909-6758.jpg"
PH_ALMERE = "File:Almerehaven.jpg"
PH_WIERINGER = "File:Wieringermeer, Bestanddeelnr 901-1844.jpg"
PH_WIERINGER_PUMPS = "File:Wieringermeer. Bij Medemblik werden hulpgemalen ingezet (voorjaar 1945) om de Wi, Bestanddeelnr 901-1846.jpg"
PH_1953_ZIER = "File:Watersnood 1953. Korte Nobelstraat te Zierikzee, Bestanddeelnr 905-5704.jpg"
PH_1953_EVAC = "File:Watersnood 1953. Evacuatie Zierikzee aankomst Dordrecht, Bestanddeelnr 905-5506.jpg"
PH_1953_HOUSE = "File:Watersnoodramp 1953 - Zwaar beschadigd huis.jpg"
PH_1953_OUDEN = "File:NIMH P101-C41 017 Watersnoodramp 1953 Oudenhoorn.jpg"
PH_EVEGROEN = "File:Monument met rechts schipper Evegroen, Bestanddeelnr 932-7296.jpg"
PH_OUWERKERK = "File:Ouwerkerk Watersnoodmuseum 1.JPG"
PH_HARINGVLIET = "File:Werkzaamheden Haringvlietdam, Bestanddeelnr 912-2127.jpg"
PH_VOLKERAK = "File:Construction of the Volkerakdam, December 1967.jpg"
PH_OSK = "File:Oosterscheldekering.jpg"
PH_OSK2 = "File:Oosterscheldekering januari 2025.jpg"
PH_MAESLANT = "File:Panorama sluiting Maeslantkering.jpg"
PH_ROTTERDAM = "File:Aerial photograph of the port of Rotterdam in 2017 (3).jpg"
PH_DIKE_FARM = "File:Dike farm at Acquoy (Netherlands 2017) (34830824861).jpg"
PH_DIKE_ROAD = "File:Dike road at Goingarijp (The Netherlands 2019) (47623059262).jpg"
PH_ALBLASSER = "File:Alblasserwaard - 19 (49924655523).jpg"
PH_ZAANSE = "File:Windmills at Zaanse Schans, Zaanstad, 2022.jpg"
PH_ASTER = "File:Netherlands dikes (ASTER).jpg"
PH_MARKER = "File:Stone dike along the west coast, Marker Wadden, 2022.jpg"
PH_NAP = "File:Centraal ijkpunt NAP ( Normaal Amsterdam Peil) ingang stadhuis (Stopera), Bestanddeelnr 934-2481.jpg"
PH_1916 = "File:Dijkdoorbraak, overstroming, watersnood, SFA022813657.jpg"
PH_BOMMEL = "File:Dijkdoorbraak bij Den Bommel, Bestanddeelnr 905-5475.jpg"
PH_SLOCHTEREN = "File:Gasbel te Slochteren Nederlandse Gas Unie werkzaamheden, Bestanddeelnr 915-2654.jpg"
PH_SPIEGELWAAL = "File:Spiegelwaal 03 met stadseiland.JPG"
PH_ZANDMOTOR_AIR = "File:Zandmotor 16 januari 2016 overzicht naar zuid 5H6A0001.jpg"
PH_ZANDMOTOR = "File:Zandmotor Ter Heijde (38868068940).jpg"
PH_HOGEBEINTUM = "File:Hogebeintum1.jpg"
PH_THWAITES = "File:Thwaites Glacier.jpg"
PH_PAPENDRECHT = "File:Watersnoodramp 1953 - Dijkdoorbraak in de Alblasserwaard bij Papendrecht.jpg"

AMS = place("Amsterdam", 4.90, 52.37)
ROT = place("Rotterdam", 4.48, 51.92)
HAGUE = place("The Hague", 4.30, 52.08)
LEIDEN = place("Leiden", 4.49, 52.16)
HAARLEM = place("Haarlem", 4.64, 52.38)
DORDT = place("Dordrecht", 4.69, 51.81)
LELY = place("Lelystad", 5.47, 52.52)
ALMERE = place("Almere", 5.22, 52.37)
ZIER = place("Zierikzee", 3.92, 51.65)
LOWEST = place("Lowest point", 4.61, 52.0, "Lowest point, 6.76 m below NAP", "site")
SCHIPHOL = place("Schiphol", 4.76, 52.31, "Schiphol airport", "site")
KDIJK = place("Kinderdijk", 4.64, 51.885, "Kinderdijk", "site")
BEEM = place("Beemster", 4.91, 52.55, "Beemster polder", "site")
HMEER = place("Haarlemmermeer", 4.69, 52.30, "Haarlemmermeer (lake until 1852)", "site")
OUWER = place("Ouwerkerk", 3.99, 51.62, "Ouwerkerk", "site")
OSK = place("Eastern Scheldt barrier", 3.69, 51.64, "Eastern Scheldt barrier", "site")
MAES = place("Maeslantkering", 4.163, 51.955, "Maeslantkering", "site")
LOBITH = place("Lobith", 6.11, 51.86, "Lobith: the Rhine enters", "site")
GRON = place("Groningen", 6.57, 53.22)
SANDM = place("Sand Motor", 4.19, 52.05, "Sand Motor", "site")
WALCH = place("Walcheren", 3.58, 51.53, "Walcheren", "site")
WIER = place("Wieringermeer", 4.98, 52.83, "Wieringermeer", "site")
AFSL = {"from": [4.99, 52.94], "to": [5.42, 53.07], "mode": "line", "color": "accent", "seconds": 1.6, "label": "Afsluitdijk, 32 km"}
STORM53 = {"from": [1.0, 56.0], "to": [3.8, 51.8], "mode": "air", "color": "red", "seconds": 1.8, "label": "Northwest storm, 31 Jan 1953"}
RHINE = {"from": [6.11, 51.86], "via": [[5.9, 51.85], [5.2, 51.85]], "to": [4.5, 51.9], "mode": "line", "color": "blue", "seconds": 1.8, "label": "Rhine and Waal"}

chapters = []
heads = iter(HEADS)


def chapter(*paras):
    title, mood = next(heads)
    chapters.append({"title": title, "mood": mood, "paragraphs": list(paras)})


chapter(
    P("P0",
      photo(0, PH_BOMMEL, "A dike breach, February 1953"),
      sat("near the town of", 4.585, 51.965, 0.12, "Nieuwerkerk aan den IJssel", date=SUM),
      m("Behind it lay the", v(NLW, highlight=[LOW], places=[LOWEST, ROT])),
      photo("The local officials decided", PH_1953_OUDEN, "Oudenhoorn under water, 1953"),
      photo("What happened to that", PH_1953_HOUSE, "February 1953"),
      m("First, how does a", v(NORTHSEA, highlight=["Netherlands@red"]))),
    P("P1",
      m(0, v(NL, highlight=["Netherlands@accent"], places=[AMS, ROT])),
      m("About a quarter of", v(NL, highlight=[LOW], places=[AMS, ROT])),
      sat("Its lowest point, in", 4.61, 52.0, 0.25, "The Zuidplaspolder near Nieuwerkerk aan den IJssel", date=SUM),
      stat("is almost seven meters", "−6.76 M", "Lowest point of the Netherlands, below NAP", "Wikipedia, extreme points of the Netherlands"),
      photo("One of Europe's busiest", PH_POLDERBAAN, "Schiphol's Polderbaan runway"),
      sat("on the bed of", 4.70, 52.30, 0.4, "The Haarlemmermeer polder, once a lake", date=SUM)),
    P("P2",
      photo(0, PH_ASTER, "Dikes and polders of the Dutch delta, from orbit"),
      photo("A thousand years ago", PH_TURF_ART, "Fishers and peat cutters in the bogs, 18th-century painting"),
      sat("Then people started to", 4.75, 51.98, 0.2, "Ditches in the peat meadows near Gouda", date=SUM),
      stat("Researchers who added up", "−1.9 M", "Average lowering of the Dutch coastal plain in 1,000 years", ERK),
      m("coastal plain dropped by", v(NLW, highlight=[LOW], places=[AMS, ROT, HAGUE]))),
    P("P3",
      photo(0, PH_HMEER_MAP, "The drained Haarlemmermeer, 19th-century map"),
      photo("a minister who turned", PH_LELY_STATUE, "Cornelis Lely, the minister who closed the Zuiderzee"),
      sat("and a province that", 5.4, 52.45, 0.6, "Flevoland, land made from the sea", date=SUM),
      sat("And at the end,", 4.80, 52.06, 0.3, "Peat meadows of the Green Heart", date=SUM),
      m("How does a country", v(NORTHSEA, highlight=["Netherlands@red"])),
      photo("and why do eighteen", PH_ROTTERDAM, "The port of Rotterdam")),
    P("P3b",
      photo(0, PH_CANALS, "Amsterdam"),
      stat("In 1684 the mayor", "1684", "Johannes Hudde fixes Amsterdam's water level, the start of NAP", "Wikipedia, Amsterdam Ordnance Datum"),
      sat("Hudde, had the water", 4.92, 52.385, 0.15, "The IJ, Amsterdam's old harbor", date=SUM),
      sat("and marble stones were", 4.90, 52.375, 0.04, "The IJ and central Amsterdam", date=SUM),
      photo("Two centuries later it", PH_NAP, "The NAP benchmark under Amsterdam's city hall, 1988"),
      m("When the Dutch say", v(NLW, highlight=[LOW], places=[LOWEST, AMS])),
      sat("they mean six meters", 4.62, 52.01, 0.12, "The Zuidplaspolder, the lowest land in the country", date=SUM),
      m("And the first reason", v(NL, highlight=["Netherlands@accent"]))),
)

chapter(
    P("P3c",
      m(0, v(NORTH, highlight=["Friesland@accent", "Groningen@alt"])),
      stat("More than two thousand", "500 BC", "About then: the first dwelling mounds (terps) in the north", "Wikipedia, Terp"),
      photo("they piled up earth", PH_TERP, "A village mound (wierde) at Geefsweer, Groningen"),
      sat("When storm tides came,", 5.85, 53.34, 0.05, "Hogebeintum, a village on a terp, Friesland", date=SUM),
      sat("Some grew to be", 6.25, 53.36, 0.6, "The northern coast and the Wadden Sea", date=SUM),
      m("Living below the sea", v(NORTH, highlight=["Friesland@accent", "Groningen@accent"], places=[GRON]))),
    P("P4",
      m(0, v(NLW, highlight=[LOW], places=[HAARLEM, LEIDEN])),
      sat("behind a line of", 4.45, 52.25, 0.25, "Dunes and polders between Leiden and the sea", date=SUM),
      photo("layers of dead moss", PH_PEAT_MEADOW, "Peat meadows at Schellingwoude"),
      photo("A peat bog is", PH_POLDER_FOG, "A ditch in a polder"),
      stat("it rose slowly, and", "ABOVE THE SEA", "Much of the coastal peat stood above sea level before drainage", ERK)),
    P("P5",
      stat(0, "1000-1300", "Drainage of the coastal peatlands for farmland", ERK),
      sat("So they dug ditches", 4.9, 52.15, 0.15, "Long strip fields cut into peat, Utrecht", date=SUM),
      photo("Farmers had to work", PH_DIKE_ROAD, "A dike road in Friesland"),
      m("from that cooperation came", v(NL, highlight=["Utrecht@alt", "South Holland@accent", "North Holland@accent"])),
      stat("and the people who", "EVERY 4 YEARS", "Residents behind the dikes elect their water boards", "Wikipedia, 2023 Dutch water board elections"),
      stat("In 1953 there were", "~2,670", "Dutch water boards in 1953; a few dozen today after mergers", "Springer, Water History 2016"),
      photo("Mergers have cut that", PH_DIKE_FARM, "A dike farm at Acquoy")),
    P("P6",
      sat(0, 4.70, 52.02, 0.12, "Peat meadows in the Krimpenerwaard", date=SUM),
      stat("Once air gets into", "ROTS", "Drained peat oxidises and compacts, so the ground sinks", ERK),
      sat("Then the ditches are", 4.88, 51.93, 0.1, "Ditches in the Alblasserwaard", date=SUM),
      photo("It is a loop,", PH_ALBLASSER, "The Alblasserwaard")),
    P("P7",
      photo(0, PH_TURF_ART, "Peat cutting, Rijksmuseum painting"),
      sat("Dried peat, called turf,", 4.93, 52.22, 0.12, "The Vinkeveen lakes, dug out for turf", date=SUM),
      stat("A 2016 study added", "19.8 KM³", "Peat lost from the Dutch coastal plain in 1,000 years", ERK),
      chart("Two thirds of that", "Why the peat is gone", "%", [["Drainage", 66], ["Digging and burning", 34]], ERK, highlight=0),
      m("The result: the coastal", v(NLW, highlight=[LOW], places=[AMS, ROT, HAGUE, LEIDEN])),
      m("and most of it", v(NORTHSEA, highlight=[LOW]))),
    P("P7b",
      sat(0, 4.89, 52.37, 0.06, "Central Amsterdam", date=SUM),
      photo("so builders drove long", PH_CANALS, "Canal houses on wooden piles, Amsterdam"),
      photo("The Royal Palace on", PH_PALACE, "The Royal Palace on Dam Square"),
      stat("stands on more than", "13,659", "Wooden piles under the Royal Palace, Amsterdam", "Wikipedia, Royal Palace of Amsterdam"),
      sat("Much of the old", 4.885, 52.367, 0.04, "The canal ring, Amsterdam", date=SUM)),
    P("P8",
      m(0, v(NL, highlight=[LOW])),
      stat("corrected a famous error", "55 %?", "What a 2007 UN climate (IPCC) report said lies below sea level", PBL),
      stat("not fifty-five percent of", "26 %", "Below sea level (the IPCC had said 55 %)", PBL),
      stat("Fifty-nine percent of the", "59 %", "Land that can flood, from the sea or the rivers", PBL),
      m("Which raises a question.", v(NL, highlight=[LOW, "Zeeland@alt"], places=[AMS, ROT])),
      photo("where does the water", PH_POLDER_FOG, "Polder water, held below the land")),
)

chapter(
    P("P9",
      sat(0, 4.72, 52.20, 0.2, "Lakes left by peat digging, Nieuwkoopse Plassen", date=SUM),
      m("The worst was the", v(NLW, places=[AMS, LEIDEN, HAARLEM, HMEER])),
      stat("about nine thousand hectares", "9,100 → 16,850 HA", "Growth of the Haarlemmermeer, 1250 to 1848", "Flevolands Geheugen"),
      sat("swallowing farms and villages", 4.69, 52.30, 0.35, "The Haarlemmermeer polder today", date=SPR)),
    P("P10",
      photo(0, PH_ZAANSE, "Windmills at the Zaanse Schans"),
      m("In 1607 a group", v(NLW, places=[AMS, BEEM])),
      photo("Each investor paid for", PH_BEEMSTER_MAP, "The Beemster, map of 1658"),
      sat("betting that the lake", 4.93, 52.56, 0.35, "The Beemster and its ring canal", date=SPR),
      stat("with a canal outside,", "43 MILLS", "Drained the Beemster, 1607-1612, behind a 38 km dike", "Canon van Nederland"),
      sat("By 1612 the lake", 4.91, 52.55, 0.2, "The Beemster's grid of fields", date=SPR),
      stat("In 1999 the Beemster", "1999", "The Beemster becomes a UNESCO World Heritage site", "UNESCO"),
      photo("a model of how", PH_BEEMSTER, "Bulb fields in the Beemster")),
    P("P11",
      photo(0, PH_LEEGHWATER, "Jan Adriaenszoon Leeghwater (1575-1650)"),
      photo("He went on to", PH_LEEGH_WORK, "Leeghwater the millwright, 19th-century print"),
      stat("His plan was never", "1629", "Leeghwater's windmill plan for the Haarlemmermeer, never built", "ASME, Cruquius landmark")),
    P("P12",
      photo(0, PH_KINDERDIJK, "The mills of Kinderdijk"),
      sat("At Kinderdijk, east of", 4.64, 51.885, 0.05, "Kinderdijk", date=SUM),
      stat("They were built in", "1738 · 1740", "The Kinderdijk mills; UNESCO World Heritage since 1997", "UNESCO"),
      sat("a sinking polder dry,", 4.75, 51.87, 0.3, "The Alblasserwaard behind the mills", date=SUM),
      photo("But every mill that", PH_KINDERDIJK_OLD, "Kinderdijk, mid-20th century")),
    P("P13",
      m(0, v(NLW, places=[AMS, LEIDEN, HMEER])),
      stat("In November the water", "1836", "Two storms: 29 Nov toward Amsterdam, 26 Dec toward Leiden", "Flevolands Geheugen"),
      m("In December it flooded", v(NLW, places=[LEIDEN, HMEER, HAARLEM])),
      photo("Three steam pumping stations,", PH_CRUQUIUS, "The Cruquius pumping station"),
      photo("Cruquius alone drove eight", PH_CRUQUIUS_IN, "Cruquius, built 1846-1849"),
      stat("lifting about two hundred", "~210 M³/MIN", "Water lifted by Cruquius's eight pumps", "ASME landmark #153"),
      photo("The station kept pumping", PH_RINGVAART, "The ring canal around the Haarlemmermeer"),
      photo("The new polder was", PH_HMEER_MAP, "The new Haarlemmermeer polder"),
      sat("Today Schiphol airport stands", 4.76, 52.31, 0.12, "Schiphol airport", date=SUM),
      stat("about three meters below", "−3 M", "Schiphol, below NAP (about)", "Wikipedia, Amsterdam Airport Schiphol"),
      photo("The sea was another", PH_MARKER, "A stone sea dike")),
)

chapter(
    P("P14",
      m(0, v(SW, places=[DORDT, KDIJK])),
      stat("On a November night", "1421", "The Saint Elizabeth flood drowns the Grote Hollandse Waard", "Wikipedia, Kinderdijk"),
      photo("broke through the dikes", PH_DORT, "Dordrecht, painted by Aelbert Cuyp, 17th century"),
      sat("Its villages disappeared under", 4.80, 51.75, 0.3, "The Biesbosch, south of Dordrecht", date=SUM),
      photo("the Alblasserwaard polder stayed", PH_ALBLASSER, "The Alblasserwaard"),
      photo("it is where the", PH_KINDERDIJK_OLD, "Kinderdijk, mid-20th century")),
    P("P15",
      m(0, v(ZZ, places=[AMS])),
      stat("In January 1916 a", "1916", "Storm surge breaks Zuiderzee dikes, 13-14 January", "Wikipedia, Flood of 1916"),
      photo("Coming during the food", PH_1916, "A dike breach, 1916")),
    P("P16",
      photo(0, PH_LELY_PLAN, "Lely's plan to close the Zuiderzee, 1891-1892"),
      photo("By 1916 he was", PH_LELY_STATUE, "Cornelis Lely, statue on the Afsluitdijk"),
      m("he had long wanted", v(ZZ, highlight=["Flevoland@alt"], places=[AMS])),
      stat("into land. In 1918", "1918", "The Zuiderzee Act becomes law", RWS),
      m("On the twenty-eighth of", v(ZZ, routes=[AFSL], places=[AMS])),
      sat("the Afsluitdijk, was closed.", 5.20, 53.0, 0.5, "The Afsluitdijk", date=SUM),
      photo("The salt sea behind", PH_AFSLUIT, "Wind turbines in the IJsselmeer")),
    P("P17",
      photo(0, PH_FLEVO_DRY, "Eastern Flevoland falling dry"),
      m("Polder after polder rose", v(ZZ, highlight=["Flevoland@red"], places=[LELY, ALMERE])),
      photo("Its towns, Lelystad, named", PH_FLEVO_WORK, "Work in the new polder, Eastern Flevoland"),
      photo("were built on what", PH_ALMERE, "Almere"),
      stat("In all, the Zuiderzee", "165,000 HA", "New land from the Zuiderzee Works", RWS),
      sat("In 1986 Flevoland became", 5.47, 52.52, 0.25, "Lelystad", date=SUM),
      ask=("Would you move to", "Would you live on the old sea floor?")),
    P("P17b",
      m(0, v(SW, places=[WALCH])),
      sat("In October 1944 Allied", 3.58, 51.53, 0.4, "Walcheren today", date=SUM),
      m("In April 1945, weeks", v(ZZ, places=[WIER], highlight=["North Holland@alt"])),
      stat("German troops blew up", "17 APR 1945", "German troops blow up the Wieringermeer dike", "Wikipedia, Inundation of the Wieringermeer"),
      photo("It filled in about", PH_WIERINGER, "The flooded Wieringermeer, 1945"),
      photo("Both were pumped dry", PH_WIERINGER_PUMPS, "Pumps draining the Wieringermeer again, 1945"),
      m("But nothing had prepared", v(SW, places=[ZIER, ROT])),
      photo("and for the barge", PH_EVEGROEN, "Skipper Arie Evegroen, remembered in stone")),
)

chapter(
    P("P18",
      m(0, v(SW, highlight=["Zeeland@accent"], places=[ROT, ZIER])),
      photo("reach the sea through", PH_ASTER, "The delta of the Rhine, Meuse and Scheldt, from orbit"),
      stat("On the night of", "31 JAN 1953", "Spring tide and a northwest storm", WSM),
      m("a spring tide met", v(NORTHSEA, routes=[STORM53])),
      m("The water rose over", v(SW, highlight=["Zeeland@red", "South Holland@red", "North Brabant@red"], places=[ROT]))),
    P("P19",
      photo(0, PH_1953_ZIER, "Zierikzee, 1953"),
      photo("Many climbed onto roofs", PH_1953_HOUSE, "A wrecked house, 1953"),
      photo("some waited in the", PH_BOMMEL, "A dike breach at Den Bommel, February 1953"),
      stat("One thousand eight hundred", "1,836", "People drowned in the Netherlands, 1953", WSM),
      photo("Around two hundred thousand", PH_1953_OUDEN, "Oudenhoorn from the air, 1953"),
      stat("and seventy-two thousand people", "72,000", "People evacuated; about 200,000 ha flooded", "Watersnoodmuseum (Louwerse)"),
      photo("Across the sea, in", PH_1953_EVAC, "Evacuees from Zierikzee arrive in Dordrecht")),
    P("P19b",
      sat(0, 4.585, 51.965, 0.06, "The Hollandse IJssel at Nieuwerkerk", date=SUM),
      m("Behind that dike lay", v(NLW, highlight=[LOW], places=[LOWEST, ROT])),
      photo("The local officials ordered", PH_EVEGROEN, "A monument to the ship, with skipper Evegroen"),
      sat("be steered into the", 4.59, 51.962, 0.045, "The dike at Nieuwerkerk", date=SUM),
      stat("volunteers piled sandbags behind", "THE TWO BROTHERS", "The barge that plugged the dike, 1 Feb 1953", "Canon van Nederland")),
    P("P19c",
      sat(0, 3.99, 51.62, 0.05, "Ouwerkerk, Zeeland", date=SUM),
      stat("was shut on the", "6 NOV 1953", "The last breach closed, at Ouwerkerk", "IADC; Watersnoodmuseum"),
      photo("caissons built in Britain", PH_OUWERKERK, "The Ouwerkerk caissons, now the flood museum"),
      m("the Normandy landings. They", v({"lon": 1.5, "lat": 50.6, "span": 7.0}, places=[place("Normandy", -0.6, 49.33, "Normandy, 1944", "site"), place("Ouwerkerk", 3.99, 51.62, "Ouwerkerk", "site")])),
      sat("Today they hold the", 3.995, 51.618, 0.035, "The caissons at Ouwerkerk", date=SUM)),
    P("P20",
      stat(0, "+20 DAYS", "The Delta Committee is set up", "Wikipedia, Delta Works"),
      photo("Its answer was the", PH_HARINGVLIET, "Building the Haringvliet dam"),
      m("dams and barriers that", v(SW, places=[OSK, MAES], highlight=["Zeeland@accent"])),
      sat("The biggest, across the", 3.95, 51.55, 0.5, "The Eastern Scheldt", date=SUM),
      sat("Fishermen, oyster farmers and", 4.05, 51.50, 0.15, "Oyster beds at Yerseke, Eastern Scheldt", date=SUM),
      photo("a closed dam would", PH_VOLKERAK, "Building a closed dam: the Volkerak, 1967"),
      stat("In 1976 the government", "1976", "The plan changes: a storm-surge barrier instead of a dam", WSM),
      stat("Instead of a wall,", "62 GATES", "The Eastern Scheldt barrier, closed only in storms", WSM),
      sat("so the tide still", 3.69, 51.64, 0.12, "The Eastern Scheldt barrier", date=SUM),
      photo("Queen Beatrix opened it", PH_OSK, "The Eastern Scheldt barrier")),
    P("P21",
      sat(0, 4.163, 51.955, 0.1, "The Maeslantkering", date=SUM),
      stat("Two gates, each about", "2 × 210 M", "The gates of the Maeslantkering", "Wikipedia, Maeslantkering"),
      sat("rest in docks on", 4.158, 51.952, 0.08, "A gate in its dock", date=SUM),
      photo("When a surge of", PH_MAESLANT, "The Maeslantkering closing"),
      sat("across a three hundred", 4.17, 51.96, 0.3, "The Nieuwe Waterweg to Rotterdam", date=SUM),
      stat("It first closed for", "8 NOV 2007", "The Maeslantkering's first storm closure", "Wikipedia, Maeslantkering"),
      photo("The walls were finished.", PH_OSK2, "The Eastern Scheldt barrier, 2025")),
)

chapter(
    P("P22",
      m(0, v(NL, highlight=[LOW], places=[AMS, ROT, HAGUE])),
      photo("Amsterdam, Rotterdam, The Hague", PH_ROTTERDAM, "The port of Rotterdam"),
      sat("Rotterdam is Europe's biggest", 4.05, 51.95, 0.4, "Maasvlakte, the port of Rotterdam", date=SUM),
      photo("Leaving would mean leaving", PH_PALACE, "Dam Square, Amsterdam")),
    P("P23",
      m(0, v(NLW, highlight=["Utrecht@alt", "South Holland@accent"], places=[AMS, ROT, LEIDEN])),
      sat("Green Heart, between the", 4.75, 52.1, 0.6, "The Green Heart, between the cities", date=SUM),
      photo("the ground still drops", PH_PEAT_MEADOW, "Peat meadows near Amsterdam"),
      stat("by about a centimeter", "~1 CM / YEAR", "Peat meadow subsidence (average)", "Regio Gooi en Vechtstreek"),
      sat("If nothing changes, some", 4.82, 52.08, 0.15, "Peat meadows in the Green Heart", date=SUM),
      stat("has called for cutting", "−70 %", "Target cut in peat subsidence by 2050 (Rli advice)", "Tweede Kamer, kst-35141-3"),
      sat("The main tool is", 4.62, 52.12, 0.15, "Peat meadows near Alphen aan den Rijn", date=SUM),
      photo("but the fields get", PH_DIKE_FARM, "A farm behind a dike"),
      m("Farmers, nature groups and", v(NLW, highlight=["Utrecht@alt", "South Holland@accent"], places=[LEIDEN])),
      sat("still arguing over where", 4.70, 52.0, 0.25, "Peat meadows of the Krimpenerwaard", date=SUM),
      stat("the extra cost of", "€22 BN", "Extra cost of subsidence to 2050 (PBL estimate)", "Tweede Kamer, kst-35141-3")),
    P("P23b",
      m(0, v(NORTH, highlight=["Groningen@red"], places=[GRON])),
      stat("Under Groningen lies one", "1959", "The Groningen gas field is found near Slochteren", "Wikipedia, Groningen gas field"),
      photo("Decades of pumping out", PH_SLOCHTEREN, "Work on the Slochteren gas field, 1963"),
      stat("By 2013 the center", "~33 CM", "Subsidence at the centre of the Groningen gas field, 2013", "de Waal et al., PIAHS 2015"),
      sat("since 1991 small earthquakes,", 6.78, 53.32, 0.6, "Above the Groningen gas field", date=SUM),
      sat("The land that the", 6.82, 53.33, 0.15, "Villages of Groningen", date=SUM)),
    P("P24",
      m(0, v(RIVERS, routes=[RHINE], places=[LOBITH, ROT])),
      sat("at the point where", 6.11, 51.86, 0.15, "Lobith, where the Rhine enters", date=SUM),
      stat("rose to almost seventeen", "16.68 M", "Rhine at Lobith above NAP, 1995", RWS),
      m("it rose so high", v(RIVERS, highlight=["Gelderland@red"], places=[LOBITH])),
      stat("about a quarter of", "~250,000", "People evacuated in 1995", "Vox (Radboud University); Rijkswaterstaat"),
      sat("the largest evacuation in", 5.43, 51.89, 0.15, "The Waal and its dikes near Tiel", date=SUM),
      stat("After that flood and", "1993 · 1995", "Two high-water years on the Rhine and the Meuse", RWS),
      sat("Instead of only raising", 5.86, 51.85, 0.08, "The new side channel of the Waal at Nijmegen", date=SUM),
      photo("gave the Rhine and", PH_SPIEGELWAAL, "The new side channel at Nijmegen"),
      stat("more space at thirty-four", "34", "Room for the River locations, 2006-2015", "Room for the River programme"),
      stat("Planners now prepare for", "18,000 M³/S", "Rhine discharge the Delta Programme plans for", "Delta Programme")),
    P("P24b",
      sat(0, 4.19, 52.05, 0.05, "The Sand Motor", date=SUM),
      stat("about twenty-one million cubic", "21.5 M M³", "Sand in the Sand Motor, 2011", "dezandmotor.nl"),
      photo("it in a giant", PH_ZANDMOTOR_AIR, "The Sand Motor from the air, 2016"),
      m("near The Hague: the", v(NLW, places=[SANDM, HAGUE])),
      photo("Instead of fighting the", PH_ZANDMOTOR, "The Sand Motor at Ter Heijde"),
      sat("currents spread the sand", 4.26, 52.09, 0.25, "Dunes and beaches near The Hague", date=SUM)),
    P("P25",
      sat(0, 4.27, 52.11, 0.1, "The coast at Scheveningen", date=SUM),
      stat("to rise between about", "59-124 CM", "Sea-level rise off the Dutch coast by 2100 if emissions stay high", "KNMI'23"),
      m("by the end of", v(NORTHSEA, highlight=["Netherlands@red"])),
      photo("and more if the", PH_THWAITES, "Thwaites Glacier, West Antarctica"),
      m("So the sea is", v(NL, highlight=[LOW], places=[AMS, ROT])),
      photo("The Dutch answer, for", PH_MARKER, "A stone dike on the Marker Wadden"),
      sat("watch the water, pump", 4.64, 51.885, 0.12, "Kinderdijk and the Lek", date=SPR),
      photo("The country that sank", PH_ZAANSE, "Windmills on the Zaan"),
      photo("also the one that", PH_HOGEBEINTUM, "Hogebeintum, a village on its terp")),
    P("P26",
      m(0, v(NLW, highlight=[LOW], places=[AMS, ROT, LOWEST])),
      photo("where a quarter of", PH_ALMERE, "Almere, built on the old sea floor"),
      photo("would you trust the", PH_DIKE_ROAD, "A dike road"),
      ask=("would you trust the", "Trust the dikes, or move to higher ground?")),
)

BEAT_WORDS = 14  # a map shot gets a camera move whenever it would hold one framing longer than this (6.5 s check)


def push_span(span):
    """Push-in target. A view above Sentinel's 2.0-degree limit stays above it (2.05), see green-sahara; a painted
    view (over 2.5) stays over 2.5 so Sentinel never patches it."""
    if span > 2.5:
        return max(2.55, round(span * 0.85, 3))
    if span > 2.0:
        return max(2.05, round(span * 0.75, 3))
    return max(0.06, round(span * 0.62, 3))


def word_at(text, at):
    if isinstance(at, int):
        return at
    ws, ph = text.split(), at.split()
    for i in range(len(ws)):
        if [w.strip(".,;:!?\"'()").lower() for w in ws[i:i + len(ph)]] == [w.strip(".,;:!?\"'()").lower() for w in ph]:
            return i
    raise ValueError(at)


for ch in chapters:
    for para in ch["paragraphs"]:
        anchors = Paragraph.model_validate(para).anchor_indices()  # also checks that every anchor phrase exists
        n = len(para["text"].split())
        for i, (sh, start) in enumerate(zip(para["shots"], anchors)):
            end = anchors[i + 1] if i + 1 < len(anchors) else n
            steps = (sh.get("map") or {}).get("steps", [])
            if sh["type"] != "map" or not steps or any(st.get("compare") for st in steps) or "view" not in steps[0]:
                continue
            if any(steps[0].get(k) for k in ("highlight", "routes", "arrows")):
                continue  # the engine zooms out to fit a painted region; a bare move step would jump to the hand span
            marks = [start] + [word_at(para["text"], st["at"]) for st in steps[1:] if st.get("at") is not None] + [end]
            last = steps[-1].get("view") or steps[0]["view"]
            for a, b in list(zip(marks, marks[1:])):
                k = (b - a) // (BEAT_WORDS + 1)
                if k == 0:
                    continue
                vw = dict(last)
                for j in range(1, k + 1):
                    vw = {"lon": vw["lon"], "lat": vw["lat"], "span": push_span(vw["span"]) if j % 2 or vw["span"] > 2.5 else round(vw["span"] * 1.6, 3)}
                    move = {"at": a + (b - a) * j // (k + 1), "view": vw}
                    for key in ("date", "layer"):
                        if steps[0].get(key):
                            move[key] = steps[0][key]
                    steps.append(move)
            steps[1:] = sorted(steps[1:], key=lambda st: word_at(para["text"], st["at"]) if st.get("at") is not None else 0)

script = {
    "title": "Why the Netherlands Sank Below the Sea",
    "voice": "am_michael",
    "voice_speed": 1.15,
    "music": "procedural",
    "map_style": "satellite",
    "look": "none",
    "sources": ["episodes/netherlands-below-sea/research.md and factcheck.md", "Contains modified Copernicus Sentinel data 2026"],
    "thumbnail": {"text": "BELOW THE SEA?"},
    "chapters": chapters,
    "youtube": {
        "title": "Why the Netherlands Sank Below the Sea",
        "description": "About a quarter of the Netherlands lies below sea level, but the sea did not rise over it. For a thousand years the Dutch drained and dug their peat bogs, and the land sank about two meters on average. This video follows how that happened: lakes that ate villages, windmills and steam pumps, the closing of the Zuiderzee, the flood of 1953 and the Delta Works, and why eighteen million people still live below the sea.",
        "tags": ["Netherlands", "below sea level", "Holland", "polder", "peat subsidence", "Zuiderzee", "Afsluitdijk", "Delta Works", "1953 flood", "Kinderdijk", "Haarlemmermeer", "geography", "satellite images"],
        "pinned_comment": "If you lived in a country where a quarter of the land is below the sea, would you trust the dikes, or would you move to higher ground?",
    },
}
out = HERE / "script.json"
out.write_text(json.dumps(script, ensure_ascii=False, indent=1) + chr(10), encoding="utf-8")
words = sum(len(p["text"].split()) for c in chapters for p in c["paragraphs"])
shots = [s for c in chapters for p in c["paragraphs"] for s in p["shots"]]
kinds = {k: sum(1 for s in shots if s["type"] == k) for k in ("map", "photo", "stat", "document", "chart")}
print(f"{words} words, {len(chapters)} chapters, {len(shots)} shots {kinds}")
