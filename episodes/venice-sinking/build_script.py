"""Builds script.json for venice-sinking.  python build_script.py

Same production logic as episodes/netherlands-below-sea (hand-placed shots, a photo or map frame at most twice,
push-ins that stay above Sentinel's 2-degree limit). The narration lives in drafts/narration.md (one "Pnn:" line
per paragraph, "## Title (mood)" per chapter); every sentence comes from research.md (OK rows).
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


def place(name, lon, lat, label=None, kind="site", icon=None):
    d = {"name": name, "lon": lon, "lat": lat, "kind": kind, "label": label if label is not None else name}
    if icon:
        d["icon"] = icon
    return d


def m(at, *steps, text=None, cut=True):
    s = {"type": "map", "at": at, "map": {"steps": list(steps)}}
    if cut:
        s["map"]["cut"] = True
    if text:
        s["on_screen_text"] = text
    return s


def step(at, **kw):
    return {"at": at, **kw}


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


CLEAR_DAY = "2025-07-12"  # wide unpainted views: a MODIS day (checked in the storyboard)


def v(view, at=None, **kw):
    if view["span"] > 2.5 and not kw.get("highlight") and "date" not in kw:
        kw["date"] = CLEAR_DAY
    d = {"view": fresh(view), **kw}
    if at is not None:
        d["at"] = at
    return d


SAT_MIN_SPAN = 0.08  # Netherlands storyboard: narrower Sentinel views were soft
SUM = "2025-06-01/2025-09-30"  # scratch test 2026-11-20: 2025-06-10 and 2025-08-12 cover the lagoon in one pass


def sat(at, lon, lat, span, label=None, **kw):
    kw.setdefault("date", SUM)
    return m(at, v(near(lon, lat, max(span, SAT_MIN_SPAN)), **kw), text=label)


def photo(at, name, text=None):
    d = {"type": "photo", "at": at, "photo": name}
    if text:
        d["on_screen_text"] = text
    return d


def stat(at, value, label, source, note=None):
    s = {"value": value, "label": label, "source": source}
    if note:
        s["note"] = note
    return {"type": "stat", "at": at, "stat": s}


def chart(at, title, unit, data, source, reveal=None, highlight=0, kind="bar"):
    c = {"type": kind, "title": title, "unit": unit, "data": data, "source": source, "highlight": highlight}
    if reveal:
        c["reveal"] = reveal
    return {"type": "chart", "at": at, "chart": c}


def doc(at, text, source, highlight=None, title=None):
    d = {"text": text, "source": source}
    if highlight:
        d["highlight"] = highlight
    if title:
        d["title"] = title
    return {"type": "document", "at": at, "document": d}


TEXT = {}
HEADS = []
for line in (HERE / "drafts" / "narration.md").read_text(encoding="utf-8").splitlines():
    if line.startswith("## "):
        mt = re.match(r"## (?:\d+\. )?(.+?) \((\w+)\)", line)
        HEADS.append((mt.group(1), mt.group(2)))
    mp = re.match(r"(P\w+)(?: \([^)]*\))?: (.+)", line)
    if mp:
        TEXT[mp.group(1)] = mp.group(2).strip()


def P(key, *shots, ask=None):
    d = {"text": TEXT[key], "shots": list(shots)}
    if ask:
        d["ask"] = {"at": ask[0], "text": ask[1]}
    return d


# ------------------------------------------------------------------ views (painted views stay above 2.5 degrees)
ITALY = {"lon": 12.6, "lat": 43.4, "span": 11.0}
NADR = {"lon": 12.7, "lat": 45.2, "span": 3.4}
MED = {"lon": 15.0, "lat": 41.0, "span": 24.0}
LAG = {"lon": 12.30, "lat": 45.37, "span": 0.55}       # the whole lagoon (Sentinel-2)
LAG_C = {"lon": 12.30, "lat": 45.42, "span": 0.30}     # central lagoon: Venice, Marghera, the Oil Canal
VEN = "Venezia@red"                                     # Natural Earth admin-1: the Metropolitan City of Venice

LS = "landsat"
CMP_LIDO = {"before": "2002-06-01/2002-09-30", "after": "2025-06-01/2025-09-30", "source": LS, "seconds": 2.6,
            "hold": 0.6, "label_before": "2002", "label_after": "2025"}
CMP_CENTRAL = {"before": "1985-06-01/1985-09-30", "after": "2025-06-01/2025-09-30", "source": LS, "seconds": 2.8,
               "hold": 1.6, "label_before": "1985", "label_after": "2025"}

# ------------------------------------------------------------------ sources (research.md)
CPSM = "Comune di Venezia, Centro Maree"
ISPRA = "ISPRA, CPSM, CNR-ISMAR (2019 report)"
CPSM21 = "Comune di Venezia / ISPRA, tide forecasts 2021"
SAR = "Sarretta et al., Continental Shelf Research 2010"
ZAN = "Zanchettin et al., NHESS 2021"
CTP = "Carbognin, Teatini, Tosi (Univ. Padova)"
AUT = "Autorità per la Laguna di Venezia, MOSE log"
CONV = "Nicholls, Haasnoot, Lionello, The Conversation, Apr 2026"
MIN = "Italian Ministry of Environment, lagoon chronology"

# ------------------------------------------------------------------ photos (Commons, licence checked)
PH_SM_FLOOD = "File:Aqua alta venice san marko.jpg"
PH_SM_NIGHT = "File:St Mark's Square, Venice flooded by extreme midnight tide.jpg"
PH_SM_2008 = "File:Acqua alta Venezia.JPG"
PH_SM_CAFE = "File:San Marco, 30100 Venice, Italy - panoramio (824).jpg"
PH_SM_WALK = "File:San Marco, 30100 Venice, Italy - panoramio (826).jpg"
PH_SM_2024 = "File:Plaza de San Marcos en 2024.jpg"
PH_NOV = "File:November in Venice.jpg"
PH_CANAL_HW = "File:Canal in Venice, high water on walkway.jpg"
PH_2019 = "File:Acqua alta del 12 novembre 2019.jpg"
PH_2019_HELP = "File:DENTAC Italy Soldiers lend a hand in Venice flood (5971263).jpg"
PH_2019_NESDIS = "File:Rising Sea Levels and Sirocco Winds Worsen Flooding for Venice (NESDIS 2019-11-14).jpg"
PH_FLOOD_DEF = "File:Flood defence.jpg"
PH_1966_A = "File:Alluvione di Venezia del 1966.jpg"
PH_1966_SM = "File:Piazza San Marco il 4 novembre 1966.jpg"
PH_1966_PZ = "File:Piazzetta San Marco - alluvione di Venezia 1966.jpg"
PH_1966_B = "File:Venezia Acqua Alta 4 novembre 1966.jpg"
PH_1966_PAGLIA = "File:Ponte della Paglia - Venezia (1966).jpg"
PH_1966_WX = "File:Bollettino meteorologico quotidiano del giorno 4 novembre 1966.jpg"
PH_1966_MARK = "File:Signe Acqua Alta 1966 - Cloître monastère San Lazzaro décembre 2022.JPG"
PH_AIR_CITY = "File:Venice Old Town Lagoon Aerial View.jpg"
PH_AIR_MARSH = "File:Venice Lagoon from above (7264045440).jpg"
PH_AIR_LIDO = "File:Aerial photographs of Venice 2013, Anton Nossik, 029.jpg"
PH_AIR_INLET = "File:Aerial photographs of Venice 2013, Anton Nossik, 012.jpg"
PH_AIR_PELL = "File:Aerial photographs of Venice 2013, Anton Nossik, 018.jpg"
PH_ISS_LAG = "File:ISS-39 Venice Lagoon, Italy.jpg"
PH_ISS_VEN = "File:ISS-46 Venice and Murano, Italy.jpg"
PH_LANDSAT_NAMES = "File:Lagoon-of-venice-landsat-1 Names.jpg"
PH_ASTER = "File:Venice, Italy (ASTER).jpg"
PH_BELLOTTO = "File:(Venice) Veduta del Canal Grande dalla Punta della Dogana - Bernardo Bellotto.jpg"
PH_CAFFI = "File:Ca' Rezzonico - Il Canal Grande verso Ca' Pesaro (Inv.219) - Ippolito Caffi.jpg"
PH_SALUTE = "File:Grand Canal Santa Maria della Salute Vaporetto Gondola Venice 01.jpg"
PH_GRAND = "File:Venice view, Grand Canal, Venice, Italy.jpg"
PH_KAUFMANN = "File:Karl Kaufmann Venedig Acqua Alta.jpg"
PH_PILES = "File:Esselborn2 dib 002.jpg"
PH_MAP_1546 = "File:Venezia 1546-smbl5.jpg"
PH_MAP_MAZA = "File:Carte hydrographique de la Vénétie - Io. Bat. Maza f. - btv1b53170332x (2 of 3).jpg"
PH_MAP_1702 = "File:Kaart van de omgeving van Venetië, ca. 1702 Les Environs de Venise (titel op object) Les Forces de l'Europe, Asie, Afrique et Amerique, ou description des principales villes avec leurs fortification, RP-P-OB-83.034-196.jpg"
PH_MAP_1804 = "File:Map of the lagoon of Venice - Roux Joseph - 1804.jpg"
PH_MAP_1893 = "File:Admiralty Chart No 1483 Chioggia Malamocco Lido and Venice, Published 1893.jpg"
PH_MAP_1975 = "File:Carta idrografica della laguna veneta - 1975.jpg"
PH_ENI = "File:Raffineria ENI Porto Marghera 2022-05.jpg"
PH_PM3 = "File:Porto Marghera 2016 3.jpg"
PH_PM5 = "File:Porto Marghera 2016 5.jpg"
PH_PM_SUNSET = "File:Porto Marghera - Tramonto (25343715761).jpg"
PH_PM_REF = "File:Porto Marghera Raffineria - panoramio.jpg"
PH_ISS_CANAL = "File:ISS046-E-45729 - View of Italy - Venetian lagoon - San Giorgio in Meergras-Alga - Canale di Malamocco-Marghera - Fusina - Moranzani - Casse di colmata - Canale Avesa (cropped).jpg"
PH_ISS_ITALY = "File:ISS048-E-6037 - View of Italy.jpg"
PH_PELL = "File:Pellestrina (Lagune de Venise) (8087744696).jpg"
PH_CNR = "File:Piattaforma ISMAR-CNR.jpg"
PH_NOMOSE = "File:\"No MOSE\" banner in Venice.jpg"
PH_MOSE_BARGE = "File:Chiatta MOSE Venezia.jpg"
PH_MOSE_1 = "File:Laguna di Venezia MOSE 001.JPG"
PH_MOSE_2 = "File:Laguna di Venezia MOSE 002.JPG"
PH_MOSE_SCHEME = "File:Le projet Mose (Venise) (5010485583).jpg"
PH_MOSE_JACK = "File:Le \"Jack-up\", pour la maintenance des barrières mobiles du projet Mose (Venise) (35696088382).jpg"
PH_MOSE_ARS = "File:Le projet Mose à lArsenal (Venise) (5010485591).jpg"
PH_MOSE_EXPO = "File:Exposition sur le projet Mose (Venise) (35056029853).jpg"
PH_LIDO_WORK = "File:Lido di Venezia - 35308936480.jpg"
PH_LIDO_WORK2 = "File:Lido di Venezia - 35527228302.jpg"
PH_1966_EXPO = "File:L'inondation de 1966 à Venise (exposition sur le projet Mose, Venise) (35696067702).jpg"

# ------------------------------------------------------------------ places
VENICE = place("Venice", 12.335, 45.437, "Venice", "city")
LIDO_IN = place("Lido inlet", 12.42, 45.42, "Lido inlet", icon="sea")
MAL_IN = place("Malamocco inlet", 12.335, 45.335, "Malamocco inlet", icon="sea")
CHI_IN = place("Chioggia inlet", 12.305, 45.232, "Chioggia inlet", icon="sea")
MARGHERA = place("Porto Marghera", 12.245, 45.455, "Porto Marghera", icon="factory")
MESTRE = place("Mestre", 12.24, 45.49, "Mestre", "city")
PELL = place("Pellestrina", 12.305, 45.285, "Pellestrina")
SALUTE = place("Punta della Salute", 12.336, 45.430, "Punta della Salute tide gauge", icon="water")
SANMARCO = place("St Mark's Square", 12.339, 45.434, "St Mark's Square")
ZACCARIA = place("San Zaccaria", 12.343, 45.434, "San Zaccaria")
CNR = place("CNR platform", 12.508, 45.314, "CNR platform, 15 km out", icon="water")
BRONDOLO = place("Brondolo", 12.29, 45.19, "Brondolo")
CAORLE = place("Caorle", 12.88, 45.60, "Caorle", "city")
FUSINA = place("Fusina", 12.255, 45.42, "Fusina")
CHIOGGIA = place("Chioggia", 12.28, 45.22, "Chioggia", "city")
PADUA = place("Padua", 11.88, 45.41, "Padua", "city")
TREVISO = place("Treviso", 12.24, 45.67, "Treviso", "city")

ARR_BRENTA_OLD = {"from": [12.10, 45.42], "to": [12.255, 45.42], "color": "blue", "label": "Brenta (old mouth)", "bend": 0.05}
ARR_BRENTA_NEW = {"from": [12.13, 45.40], "to": [12.29, 45.19], "color": "accent", "label": "Brenta, sent south", "bend": -0.2}
ARR_PIAVE = {"from": [12.55, 45.55], "to": [12.88, 45.60], "color": "accent", "label": "Piave, turned east", "bend": 0.2}
ARR_SILE = {"from": [12.40, 45.58], "to": [12.62, 45.48], "color": "accent", "label": "Sile, into the old Piave bed", "bend": 0.15}
ARR_SCIROCCO = {"from": [19.5, 39.6], "to": [12.9, 45.1], "color": "red", "label": "Scirocco", "bend": 0.1}
ARR_SEA_IN = [{"from": [12.62, 45.30], "to": [12.42, 45.42], "color": "blue", "label": "Tide", "bend": 0.1},
              {"from": [12.52, 45.20], "to": [12.335, 45.335], "color": "blue", "bend": 0.1},
              {"from": [12.45, 45.12], "to": [12.305, 45.232], "color": "blue", "bend": 0.1}]
ARR_RIVERS_IN = [{"from": [11.95, 45.50], "to": [12.22, 45.42], "color": "accent", "label": "Rivers and mud", "bend": 0.1},
                 {"from": [12.25, 45.68], "to": [12.40, 45.52], "color": "accent", "bend": -0.1}]
OIL_CANAL = {"from": [12.335, 45.335], "via": [[12.27, 45.37], [12.235, 45.41]], "to": [12.245, 45.445], "mode": "line",
             "color": "red", "seconds": 1.8, "label": "Oil Canal, 1960s"}

chapters = []
heads = iter(HEADS)


def chapter(*paras):
    title, mood = next(heads)
    chapters.append({"title": title, "mood": mood, "paragraphs": list(paras)})


chapter(
    P("P0",
      m(0, v(near(12.45, 45.33, 0.35), places=[CNR], date=SUM)),
      stat("rose to one hundred", "173 CM", "Sea level off Venice, 22 November 2022", AUT),
      photo("That is the kind", PH_2019, "12 November 2019"),
      photo("had put most of", PH_SM_NIGHT, "St Mark's Square at high water"),
      photo("This time, almost nobody", PH_SM_2024, "St Mark's Square"),
      m("Somewhere under the sea,", v(near(12.40, 45.38, 0.30), places=[LIDO_IN, MAL_IN], date=SUM)),
      photo("We will get to", PH_MOSE_2, "MOSE works in the lagoon")),
    P("P1",
      m(0, v(ITALY, highlight=[VEN], places=[VENICE])),
      m("in a shallow lagoon", v(NADR, highlight=[VEN], places=[VENICE, PADUA, TREVISO])),
      sat("The lagoon covers about", 12.30, 45.37, 0.55, "The Venetian lagoon"),
      stat("five hundred and fifty", "550 KM²", "The Venetian lagoon, the largest wetland in the Mediterranean", "MOSE Venezia"),
      sat("three gaps in a", 12.36, 45.31, 0.40, None, places=[LIDO_IN, MAL_IN, CHI_IN]),
      sat("the Lido inlet, about", 12.42, 45.42, 0.10, "The Lido inlet"),
      sat("Malamocco, about four hundred,", 12.335, 45.335, 0.10, "The Malamocco inlet"),
      sat("and Chioggia, a little", 12.305, 45.232, 0.10, "The Chioggia inlet"),
      photo("For more than a", PH_BELLOTTO, "The Grand Canal, painted by Bernardo Bellotto, 18th century")),
    P("P2",
      photo(0, PH_SM_FLOOD, "St Mark's Square, December 2008"),
      stat("Of all the exceptional", "≥ 140 CM", "Exceptional tides, recorded since 1872", CPSM21),
      photo("the ones above one", PH_SM_WALK, "Walkways on St Mark's Square"),
      chart("more than a quarter", "Exceptional tides (≥ 140 cm) in Venice", "", [["1872-2017", 18], ["2018-2019", 7]], CPSM21,
            reveal=["2018 and 2019."], highlight=1),
      photo("The water is higher", PH_CANAL_HW, "High water on a canal walkway, 2024")),
    P("P3",
      m(0, v(NADR, arrows=[ARR_BRENTA_NEW], places=[VENICE])),
      photo("wells that pulled a", PH_PM_REF, "Porto Marghera"),
      sat("a canal dug for", 12.28, 45.38, 0.20, "The Malamocco-Marghera canal"),
      photo("one terrible night in", PH_1966_SM, "St Mark's Square, 4 November 1966"),
      photo("and a six-billion-euro machine", PH_MOSE_BARGE, "A MOSE work barge"),
      sat("Why is Venice sinking", 12.335, 45.437, 0.10, "Venice"),
      photo("The first reason lies", PH_AIR_CITY, "Venice from the air")),
)

chapter(
    P("P4",
      m(0, v(ITALY, highlight=[VEN], places=[VENICE, PADUA])),
      stat("In the fifth and", "400s-500s", "Mainland refugees settle the lagoon islands", "Standard history"),
      m("people from the mainland", v(NADR, arrows=[{"from": [11.88, 45.41], "to": [12.30, 45.43], "color": "accent", "label": "To the lagoon", "bend": 0.1}], places=[PADUA])),
      photo("The marshy islands were", PH_AIR_MARSH, "Marsh islands of the Venetian lagoon"),
      sat("That was the point.", 12.42, 45.49, 0.20, "Marshes of the northern lagoon")),
    P("P5",
      photo(0, PH_GRAND, "The Grand Canal"),
      stat("Under Venice lie layers", "SILT · SAND · CLAY", "The ground under the city", "Cola & Simonini 2002"),
      stat("To build on it,", "WOODEN PILES", "Driven into the mud, with stone foundations on top", "CNR wood study"),
      stat("mostly oak and larch,", "OAK · LARCH", "Most of the piles, plus alder, pine and elm", "CNR wood study"),
      photo("and set stone foundations", PH_SALUTE, "Santa Maria della Salute"),
      stat("Many piles reach a", "CARANTO", "A stiff clay layer, dried out 18,000-7,000 years ago", "Cola & Simonini 2002; Donnici et al. 2011"),
      photo("out and hardened during", PH_ISS_LAG, "The lagoon from the space station")),
    P("P6",
      photo(0, PH_CAFFI, "The Grand Canal, Ippolito Caffi, 19th century"),
      stat("Down in the waterlogged", "NO OXYGEN", "Wet mud keeps the wood from rotting", "CNR wood study"),
      photo("and the microbes that", PH_AIR_PELL, "Houses on the water's edge"),
      sat("Centuries later, much of", 12.333, 45.435, 0.08, "The historic city")),
    P("P7",
      photo(0, PH_ISS_VEN, "Venice and Murano from the space station"),
      m("The sea comes in", v(near(12.36, 45.36, 0.55), arrows=ARR_SEA_IN, date=SUM)),
      m("Rivers from the Alps", v(NADR, arrows=ARR_RIVERS_IN, places=[VENICE])),
      sat("Too much mud, and", 12.43, 45.52, 0.15, "Marsh at the lagoon's northern edge"),
      sat("Too much sea, and", 12.40, 45.33, 0.25, "The sea side of the lagoon"),
      photo("Venice needed the lagoon", PH_MAP_1893, "Venice, Lido and Malamocco, Admiralty chart of 1893"),
      photo("So the Venetians did", PH_ASTER, "Venice from orbit (ASTER)"),
      m("They moved the rivers.", v(NADR, arrows=[ARR_BRENTA_NEW, ARR_PIAVE], places=[VENICE]))),
)

chapter(
    P("P8",
      photo(0, PH_MAP_MAZA, "Hydrographic map of the Veneto, 17th century"),
      m("The Brenta, the Piave,", v(NADR, arrows=ARR_RIVERS_IN, places=[VENICE, PADUA, TREVISO])),
      sat("that channels were clogging", 12.47, 45.50, 0.20, "Channels and marshes, northern lagoon"),
      photo("For the Republic of", PH_KAUFMANN, "Venice, painted by Karl Kaufmann, around 1900"),
      sat("mud meant ships that", 12.34, 45.44, 0.18, "The channels around Venice"),
      sat("and a city no", 12.25, 45.30, 0.25, "Shallow flats of the southern lagoon")),
    P("P9",
      stat(0, "1501", "The Savi alle Acque take charge of the lagoon and its rivers", "edatlas; Gronda lagunare"),
      photo("the wise men of", PH_MAP_1702, "The surroundings of Venice, map of about 1702"),
      stat("A few years later", "1505", "A larger water council, led by the Doge", "edatlas"),
      m("On questions about the", v(NADR, highlight=["Padova@alt", "Treviso@alt", VEN], places=[PADUA, TREVISO, VENICE])),
      sat("last word, even over", 12.05, 45.40, 0.40, "The mainland west of the lagoon")),
    P("P10",
      sat(0, 12.25, 45.42, 0.30, "Fusina, where the Brenta reached the lagoon", places=[FUSINA]),
      m("the Brenta was pushed", v(NADR, arrows=[ARR_BRENTA_OLD], places=[FUSINA, VENICE])),
      stat("Between 1554 and 1577,", "1554-1577", "Brenta and Bacchiglione sent to the sea near Brondolo", MIN),
      m("to the sea near", v(NADR, arrows=[ARR_BRENTA_NEW], places=[BRONDOLO, CHIOGGIA])),
      sat("In 1610 work began", 12.18, 45.30, 0.30, "Along the lagoon's western edge"),
      stat("In 1579 a cut", "1579 · 1664", "The Piave is turned east toward Caorle, twice", MIN),
      m("turned the Piave east", v(NADR, arrows=[ARR_PIAVE], places=[CAORLE, VENICE])),
      m("In the 1680s the", v(NADR, arrows=[ARR_SILE, ARR_PIAVE], places=[CAORLE])),
      photo("and out to sea.", PH_MAP_1804, "The lagoon of Venice, map of 1804")),
    P("P11",
      photo(0, PH_LANDSAT_NAMES, "The lagoon and its inlets from Landsat"),
      sat("But the mainland paid.", 12.12, 45.32, 0.30, "Farmland on the lagoon's mainland edge"),
      photo("And the lagoon lost", PH_AIR_MARSH, "Marsh islands, central lagoon"),
      sat("A lagoon without new", 12.32, 45.30, 0.20, "Open flats of the central lagoon"),
      photo("In the twentieth century,", PH_PM_SUNSET, "Porto Marghera at sunset")),
)

chapter(
    P("P12",
      sat(0, 12.30, 45.44, 0.20, "From Venice to the mainland", places=[VENICE, MARGHERA]),
      photo("cranes, tanks and chimneys.", PH_PM3, "Porto Marghera, 2016"),
      sat("That is Porto Marghera,", 12.24, 45.45, 0.12, "Porto Marghera"),
      stat("Between 1927 and 1960,", "22 KM²", "Salt marsh filled in for the industrial zone, 1927-1960", SAR),
      sat("and the airport and", 12.33, 45.50, 0.15, "Venice airport and Mestre's lagoon edge")),
    P("P13",
      photo(0, PH_ENI, "The ENI refinery, Porto Marghera"),
      stat("From around the 1930s,", "1930s", "Industrial wells tap the groundwater under the lagoon", CTP),
      photo("and pumped out fresh", PH_PM5, "Porto Marghera"),
      stat("The pumping peaked between", "1950-1970", "Peak years of groundwater pumping", CTP)),
    P("P14",
      sat(0, 12.25, 45.45, 0.20, "Marghera and the lagoon"),
      stat("In soft layers of", "WATER HOLDS", "Groundwater keeps the grains of sand and clay apart", CTP),
      stat("Pump it out, and", "LAYERS SQUEEZE", "Take the water out, and the ground compacts", CTP),
      stat("Between 1950 and 1970,", "−12 CM", "Venice, 1950-1970", "Comune di Venezia"),
      sat("At the peak, the", 12.335, 45.437, 0.10, "Venice"),
      stat("about five millimeters a", "~5 MM / YEAR", "Sinking of Venice at the peak of pumping", CTP)),
    P("P15",
      photo(0, PH_PM_REF, "Industry at Porto Marghera"),
      stat("In the early 1970s", "1970s", "The wells are closed by law; sinking drops to about a tenth", CTP),
      sat("slowed sharply, to about", 12.26, 45.47, 0.16, "Marghera today"),
      photo("But the twelve centimeters", PH_1966_MARK, "A 1966 high-water mark, San Lazzaro"),
      sat("Venice was permanently lower,", 12.335, 45.43, 0.12, "Venice"),
      photo("And Marghera had brought", PH_ISS_CANAL, "The Malamocco-Marghera canal from the space station"),
      sat("ships far bigger than", 12.235, 45.44, 0.08, "Tanker docks at Marghera")),
)

chapter(
    P("P16",
      photo(0, PH_ENI, "Refinery tanks at Marghera"),
      m("In the 1960s, engineers", v(LAG_C, routes=[OIL_CANAL], places=[MAL_IN, MARGHERA], date=SUM)),
      sat("It runs from the", 12.31, 45.35, 0.12, "The canal at the Malamocco inlet"),
      sat("You can see it", 12.27, 45.39, 0.16, "The Oil Canal across the central lagoon"),
      photo("a dark, straight line", PH_ISS_ITALY, "The lagoon from the space station, 2016")),
    P("P17",
      stat(0, "40M M³", "Sediment dug out for the Oil Canal, much of it dumped on land", SAR),
      sat("much of that was", 12.20, 45.38, 0.15, "West of the Oil Canal"),
      sat("Worse, the straight, deep", 12.26, 45.38, 0.20, "The canal and the shallows around it"),
      m("Tides and waves pushed", v(near(12.29, 45.40, 0.26), arrows=[{"from": [12.335, 45.335], "to": [12.25, 45.40], "color": "blue", "label": "Stronger tides", "bend": 0.1}], date=SUM)),
      sat("stirring up the mud", 12.24, 45.36, 0.15, "Muddy water on the central flats")),
    P("P18",
      photo(0, PH_MAP_1975, "Hydrographic chart of the lagoon, 1975"),
      sat("from 1927, 1970 and", 12.32, 45.30, 0.30, "The central and southern lagoon"),
      stat("The lagoon lost about", "110M M³", "Sediment lost by the lagoon, 1927-2002", SAR),
      chart("Its typical depth went", "Typical depth of the lagoon", "cm", [["1927", 62], ["2002", 88]], SAR, reveal=["to eighty-eight."], highlight=1),
      sat("two meters deep more", 12.28, 45.33, 0.12, "Open flats"),
      chart("from eighty-eight square kilometers", "Open flats 0.75-2 m deep", "km²", [["1927", 88], ["2002", 206]], SAR, reveal=["to two hundred and six."], highlight=1),
      m("Salt marshes, the low", v(LAG_C, compare=CMP_CENTRAL)),
      chart("to thirty-two, less", "Salt marsh in the lagoon", "km²", [["1927", 68], ["2002", 32]], SAR, highlight=1),
      sat("In the later decades,", 12.22, 45.33, 0.15, "Flats of the southern-central lagoon"),
      chart("and the yearly loss", "Sediment lost per year", "million m³", [["1927-1970", 0.3], ["1970-2002", 0.8]], SAR, reveal=["point eight million"], highlight=1)),
    P("P19",
      sat(0, 12.28, 45.36, 0.50, "The lagoon today"),
      stat("The researchers described it", "SEDIMENT-STARVED", "How the 2010 study described the lagoon", SAR),
      sat("A deeper lagoon lets", 12.36, 45.33, 0.30, "Open water between the inlets"),
      photo("And a city that", PH_AIR_LIDO, "The Lido and the lagoon from the air"),
      photo("All it needed was", PH_1966_WX, "The weather map of 4 November 1966")),
)

chapter(
    P("P20",
      m(0, v(MED, arrows=[ARR_SCIROCCO], places=[VENICE])),
      stat("a deep low-pressure system", "3-4 NOV 1966", "Low pressure and a scirocco storm", "Il Post, 2018"),
      photo("the warm southeast wind,", PH_ISS_ITALY, "The northern Adriatic from orbit"),
      m("It piled the sea", v(ITALY, arrows=[ARR_SCIROCCO], highlight=[VEN])),
      photo("On the morning of", PH_PELL, "Pellestrina and its sea wall"),
      sat("the thin strip of", 12.305, 45.285, 0.12, "Pellestrina", places=[PELL])),
    P("P21",
      photo(0, PH_1966_SM, "St Mark's Square, 4 November 1966"),
      stat("reached one hundred and", "194 CM", "Venice, 4 November 1966: the highest tide on record", ISPRA),
      photo("On the city's own", PH_1966_PZ, "The Piazzetta, 1966"),
      stat("puts about nine tenths", "~90 %", "Of the city's walkways under water at that level", CPSM),
      photo("Electricity failed across the", PH_1966_A, "Venice under water, 1966"),
      photo("Heating oil leaked from", PH_1966_PAGLIA, "Ponte della Paglia, 1966"),
      stat("More than two thousand", "2,000+", "Shops and workshops damaged", "Il Post, 2018"),
      sat("That evening, the hospital", 12.37, 45.40, 0.12, "The Lido", places=[PELL])),
    P("P22",
      photo(0, PH_1966_EXPO, "The 1966 flood, MOSE exhibition"),
      stat("In 1973 Italy passed", "1973", "Italy's Special Law for Venice", "Camera dei deputati"),
      doc("declaring the protection of", "Law 171 of 16 April 1973: the safeguarding of Venice and its lagoon is of primary national interest.",
          "Camera dei deputati", highlight="primary national interest", title="Special Law for Venice"),
      sat("That law started half", 12.38, 45.39, 0.35, "The lagoon and its inlets"),
      photo("But the water did", PH_SM_2008, "St Mark's Square, 2008")),
    P("P23",
      sat(0, 12.336, 45.430, 0.08, "Punta della Salute", places=[SALUTE]),
      stat("Since then the average", "+32 CM", "Average sea level above the 1897 mark (2021)", CPSM21),
      photo("A study of a", PH_ISS_VEN, "Venice from the space station"),
      chart("roughly half of that", "Why the water is higher at Venice, 1872-2019", "%", [["The sea rose", 50], ["Venice sank", 50]], ZAN, highlight=1),
      photo("Every centimeter lost on", PH_SM_CAFE, "St Mark's Square at high water")),
    P("P23b",
      photo(0, PH_SM_WALK, "Walkways on St Mark's Square"),
      stat("At ninety centimeters, about", "2 %", "Walkways under water at a 90 cm tide", CPSM),
      sat("are wet, mostly around", 12.339, 45.433, 0.10, "The lowest streets, around St Mark's", places=[SANMARCO]),
      chart("At one hundred and ten,", "Share of Venice's walkways under water", "%",
            [["90 cm", 2], ["110 cm", 12], ["120 cm", 28], ["140 cm", 59]], CPSM,
            reveal=["At one hundred and twenty,", "At one hundred and forty,"], highlight=3),
      photo("Each step of ten", PH_NOV, "Venice in November"),
      sat("so a city that", 12.325, 45.442, 0.09, "Cannaregio"),
      stat("In August 2020 the", "103 CM", "30 August 2020, the highest August tide since 1872", CPSM21),
      sat("centimeters, the highest August", 12.33, 45.44, 0.14, "Venice")),
    P("P24",
      photo(0, PH_2019, "12 November 2019"),
      stat("It was a spring", "1 · SPRING TIDE", "Sun and moon pulling together", ISPRA),
      stat("The whole northern Adriatic", "2 · HIGH SEA", "November mean level almost 30 cm above normal", ISPRA),
      photo("average sea level in", PH_2019_NESDIS, "Venice and the Adriatic from orbit, 14 November 2019"),
      m("The scirocco was blowing", v(ITALY, arrows=[ARR_SCIROCCO], places=[VENICE])),
      stat("And that evening a", "3 · 4 · LOW AND WIND", "A local low; wind ~100 km/h, gusts 110", ISPRA),
      sat("of about a hundred", 12.36, 45.42, 0.20, "Across the lagoon"),
      sat("City workers at San", 12.343, 45.434, 0.09, "The waterfront at San Zaccaria", places=[ZACCARIA]),
      stat("The tide reached one", "187 CM", "12 November 2019, second highest on record", ISPRA),
      photo("and almost ninety percent", PH_SM_NIGHT, "St Mark's Square at high water"),
      stat("That year Venice had", "28", "Tides of 110 cm or more in 2019 (record)", ISPRA),
      photo("ten centimeters or more,", PH_CANAL_HW, "High water on a canal walkway"),
      stat("Five tides reached one", "5", "Tides of 140 cm or more in 2019; never more than 2 before", ISPRA),
      photo("had never shown more", PH_1966_PZ, "The Piazzetta at high water, 1966"),
      sat("Three of them came", 12.345, 45.438, 0.12, "Venice"),
      stat("In that November alone,", "~50 HOURS", "Above 110 cm in November 2019 (previous record ~24)", ISPRA),
      sat("The previous record for", 12.33, 45.43, 0.10, "The historic city"),
      photo("Tides once rare enough", PH_SM_CAFE, "Cafe tables in the water, St Mark's Square")),
)

chapter(
    P("P25",
      photo(0, PH_MOSE_EXPO, "The MOSE exhibition at the Arsenale"),
      stat("Construction began in 2003.", "2003", "MOSE construction begins", "Wikipedia, MOSE"),
      photo("rows of steel gates", PH_MOSE_SCHEME, "A MOSE gate in its seabed housing, exhibition panel"),
      photo("hollow boxes filled with", PH_LIDO_WORK, "Works at the Lido inlet, 2017"),
      m("There are seventy-eight of", v(near(12.33, 45.33, 0.48), places=[LIDO_IN, MAL_IN, CHI_IN], date=SUM)),
      m("twenty-one and twenty at", v(near(12.42, 45.42, 0.12), compare=CMP_LIDO)),
      sat("in the middle of", 12.42, 45.425, 0.08, "The artificial island between the Lido barriers"),
      sat("nineteen at Malamocco and", 12.335, 45.335, 0.10, "Malamocco: 19 gates"),
      sat("and eighteen at Chioggia.", 12.305, 45.232, 0.10, "Chioggia: 18 gates"),
      stat("Each gate is twenty", "20 × 29 M", "Width × length of the biggest gates", "Sky TG24; Structurae")),
    P("P26",
      photo(0, PH_MOSE_1, "MOSE works in the lagoon"),
      stat("one hundred and ten", "> 110 CM", "Forecast tide that raises the gates", AUT),
      photo("compressed air pushes the", PH_MOSE_ARS, "A MOSE gate at the Arsenale"),
      sat("swing up on their", 12.33, 45.333, 0.08, "The Malamocco barrier"),
      photo("and the lagoon is", PH_MOSE_2, "The barrier works"),
      sat("When the tide falls,", 12.40, 45.42, 0.12, "The Lido inlet")),
    P("P27",
      photo(0, PH_NOMOSE, "A \"No MOSE\" banner in Venice"),
      stat("In June 2014, police", "35 ARRESTS", "June 2014, including the mayor of Venice", "ANSA, 2014"),
      photo("the project, among them", PH_AIR_INLET, "An inlet of the lagoon from the air"),
      sat("who resigned days later.", 12.336, 45.44, 0.09, "Venice"),
      stat("The bill came to", "~€6 BN", "MOSE, in 2024 prices", CONV),
      photo("All seventy-eight gates were", PH_LIDO_WORK2, "The Lido inlet works, 2017"),
      stat("On the third of", "3 OCT 2020", "First raising for a real high tide", AUT)),
    P("P28",
      chart(0, "MOSE closures per season", "", [["2020/21", 20], ["2021/22", 13], ["2022/23", 19], ["2023/24", 32], ["2024/25", 23], ["2025/26", 49]], AUT,
            reveal=["thirteen,", "nineteen,", "thirty-two,", "twenty-three,", "and then forty-nine"], highlight=5),
      stat("thirty of them in", "30", "Closures in January and February 2026", CONV),
      stat("By November 2026 the", "160", "MOSE closures, October 2020 to November 2026", AUT),
      m("On the twenty-second of", v(near(12.40, 45.33, 0.45), places=[CNR], date=SUM)),
      photo("hundred and seventy-three centimeter", PH_SM_2008, "St Mark's Square"),
      m("all four barriers were", v(near(12.36, 45.31, 0.42), places=[LIDO_IN, MAL_IN, CHI_IN], date=SUM)),
      stat("Outside the gates, the", "187 · 191 · 204", "Sea level at the Lido, Chioggia and Malamocco inlets, 22 Nov 2022 (cm)", AUT),
      sat("one hundred and ninety-one", 12.305, 45.232, 0.14, "The Chioggia inlet"),
      chart("On the city's own", "Walkways under water at 170 cm", "%", [["170 cm", 82]], CPSM, highlight=0)),
    P("P29",
      sat(0, 12.335, 45.335, 0.12, "The Malamocco inlet"),
      photo("The tide is what", PH_AIR_INLET, "An inlet from the air"),
      photo("and ships need the", PH_MOSE_JACK, "A maintenance vessel for the gates"),
      stat("As the sea rises,", "WEEKS A YEAR", "How long the gates may have to stay shut as seas rise", CONV),
      photo("more often and for", PH_AIR_LIDO, "The Lido from the air"),
      sat("A barrier built for", 12.43, 45.415, 0.15, "The Lido barrier")),
)

chapter(
    P("P30",
      photo(0, PH_SM_FLOOD, "St Mark's Square at high water"),
      photo("A review of Venice's", PH_1966_MARK, "A 1966 high-water mark"),
      stat("somewhere between eleven centimeters", "11-110 CM", "Likely sea-level rise at Venice from climate change by 2100", ZAN),
      stat("In April 2026, three", "4 PATHS", "Every plan to save Venice, reviewed in April 2026", CONV),
      photo("plan to save the", PH_GRAND, "The Grand Canal"),
      sat("Keep MOSE and add", 12.42, 45.42, 0.12, "MOSE at the Lido"),
      sat("Build ring dikes around", 12.335, 45.437, 0.12, "The historic city"),
      stat("for up to four", "€0.5-4.5 BN", "Ring dikes around the city", CONV),
      m("Seal off the whole", v(near(12.26, 45.40, 0.60), date=SUM)),
      stat("for more than thirty", "€30 BN+", "A sealed lagoon with permanent pumping", CONV),
      m("Or, if the sea", v(NADR, highlight=[VEN], places=[VENICE, PADUA, TREVISO])),
      stat("for up to a", "€100 BN", "Moving people inland, if seas rise by several meters", CONV)),
    P("P31",
      sat(0, 12.25, 45.45, 0.15, "Marghera, where the wells were"),
      stat("A 2011 study by", "+25-30 CM", "Modelled uplift in 10 years from 12 seawater wells (2011)", "Teatini et al. 2011"),
      sat("modeled twelve wells in", 12.335, 45.43, 0.30, "A ring around the city"),
      stat("Other scientists have warned", "TEST FIRST", "Critics ask for far more study before injecting", "Schrefler et al. 2009"),
      photo("If it works, the", PH_MOSE_BARGE, "MOSE equipment in Venice"),
      sat("a meter of sea-level", 12.30, 45.38, 0.40, "The lagoon")),
    P("P32",
      photo(0, PH_AIR_CITY, "Venice from the air"),
      chart("In 1951, one hundred", "People living in historic Venice", "", [["1951", 174808], ["1961", 145402], ["1971", 108426], ["2015", 55589], ["2024", 48489]],
            "Comune di Venezia, statistics office", reveal=["Ten years later", "by 1971 a", "and by 2015", "At the end of 2024"], highlight=4, kind="line"),
      photo("Venice may stay above", PH_SALUTE, "Santa Maria della Salute"),
      photo("Whether it stays a", PH_BELLOTTO, "The Grand Canal, 18th century")),
    P("P33",
      photo(0, PH_SM_2024, "St Mark's Square"),
      sat("or seal the lagoon", 12.32, 45.39, 0.52, "The Venetian lagoon"),
      ask=("If you were in", "Keep closing the gates, or seal the lagoon for good?")),
)

BEAT_WORDS = 14


def push_span(span):
    if span > 2.5:
        return max(2.55, round(span * 0.85, 3))
    if span > 2.0:
        return max(2.05, round(span * 0.75, 3))
    return max(0.08, round(span * 0.62, 3))


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
        anchors = Paragraph.model_validate(para).anchor_indices()
        n = len(para["text"].split())
        for i, (sh, start) in enumerate(zip(para["shots"], anchors)):
            end = anchors[i + 1] if i + 1 < len(anchors) else n
            steps = (sh.get("map") or {}).get("steps", [])
            if sh["type"] != "map" or not steps or any(st.get("compare") for st in steps) or "view" not in steps[0]:
                continue
            if any(steps[0].get(k) for k in ("highlight", "routes", "arrows")):
                continue
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
    "title": "Why Venice Is Sinking Into Its Own Lagoon",
    "voice": "am_michael",
    "voice_speed": 1.15,
    "music": "procedural",
    "map_style": "satellite",
    "look": "none",
    "photo_upscale": True,
    "sources": ["episodes/venice-sinking/research.md and factcheck.md", "Contains modified Copernicus Sentinel data 2026", "Landsat imagery courtesy of the U.S. Geological Survey"],
    "thumbnail": {"text": "THE SEA IS WINNING"},
    "chapters": chapters,
    "youtube": {
        "title": "Why Venice Is Sinking Into Its Own Lagoon",
        "description": "Venice is lower than it used to be and the sea is higher. This video follows how that happened: the wooden piles under the city, the rivers the Venetian Republic moved by hand, the industrial wells that sank the city twelve centimeters in twenty years, the oil-tanker canal that helped empty the lagoon of mud, the floods of 1966 and 2019, and MOSE, the 78 steel gates that now rise from the seabed. And what comes after them.",
        "tags": ["Venice", "Venice sinking", "acqua alta", "MOSE", "Venetian lagoon", "Italy", "flood barrier", "1966 Venice flood", "sea level rise", "subsidence", "Porto Marghera", "geography", "satellite images"],
        "pinned_comment": "If you were in charge of Venice, would you keep closing the gates, or seal the lagoon for good and lose what made it Venice?",
    },
}
out = HERE / "script.json"
out.write_text(json.dumps(script, ensure_ascii=False, indent=1) + chr(10), encoding="utf-8")
words = sum(len(p["text"].split()) for c in chapters for p in c["paragraphs"])
shots = [s for c in chapters for p in c["paragraphs"] for s in p["shots"]]
kinds = {k: sum(1 for s in shots if s["type"] == k) for k in ("map", "photo", "stat", "document", "chart")}
print(f"{words} words, {len(chapters)} chapters, {len(shots)} shots {kinds}")
