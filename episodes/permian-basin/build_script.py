"""Builds script.json for permian-basin.  python build_script.py

Same production logic as episodes/florida-big-bend (hand-placed shots, a photo or map frame at most twice, 60 s apart).
The narration lives in drafts/narration.md (one "Pnn:" line per paragraph, "## Title (mood)" per chapter); every
sentence comes from research.md. Photos and satellite tests: visuals.md. Painted regions: geo/make_regions.py (EIA 2017
Permian Basin boundary, sub-basins and Capitan Reef trend).
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


CLEAR_DAY = "2025-10-03"  # Sentinel-2 single-day scenes 2025-10-03/04 clear over every test view (scratch pbsat.py)


def v(view, at=None, **kw):
    if view["span"] > 2.5 and not kw.get("highlight") and "date" not in kw and kw.get("layer") != "night":
        kw["date"] = CLEAR_DAY
    d = {"view": fresh(view), **kw}
    if at is not None:
        d["at"] = at
    return d


SAT_MIN_SPAN = 0.08
DRY = "2025-10-01/2025-11-30"  # scratch pbsat.py 2026-11-21: one clear day (10-03 / 10-04) covers each view, richer colour than May
SPRING = "2025-04-01/2025-05-31"  # second look at a place (05-11 .. 05-29 single days)


def sat(at, lon, lat, span, label=None, **kw):
    kw.setdefault("date", DRY)
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
USA = {"lon": -97.0, "lat": 37.5, "span": 30.0}
TX = {"lon": -100.0, "lat": 31.2, "span": 13.0}
PB = {"lon": -102.6, "lat": 31.75, "span": 6.4}  # the whole Permian Basin (EIA extent)
DEL = {"lon": -103.85, "lat": 31.75, "span": 3.0}  # Delaware Basin and the reef
MIDB = {"lon": -101.7, "lat": 32.0, "span": 3.4}  # Midland Basin
EXT = "file:basin_extent.geojson@accent"
DELW = "file:delaware.geojson@blue"
CBPW = "file:cbp.geojson@alt"
MIDW = "file:midland.geojson@blue"
REEF = "file:capitan_reef.geojson@red"
TXR = "Texas@alt"

# ------------------------------------------------------------------ sources (research.md)
EIA = "U.S. Energy Information Administration (Today in Energy, 2026)"
USGS = "U.S. Geological Survey, Guadalupe Mountains geology"
USGS18 = "USGS Fact Sheet 2018-3073"
NPS = "National Park Service"
NAS = "National Academies Press (WIPP geology)"
DOE = "U.S. Department of Energy, WIPP"
BRIT = "Encyclopaedia Britannica, Permian extinction"
CENSUS = "U.S. Census Bureau via City of Midland, 2024 estimates"
CENSUS20 = "U.S. Census Bureau, 2020 census"
UTIMCO = "UTIMCO, Permanent University Fund"
UL = "University Lands, FY2025 annual report"
UTS = "University of Texas System"
THC = "Texas Historical Commission marker"
DALLAS = "Federal Reserve Bank of Dallas"
FDIC = "FDIC, History of the Eighties"
IHS = "IHS Markit analysis (reported by BIC Magazine)"
BEG = "Bureau of Economic Geology, UT Austin"
BEG_TTU = "BEG; Texas Tech Water Consortium (estimates)"
RRC = "Railroad Commission of Texas"
USGS_Q = "USGS (TexNet: M5.3)"
FLARE = "Peer-reviewed study (PMC7176423), VIIRS data"
JOHNSON = "Johnson 1989, Environ. Geology and Water Sciences"
KIMLU = "Kim & Lu 2021, radar (InSAR) study"

# ------------------------------------------------------------------ photos (Commons, licence checked: visuals.md)
PH_PECOS_PANO = "File:Panorama across a desert basin toward distant mesas, Pecos County, Texas.jpg"
PH_PECOS_SHRUB = "File:Desert shrubs above a wide basin under cirrus, Pecos County, Texas.jpg"
PH_FLARE_NM1 = "File:Natural gas flare at petroleum well site (Whites City, New Mexico, USA) 1.jpg"
PH_FLARE_NM2 = "File:Natural gas flare at petroleum well site (Whites City, New Mexico, USA) 2.jpg"
PH_FLARE = "File:Natural Gas Flare.jpg"
PH_MIDLAND_SKY = "File:Midland, TX skyline (cropped).jpg"
PH_MIDLAND_TOWER = "File:Wall Tower West Midland, TX skyline (cropped).jpg"
PH_ODESSA = "File:Odessa, Texas.jpg"
PH_ISS_ODESSA = "File:ISS-65 Odessa, Texas.jpg"
PH_LOVING_ROAD = "File:Road in Loving County, Texas.jpg"
PH_LOVING_LINE = "File:Loving County, Texas line.jpg"
PH_MENTONE = "File:Honorable Mentone (4557178429).jpg"
PH_WINK = "File:Wink, Texas.jpg"
PH_WINK_LIMITS = "File:Wink City Limits (15217979052).jpg"
PH_ELCAP_GUMO = "File:El Cap GUMO.jpg"
PH_ELCAP_SNOW = "File:El Capitan (4389347934).jpg"
PH_GM1 = "File:Guadalupe Mountains National Park - 53196461646.jpg"
PH_GM2 = "File:Guadalupe Mountains National Park - 53196001807.jpg"
PH_GM_LOC = "File:View of the Guadalupe Mountains in Guadalupe Mountains National Park in Hudspeth County, Texas LCCN2014631688.tif"
PH_GM_LOC2 = "File:View of the Guadalupe Mountains in Guadalupe Mountains National Park in Hudspeth County, Texas LCCN2014631689.tif"
PH_GPEAK = "File:Guadalupe Peak.JPG"
PH_ESCARP = "File:Guadalupe Escarpment (between Guadalupe Mountains National Park & Carlsbad Caverns National Park).jpg"
PH_STYLO = "File:Stylolites in limestone (Lamar Limestone or Capitan Limestone, Upper Permian; McKittrick Canyon, Guadalupe Mountains, Texas, USA) 2 (24638404778).jpg"
PH_CARLS_PANO = "File:Carlsbad Caverns National Park and White's City, New Mexico, USA - 48344881691.jpg"
PH_BIGROOM1 = "File:Big Room, Carlsbad Cavern (51203204939).jpg"
PH_BIGROOM2 = "File:Big Room, Carlsbad Cavern (51234085016).jpg"
PH_DRAPERIES = "File:Draperies, Big Room, Carlsbad Cavern (51202478206).jpg"
PH_GIANT_DOME = "File:Giant Dome, Big Room, Carlsbad Cavern (51201755657).jpg"
PH_LECH = "File:Lechuguilla-Cave-Overview-20190715.jpg"
PH_SHAFT_1924 = "File:Shaft of light at natural entrance. (8a25cd96-de5c-4e5d-ac1b-be268f59b891).jpg"
PH_DOME_1924 = "File:Jim White and early visitors in Dome Room. (5340b2d9-6c4d-4a79-b17e-38cf65d3575f).jpg"
PH_GYPSUM_CAVE = "File:My Public Lands Roadtrip- Parks Ranch Cave in New Mexico (20332603939).jpg"
PH_FOSSIL1 = "File:Grand Canyon National Park- Fossils in Kaibab Limestone 0370 (7706171986).jpg"
PH_BRACH = "File:Grand Canyon National Park- Brachiopod Fossils in Kaibab Limestone 0378 (7706182918).jpg"
PH_HALITE = "File:Halite crystal.jpg"
PH_ROCKSALT = "File:Rock salt (halitite) (Haselgebirge Formation, Upper Permian to Lower Triassic; salt mine at or near Halle-in-Tyrol, Northern Calcareous Alps, western Austria) (15195697744).jpg"
PH_WIPP = "File:Waste Isolation Pilot Plant 2004.jpg"
PH_WIPP_MINE = "File:DOE Begins Mining Operations for Salt Disposal Investigations at WIPP.jpg"
PH_WIPP_MINE2 = "File:DOE Begins Mining Operations for Salt Disposal Investigations at WIPP 2.jpg"
PH_SCHEM = "File:Schematic cross-section of general types of oil and gas resources and the orientations of production wells used in hydraulic fracturing.jpg"
PH_SANTA_FRONT = "File:Santa Rita No. 1 Oil Well Front.jpg"
PH_SANTA_SIDE = "File:Santa Rita No. 1 Oil Well Side.jpg"
PH_SANTA_INFO = "File:Santa Rita No. 1 Oil Well Info.jpg"
PH_TEXON = "File:Oil tower, Texon Texas 12-4-2012.jpg"
PH_YATES_NASA = "File:YatesOilfieldNASA.jpg"
PH_ODESSA_CARD = "File:Greetings from Odessa, Texas, \"Hub City of Odessa West Texas Oil Field\" - Large Letter Postcard (9428792540).jpg"
PH_SUPERIOR_1949 = "File:Superior Oil Co. drill site, West Texas 1949.jpg"
PH_JACKKNIFE = "File:Navion at jackknife rig near Midland, Texas - Superior Oil Co. (8660568313).jpg"
PH_GULF_1956 = "File:Gulf Oil Corporation, Waddell Gasoline Plant, West Texas (9576013391).jpg"
PH_CANTINA_1972 = "File:ABANDONED CANTINA - NARA - 545814.jpg"
PH_PJ_SUNSET = "File:West Texas Pumpjack.JPG"
PH_PJ_ORANGE = "File:Pump Jack (8744524982).jpg"
PH_PJ_ROW = "File:Pumpjacks in Texas.JPG"
PH_RIG33 = "File:No accidents today on rig 33 (9406569933).jpg"
PH_NIGHT12 = "File:Changes in the Permian Basin Oil Field Over the Years (CIRA 2024-05-23 - 201208010902 snpp viirs dnb permianoil nolabels0).png"
PH_NIGHT24 = "File:Changes in the Permian Basin Oil Field Over the Years (CIRA 2024-05-23 - 202405230754 snpp viirs dnb permianoil nolabels0).png"

# ------------------------------------------------------------------ places
MIDLAND = place("Midland", -102.08, 32.00, "Midland", "city")
ODESSA = place("Odessa", -102.37, 31.85, "Odessa", "city")
CARLSBAD = place("Carlsbad", -104.23, 32.42, "Carlsbad, NM", "city")
PECOS = place("Pecos", -103.49, 31.42, "Pecos", "city")
ELPASO = place("El Paso", -106.44, 31.76, "El Paso", "city")
AUSTIN = place("Austin", -97.74, 30.27, "Austin", "city")
BIGLAKE = place("Big Lake", -101.46, 31.19, "Big Lake", "city")
SANTA = place("Santa Rita No. 1", -101.68, 31.21, "Santa Rita No. 1 (1923)", icon="warning")
IRAAN = place("Iraan", -101.90, 30.91, "Iraan (Yates field, 1926)", "city")
WINK = place("Wink", -103.16, 31.75, "Wink", "city")
MENTONE = place("Mentone", -103.60, 31.70, "Mentone", "city")
QUAKE = place("2022 quake", -104.00, 31.64, "M5.4, 16 Nov 2022", icon="warning")
GPEAK = place("Guadalupe Peak", -104.861, 31.891, "Guadalupe Peak", icon="mountain")
CAVERN = place("Carlsbad Cavern", -104.444, 32.175, "Carlsbad Cavern", icon="water")
WIPP_PT = place("WIPP", -103.79, 32.37, "WIPP (nuclear waste in salt)", icon="warning")

CB = "File:Carlsbad Caverns National Park and White's City, New Mexico, USA - {}.jpg"
PH_CB_CREEK = CB.format(48344861051)
PH_CB_TRAIL = CB.format(48344864041)
PH_CB_VIEW = CB.format(48344879646)
PH_CB_SIGN = CB.format(48344850747)
PH_CB_ROAD = CB.format(48344858762)
PH_CB_COLUMN = CB.format(48347954181)
PH_BIGROOM3 = "File:Big Room, Carlsbad Cavern (51202483276).jpg"
PH_BIGROOM4 = "File:Big Room, Carlsbad Cavern (51202438416).jpg"
PH_BR_VISITORS = "File:Visitors - Big Room, Carlsbad Cavern (51203926399).jpg"
PH_GM3 = "File:Guadalupe Mountains National Park - 53196461806.jpg"
PH_GM4 = "File:Guadalupe Mountains National Park - 53196661490.jpg"
PH_GM5 = "File:Guadalupe National Park (7671839588).jpg"
PH_ELCAP_BW = "File:El Capitan (9330499901).jpg"
PH_LOVING_TOWER = "File:Loving County watertower.jpg"
PH_LOVING_CH = "File:Loving County Courthouse.jpg"
PH_FAREWELL = "File:Fond farewell to the Guadalupe Mountains (4570857897).jpg"
PH_WINK_PINK = "File:Pink rhymes with Wink, which is the West Texas town in which this store window was photographed LCCN2014630679.tif"
PH_WINKLER_CH = "File:County courthouse for Winkler County, near the New Mexico line in far-west Texas LCCN2014630676.jpg"
PH_REAGAN_CH = "File:Reagan county tx courthouse 2014.jpg"
PH_PITCHFORK = "File:A scenic hill top view of the Pitchfork Ranch located outside of Fort Stockton, Texas (24745816479).jpg"
PH_PJ_RUNNELS = "File:Colorful \"pumpjack,\" a type of small oil pump that's a common sight in West Texas, along U.S. 83 near the town of Winters in Runnels County, Texas LCCN2014631353.tif"
PH_PJ_NIGHT = "File:Face. Horse head on pumpjack. - Flickr - Night Photo.jpg"
PH_SANTA_EVENT = "File:Santa Rita No. 1 Oil Well Event.jpg"
PH_HALITE_GSL = "File:Halite (Great Salt Lake Desert, Utah, USA) 1.jpg"
PH_HALITE_PINK = "File:Pink halite (Holocene; Searles Lake, near Trona, California, USA) 1.jpg"
PH_MIDLAND_1928 = "File:Directory Map, City of Midland - NARA - 109182530.jpg"
PH_BEECH = "File:Beech Bonanza at jackknife rig near Midland, Texas - Superior Oil Co. (8552972042).jpg"
NIGHT_PB = {"lon": -103.0, "lat": 31.9, "span": 3.2}

chapters = []
heads = iter(HEADS)


def chapter(*paras):
    title, mood = next(heads)
    chapters.append({"title": title, "mood": mood, "paragraphs": list(paras)})


chapter(
    P("P0",
      sat(0, -103.65, 31.82, 0.9, "West Texas from orbit"),
      photo("Brown scrub, dry riverbeds,", PH_PECOS_PANO, "Pecos County, West Texas"),
      sat("But zoom in, and", -103.65, 31.82, 0.25, "Loving County, Texas"),
      sat("thousands of them, laid", -103.70, 31.85, 0.10, "Each pale square is a drilling pad"),
      photo("Each square is a", PH_FLARE_NM1, "A well site in the Permian Basin, New Mexico"),
      m("And together, these squares", v(PB, highlight=[EXT], places=[MIDLAND, ODESSA, CARLSBAD])),
      stat("produced about six point", "6.6 MILLION", "Barrels of crude oil a day, Permian Basin, 2025", EIA),
      photo("According to the U.S.", PH_PJ_NIGHT, "A pumpjack at night"),
      stat("that is forty-eight percent", "48%", "Of all U.S. crude oil production, 2025", EIA)),
    P("P1",
      m(0, v(USA, highlight=[EXT], places=[MIDLAND]), step("biggest oil producer comes", view=near(-101.5, 32.5, 10.0))),
      m("about two hundred and", v(PB, highlight=[EXT], places=[MIDLAND, ODESSA])),
      photo("The biggest towns here,", PH_MIDLAND_SKY, "Midland, Texas"),
      stat("have about a hundred", "143,687", "People in Midland, 2024", CENSUS, note="Odessa: 119,748"),
      sat("There is no great", -102.37, 31.86, 0.20, "Odessa from orbit"),
      photo("So why here?", PH_LOVING_ROAD, "Loving County, Texas")),
    P("P2",
      sat(0, -105.0, 31.8, 0.4, "Salt flats west of the Guadalupe Mountains"),
      photo("you'll see a reef", PH_ELCAP_GUMO, "El Capitan, Guadalupe Mountains"),
      photo("caves dissolved by acid", PH_BIGROOM1, "Carlsbad Cavern"),
      photo("a layer of salt", PH_WIPP_MINE, "Salt, 2,150 ft down: the Waste Isolation Pilot Plant"),
      photo("and a well on", PH_SANTA_FRONT, "Santa Rita No. 1"),
      photo("And you'll see what", PH_FLARE_NM2, "Gas flare at a well site, New Mexico"),
      sat("from earthquakes to holes", -103.14, 31.79, 0.08, "Wink, Texas"),
      m("It starts about two", v(TX, highlight=[TXR, EXT], places=[MIDLAND, ELPASO, AUSTIN]), step("years ago, when this", view=PB))),
)

chapter(
    P("P3",
      stat(0, "PANGEA", "All the continents joined in one supercontinent", USGS),
      m("What is now West", v({"lon": -101.0, "lat": 31.5, "span": 9.0}, highlight=[TXR], places=[MIDLAND, ELPASO])),
      m("And here, the crust", v(PB, highlight=[EXT])),
      m("A wide hollow formed,", v(PB, highlight=[DELW, MIDW], places=[CARLSBAD, MIDLAND])),
      stat("The U.S. Geological Survey", "INLAND SEA", "Joined to the ocean around Pangea by one narrow channel", USGS),
      photo("connected to the vast", PH_PITCHFORK, "Pecos County hills, West Texas")),
    P("P4",
      m(0, v(PB, highlight=[EXT], places=[MIDLAND, CARLSBAD])),
      m("In the west was", v(DEL, highlight=[DELW], places=[CARLSBAD, PECOS]), text="Delaware Basin"),
      m("In the east, a", v(MIDB, highlight=[MIDW], places=[MIDLAND, ODESSA]), text="Midland Basin"),
      m("And between them, a", v(PB, highlight=[DELW, CBPW, MIDW]), step("the Central Basin Platform,", view=near(-102.6, 31.8, 3.2)),
        text="Central Basin Platform (between)"),
      m("The whole region took", v(PB, highlight=[EXT], places=[MIDLAND, CARLSBAD, PECOS]), step("from the rocks laid", view=near(-102.8, 31.9, 5.0)),
        text="The Permian Basin (EIA)")),
    P("P5",
      photo(0, PH_FOSSIL1, "Permian sea fossils (Kaibab Limestone, Arizona)"),
      photo("Sponges, algae and small", PH_BRACH, "Permian brachiopods, shelled sea animals"),
      m("When they died, many", v(DEL, highlight=[DELW]), step("parts of the basins.", view=near(-103.9, 31.6, 2.6))),
      stat("The USGS explains that", "NO OXYGEN", "Decay used up the oxygen in the deep basin water", USGS),
      photo("used up the oxygen", PH_CB_TRAIL, "Permian limestone, Carlsbad Caverns National Park"),
      sat("Without oxygen, nothing finished", -103.3, 31.3, 0.3, "Reeves County, in the Delaware Basin"),
      sat("The remains were simply", -103.9, 31.55, 0.6, "The Delaware Basin floor today")),
    P("P6",
      photo(0, PH_STYLO, "Limestone squeezed by the rock above (stylolites)"),
      stat("Heat and pressure turned", "OIL + GAS", "Made from buried life by heat and pressure", USGS),
      photo("That is the first", PH_PJ_RUNNELS, "A pumpjack in West Texas"),
      photo("The oil under West", PH_PJ_SUNSET, "West Texas"),
      sat("buried in a basin", -103.5, 31.7, 1.0, "The Delaware Basin")),
    P("P7",
      photo(0, PH_TEXON, "An old derrick at Texon, Reagan County"),
      sat("Left alone, it creeps", -104.2, 32.0, 0.3, "Reef country near the New Mexico line"),
      m("For a field to", v(PB, highlight=[DELW, MIDW]), step("fifty million years, something", view=near(-103.2, 31.9, 3.4))),
      m("And around the edge", v(DEL, highlight=[REEF, DELW], places=[CARLSBAD]))),
)

chapter(
    P("P8",
      m(0, v(DEL, highlight=[REEF], places=[CARLSBAD, GPEAK]), text="Capitan Reef trend (EIA)"),
      stat("The USGS dates it", "277-275 MILLION YEARS", "Age of the Capitan Reef", USGS),
      photo("million years ago. Geologists", PH_ESCARP, "The Guadalupe escarpment: the old reef front"),
      photo("It grew in a", PH_GM5, "Guadalupe Mountains"),
      stat("and according to the", "400 MILES", "Length of the Capitan Reef complex, mostly buried", NPS),
      photo("In places, it is", PH_ELCAP_SNOW, "El Capitan")),
    P("P9",
      photo(0, PH_GM1, "Guadalupe Mountains National Park"),
      sat("About eighty million years", -104.85, 31.90, 0.30, "The Guadalupe Mountains from orbit"),
      photo("Later, faults lifted one", PH_GM_LOC, "The Guadalupe Mountains"),
      photo("Today that block is", PH_GM3, "Guadalupe Mountains National Park"),
      photo("The highest point, Guadalupe", PH_GPEAK, "Guadalupe Peak"),
      stat("stands eight thousand seven", "8,751 FT", "Guadalupe Peak, the highest point in Texas", NPS),
      photo("It is the highest", PH_GM4, "Guadalupe Mountains")),
    P("P10",
      photo(0, PH_GM2, "El Capitan, the south end of the Guadalupe Mountains"),
      sat("It is part of", -104.86, 31.88, 0.10, "El Capitan from orbit"),
      photo("The highest ground in", PH_ELCAP_BW, "El Capitan"),
      photo("sponges and algae at", PH_CB_CREEK, "Reef limestone, Carlsbad Caverns National Park"),
      m("The exposed stretch of", v(near(-104.5, 32.15, 0.9), date=DRY, places=[CARLSBAD, GPEAK]),
        step("the national park northeast,", view=near(-104.35, 32.3, 0.5)))),
    P("P11",
      photo(0, PH_CARLS_PANO, "The reef above Carlsbad Caverns"),
      photo("Carlsbad Cavern runs for", PH_BIGROOM2, "Big Room, Carlsbad Cavern"),
      photo("Nearby Lechuguilla Cave, also", PH_LECH, "Lechuguilla Cave"),
      stat("has been mapped for", "138+ MILES", "Lechuguilla Cave, mapped so far", NPS),
      photo("Most caves are carved", PH_DRAPERIES, "Draperies, Carlsbad Cavern"),
      photo("According to the National", PH_GIANT_DOME, "Giant Dome, Carlsbad Cavern")),
    P("P12",
      photo(0, PH_CB_SIGN, "Carlsbad Caverns National Park"),
      stat("The USGS says this", "12 MILLION YEARS AGO", "Hydrogen sulfide was still rising from the oil", USGS),
      sat("When the gas met", -104.44, 32.17, 0.12, "Above Carlsbad Cavern"),
      photo("acid, and the acid", PH_CB_COLUMN, "Inside the reef: Carlsbad Cavern"),
      photo("The proof is a", PH_GYPSUM_CAVE, "Gypsum walls, Parks Ranch Cave, New Mexico"),
      photo("which forms when that", PH_BIGROOM3, "Big Room, Carlsbad Cavern"),
      photo("So one of America's", PH_BR_VISITORS, "Visitors in the Big Room")),
    P("P13",
      m(0, v(DEL, highlight=[REEF, DELW])),
      photo("But the reef could", PH_GM_LOC2, "The Guadalupe Mountains"),
      m("What finally locked the", v(PB, highlight=[EXT], places=[CARLSBAD, MIDLAND]), step("the end, when the", view=near(-103.6, 31.9, 3.6)))),
)

chapter(
    P("P14",
      m(0, v(PB, highlight=[DELW], places=[CARLSBAD]), step("sea was gradually cut", view=near(-104.0, 31.6, 2.8))),
      sat("And under the hot", -105.0, 31.75, 0.25, "Salt Basin flats, West Texas"),
      photo("As it shrank, it", PH_HALITE_GSL, "Halite: rock salt"),
      photo("began to fall out", PH_HALITE_PINK, "A salt crystal")),
    P("P15",
      photo(0, PH_ROCKSALT, "Rock salt from the Permian (Austria)"),
      m("Two formations hold most", v(DEL, highlight=[DELW], places=[WIPP_PT, CARLSBAD]), text="Delaware Basin"),
      stat("the Salado alone as", "200-400 M", "Thickness of the Salado salt", NAS),
      stat("That is up to", "1,300 FT", "Of salt, left by a sea that dried in place", NAS),
      photo("left behind by a", PH_WIPP_MINE2, "Permian salt at WIPP")),
    P("P16",
      stat(0, "SALT FLOWS", "Under pressure, salt slowly creeps and closes cracks", NAS),
      m("and it closes cracks", v(PB, highlight=[DELW, REEF]), step("A thick blanket of", view=near(-103.8, 31.9, 2.8))),
      photo("Together with the dense", PH_ESCARP, "The reef rock along the basin edge"),
      photo("the oil and gas", PH_CB_VIEW, "From the reef, looking over the basin")),
    P("P17",
      photo(0, PH_BRACH, "Permian sea fossils"),
      stat("About two hundred and", "252 MILLION YEARS AGO", "The end-Permian mass extinction", BRIT),
      stat("Britannica estimates that about", "~90%", "Of all species on Earth lost", BRIT),
      stat("including more than ninety-five", ">95%", "Of marine species lost", BRIT),
      sat("The sea that made", -103.9, 31.6, 1.2, "West Texas today")),
    P("P18",
      m(0, v(DEL, highlight=[DELW], places=[WIPP_PT, CARLSBAD])),
      sat("Department of Energy runs", -103.79, 32.37, 0.08, "WIPP from orbit"),
      photo("Pilot Plant, which takes", PH_WIPP, "Waste Isolation Pilot Plant, New Mexico"),
      stat("dug into the Salado", "2,150 FT", "Depth of WIPP's disposal rooms, in Permian salt", DOE),
      photo("The Department of Energy", PH_WIPP_MINE, "Mining the salt at WIPP"),
      photo("laid down about two", PH_HALITE_GSL, "Rock salt"),
      stat("and that its most", "SALT SEALS", "Fractures close and openings close over time", DOE),
      sat("The same property that", -103.79, 32.37, 0.2, "WIPP in the desert east of Carlsbad")),
    P("P19",
      m(0, v(PB, highlight=[DELW, CBPW, MIDW]), step("ready. A thick layer", view=near(-102.7, 31.7, 4.0))),
      sat("A reef along the", -104.86, 31.90, 0.20, "The reef: Guadalupe Mountains"),
      photo("Then the oil waited", PH_PECOS_SHRUB, "Pecos County, Texas"),
      photo("until someone came out", PH_SUPERIOR_1949, "Drill site, West Texas, 1949")),
)

chapter(
    P("P20",
      stat(0, "1,000,000 ACRES", "West Texas land granted to the university, 1876", UTIMCO),
      photo("future state university one", PH_REAGAN_CH, "Reagan County courthouse, Big Lake"),
      stat("In 1883, the legislature", "+1,000,000 ACRES", "1883: land considered too worthless to survey", UTIMCO),
      photo("had handed back because", PH_FAREWELL, "West Texas road"),
      photo("Historians have called the", PH_PECOS_PANO, "West Texas range land"),
      m("For decades, nobody disagreed.", v(PB, highlight=[EXT], places=[BIGLAKE, MIDLAND]))),
    P("P21",
      photo(0, PH_SANTA_INFO, "Santa Rita No. 1 marker"),
      sat("a well called Santa", -101.66, 31.21, 0.15, "West of Big Lake, Reagan County"),
      photo("It stood on university", PH_SANTA_SIDE, "Santa Rita No. 1"),
      stat("According to the University", "28 MAY 1923", "Santa Rita No. 1: the first major Permian discovery", UTS),
      photo("the first major oil", PH_SANTA_EVENT, "Santa Rita No. 1 plaque"),
      photo("Its rig now stands", PH_SANTA_FRONT, "Santa Rita No. 1 rig, UT Austin campus")),
    P("P22",
      stat(0, "2.1 MILLION ACRES", "Permanent University Fund lands, mostly West Texas", UTIMCO),
      m("Today, the Permanent University", v(PB, highlight=[EXT], places=[SANTA, BIGLAKE, MIDLAND])),
      stat("In fiscal year 2025,", "$1.72 BILLION", "Mineral revenue from PUF lands, fiscal 2025", UL),
      photo("in about one point", PH_PJ_RUNNELS, "Pumpjack, West Texas"),
      stat("And the fund itself", "$39.5 BILLION", "Permanent University Fund, 30 June 2025", UTIMCO),
      photo("A sea that died", PH_PJ_ROW, "Pumpjacks, West Texas"),
      photo("years ago now helps", PH_PITCHFORK, "West Texas")),
    P("P23",
      sat(0, -101.90, 30.90, 0.25, "The Yates field, Pecos County"),
      sat("came in Pecos County,", -101.85, 30.93, 0.10, "Yates field wells near Iraan", date=SPRING),
      stat("The state historical marker", "72,869", "Barrels a day: rated flow of the 1926 discovery well", THC),
      sat("thousand barrels a day,", -101.97, 30.88, 0.15, "The Yates field from orbit", date=SPRING),
      sat("The town that grew", -101.90, 30.91, 0.08, "Iraan, Texas"),
      stat("The Yates field has", "500+ MILLION", "Barrels produced by the Yates field", THC)),
    P("P24",
      sat(0, -102.37, 31.86, 0.12, "Odessa", date=SPRING),
      sat("Midland became the office", -102.08, 32.00, 0.25, "Midland"),
      stat("By 1929, according to", "36", "Oil companies with offices in Midland by 1929", DALLAS),
      photo("Odessa, closer to the", PH_SUPERIOR_1949, "Drill site, West Texas, 1949"),
      sat("And production kept rising,", -102.0, 31.75, 0.2, "Oil field south of Midland"),
      stat("According to the Federal", "1973", "Permian oil production begins to decline", DALLAS),
      photo("production began to decline", PH_MIDLAND_1928, "Midland street map, 1928")),
    P("P25",
      photo(0, PH_ODESSA, "Odessa, Texas"),
      stat("In the 1980s, oil", "~$10", "A barrel of oil after the 1980s crash", FDIC),
      photo("barrel. The FDIC, the", PH_WINKLER_CH, "Winkler County courthouse, Kermit"),
      stat("counts four hundred and", "425", "Texas commercial banks failed, 1980-1989", FDIC),
      stat("and 1989, including nine", "9 OF 10", "Largest Texas bank holding companies among them", FDIC),
      photo("The oil boom had", PH_WINK_PINK, "Shop window, Wink, Texas")),
    P("P26",
      photo(0, PH_PJ_ROW, "Pumpjacks in Texas"),
      photo("an old field. The", PH_TEXON, "Old derrick, Texon"),
      m("The rock that held", v(PB, highlight=[DELW, MIDW]), step("was still down there,", view=near(-103.0, 31.8, 3.0))),
      photo("Who would make it", PH_FLARE_NM1, "A modern well site, New Mexico")),
)

chapter(
    P("P27",
      m(0, v(DEL, highlight=[DELW]), step("source of all that", view=near(-103.7, 31.8, 2.6))),
      sat("Much of the oil", -103.55, 31.70, 0.3, "The Delaware Basin"),
      photo("pores far too small", PH_STYLO, "Tight rock: no room for oil to flow"),
      stat("One of the richest", "WOLFCAMP", "One of the richest oil-bearing shale layers", USGS18)),
    P("P28",
      sat(0, -103.72, 31.86, 0.12, "Well pads, Loving County"),
      sat("straight down, then turns", -103.50, 32.05, 0.10, "Pads in rows, Reeves County"),
      sat("The second is hydraulic", -103.42, 31.82, 0.10, "New pads, Reeves County"),
      sat("pumped down at high", -103.35, 31.95, 0.12, "Ponds and pads"),
      sat("with the sand holding", -103.60, 31.95, 0.15, "Pads and access roads")),
    P("P29",
      sat(0, -103.65, 31.82, 0.5, "The Delaware Basin oil field"),
      stat("In May 2009, according", "92", "Drilling rigs working in the Permian Basin, May 2009", DALLAS),
      chart("By June 2012, there", "Drilling rigs working in the Permian Basin", "rigs",
            [("May 2009", 92), ("June 2012", 525)], DALLAS, highlight=1),
      sat("Horizontal wells took over.", -103.45, 32.15, 0.25, "Southeastern New Mexico"),
      stat("By 2018, ninety percent", "90% → 95%", "Permian rigs drilling horizontally, 2018 → 2022", DALLAS)),
    P("P30",
      sat(0, -103.66, 31.83, 0.18, "From orbit: a grid of pads"),
      m("Every pad is a", v(near(-103.58, 31.98, 0.09), date=SPRING)),
      sat("horizontal wells run out", -103.80, 31.92, 0.20, "Pads in parallel rows"),
      photo("The grid you see", PH_ISS_ODESSA, "Odessa from the space station")),
    P("P31",
      stat(0, "2017", "Permian output passes its 1973 record", IHS),
      sat("oil in a year", -102.20, 31.95, 0.3, "The Midland Basin, between Midland and Odessa"),
      photo("And it kept climbing.", PH_MIDLAND_SKY, "Midland, Texas"),
      stat("By 2025, the EIA", "6.6 MILLION", "Barrels a day, Permian Basin, 2025", EIA),
      stat("That is close to", "13.6 MILLION", "U.S. crude oil a day, 2025: a national record", EIA),
      photo("set a national record", PH_PJ_NIGHT, "Pumpjack at night")),
    P("P32",
      m(0, v(DEL, highlight=[DELW], places=[CARLSBAD, PECOS]), step("the Wolfcamp and Bone", view=near(-103.7, 31.9, 2.6))),
      stat("It estimated forty-six point", "46.3 BILLION", "Barrels, undiscovered but recoverable: Delaware Basin shale", USGS18,
           note="Wolfcamp + Bone Spring, USGS 2018 estimate"),
      sat("been discovered yet but", -103.30, 32.25, 0.3, "Lea County, New Mexico"),
      stat("this the largest continuous", "LARGEST", "Continuous oil and gas resource the USGS had ever assessed", USGS18),
      photo("That is an estimate", PH_PJ_SUNSET, "Pumpjack, West Texas"),
      sat("not oil that is", -103.95, 32.30, 0.3, "Eddy County, New Mexico"),
      sat("Still, the dead sea", -103.40, 31.70, 0.9, "The Delaware Basin")),
    P("P33",
      photo(0, PH_LOVING_LINE, "Loving County line"),
      m("And the bill for", v(PB, layer="night", places=[MIDLAND, ODESSA, CARLSBAD]))),
)

chapter(
    P("P34",
      sat(0, -103.70, 31.84, 0.12, "Pads and ponds, Loving County", date=SPRING),
      sat("the oil comes salty", -103.25, 31.75, 0.12, "Pads near Wink and Pyote"),
      stat("In the Midland Basin,", "2.6 : 1", "Barrels of water per barrel of oil, Midland Basin", BEG),
      sat("puts it at about", -102.15, 31.70, 0.12, "Pads in the Midland Basin"),
      stat("every barrel of oil.", "5 : 1", "Barrels of water per barrel of oil, Delaware Basin", BEG),
      stat("Across the basin, estimates", "21-25 MILLION", "Barrels of produced water a day, 2025 estimates", BEG_TTU),
      photo("million barrels of water", PH_LOVING_TOWER, "Loving County water tower")),
    P("P35",
      photo(0, PH_ISS_ODESSA, "Odessa from the space station"),
      sat("Most of it is", -103.45, 31.90, 0.12, "Pads and pipelines, Reeves County"),
      m("And that is where", v(DEL, highlight=[DELW], places=[MENTONE, PECOS])),
      stat("A member of the", "DEEP INJECTION", "Likely cause of recent Permian quakes (RRC commissioner, 2022)", RRC),
      photo("regulator, wrote in 2022", PH_LOVING_CH, "Loving County courthouse, Mentone"),
      sat("the deeper formations likely", -103.70, 31.65, 0.3, "Near Mentone")),
    P("P36",
      m(0, v(near(-103.75, 31.66, 1.0), date=DRY, places=[QUAKE, MENTONE, PECOS])),
      photo("the only community in", PH_MENTONE, "Mentone, Loving County"),
      stat("At the 2020 census,", "64", "Residents of Loving County, 2020: fewest of any U.S. county", CENSUS20),
      photo("residents, the fewest of", PH_LOVING_ROAD, "Loving County"),
      stat("The USGS measured it", "M5.4", "Earthquake west of Pecos, 16 November 2022", USGS_Q),
      m("It was felt as", v(TX, highlight=[TXR], places=[QUAKE, ELPASO, MIDLAND]), step("and called it the", view=near(-103.0, 31.5, 6.0))),
      stat("The Railroad Commission now", "M3.5+", "Quakes that trigger action by the Railroad Commission", RRC),
      sat("strike, and it has", -103.55, 31.80, 0.4, "Well pads, Delaware Basin")),
    P("P37",
      photo(0, PH_FLARE_NM2, "Gas flare, Permian Basin, New Mexico"),
      photo("natural gas, and where", PH_FLARE, "A gas flare"),
      sat("it is burned at", -103.62, 31.90, 0.10, "Pads in the Delaware Basin", date=SPRING),
      m("Satellite instruments run by", v(NIGHT_PB, layer="night", places=[MIDLAND, ODESSA, CARLSBAD, PECOS]),
        step("A peer-reviewed study estimated", view=near(-103.6, 31.9, 2.6), layer="night")),
      stat("and averaged about five", "5.9 BILLION M³", "Gas flared a year in the Permian, study period", FLARE),
      sat("period it studied. That's", -103.9, 32.1, 0.15, "Well pads, Eddy County, New Mexico")),
    P("P38",
      photo(0, PH_WINK_LIMITS, "Wink, Texas"),
      sat("On the third of", -103.14, 31.79, 0.08, "The Wink sinkholes from orbit"),
      stat("the ground collapsed into", "110 FT", "Depth of Wink Sink, 3 June 1980", BEG),
      m("Wink Sink sits right", v(DEL, highlight=[REEF], places=[WINK]), step("Reef. Geologists traced it", view=near(-103.4, 32.0, 2.6))),
      photo("Water had reached the", PH_ROCKSALT, "Rock salt"),
      stat("A 1989 study concluded", "1928", "An old oil well stood inside the sinkhole's rim", JOHNSON),
      photo("activity: an old well,", PH_WINKLER_CH, "Winkler County courthouse, Kermit"),
      sat("the hole, and may", -103.14, 31.79, 0.12, "Around Wink Sink", date=SPRING)),
    P("P39",
      stat(0, "2002", "Wink Sink 2 opens nearby", BEG),
      sat("Using radar satellites, researchers", -103.13, 31.79, 0.2, "Around the Wink sinkholes"),
      photo("years later, and that", PH_WINK, "Wink, Texas"),
      stat("was sinking by more", "60+ CM/YR", "Ground 1 km east of Wink Sink 2, 2015-16", KIMLU),
      photo("The salt that sealed", PH_WINK_PINK, "Wink, Texas"),
      photo("fifty million years is", PH_HALITE_PINK, "Salt")),
)

chapter(
    P("P40",
      m(0, v(PB, highlight=[EXT], places=[MIDLAND, CARLSBAD])),
      sat("The empty desert is", -103.65, 31.82, 0.7, "The floor of a sea"),
      photo("The highest mountain in", PH_GM1, "Guadalupe Mountains: the reef"),
      photo("The caves under Carlsbad", PH_BIGROOM4, "Carlsbad Cavern"),
      photo("The salt is its", PH_WIPP_MINE2, "Permian salt, WIPP"),
      sat("And the grid of", -103.70, 31.85, 0.14, "Drilling pads, Loving County", date=SPRING),
      sat("back out, about six", -103.40, 32.00, 0.5, "The Permian Basin", date=SPRING)),
    P("P41",
      photo(0, PH_FAREWELL, "West Texas"),
      photo("The water, the quakes", PH_WINK_LIMITS, "Wink, Texas"),
      m("So here is the", v(PB, layer="night", places=[MIDLAND, ODESSA, CARLSBAD]), step("should Texas keep pumping", view=near(-103.2, 31.8, 3.0), layer="night")),
      ask=("So here is the", "How long should Texas keep pumping its dead sea?")),
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

TITLE = "Why Half of America's Oil Comes From One Empty Corner of Texas"
script = {
    "title": TITLE,
    "voice": "am_michael",
    "voice_speed": 1.15,
    "music": "procedural",
    "map_style": "satellite",
    "look": "none",
    "photo_upscale": True,
    "sources": ["episodes/permian-basin/research.md and factcheck.md", "Contains modified Copernicus Sentinel data 2026",
                "Permian Basin boundaries: U.S. Energy Information Administration (2017)", "Night lights: NOAA/NASA VIIRS"],
    "thumbnail": {"text": "48% OF U.S. OIL FROM HERE"},
    "chapters": chapters,
    "youtube": {
        "title": TITLE,
        "description": "A dry corner of West Texas and New Mexico, home to fewer people than many single cities, pumps about 6.6 million barrels of crude oil a day: 48 percent of all U.S. production in 2025. The reason is a sea that died about 250 million years ago. We follow it from orbit: the inland sea at the edge of Pangea, the Capitan Reef that became Guadalupe Peak, the highest point in Texas, the caves of Carlsbad dissolved by acid rising from the oil, the salt that sealed it all and now holds nuclear waste, the Santa Rita well on university land, the 1980s bust, the shale boom, and the bill: produced water, earthquakes, flares and the Wink sinkholes.",
        "tags": ["Permian Basin", "West Texas", "Texas oil", "Midland", "Odessa", "Guadalupe Mountains", "Capitan Reef", "Carlsbad Caverns",
                 "WIPP", "Santa Rita No. 1", "fracking", "shale oil", "Wink sinkhole", "geography", "satellite images"],
        "pinned_comment": "How long should Texas keep pumping its dead sea?",
    },
}
out = HERE / "script.json"
out.write_text(json.dumps(script, ensure_ascii=False, indent=1) + chr(10), encoding="utf-8")
words = sum(len(p["text"].split()) for c in chapters for p in c["paragraphs"])
shots = [s for c in chapters for p in c["paragraphs"] for s in p["shots"]]
kinds = {k: sum(1 for s in shots if s["type"] == k) for k in ("map", "photo", "stat", "document", "chart")}
print(f"{words} words, {len(chapters)} chapters, {len(shots)} shots {kinds}")
