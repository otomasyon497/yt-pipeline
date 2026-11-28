"""Builds script.json for northern-idaho.  python build_script.py

Same production logic as episodes/wyoming-empty (hand-placed shots, a photo or map frame at most twice, 60 s apart,
every reason opens on a painted map). The narration lives in drafts/narration.md; every sentence comes from
research.md. Photos and satellite tests: visuals.md. Regions: geo/make_regions.py; measurements: geo/measure_*.py.
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
    zoom = [1.08, 1.16, 1.24, 1.12, 1.2, 1.04, 1.28, 1.32][(k - 1) % 8] * (1.03 ** ((k - 1) // 8))  # out only: prefit snaps zoom-ins back
    return {"lon": round(view["lon"] + dx * view["span"], 3), "lat": round(view["lat"] + dy * view["span"], 3), "span": round(view["span"] * zoom, 3)}


def v(view, at=None, **kw):
    d = {"view": fresh(view), **kw}
    if at is not None:
        d["at"] = at
    return d


SAT_MIN_SPAN = 0.08

SU = "2025-07-01/2025-09-15"    # northern summer 2025: scratch nisat.py 2026-11-28


def sat(at, lon, lat, span, label=None, date=SU, **kw):
    return m(at, v(near(lon, lat, max(span, SAT_MIN_SPAN)), date=date, **kw), text=label)


def photo(at, name, text=None):
    d = {"type": "photo", "at": at, "photo": name if name.startswith("File:") else "File:" + name}
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
USA = {"lon": -104.0, "lat": 42.0, "span": 40.0}      # the lower 48, west half
NW = {"lon": -116.5, "lat": 46.3, "span": 13.0}       # Pacific Northwest: WA, ID, MT, OR
IDV = {"lon": -114.6, "lat": 45.4, "span": 8.6}       # Idaho
NORTHV = {"lon": -116.0, "lat": 46.9, "span": 4.8}    # North Idaho
PANH = {"lon": -116.6, "lat": 47.9, "span": 3.0}      # the panhandle
SILV = {"lon": -116.1, "lat": 47.5, "span": 2.6}      # Coeur d'Alene - Silver Valley
CLEAR = {"lon": -115.9, "lat": 46.4, "span": 3.2}     # Clearwater / Lewiston / Pierce / Orofino
CENTV = {"lon": -115.6, "lat": 45.6, "span": 4.4}     # the wall: Salmon River country
WESTUS = {"lon": -113.0, "lat": 45.5, "span": 19.0}   # West: WA to Montana, Oregon

N_RED = "file:north.geojson@red"
S_ALT = "file:south.geojson@alt"
ID_ALT = "file:idaho.geojson@alt"
IDC_RED = "file:idaho_county.geojson@red"
KOOT_RED = "file:kootenai.geojson@red"
SHO_RED = "file:shoshone.geojson@red"
CLW_RED = "file:clearwater_co.geojson@red"
NZP_RED = "file:nezperce_co.geojson@red"
LAT_RED = "file:latah.geojson@red"
WA_BLUE = "file:washington.geojson@blue"
MT_ALT = "file:montana.geojson@alt"
FIRE_RED = "file:fire1910.geojson@red"
TERR_RED = "file:territory1863.geojson@red"
VTNH_BLUE = "file:vt_nh.geojson@blue"
FC_RED = "file:frank_church.geojson@red"
SEL_RED = "file:selway.geojson@red"
GOS_RED = "file:gospel.geojson@red"
WILD_RED = "file:wilderness.geojson@red"
FOR_RED = "file:forests.geojson@red"
SAL_BLUE = "file:salmon.geojson@blue"

# ------------------------------------------------------------------ sources (research.md)
CENSUS = "US Census Bureau, 2020 census"
OWN_POP = "Own count: 2020 census block groups, ten northern counties (geo/measure_population.py)"
OSRM = "Own route test: OSRM / OpenStreetMap (geo/drive_osrm.txt)"
N24 = "2024-07-01/2024-09-15"   # clear Silver Valley / delta (scratch nisat2, 2026-11-28)

# ------------------------------------------------------------------ photos (visuals.md; PD / CC0 / CC BY)
PH_WAL1 = "Commercial building, Wallace, Idaho LCCN2017707015.tif"
PH_WAL_I90 = "I-90 Wallace (10490280433).jpg"
PH_WAL2 = "Wallace (10490090386).jpg"
PH_WAL3 = "Wallace (10490103134).jpg"
PH_WAL4 = "Wallace, ID. (10490267103).jpg"
PH_WAL5 = "Holohan & McKinley Bldg, Wallace, Idaho.jpg"
PH_F1 = "Aftermath of the 1910 Fires (4929720525).jpg"
PH_F2 = "Aftermath of the 1910 Fires (4929725611).jpg"
PH_F4 = "Aftermath of the 1910 Fires (4929731503).jpg"
PH_F5 = "Aftermath of the 1910 Fires (4929732171).jpg"
PH_F6 = "Aftermath of the 1910 Fires (4929735451).jpg"
PH_F15 = "Aftermath of the 1910 Fires (4929751287).jpg"
PH_F22 = "Aftermath of the 1910 Fires (4929769257).jpg"
PH_F38 = "Aftermath of the 1910 Fires (4929810323).jpg"
PH_F43 = "Aftermath of the 1910 Fires (4929824539).jpg"
PH_F47 = "Aftermath of the 1910 Fires (4930314546).jpg"
PH_KEL_DRONE = "Drone view from Kellogg, Idaho.jpg"
PH_KEL_GOND = "Gondola crossing Kellogg, ID. (10490100815).jpg"
PH_BH_AIR = "Idaho - Kellogg through Ketchum - NARA - 23939441 (cropped).jpg"
PH_KEL = "Kellogg, ID. (10490112586).jpg"
PH_BH1 = "BUNKER HILL LEAD SMELTER. VIEW IS FROM CENTRAL IMPOUNDMENT AREA LOOKING SOUTH. PLANT DRY IS IN CENTER FOREGROUND, SLAG FUMING PLANT IS IN RIGHT FOREGROUND, AND BAG HOUSE IS IN HAER ID,40-KELL,2-1.tif"
PH_BH2 = "BUNKER HILL LEAD SMELTER. VIEW IS FROM CIA TO THE SOUTH. IN FOREGROUND, PLANT DRY, SLAG FUMING PLANT, BLAST FURNACE, SMELTER OFFICE, LEAD AND SILVER REFINERIES ARE VISIBLE, L. TO R HAER ID,40-KELL,2-2.tif"
PH_BH4 = "BUNKER HILL LEAD SMELTER. VIEW IS FROM RIDGE ABOVE GOVERNMENT GULCH LOOKING TO THE EAST. IN THE RIGHT MID GROUND, CARPENTER SHOP BUILDINGS AND FRAMING SHEDS ARE VISIBLE. THE HAER ID,40-KELL,2-4.tif"
PH_LEW_2000 = "20000916 04 Lewiston, ID (7298922822).jpg"
PH_LEW_OLD = "Bird's-eye view of farmland and mountain, with orchard in foreground, Lewiston valley, Idaho) - Fair & Thompson, Lewiston, Idaho LCCN89711646.jpg"
PH_HELLS_NARA = "BOATERS ON A TRIP THROUGH HELLS CANYON PAUSE FOR A REST ON A QUIET STRETCH OF THE SNAKE RIVER - NARA - 549461.jpg"
PH_CONFL = "Confluence of Clearwater and Snake rivers - Lewiston, Idaho (21116852016).jpg"
PH_LEW_AIR = "Idaho - Lewiston - NARA - 23939445 (cropped).jpg"
PH_SEAL = "US-NBN-ID-territory seal detail (Series 1882BB reverse) proof.jpg"
PH_JOSEPH = "Chief Joseph, Nez Perce - NARA - 523606.jpg"
PH_CLEVE = "Grover Cleveland, bust portrait, seated, facing right LCCN2014648289.jpg"
PH_LOCHSA_1910 = "Fording Lochsa River, 1910 - Lewiston, Idaho (32873356827).jpg"
PH_LOCHSA1 = "Lochsa River (6050298041).jpg"
PH_LOCHSA2 = "Lochsa River (6050308577).jpg"
PH_LOCHSA3 = "Lochsa River in Clearwater NF.jpg"
PH_HELLS1 = "Along the River (11442531196).jpg"
PH_HELLS2 = "Along the River (11442600913).jpg"
PH_DUGBAR = "Dug-bar-hells-canyon-07242011-rogermpeterson (6097008242).jpg"
PH_SALMON_RIG = "20000914 11 Salmon River Valley near Riggins, ID (7291310278).jpg"
PH_SALMON_LOW = "Along-the-npnht-lower-salmon-river-at-coopers-ferry-near-cottonwood-id-07212011-rogermpeterson-006 (6081074906).jpg"
PH_BOXCANYON = "Box Canyon on the Salmon River, circa 1925 - Slate Creek, Idaho (50346450768).jpg"
PH_WHITEBIRD = "White Bird Hill Grade, 1924 - White Bird, Idaho (50901386962).jpg"
PH_BAYVIEW = "Bayview - Flickr - MonikaMurren.jpg"
PH_PO_BROTEN = "Broten, Idaho, US.jpg"
PH_PO = "Lake Pend Oreille.jpg"
PH_NTS1 = "U.S. Naval Training Staion (Lake Pend Oreille) Farragut, Idaho. - NARA - 195430.jpg"
PH_FARR_SIGN = "Farragut State Park Welcome Sign, Idaho (40479710922).jpg"
PH_NTS_CLASS = "Farragut NTS Idaho Class 218 1943.jpg"
PH_NTS2 = "U.S. Naval Training Station, (Lake Pend Oreille) Farragut, Idaho. - NARA - 195431.jpg"
PH_SEAJET1 = "US Navy 051130-N-7676W-033 The Advanced Electric Ship Demonstrator (AESD), Sea Jet, undergoes sea trials on Lake Pend Oreille at the Naval Surface Warfare Center Carderock Division, Acoustic Research Detachment in Bayview, Idah.jpg"
PH_SEAJET2 = "US Navy 051130-N-7676W-064 The Advanced Electric Ship Demonstrator (AESD), Sea Jet, undergoes sea trials on Lake Pend Oreille at the Naval Surface Warfare Center Carderock Division, Acoustic Research Detachment in Bayview, Idah.jpg"
PH_LOGPOND = "Log Pond and Railroad Log Dump, Potlatch Lumber Company, 1907 - Potlatch, Idaho (18572366416).jpg"
PH_POT1906 = "Potlatch, Idaho (1906).jpg"
PH_POTMILL = "Sawmill Looking Northeast, Potlatch Lumber Company, 1907 - Potlatch, Idaho (18411041298).jpg"
PH_LOGTRAIN = "The Largest Log Train on Washington, Idaho & Montana Railway, Potlatch Lumber Company, 1907 - Potlatch, Idaho (18600423811).jpg"
PH_AHSAHKA = "Clearwater River in Ahsahka, Idaho.jpg"
PH_BIGMILL = "Big Mill, circa 1910 - Potlatch, Idaho (17489419750).jpg"
PH_ELKRIVER = "Bird's Eye View, circa 1912 - Elk River, Idaho (4263609151).jpg"
PH_UI1908 = "University of Idaho, 1908 - Moscow, Idaho (15454115069).jpg"
PH_BLUEFOX = "Blue Fox Theater, Grangeville, Idaho LCCN2017707953.tif"
PH_GRANGE1910 = "Grangeville, Idaho (circa 1910).jpg"
PH_SANDPOINT = "Sandpoint Idaho from Schweitzer.jpg"
PH_CDA_ROOF = "City of Coeur d'Alene, from a rooftop, 2006.jpg"
PH_CDA_AIR = "Coeur d'Alene aerial, May 2023.png"
PH_CDA_AIR2 = "Coeur d'Alene aerial, May 2023 (cropped).png"
PH_CDA_SIGN = "Couer d' Alene (10490631594).jpg"
PH_FC_CANYON = "Another Canyon View in Frank Church Wilderness.jpg"
PH_FC_CABIN = "Cabin Creek Frank Church.jpg"
PH_FC_SIGN = "Entering the Frank Church.jpg"
PH_MF1 = "Middle Fork Salmon River Frank Church Wilderness.jpg"
PH_MF2 = "Middle Fork Salmon River Idaho.jpg"
PH_PULASKI_TOOL = "Fire tools- pulaski.jpg"
PH_HAYWOOD3 = "Bill Haywood - Charles Moyer - George Pettibone LCCN2004677537.jpg"
PH_STEUN = "Frank Steunenberg statue.jpg"
PH_ORCHARD = "Orchard-Harry-1911.jpg"
PH_PULASKI_TRAIL = "Pulaski Tunnel Trail bridge installation.jpg"
PH_BULLPEN = "Bull Pen Wardner ID 1899.png"
PH_BULLPEN2 = "Prisoners in Bullpen Wardner ID 1899.png"
PH_BHRUINS = "Bunker Hill Mill Ruins Wardner ID.png"
PH_BARGE = "Tidewater Barge - Columbia River.jpg"
PH_HAYDEN = "Honeysuckle Bay, Hayden Lake, ID - panoramio.jpg"
PH_ISS1 = "ISS007-E-12239 - View of Idaho.jpg"
PH_FC_TRAIL = "Along trail in Frank Church Wilderness.jpg"
PH_FC_SKY = "Beautiful Skies over Frank Church Wilderness.jpg"
PH_MF3 = "Middle Fork Salmon River.jpg"
PH_LINCOLN = "Lincoln School, Cameron Avenue, Kellogg, Idaho LCCN2017706076.tif"
PH_MASONIC = "Masonic Temple, Main Street, Kellogg, Idaho LCCN2017706247.tif"
PH_MINERSHAT = "Miner's Hat Realty, Kellogg, Idaho LCCN2017709172.tif"
PH_ORE = "Freibergite (GeoDIL number - 1257).jpg"
PH_LEW_MAIN = "Lewis-Clark Center for Arts and History, Main Street, Lewiston, Idaho LCCN2017706091.tif"
PH_F3 = "Aftermath of the 1910 Fires (4929726023).jpg"
PH_F7 = "Aftermath of the 1910 Fires (4929737957).jpg"
PH_F11 = "Aftermath of the 1910 Fires (4929743673).jpg"
PH_F16 = "Aftermath of the 1910 Fires (4929753575).jpg"
PH_F18 = "Aftermath of the 1910 Fires (4929757963).jpg"
PH_F29 = "Aftermath of the 1910 Fires (4929786873).jpg"
PH_HAYWOOD = "HAYWOOD, WILLIAM. 'BIG BILL,' LABOR AGITATOR LCCN2016866412.jpg"
PH_LOCHSA4 = "Lochsa River (6050852672).jpg"
PH_BH5 = "PELLETIZING PLANT SECTION OF ORE PREPARATION PLANT. VIEW IS FROM WITHIN SMELTER COMPLEX LOOKING TO THE SOUTH. - Bunker Hill Lead Smelter, Bradley Rail Siding, Kellogg, Shoshone HAER ID,40-KELL,2-5.tif"
PH_F31 = "Aftermath of the 1910 Fires (4929791753).jpg"
PH_F33 = "Aftermath of the 1910 Fires (4929795871).jpg"
PH_DARROW = "Bill Haywood & defense counsels, Clarence Darrow, Wilson & Richardson LCCN2016652448.jpg"

# ------------------------------------------------------------------ places, routes and arrows
CDA = place("Coeur d'Alene", -116.78, 47.68, "Coeur d'Alene", "city")
BOISE = place("Boise", -116.20, 43.62, "Boise", "capital")
SPOKANE = place("Spokane", -117.43, 47.66, "Spokane", "city")
SEATTLE = place("Seattle", -122.33, 47.61, "Seattle", "city")
OLYMPIA = place("Olympia", -122.90, 47.04, "Olympia", "capital")
SANDPOINT = place("Sandpoint", -116.55, 48.28, "Sandpoint", "city")
LEWISTON = place("Lewiston", -117.02, 46.42, "Lewiston", "city")
MOSCOW = place("Moscow", -117.00, 46.73, "Moscow", "city")
GRANGE = place("Grangeville", -116.12, 45.93, "Grangeville", "city")
WALLACE = place("Wallace", -115.93, 47.47, "Wallace", "city")
KELLOGG = place("Kellogg", -116.12, 47.54, "Kellogg", "city")
MULLAN = place("Mullan", -115.80, 47.47, "Mullan", "site")
WARDNER = place("Wardner", -116.13, 47.52, "Wardner", "site", icon="conflict")
PIERCE = place("Pierce", -115.80, 46.49, "Pierce", "site")
OROFINO = place("Orofino", -116.25, 46.48, "Orofino", "site")
STMARIES = place("St. Maries", -116.56, 47.31, "St. Maries", "site")
POTLATCH = place("Potlatch", -116.90, 46.92, "Potlatch", "site", icon="factory")
WHITEBIRD = place("White Bird", -116.30, 45.76, "White Bird Hill", "site")
WB_BATTLE = place("White Bird Canyon", -116.27, 45.80, "White Bird Canyon, 1877", "site", icon="conflict")
LOLO = place("Lolo Pass", -114.58, 46.63, "Lolo Pass", "site")
MISSOULA = place("Missoula", -114.00, 46.87, "Missoula", "city")
BAYVIEW = place("Bayview", -116.56, 47.98, "Bayview", "site")
FARRAGUT = place("Farragut", -116.58, 47.95, "Farragut naval base", "site")
CALDWELL = place("Caldwell", -116.69, 43.66, "Caldwell", "site", icon="conflict")
LAPWAI = place("Fort Lapwai", -116.80, 46.40, "Fort Lapwai", "site")
BOISEBASIN = place("Boise Basin", -115.83, 43.83, "Boise Basin gold", "site")
BEARPAW = place("Bear Paw", -109.20, 48.37, "Bear Paw, Oct 1877", "site", icon="conflict")
HAYDEN = place("Hayden Lake", -116.75, 47.78, "Hayden Lake", "site")
POSTFALLS = place("Post Falls", -116.95, 47.72, "Post Falls", "site")
SUNSHINE = place("Sunshine Mine", -116.07, 47.50, "Sunshine Mine", "site", icon="conflict")
HELLS = place("Hells Canyon", -116.70, 45.28, "Hells Canyon", "site")
RIGGINS = place("Riggins", -116.32, 45.42, "Riggins", "site")
PORTLAND = place("Portland", -122.68, 45.52, "Portland", "city")
L_PAC = place("Pacific", -126.0, 46.0, "PACIFIC OCEAN", "label")
L_PT = place("pt", -116.6, 47.2, "PACIFIC TIME", "label")
L_MT = place("mt", -115.2, 44.4, "MOUNTAIN TIME", "label")
L_CW = place("cw", -115.6, 46.6, "Clearwater Mountains", "label")
L_SR = place("sr", -115.2, 45.1, "Salmon River Mountains", "label")
L_BR = place("br", -114.7, 46.1, "Bitterroot Range", "label")
L_45 = place("45", -116.5, 49.05, "45 MILES", "label")

US95 = [{"from": [-116.78, 47.68], "via": [[-116.90, 47.05], [-117.00, 46.73], [-116.98, 46.40], [-116.30, 45.76], [-116.32, 45.42], [-116.29, 44.97], [-116.33, 44.30]],
         "to": [-116.20, 43.62], "mode": "line", "label": "US 95", "color": "red", "seconds": 3}]
VIAWA = [{"from": [-116.55, 48.28], "via": [[-117.43, 47.66], [-119.10, 46.23], [-118.79, 45.67], [-116.96, 44.03]],
          "to": [-116.20, 43.62], "mode": "line", "label": "Via Washington and Oregon: 496 mi", "color": "blue", "seconds": 3}]
INID = [{"from": [-116.55, 48.28], "via": [[-116.78, 47.68], [-117.00, 46.73], [-116.98, 46.40], [-116.30, 45.76], [-116.32, 45.42]],
         "to": [-116.20, 43.62], "mode": "line", "label": "Through Idaho: 423 mi", "color": "red", "seconds": 3}]
US12 = [{"from": [-117.02, 46.42], "via": [[-116.25, 46.48], [-115.98, 46.15], [-115.60, 46.14], [-115.10, 46.45]],
         "to": [-114.58, 46.63], "mode": "line", "label": "US 12, finished 1962", "color": "accent", "seconds": 3}]
FLIGHT = [{"from": [-116.27, 45.80], "via": [[-114.58, 46.63], [-113.64, 45.65], [-110.50, 44.60], [-109.30, 46.50]],
           "to": [-109.20, 48.37], "mode": "line", "label": "1,170 miles, 1877", "color": "red", "seconds": 3.5}]
TOBOISE = [{"from": [-117.02, 46.42], "to": [-116.20, 43.62], "color": "red", "label": "The capital moves, 1865", "bend": 0.15}]
GOLDSOUTH = [{"from": [-117.02, 46.42], "to": [-115.83, 43.83], "color": "accent", "label": "Miners move south", "bend": -0.15}]
TOWA = [{"from": [-116.5, 47.6], "to": [-118.6, 47.4], "color": "blue", "label": "1887: to Washington?", "bend": 0.1}]
EVAC = [{"from": [-115.93, 47.47], "to": [-117.43, 47.66], "color": "blue", "label": "To Spokane", "bend": 0.1},
        {"from": [-115.93, 47.47], "to": [-114.00, 46.87], "color": "blue", "label": "To Missoula", "bend": -0.1}]
WIND = [{"from": [-118.2, 46.3], "to": [-115.6, 47.3], "color": "red", "label": "Wind, 20 August", "bend": 0.05}]
I90 = [{"from": [-117.43, 47.66], "via": [[-116.95, 47.72], [-116.78, 47.68], [-116.42, 47.58], [-116.12, 47.54], [-115.93, 47.47]],
        "to": [-115.70, 47.46], "mode": "line", "label": "I-90, on the Mullan Road", "color": "accent", "seconds": 3}]
BARGE = [{"from": [-117.02, 46.42], "via": [[-118.30, 46.55], [-119.10, 46.23], [-120.50, 45.70], [-121.90, 45.65], [-122.75, 45.85]],
          "to": [-123.90, 46.22], "mode": "line", "label": "465 river miles", "color": "blue", "seconds": 3}]
TAILINGS = [{"from": [-116.05, 47.52], "via": [[-116.35, 47.55], [-116.62, 47.47]], "to": [-116.78, 47.45], "mode": "line",
             "label": "Mine waste down the river", "color": "red", "seconds": 2.5}]

chapters = []
heads = iter(HEADS)


def chapter(*paras):
    title, mood = next(heads)
    chapters.append({"title": title, "mood": mood, "paragraphs": list(paras)})


# ================================================================== Hook
chapter(
    P("P0",
      m(0, v(NW, highlight=[N_RED, S_ALT], places=[SPOKANE, BOISE])),
      m("a block of mountains", v(NORTHV, highlight=[N_RED, VTNH_BLUE]))),
    P("P1",
      stat(0, "1 IN 5", "Idahoans who live in the ten northern counties", OWN_POP),
      photo("and most of them", PH_CDA_AIR, "Coeur d'Alene, where most of the north lives"),
      m("Idaho County, the biggest", v(IDV, highlight=[IDC_RED, ID_ALT], places=[GRANGE])),
      stat("Only sixteen thousand people", "2 PER SQ MI", "Idaho County: 16,541 people on 8,477 sq mi", CENSUS)),
    P("P2",
      photo(0, PH_FC_CANYON, "The Frank Church wilderness")),
    P("P3",
      m(0, v(PANH, highlight=[N_RED], places=[L_45, SANDPOINT])),
      sat("until at the Canadian", -116.45, 48.90, 0.6, "Idaho's short border with Canada"),
      m("And above the Salmon", v(NW, highlight=[N_RED, S_ALT, SAL_BLUE], places=[L_PT, L_MT])),
      sat("the north keeps Pacific", -116.31, 45.42, 0.15, "The Salmon River at Riggins: the time line"),
      m("the south keeps Mountain", v(WESTUS, places=[SEATTLE, BOISE], highlight=[N_RED]))),
    P("P4",
      photo(0, PH_LEW_AIR, "Lewiston, Idaho's first capital"),
      photo("a fire that burned", PH_F1, "After the fires of 1910"),
      sat("and a valley that", -116.13, 47.54, 0.12, "Kellogg, in the Silver Valley", date=N24),
      photo("and then poisoned its", PH_BH1, "The Bunker Hill lead smelter")),
    P("P5",
      m(0, v(CENTV, places=[L_CW, L_SR, L_BR])),
      photo("a wall of mountains", PH_FC_CABIN, "Central Idaho")),
)

# ================================================================== 1. The Wall in the Middle
chapter(
    P("P6",
      m(0, v(NORTHV, highlight=[N_RED], places=[CDA, GRANGE]))),
    P("P7",
      m(0, v(CENTV, places=[L_CW, L_SR, L_BR, GRANGE])),
      sat("the Clearwater, the Salmon", -116.30, 45.42, 0.3, "The Salmon River canyon"),
      photo("It is some of", PH_MF1, "Middle Fork of the Salmon")),
    P("P8",
      photo(0, PH_FC_SIGN, "Entering the Frank Church wilderness"),
      m("Along the Salmon River", v(CENTV, highlight=[FC_RED, SAL_BLUE])),
      stat("almost two and a", "2.37 MILLION ACRES", "Frank Church-River of No Return Wilderness, no roads", "US Forest Service"),
      sat("It is the largest", -115.00, 45.20, 0.6, "Inside the Frank Church wilderness"),
      m("Next to it lie", v(CENTV, highlight=[FC_RED, SEL_RED, GOS_RED])),
      photo("and around them millions", PH_MF2, "Middle Fork of the Salmon")),
    P("P8b",
      photo(0, PH_SALMON_LOW, "The lower Salmon River"),
      photo("freight boats could ride", PH_MF3, "Rapids on the Middle Fork of the Salmon"),
      sat("so at the end", -116.30, 45.78, 0.15, "The Salmon's canyon near White Bird")),
    P("P8c",
      sat(0, -116.70, 45.28, 0.25, "Hells Canyon of the Snake River"),
      photo("the deepest river gorge", PH_DUGBAR, "Hells Canyon of the Snake River"),
      stat("almost eight thousand feet", "7,993 FT", "Hells Canyon, rim to river", "US Forest Service")),
    P("P9",
      m(0, v(IDV, places=[CDA, BOISE], routes=US95)),
      sat("and for about forty", -116.32, 45.55, 0.2, "US 95 in the Salmon River canyon"),
      photo("over a single grade", PH_WHITEBIRD, "The White Bird grade, 1924"),
      sat("a road of switchbacks", -116.30, 45.78, 0.08, "White Bird Hill"),
      stat("The faster road over", "1975", "New US 95 grade over White Bird Hill opens", "Wikipedia; ITD")),
    P("P10",
      m(0, v(CLEAR, places=[LEWISTON, LOLO, MISSOULA], routes=US12)),
      photo("along the Lochsa River", PH_LOCHSA1, "The Lochsa River"),
      photo("close to the route", PH_LOCHSA_1910, "Fording the Lochsa, 1910"),
      stat("in 1805, was finished", "1962", "US 12 over Lolo Pass is finished", "Idaho State Historical Society")),
    P("P11",
      photo(0, PH_SANDPOINT, "Sandpoint, in the panhandle"),
      m("The road through Idaho", v(WESTUS, places=[SANDPOINT, BOISE], routes=INID)),
      m("The road that leaves", v(WESTUS, places=[SANDPOINT, BOISE], routes=VIAWA)),
      stat("and it takes about", "423 MI vs 496 MI", "Sandpoint to Boise, about 9 hours either way", OSRM)),
    P("P12",
      m(0, v(PANH, highlight=[KOOT_RED], places=[SPOKANE, CDA])),
      sat("Spokane, just across the", -117.10, 47.68, 0.6, "Spokane to Coeur d'Alene along I-90"),
      photo("It shops there, flies", PH_CDA_ROOF, "Coeur d'Alene")),
    P("P13",
      photo(0, PH_LOCHSA3, "Forest along the Lochsa"),
      m("which brings us to", v(IDV, highlight=[FOR_RED]))),
)

# ================================================================== 2. The Land Is Not for Sale
chapter(
    P("P14",
      m(0, v(NORTHV, highlight=[FOR_RED, WILD_RED]))),
    P("P15",
      stat(0, "62 %", "Of Idaho is federal land (CRS)", "Congressional Research Service via Ballotpedia"),
      m("Only Nevada and Utah", v(USA, highlight=[ID_ALT])),
      sat("In the north the", -115.80, 46.50, 0.3, "Forest near Pierce"),
      m("Its two national forests", v(NORTHV, highlight=[FOR_RED], places=[CDA, LEWISTON])),
      stat("cover about seven million", "7 MILLION ACRES", "Idaho Panhandle + Nez Perce-Clearwater national forests", "US Forest Service")),
    P("P16",
      photo(0, PH_LOCHSA2, "National forest along the Lochsa"),
      photo("And in the summer", PH_F3, "The forest after 1910")),
    P("P17",
      m(0, v(NW, highlight=[FIRE_RED], places=[WALLACE, MISSOULA])),
      photo("By August hundreds of", PH_F4, "Burned slopes, 1910"),
      m("Then, on the twentieth", v(NORTHV, highlight=[FIRE_RED], arrows=WIND)),
      stat("a hurricane-force wind came", "20 AUGUST 1910", "The wind that joined the fires", "Wikipedia; PBS")),
    P("P18",
      photo(0, PH_F5, "The 1910 burn"),
      stat("They burned about three", "3 MILLION ACRES", "Burned in two days, Idaho and Montana", "Wikipedia; NWCG"),
      stat("About eighty-five people died", "~85 DEAD", "Most of them firefighters", "Wikipedia; HistoryLink"),
      photo("A third of the", PH_F6, "After the 1910 fires")),
    P("P18b",
      m(0, v(SILV, places=[WALLACE, SPOKANE, MISSOULA], arrows=EVAC)),
      photo("Trains carried them west", PH_F16, "The rail line through the burn, 1910"),
      photo("and soldiers pulled men", PH_F15, "Burned forest above the rail line, 1910")),
    P("P19",
      photo(0, PH_F22, "The 1910 burn"),
      stat("with a crew of", "45 MEN", "Ed Pulaski's crew, 20 August 1910", "Wikipedia; PBS"),
      photo("He led them into", PH_F18, "The burned forest near Wallace, 1910"),
      photo("and hung wet blankets", PH_F38, "After the 1910 fires"),
      stat("All but five or", "~40 OF 45", "Pulaski's crew who came out alive", "Wikipedia; PBS")),
    P("P20",
      photo(0, PH_F43, "The burned forest, 1910"),
      photo("From then on its", PH_F31, "Burned slopes, 1910"),
      stat("and by 1935 the", "TEN A.M.", "From 1935: every fire out by 10 the next morning", "US Forest Service history"),
      photo("The tool Pulaski designed", PH_PULASKI_TOOL, "Pulaski tools, still in use"),
      stat("is still carried by", "AXE + HOE", "The Pulaski tool, designed after the fire", "US Forest Service")),
    P("P21",
      photo(0, PH_F47, "Forest after the 1910 fires"),
      photo("But to understand why", PH_F33, "The burned hills, 1910"),
      m("we have to go", v(NW, highlight=[TERR_RED]))),
)

# ================================================================== 3. A Territory Run from Far Away
chapter(
    P("P22",
      m(0, v(USA, highlight=[TERR_RED], places=[LEWISTON]))),
    P("P23",
      m(0, v(CLEAR, highlight=[CLW_RED, NZP_RED], places=[PIERCE, LEWISTON])),
      photo("Within a year thousands", PH_AHSAHKA, "The Clearwater River"),
      sat("and a tent town", -117.02, 46.42, 0.12, "Lewiston, where the Clearwater meets the Snake")),
    P("P24",
      m(0, v(CLEAR, highlight=[IDC_RED], places=[LAPWAI, LEWISTON, WB_BATTLE])),
      photo("In 1863 the United", PH_SALMON_LOW, "Nez Perce country on the lower Salmon"),
      stat("cut their reservation by", "-90 %", "Nez Perce reservation under the 1863 treaty", "National Park Service"),
      photo("and the anger it", PH_HELLS1, "Nez Perce country along the Snake")),
    P("P24b",
      sat(0, -116.30, 45.78, 0.15, "White Bird Canyon"),
      stat("Nez Perce warriors routed", "17 JUNE 1877", "Battle of White Bird Canyon", "US Army"),
      photo("It was the first", PH_LOCHSA4, "The Lochsa, on the Nez Perce route east"),
      m("The bands that refused", v(WESTUS, places=[WB_BATTLE, BEARPAW], routes=FLIGHT)),
      stat("about eleven hundred and", "1,170 MILES", "126 days through four states", "National Park Service"),
      photo("They were caught in", PH_LOCHSA_1910, "The Lochsa country they crossed"),
      photo("and Chief Joseph surrendered", PH_JOSEPH, "Chief Joseph")),
    P("P25",
      m(0, v(WESTUS, highlight=[TERR_RED], places=[LEWISTON])),
      photo("and Lewiston became its", PH_CONFL, "Lewiston, at the confluence"),
      m("But the miners had", v(IDV, places=[LEWISTON, BOISEBASIN], arrows=GOLDSOUTH)),
      stat("south to the Boise", "BOISE BASIN", "Richer gold draws the miners south", "Idaho State Historical Society"),
      stat("By 1864 most of", "1864", "Most of the territory's voters now live in the south", "Idaho State Historical Society")),
    P("P26",
      stat(0, "DEC 1864", "Legislature votes to move the capital to Boise", "Idaho State Historical Society"),
      m("So in 1865 the", v(IDV, places=[LEWISTON, BOISE, LAPWAI], arrows=TOBOISE)),
      stat("took the territorial seal", "SEAL + ARCHIVES", "Taken from Lewiston to Boise, 1865", "Idaho State Historical Society"),
      stat("The territory's supreme court", "1866", "Court settles the capital in Boise", "Wikipedia")),
    P("P27",
      m(0, v(WESTUS, highlight=[TERR_RED])),
      m("In 1864 Congress cut", v(WESTUS, highlight=[ID_ALT, MT_ALT])),
      photo("Montana's border was drawn", PH_FC_SKY, "Mountain country of central Idaho"),
      m("and in the north", v(NORTHV, highlight=[N_RED, MT_ALT], places=[L_BR]))),
    P("P28",
      m(0, v(NORTHV, places=[CDA, MOSCOW], highlight=[N_RED])),
      m("In 1887 Congress actually", v(NW, highlight=[N_RED, WA_BLUE], arrows=TOWA)),
      photo("Idaho's governor sent a", PH_CLEVE, "President Grover Cleveland"),
      stat("and Cleveland let the", "1887", "The bill to give the panhandle to Washington dies", "Wikipedia; Spokesman-Review")),
    P("P28b",
      m(0, v(CLEAR, highlight=[LAT_RED], places=[MOSCOW, LEWISTON])),
      photo("In January 1889 its", PH_UI1908, "University of Idaho, 1908"),
      stat("and the university was", "1889", "University of Idaho founded in Moscow", "University of Idaho"),
      sat("It helped stop the", -117.00, 46.73, 0.12, "Moscow")),
    P("P29",
      m(0, v(NW, highlight=[ID_ALT], places=[BOISE, OLYMPIA])),
      stat("in 1890, Idaho became", "1890", "Idaho becomes a state", "Wikipedia"),
      photo("Should the north have", PH_SANDPOINT, "Sandpoint and Lake Pend Oreille"),
      photo("People in North Idaho", PH_PO_BROTEN, "Lake Pend Oreille"),
      photo("What they did have", PH_MINERSHAT, "Kellogg, a mining town")),
)

# ================================================================== 4. Silver, Dynamite and Lead
chapter(
    P("P30",
      m(0, v(SILV, highlight=[SHO_RED], places=[CDA, KELLOGG, WALLACE])),
      sat("also did the most", -116.00, 47.52, 0.4, "The Silver Valley", date=N24)),
    P("P31",
      photo(0, PH_KEL_DRONE, "The Silver Valley from above Kellogg"),
      sat("along the South Fork", -116.05, 47.50, 0.2, "The South Fork of the Coeur d'Alene", date=N24),
      m("The narrow canyon there", v(SILV, highlight=[SHO_RED], places=[WALLACE, KELLOGG, MULLAN, WARDNER])),
      photo("with Wallace, Kellogg and", PH_WAL1, "Wallace")),
    P("P31b",
      sat(0, -115.92, 47.475, 0.06, "Wallace and the I-90 viaduct", date=N24),
      photo("Until 1991 it had", PH_WAL5, "Wallace's main street"),
      stat("When the freeway was", "1991", "The last traffic light on I-90 is removed", "Idaho Transportation Department"),
      sat("held a funeral for", -115.93, 47.47, 0.1, "Wallace in its canyon", date=N24)),
    P("P32",
      stat(0, "1 BILLION+ OZ", "Silver from the Coeur d'Alene district since 1884", "Idaho State University; Mining.com"),
      photo("It is one of", PH_ORE, "Freibergite, a silver ore")),
    P("P33",
      photo(0, PH_BH_AIR, "Mines and mills of the Silver Valley"),
      stat("In 1892 and again", "1892 + 1899", "Mine wars in the Coeur d'Alene district", "Wikipedia; ISHS"),
      photo("On the twenty-ninth of", PH_BH2, "The Bunker Hill works at Kellogg"),
      stat("loaded it with about", "3,000 LB", "Of dynamite, 29 April 1899", "Wikipedia; ISHS"),
      sat("and blew up the", -116.13, 47.52, 0.06, "Wardner today", date=N24)),
    P("P34",
      photo(0, PH_STEUN, "Frank Steunenberg's statue in Boise"),
      stat("Federal troops came, and", "MARTIAL LAW", "Shoshone County, May 1899", "Wikipedia; ISHS"),
      m("in open-air pens called", v(SILV, highlight=[SHO_RED], places=[WARDNER, KELLOGG]))),
    P("P35",
      m(0, v(IDV, highlight=[ID_ALT], places=[CALDWELL, WARDNER])),
      stat("on the thirtieth of", "30 DEC 1905", "Ex-governor Steunenberg killed by a bomb", "Wikipedia; Idaho PTV"),
      sat("opened the gate of", -116.69, 43.66, 0.1, "Caldwell"),
      stat("The man who planted", "HARRY ORCHARD", "Said union leaders had paid him", "Wikipedia"),
      photo("The union's leader Big", PH_HAYWOOD, "Big Bill Haywood"),
      stat("in one of the", "ACQUITTED, 1907", "Haywood's murder trial in Boise", "Wikipedia")),
    P("P36",
      sat(0, -116.07, 47.50, 0.1, "Big Creek, site of the Sunshine Mine", date=N24),
      stat("One hundred and seventy-three", "173", "Men underground, 2 May 1972", "MSHA"),
      m("Smoke and carbon monoxide", v(SILV, highlight=[SHO_RED], places=[SUNSHINE, KELLOGG, WALLACE])),
      stat("and ninety-one of them", "91 MINERS", "Died in the Sunshine Mine fire", "MSHA"),
      stat("It led to the", "1977", "Federal Mine Safety and Health Act", "MSHA")),
    P("P37",
      photo(0, PH_BH4, "The Bunker Hill smelter"),
      stat("In September 1973 a", "SEPT 1973", "Baghouse fire; the smelter keeps running", "EPA"),
      photo("The company kept the", PH_BH5, "Inside the smelter complex")),
    P("P38",
      sat(0, -116.15, 47.54, 0.06, "Kellogg and the smelter site", date=N24),
      stat("their blood lead levels", "HIGHEST EVER", "Children's blood lead in Kellogg, 1974", "EPA")),
    P("P39",
      photo(0, PH_LINCOLN, "A school in Kellogg"),
      stat("Two years later the", "SUPERFUND 1983", "The Bunker Hill site is listed", "EPA"),
      stat("Crews have since replaced", "7,000+", "Homes and businesses given clean soil or barriers", "EPA"),
      photo("laid clean barriers over", PH_MASONIC, "Kellogg today")),
    P("P39b",
      m(0, v(SILV, highlight=[SHO_RED, KOOT_RED], places=[KELLOGG, CDA], routes=TAILINGS)),
      sat("Until 1968 most of", -116.80, 47.45, 0.15, "Where the Coeur d'Alene River enters the lake", date=N24),
      stat("About seventy-five million metric", "75 MILLION TONS", "Metal-rich sediment on the bed of Lake Coeur d'Alene", "USGS 1993"),
      sat("now lie on the", -116.80, 47.56, 0.3, "Lake Coeur d'Alene", date=N24)),
    P("P40",
      stat(0, "-39 %", "Kellogg: 3,811 people in 1970, 2,314 in 2020", "US Census"),
      photo("And the Silver Valley", PH_MINERSHAT, "Kellogg")),
    P("P40b",
      photo(0, PH_KEL_DRONE, "Kellogg and the slopes of Silver Mountain"),
      stat("with a gondola that", "3.1 MILES", "Silver Mountain gondola, opened 1990", "Silver Mountain Resort"),
      sat("the longest single-stage gondola", -116.13, 47.54, 0.12, "Kellogg", date=N24)),
)

# ================================================================== 5. When the Mills Closed
chapter(
    P("P41",
      m(0, v(CLEAR, highlight=[CLW_RED, LAT_RED], places=[POTLATCH, OROFINO, PIERCE, STMARIES])),
      photo("paid its wages for", PH_POTMILL, "The Potlatch sawmill, 1907")),
    P("P42",
      photo(0, PH_LOGTRAIN, "A log train of the Potlatch Lumber Company, 1907"),
      photo("In 1906 the Potlatch", PH_POT1906, "Potlatch, 1906"),
      sat("on the edge of", -116.90, 46.92, 0.08, "Potlatch today"),
      photo("and next to it", PH_BIGMILL, "The big mill at Potlatch, about 1910")),
    P("P43",
      sat(0, -116.25, 46.48, 0.1, "Orofino"),
      photo("lived on the logs", PH_LOGPOND, "The Potlatch log pond, 1907"),
      sat("Then, from the 1980s", -115.80, 46.50, 0.3, "Logged forest near Pierce"),
      photo("machines replaced workers, and", PH_ELKRIVER, "Elk River, a mill town, about 1912")),
    P("P44",
      stat(0, "1983", "The Potlatch mill closes", "Idaho Capital Sun"),
      stat("The plywood plant near", "215 JOBS", "Plywood plant near Pierce closes, 2000", "Spokesman-Review"),
      photo("In 2016 two sawmills", PH_AHSAHKA, "The Clearwater near Orofino")),
    P("P45",
      sat(0, -116.25, 46.48, 0.2, "Orofino and the Clearwater"),
      photo("Should the national forests", PH_LOCHSA3, "National forest on the Lochsa"),
      photo("Or are they worth", PH_FC_CANYON, "Wild country in central Idaho"),
      photo("and the people who", PH_FC_TRAIL, "A trail in the Frank Church wilderness"),
      ask=("Should the national forests", "Open the national forests to more logging, or keep them standing?")),
    P("P46",
      photo(0, PH_F29, "After the 1910 fires"),
      m("And yet in one", v(NORTHV, highlight=[KOOT_RED], places=[CDA])),
      sat("people are arriving faster", -116.95, 47.72, 0.2, "New streets in Post Falls")),
)

# ================================================================== 6. Where People Do Live
chapter(
    P("P47",
      m(0, v(NORTHV, highlight=[N_RED, KOOT_RED], places=[CDA, LEWISTON])),
      photo("It is full in", PH_CDA_AIR2, "Coeur d'Alene")),
    P("P48",
      m(0, v(NORTHV, highlight=[KOOT_RED], places=[CDA, MOSCOW, LEWISTON])),
      stat("holds almost half of", "47 % ON 6 %", "Of the north's people, on this share of its land", OWN_POP),
      stat("Two in three northern", "2 IN 3", "Northern Idahoans within ~15 mi of three towns", OWN_POP),
      sat("Coeur d'Alene, Lewiston and", -116.78, 47.68, 0.15, "Coeur d'Alene")),
    P("P48b",
      sat(0, -116.99, 46.43, 0.06, "The Port of Lewiston"),
      m("Barges come up the", v(WESTUS, places=[LEWISTON, PORTLAND, L_PAC], routes=BARGE)),
      stat("about four hundred and", "465 RIVER MILES", "Lewiston, the most inland West Coast seaport", "Port of Lewiston"),
      sat("and carry wheat, peas", -117.02, 46.42, 0.12, "Lewiston and Clarkston"),
      photo("It is the most", PH_CONFL, "The Snake and the Clearwater at Lewiston")),
    P("P48c",
      sat(0, -116.73, 47.78, 0.15, "Hayden Lake"),
      photo("From the 1970s a", PH_HAYDEN, "Hayden Lake"),
      stat("In 2000 a local", "$6.3 MILLION", "Jury verdict against the Aryan Nations, 2000", "SPLC; Spokesman-Review"),
      photo("a mother and son", PH_PO_BROTEN, "North Idaho's lake country"),
      m("The group went bankrupt,", v(PANH, highlight=[KOOT_RED], places=[HAYDEN, CDA]))),
    P("P49",
      sat(0, -116.95, 47.72, 0.12, "Post Falls, between Spokane and Coeur d'Alene"),
      stat("it gained about seventeen", "+9.9 %", "Kootenai County, 2020-2024", "US Census Bureau QuickFacts"),
      photo("Most of the newcomers", PH_CDA_ROOF, "Coeur d'Alene")),
    P("P50",
      photo(0, PH_CDA_AIR, "Coeur d'Alene"),
      m("It sits on Interstate", v(SILV, highlight=[KOOT_RED, SHO_RED], places=[SPOKANE, CDA, WALLACE], routes=I90)),
      sat("The road follows the", -116.55, 47.60, 0.15, "Fourth of July Pass, on the old Mullan Road", date=N24),
      stat("the first wagon road", "1862", "The Mullan Road is finished", "Kootenai County; Wikipedia")),
    P("P51",
      sat(0, -116.40, 48.10, 0.5, "Lake Pend Oreille"),
      stat("It is about eleven", "1,150 FT", "Depth of Lake Pend Oreille", "US Navy"),
      photo("carved by the ice", PH_PO, "Lake Pend Oreille")),
    P("P52",
      m(0, v(PANH, highlight=[KOOT_RED], places=[FARRAGUT, CDA, SANDPOINT])),
      photo("hundreds of miles from", PH_NTS1, "Farragut Naval Training Station"),
      photo("In about two and", PH_BAYVIEW, "Lake Pend Oreille at Bayview"),
      stat("almost three hundred thousand", "293,381", "Recruits trained at Farragut, 1942-45", "Idaho Military Museum"),
      photo("For a while it", PH_NTS2, "Farragut, Lake Pend Oreille")),
    P("P53",
      photo(0, PH_FARR_SIGN, "Farragut State Park"),
      sat("But the Navy never", -116.56, 47.98, 0.08, "Bayview, the Navy's lake station"),
      photo("Its deep, quiet water", PH_SEAJET1, "Navy test craft Sea Jet on Lake Pend Oreille, 2005")),
    P("P54",
      m(0, v(IDV, highlight=[IDC_RED], places=[CDA, GRANGE])),
      photo("and it is a", PH_FC_CABIN, "Idaho County back country"),
      stat("More than eight thousand", "8,477 SQ MI", "Idaho County: more land than New Jersey", CENSUS),
      sat("Grangeville, its largest town", -116.12, 45.93, 0.1, "Grangeville")),
)

# ================================================================== Ending
chapter(
    P("P55",
      m(0, v(NW, highlight=[N_RED, S_ALT], places=[CDA, BOISE]))),
    P("P56",
      photo(0, PH_MF2, "Central Idaho"),
      photo("with one road over", PH_WHITEBIRD, "White Bird Hill"),
      photo("Because most of its", PH_LOCHSA2, "National forest"),
      photo("and in 1910 that", PH_F1, "After 1910")),
    P("P57",
      photo(0, PH_LEW_AIR, "Lewiston"),
      photo("and the bill that", PH_CLEVE, "Grover Cleveland"),
      photo("Because the Silver Valley", PH_BH1, "Bunker Hill"),
      photo("And because the mills", PH_POT1906, "Potlatch")),
    P("P58",
      m(0, v(NORTHV, highlight=[N_RED, KOOT_RED], places=[CDA, L_PT])),
      sat("and nearly empty everywhere", -115.00, 45.20, 0.6, "Central Idaho")),
    P("P59",
      m(0, v(NW, highlight=[N_RED], places=[BOISE, OLYMPIA])),
      m("or from Olympia in", v(WESTUS, highlight=[N_RED, WA_BLUE], places=[OLYMPIA, BOISE])),
      ask=("If you lived in", "Govern North Idaho from Boise, or from Olympia in Washington?")),
)

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


BEAT_WORDS = 14
for ch in chapters:
    for para in ch["paragraphs"]:
        anchors = Paragraph.model_validate(para).anchor_indices()
        n = len(para["text"].split())
        for i, (sh, start) in enumerate(zip(para["shots"], anchors)):
            end = anchors[i + 1] if i + 1 < len(anchors) else n
            steps = (sh.get("map") or {}).get("steps", [])
            if sh["type"] != "map" or not steps or any(st.get("compare") for st in steps) or "view" not in steps[0]:
                continue
            if any(st.get(k) for st in steps for k in ("highlight", "routes", "arrows")):
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


def prefit_views():
    """Write the camera the pipeline would choose into the script (see scottish-highlands/build_script.py)."""
    import math
    import geo
    from maps import _arrow_hull, _inside_safe, _bounds_of, _span_for, fit, resolve_area, union_box, unit_pt, view_box

    def items_of(st):
        out = [("pt", (*unit_pt(pl["lon"], pl["lat"]), "site")) for pl in st.get("places", [])]
        for a in st.get("arrows", []):
            out.append(("line", _arrow_hull(unit_pt(*a["from"]), unit_pt(*a["to"]), a.get("bend", 0.2))))
        for r in st.get("routes", []):
            out.append(("line", [unit_pt(*q) for q in [r["from"], *r.get("via", []), r["to"]]]))
        for h in st.get("highlight", []):
            area = resolve_area(h.split("@")[0], HERE)
            if area:
                out.append(("geom", area[2]))
        return out

    def to_view(t):
        lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * t["y"]))))
        span = t["w"] * 360
        lon = t["x"] * 360 - 180
        return {"lon": round(lon, 3), "lat": round(lat, 3), "span": round(span, 3)}

    n = 0
    for ch in chapters:
        for para in ch["paragraphs"]:
            for sh in para["shots"]:
                if sh["type"] != "map":
                    continue
                cur = None
                for st in sh["map"]["steps"]:
                    if st.get("compare"):
                        cur = None
                        continue
                    if st.get("view"):
                        cur = {"x": float(geo.mx(st["view"]["lon"])), "y": float(geo.my(st["view"]["lat"])), "w": st["view"]["span"] / 360.0}
                    items = items_of(st)
                    if cur is None or not items or _inside_safe(_bounds_of(items), cur, True, slack=0.0):
                        continue
                    span0 = cur["w"] * 360
                    cur = fit(union_box([_bounds_of(items), view_box(cur, 0.4)]), True, min(_span_for(items), span0))
                    st["view"] = to_view(cur)
                    n += 1
    print(f"prefit: {n} views widened to fit their content")


prefit_views()


TITLE = "Why Almost Nobody Lives in Northern Idaho"
script = {
    "title": TITLE,
    "voice": "am_michael",
    "voice_speed": 1.15,
    "music": "procedural",
    "map_style": "satellite",
    "look": "none",
    "photo_upscale": True,
    "sources": ["episodes/northern-idaho/research.md and factcheck.md", "Contains modified Copernicus Sentinel data 2024-2025",
                "People in North Idaho: own count from the 2020 census, block groups (geo/measure_population.py)",
                "Counties: US Census Bureau; states, rivers: Natural Earth; wildernesses and national forests: US Forest Service (geo/make_regions.py)",
                "Drive Sandpoint-Boise: OSRM, (c) OpenStreetMap contributors (ODbL) (geo/drive_osrm.txt)",
                "Idaho Territory 1863 and the 1910 fire area drawn as approximate areas; routes drawn through main points (approximate)"],
    "thumbnail": {"text": "1 IN 5"},
    "chapters": chapters,
    "youtube": {
        "title": TITLE,
        "title_candidates": [TITLE, "Why North Idaho Is So Empty", "Why Idaho's Panhandle Is Almost Empty"],
        "description": "Northern Idaho is a quarter of the state, bigger than Vermont and New Hampshire together, yet only about one Idahoan in five lives there, most of them around Coeur d'Alene. We follow why: the wall of mountains and the largest wilderness in the lower 48, one road over White Bird Hill, national forest that covers most of the land, the Big Burn of 1910, a territorial capital taken from Lewiston to Boise in 1865 and the 1887 bill that nearly gave the panhandle to Washington, the Silver Valley's billion ounces of silver, its mine wars, the Sunshine Mine fire and the Bunker Hill lead poisoning, the timber mills that closed, and the corner around Coeur d'Alene that is now growing fast.",
        "tags": ["North Idaho", "Idaho", "Idaho Panhandle", "Coeur d'Alene", "Silver Valley", "Wallace Idaho", "Kellogg Idaho",
                 "Lewiston", "Big Burn 1910", "Bunker Hill", "Sunshine Mine", "Lake Pend Oreille", "geography", "satellite images"],
        "pinned_comment": "If you lived in North Idaho, would you rather be governed from Boise, or from Olympia in Washington?",
    },
}
out = HERE / "script.json"
out.write_text(json.dumps(script, ensure_ascii=False, indent=1) + chr(10), encoding="utf-8")
words = sum(len(p["text"].split()) for c in chapters for p in c["paragraphs"])
shots = [s for c in chapters for p in c["paragraphs"] for s in p["shots"]]
kinds = {k: sum(1 for s in shots if s["type"] == k) for k in ("map", "photo", "stat", "document", "chart")}
print(f"{words} words, {len(chapters)} chapters, {len(shots)} shots {kinds}")
