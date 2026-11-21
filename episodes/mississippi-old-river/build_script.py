"""Builds script.json for mississippi-old-river.  python build_script.py

Same production logic as episodes/venice-sinking (hand-placed shots, a photo or map frame at most twice). The narration
lives in drafts/narration.md (one "Pnn:" line per paragraph, "## Title (mood)" per chapter); every sentence comes from
research.md (OK rows). Photos and satellite tests: visuals.md.
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


CLEAR_DAY = "2025-10-14"  # cloud-free MODIS day over Louisiana (scored 15 Sep-15 Nov 2025, checked by eye)


def v(view, at=None, **kw):
    if view["span"] > 2.5 and not kw.get("highlight") and "date" not in kw:
        kw["date"] = CLEAR_DAY
    d = {"view": fresh(view), **kw}
    if at is not None:
        d["at"] = at
    return d


SAT_MIN_SPAN = 0.08  # Netherlands storyboard: narrower Sentinel views were soft
SUM = "2025-09-01/2025-10-31"  # scratch msat.py 2026-11-21: 2025-09-18 / 2025-10-16 cover the views in one pass


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
USA = {"lon": -95.5, "lat": 38.0, "span": 34.0}
LA = {"lon": -91.4, "lat": 30.5, "span": 5.6}
LOWER = {"lon": -90.9, "lat": 29.9, "span": 3.0}
GULF = {"lon": -90.3, "lat": 29.6, "span": 4.2}
LAR = "Louisiana@red"

LS = "landsat"
CMP_OLD = {"before": "1985-08-01/1985-10-31", "after": "2025-09-01/2025-10-31", "source": LS, "seconds": 2.8,
           "hold": 1.0, "label_before": "1985", "label_after": "2025"}
CMP_DELTA = {"before": "1986-08-01/1986-08-31", "after": "2025-09-01/2025-10-31", "source": LS, "seconds": 3.0,
             "until": "And here it is", "label_before": "1986", "label_after": "2025"}

# ------------------------------------------------------------------ sources (research.md)
CORPS = "USACE New Orleans District, Old River Control (2009)"
FISK = "H. N. Fisk, report to the Mississippi River Commission (1952)"
NASA = "NASA Earth Observatory"
NPS = "National Park Service, Mississippi River facts"
USGS = "USGS, Couvillion et al. 2017 (SIM 3381)"
OWN = "Own measurement: Landsat (USGS), Oct-Nov water index"
USACE24 = "USACE New Orleans District, Sep 2024"
WCSC = "USACE Waterborne Commerce, 2023"

# ------------------------------------------------------------------ photos (Commons, licence checked: visuals.md)
NARA73 = "File:IN THE SPRING OF 1973 THE MISSISSIPPI RIVER REACHED ITS HIGHEST LEVEL IN MORE THAN 150 YEARS. UNPRECEDENTED FLOODING... - NARA - {}.jpg"
PH_NOLA_RIVER = "File:Ronald Keohane visit 8.23.2024-08-23 Greater New Orleans Mississippi River.jpg"
PH_NOLA_2019 = "File:New Orleans from the Air September 2019 - French Quarter and CBD - River to Lake.jpg"
PH_NOLA_1985 = "File:New Orleans from the air, 14 December 1985, French Quarter - crop.jpg"
PH_NOLA_SKY = "File:Aerial - New Orleans Skyline 2013 - panoramio.jpg"
PH_ORCS_AIR = "File:Old River Control Structure Complex.jpg"
PH_OR24_1 = "File:Old River Control Complex, Louisiana, 17 June 2024 - 1.jpg"
PH_OR24_5 = "File:Old River Control Complex, Louisiana, 17 June 2024 - 5.jpg"
PH_AUX = "File:Old River Auxillary Control Structure.jpg"
PH_RAFT25 = "File:Photographic Views of Red River Raft 25.jpg"
PH_RAFT27 = "File:Photographic Views of Red River Raft 27.jpg"
PH_RAFT05 = "File:Photographic Views of Red River Raft 05.jpg"
PH_RAFT20 = "File:Photographic Views of Red River Raft 20.jpg"
PH_RAFT22 = "File:Photographic Views of Red River Raft 22.jpg"
PH_RAFT01 = "File:Photographic Views of Red River Raft 01.jpg"
PH_FISK1 = "File:Ancient Courses Mississippi River Meander Belt, Plate 22 Sheet 01.jpg"
PH_FISK7 = "File:Ancient Courses Mississippi River Meander Belt, Plate 22 Sheet 07.jpg"
PH_73_LEVEE = NARA73.format("552813")
PH_73_CAMPS = NARA73.format("552837")
PH_73_RING = NARA73.format("552836")
PH_73_TOWN = NARA73.format("552841")
PH_73_SALE = NARA73.format("552816")
PH_73_FOREST = NARA73.format("552847")
PH_SILL_1 = "File:Sill Construction on Lower Mississippi River, July 2023 - 1.jpg"
PH_SILL_4 = "File:Sill Construction on Lower Mississippi River, July 2023 - 9.jpg"
PH_SILL_6 = "File:Sill Construction on Lower Mississippi River, July 2023 - 6.jpg"
PH_SILL_AUG = "File:Underwater Sill Augmentation in Mississippi River 26 Sept 2023 - 10.jpg"
PH_BARGE07 = "File:First Water Barge to Plaquemines Parish Louisiana, 1 October 2023 - 07.jpg"
PH_BARGE11 = "File:First Water Barge to Plaquemines Parish Louisiana, 1 October 2023 - 28.jpg"
PH_SALT_MAP = "File:Mississippi River Saltwater Progression Forecast September 2023 Metro New Orleans.jpg"
PH_DOW = "File:Dow Chemical St. Charles plant at Taft LA on the Mississippi River.jpg"
PH_DOW2 = "File:Dow Chemical Plant, Taft, St. Charles Parish, Louisiana on the Mississippi River - panoramio.jpg"
PH_GARYVILLE = "File:Garyville and Reserve, Louisiana, and the Marathon Petroleum oil refinery.tif"
PH_DELTA_MODIS = "File:Mississippi River Delta (MODIS 2018-11-21).jpg"
PH_DELTA_1976 = "File:Mississippi Delta 1976.jpg"
PH_BR_2011 = "File:Mississippi River high water in Baton Rouge.jpg"
PH_LEVEE_2025 = "File:East Jefferson Levee District Police - Louisiana Levee Inspection, April 2025.jpg"
PH_1927 = "File:Floods - Mississippi River Flood - NARA - 68157473.jpg"
PH_ATCH_DELTA_99 = "File:Atchafalaya River delta.jpg"
PH_LAROSE = "File:Larose Louisiana aerial view.jpg"
PH_HARPER = "File:Harper's weekly (1867) Coming from the Church, Bayou LaFourche, Louisiana.jpg"
PH_ATCH_BASIN = "File:Atchafalaya Basin.jpg"
PH_BANKS_MAP = "File:Atchafalaya Basin. Prepared by order of Maj. Gen. N. P. Banks. Henry L. Abbot, Capt. & Chief Top. Eng'rs., Feb.... - NARA - 305632.jpg"
PH_CYPRESS = "File:Bald cypress Atchafalaya Basin.jpg"
PH_PANO = "File:AtchafalayaBasinPanorama.jpg"
PH_SG_AVOCA = "File:Sea Grant - Atchafalaya River looking towards Avoca Island Cutoff.jpg"
PH_SG_AVOCA2 = "File:Sea Grant - Atchafalaya River looking towards Avoca Island Cutoff.2.jpg"
PH_SG_WEST = "File:Sea Grant - Atchafalaya River's west bank near Sweetbay Lake.jpg"
PH_SG_MORGAN = "File:Sea Grant - Atchafalaya at Morgan City.jpg"
PH_SG_DELTA = "File:Sea Grant - Atchafalaya Delta landscape.jpg"
PH_SG_CHANNELS = "File:Sea Grant - Atchafalaya Delta channels.jpg"
PH_SG_NORTH = "File:Sea Grant - Atchafalaya delta looking north.jpg"
PH_I10 = "File:Atchafalaya Bridge.jpg"
PH_MORGAN_AIR = "File:Morgan City Louisiana aerial view.jpg"
PH_MORG_1973 = "File:Morganza Spillway, Louisiana 5 May 1973.jpg"
PH_MORG_NASA = "File:May 2011 Morganza Spillway Opens in Louisiana.jpg"
PH_MORG11_A = "File:Floodway opening, geo tagged stills 05.16.11 049.jpg"
PH_MORG11_B = "File:Floodway opening, geo tagged stills 05.16.11 006.jpg"
PH_BC_1 = "File:Bonnet Carre' Spillway test operation, 21 April 2025 - 1.jpg"
PH_BC_3 = "File:Bonnet Carre' Spillway test operation, 21 April 2025 - 3.jpg"
PH_WAX_NASA = "File:Waxlake 2014298 lrg.jpg"
PH_RAFT16 = "File:Photographic Views of Red River Raft 16.jpg"
PH_RESHAPE = "File:Reshaping Coastal Louisiana.jpeg"
PH_EMPIRE = "File:Empire-View of Mississippi River and south Plaquemines Parish near.jpg"
PH_FOX = "File:VIEW NORTHEAST AT NORTHERN BANK OF BAYOU LAFOURCHE; M-V 'FOX' LIES UNDER TREES AT CENTER OF PHOTOGRAPH - Motorized Sailing Vessel \"Fox\", Beached on East Bank ofBayou Lafourche, HAER LA,29-LAR,1-2.tif"
PH_SG_GUIDE = "File:Sea Grant - Atchafalaya Basin Guide Levee.jpg"
PH_SG_GUIDE_W = "File:Sea Grant - Atchafalaya Basin West Guide Levee.jpg"
PH_DEPT_GULF = "File:Department of the Gulf Map No. 48. Atchafalaya Basin - NARA - 102278585.jpg"
PH_NOLA_LOC = "File:Aerial view of the winding Mississippi River through New Orleans, Louisiana LCCN2011634562.tif"
PH_1927B = "File:Floods - Mississippi River Flood - NARA - 68157471.jpg"
PH_SHRIMP = "File:Shrimp Boat on Bayou Lafourche in Golden Meadows, LA.jpg"
PH_RAFT26 = "File:Photographic Views of Red River Raft 26.jpg"
PH_SG_FLANK = "File:Sea Grant - Atchafalaya Delta flank.jpg"
PH_SG_CHL = "File:Sea Grant - Atchafalaya Delta channels and associated landscape.jpg"
PH_LANDLOSS = "File:Land loss in coastal Louisiana since 1932 NOAA2013.jpg"
PH_SALT_PRESS = "File:Saltwater Wedge Press Conference, 2022-09-28 New Orleans - 04.jpg"

# ------------------------------------------------------------------ places
NOLA = place("New Orleans", -90.07, 29.95, "New Orleans", "city")
BR = place("Baton Rouge", -91.15, 30.45, "Baton Rouge", "city")
OLDR = place("Old River Control", -91.598, 31.076, "Old River Control", icon="water")
SHREVE = place("Shreveport", -93.75, 32.52, "Shreveport", "city")
NATCHEZ = place("Natchez", -91.40, 31.56, "Natchez", "city")
MORGAN = place("Morgan City", -91.20, 29.70, "Morgan City", "city")
MORGANZA = place("Morganza Floodway", -91.59, 30.74, "Morganza Floodway", icon="water")
DONALD = place("Donaldsonville", -90.99, 30.10, "Donaldsonville", "city")
THIBO = place("Thibodaux", -90.82, 29.80, "Thibodaux", "city")
GOLDEN = place("Golden Meadow", -90.27, 29.38, "Golden Meadow", "city")
NEWIB = place("New Iberia", -91.82, 30.00, "New Iberia", "city")
FRANKLIN = place("Franklin", -91.51, 29.80, "Franklin", "city")
HOP = place("Head of Passes", -89.25, 29.15, "Mouth of the Mississippi", icon="sea")
MYRTLE = place("Myrtle Grove", -89.98, 29.63, "Myrtle Grove sill", icon="warning")
WAXOUT = place("Wax Lake Outlet", -91.44, 29.58, "Wax Lake Outlet", icon="water")

MISS = {"from": [-91.60, 31.07], "via": [[-91.52, 30.90], [-91.38, 30.76], [-91.19, 30.45], [-91.23, 30.28], [-90.99, 30.10],
        [-90.70, 30.03], [-90.40, 30.02], [-90.07, 29.95], [-89.95, 29.86], [-89.79, 29.58], [-89.55, 29.40], [-89.35, 29.27]],
        "to": [-89.25, 29.15], "mode": "line", "color": "blue", "seconds": 3.0, "label": "Mississippi: 315 miles"}
ATCH = {"from": [-91.63, 31.05], "via": [[-91.80, 30.97], [-91.74, 30.69], [-91.75, 30.54], [-91.70, 30.28], [-91.52, 30.02],
        [-91.33, 29.85], [-91.20, 29.70]], "to": [-91.27, 29.45], "mode": "line", "color": "red", "seconds": 2.5,
        "label": "Atchafalaya: 142 miles"}
RED = {"from": [-93.75, 32.52], "via": [[-93.0, 31.9], [-92.45, 31.31], [-92.05, 31.10]], "to": [-91.80, 30.98], "mode": "line",
       "color": "accent", "seconds": 2.0, "label": "Red River"}
LAF = {"from": [-90.99, 30.10], "via": [[-91.03, 29.94], [-90.82, 29.80], [-90.60, 29.73], [-90.54, 29.65], [-90.38, 29.57],
       [-90.27, 29.38]], "to": [-90.21, 29.25], "mode": "line", "color": "accent", "seconds": 2.2, "label": "Bayou Lafourche"}
TECHE = {"from": [-91.95, 30.56], "via": [[-91.90, 30.27], [-91.83, 30.12], [-91.82, 30.00], [-91.66, 29.91], [-91.51, 29.80]],
         "to": [-91.30, 29.69], "mode": "line", "color": "alt", "seconds": 2.2, "label": "Bayou Teche"}
ARC = {"from": [-92.2, 29.7], "to": [-89.2, 29.5], "color": "accent", "label": "About a 200-mile arc", "bend": 0.45}
ARR_MISS_N = {"from": [-91.50, 31.45], "to": [-91.58, 31.12], "color": "blue", "label": "Mississippi", "bend": 0.1}
ARR_RED_W = {"from": [-92.15, 31.15], "to": [-91.82, 31.01], "color": "accent", "label": "Red River", "bend": 0.1}
ARR_ATCH_S = {"from": [-91.79, 30.95], "to": [-91.75, 30.65], "color": "red", "label": "Atchafalaya", "bend": 0.1}
ARR_PULL = {"from": [-91.62, 31.04], "to": [-91.40, 29.80], "color": "red", "label": "The shortcut pulls harder", "bend": -0.15}
ARR_MORG = {"from": [-91.59, 30.74], "to": [-91.55, 30.10], "color": "blue", "label": "Into the Atchafalaya Basin", "bend": 0.1}
ARR_TOW = {"from": [-90.15, 29.92], "to": [-91.58, 31.05], "color": "accent", "label": "Towed 208 miles upriver", "bend": 0.25}
ARR_SALT = {"from": [-89.40, 29.10], "to": [-89.98, 29.63], "color": "red", "label": "Salt water along the bottom", "bend": 0.1}

chapters = []
heads = iter(HEADS)


def chapter(*paras):
    title, mood = next(heads)
    chapters.append({"title": title, "mood": mood, "paragraphs": list(paras)})


chapter(
    P("P0",
      photo(0, PH_NOLA_RIVER, "The Mississippi at New Orleans"),
      stat("about six hundred thousand", "600,000 FT³/S", "Average flow of the Mississippi at New Orleans", NPS),
      sat("This is the Mississippi", -90.06, 29.95, 0.25, "New Orleans"),
      stat("carrying rain from all", "31 STATES", "All or part of them drain into the Mississippi", NPS),
      m("about forty percent of", v(USA, highlight=[LAR], places=[NOLA]), text="About 40 % of the continental US drains here"),
      m("But upstream, about fifty", v(LA, highlight=[LAR], places=[OLDR, BR, NOLA])),
      sat("this river is trying", -91.60, 31.075, 0.16, "Old River, Louisiana"),
      photo("Why does the biggest", PH_ORCS_AIR, "Old River Control, where the river is held"),
      photo("and what is holding", PH_OR24_5, "Old River Control Complex, June 2024")),
    P("P1",
      photo(0, PH_RAFT27, "A log raft on the Red River, 1873"),
      photo("a government geologist who", PH_FISK1, "Old courses of the Mississippi, Harold Fisk, 1944"),
      photo("and a spring in", PH_MORG_1973, "The Morganza Floodway area, 5 May 1973 (Landsat 1)"),
      sat("dug a hole under", -91.598, 31.077, 0.09, "Old River Control Structure"),
      sat("It also involves one", -91.35, 29.48, 0.45, "Atchafalaya Bay"),
      photo("and a summer when", PH_SILL_1, "Building an underwater sill, July 2023"),
      photo("toward the drinking water", PH_BARGE07, "Fresh water by barge, Plaquemines Parish, October 2023")),
    P("P2",
      sat(0, -90.55, 30.05, 0.40, "The river above New Orleans"),
      stat("the busiest port in", "#1", "US port by tonnage: the Port of South Louisiana (2023)", WCSC),
      photo("a long row of", PH_DOW, "A chemical plant on the river at Taft"),
      photo("and the water intakes", PH_NOLA_2019, "New Orleans"),
      photo("All of it depends", PH_GARYVILLE, "Garyville and Reserve, and the Marathon refinery"),
      m("The first reason it", v(GULF, highlight=[LAR], places=[NOLA, BR]), step("has never stayed in", routes=[LAF, TECHE]))),
)

chapter(
    P("P3",
      m(0, v(GULF, highlight=[LAR], places=[NOLA, HOP])),
      photo("When the water reaches", PH_RESHAPE, "Coastal Louisiana from orbit (NASA, 2020)"),
      sat("and over centuries the", -89.35, 29.15, 0.60, "The river's mouth today"),
      photo("Every mile of new", PH_EMPIRE, "The Mississippi near Empire, Plaquemines Parish"),
      sat("The water slows even", -89.50, 29.38, 0.25, "Plaquemines Parish: the river between its banks"),
      photo("In time, the river", PH_BR_2011, "The Mississippi at high water, Baton Rouge, 2011"),
      photo("held in by the", PH_LEVEE_2025, "Levee inspection, Jefferson Parish, April 2025")),
    P("P4",
      photo(0, PH_1927, "Mississippi River flood, April 1927"),
      photo("finds a shorter and", PH_1927B, "Mississippi River flood, April 1927"),
      stat("Geologists call that jump", "AVULSION", "A river jumping to a new course", FISK),
      sat("is left behind with", -91.70, 31.05, 0.25, "Abandoned river loops near Old River"),
      photo("and the river starts", PH_ATCH_DELTA_99, "A young delta: the Atchafalaya, 1999")),
    P("P5",
      m(0, v(LA, highlight=[LAR], places=[BR])),
      stat("According to the Army", "5,000-6,000 YRS", "Since the sea rose close to today's level", CORPS),
      sat("since the sea rose", -89.40, 29.20, 1.0, "The river's present delta"),
      stat("has migrated back and", "7+ TIMES", "The river below Baton Rouge moved across Louisiana", CORPS),
      stat("Geologists who dated the", "16 LOBES", "Separate delta lobes in the buried deposits", "Frazier 1967"),
      m("Left alone, NASA's Earth", v(LA, places=[BR, NOLA]), step("would probably swing across", arrows=[ARC]))),
    P("P6",
      photo(0, PH_FISK7, "Old courses of the Mississippi, Fisk 1944 (plate 22, sheet 7)"),
      photo("courses for the Mississippi", PH_FISK1, "Ancient courses of the Mississippi, Fisk 1944 (plate 22, sheet 1)"),
      sat("They look like tangled", -91.45, 31.45, 0.40, "The river valley near Natchez today"),
      photo("thousands of years of", PH_PANO, "The Atchafalaya Basin")),
    P("P7",
      m(0, v(LOWER, routes=[LAF], places=[DONALD, THIBO, GOLDEN])),
      sat("This thin line of", -90.40, 29.62, 0.35, "Bayou Lafourche"),
      photo("The houses stand on", PH_FOX, "Bayou Lafourche at Larose"),
      sat("with long, narrow fields", -90.55, 29.70, 0.12, "Long lots on the bayou ridge"),
      m("Further west, Bayou Teche", v(LOWER, routes=[TECHE], places=[NEWIB, FRANKLIN]))),
    P("P8",
      photo(0, PH_HARPER, "Bayou Lafourche, Harper's Weekly, 1867"),
      photo("and the river found", PH_SHRIMP, "A shrimp boat on Bayou Lafourche"),
      sat("Today, a shorter road", -91.65, 31.05, 0.40, "Where the Mississippi meets the Atchafalaya"),
      photo("people have been widening", PH_SG_GUIDE_W, "West guide levee of the Atchafalaya Basin")),
)

chapter(
    P("P9",
      m(0, v(LA, highlight=[LAR], places=[OLDR, BR])),
      m("The Mississippi comes down", v(near(-91.75, 31.05, 0.70), date=SUM, arrows=[ARR_MISS_N]), step("the Red River comes", arrows=[ARR_RED_W]),
        step("and the Atchafalaya leaves", arrows=[ARR_ATCH_S])),
      stat("According to the Corps,", "1400s", "A Mississippi loop captures the Red River", CORPS),
      sat("later called Turnbull's Bend,", -91.70, 31.00, 0.30, "The old loops around Old River")),
    P("P10",
      photo(0, PH_BANKS_MAP, "The Atchafalaya Basin, Union army map, 1860s"),
      sat("out of the Red,", -91.78, 31.00, 0.20, "Where the Atchafalaya leaves the Red"),
      sat("Once the loop had", -91.70, 31.02, 0.45, "The Red now feeds the Atchafalaya"),
      sat("Usually the current ran", -91.60, 31.07, 0.12, "Old River")),
    P("P11",
      m(0, v(LA, routes=[MISS], places=[OLDR, BR, NOLA]), step("past Baton Rouge and", places=[DONALD]), step("and out through its", places=[HOP])),
      stat("three hundred and fifteen", "315 MILES", "Old River to the Gulf, down the Mississippi", CORPS),
      m("The Atchafalaya runs almost", v(LA, routes=[MISS, ATCH], places=[OLDR, MORGAN])),
      photo("through the largest river", PH_PANO, "The Atchafalaya Basin"),
      stat("one hundred and forty-two", "142 MILES", "Old River to the Gulf, down the Atchafalaya", CORPS),
      chart("for the same drop", "Old River to the Gulf of Mexico", " mi", [["Mississippi", 315], ["Atchafalaya", 142]], CORPS, highlight=1)),
    P("P12",
      photo(0, PH_SG_AVOCA, "The Atchafalaya near its mouth"),
      photo("A steeper channel runs", PH_I10, "A highway bridge across the Atchafalaya Basin"),
      sat("and a bigger channel", -91.75, 30.70, 0.30, "The Atchafalaya"),
      sat("For a long time", -91.80, 30.95, 0.20, "The head of the Atchafalaya")),
)

chapter(
    P("P13",
      m(0, v(LA, highlight=[LAR], places=[SHREVE, OLDR])),
      stat("In 1831, Captain Henry", "1831", "Henry M. Shreve cuts across Turnbull's Bend", CORPS),
      sat("dug a cut across", -91.66, 31.02, 0.40, "Around Shreve's cut, today"),
      sat("The upper part of", -91.70, 31.06, 0.18, "Old loops beside the river"),
      sat("People called it, simply,", -91.62, 31.06, 0.10, "Old River")),
    P("P14",
      photo(0, PH_RAFT05, "Drift logs on the Red River, 1873"),
      photo("Not a boat: a", PH_RAFT27, "Part of the Red River raft, 1873"),
      stat("that blocked the head", "20-30 MI", "The log raft at the head of the Atchafalaya", "Fisk 1952; USACE"),
      sat("It may have started", -91.78, 30.90, 0.22, "The head of the Atchafalaya today")),
    P("P15",
      stat(0, "1839", "A drought on the Atchafalaya", FISK),
      stat("people crossed the channel", "15 FT", "A plank was enough to cross the channel", FISK),
      m("Local residents set the", v(LA, places=[place("The raft", -91.78, 30.92, "The raft, 1839", icon="fire"), OLDR])),
      photo("According to an account", PH_SG_WEST, "The Atchafalaya River"),
      stat("the fire burned about", "~20 MI", "Of the raft burned to the waterline", FISK),
      photo("The state of Louisiana", PH_RAFT22, "Clearing the Red River raft, 1873"),
      stat("and by 1855 the", "1855", "The last of the raft removed", FISK)),
    P("P16",
      photo(0, PH_RAFT16, "From the Red River raft album, 1873"),
      photo("being cleared in 1873.", PH_RAFT26, "The Red River after clearing, 1873"),
      photo("Imagine twenty miles of", PH_RAFT20, "Steam saws on the Red River raft, 1873"),
      photo("and then imagine it", PH_RAFT01, "Explosives camp on the Red River raft, 1873"),
      sat("Without the raft, the", -91.76, 30.80, 0.30, "The Atchafalaya today")),
    P("P17",
      photo(0, PH_SG_AVOCA2, "The Atchafalaya River"),
      stat("An 1881 report of", "1881", "Rapid enlargement of the Atchafalaya noted", "Mississippi River Commission, via Fisk 1952"),
      chart("In 1900 it was", "Atchafalaya's share of the Mississippi's flow", " %", [["1900", 5], ["1950", 25]], FISK,
            reveal=["By 1950 it"], highlight=1, kind="line"),
      stat("Counting the Red River", "15 → 30 %", "Share of the Mississippi + Red flow, 1900-1950", FISK),
      m("Every year the shortcut", v(LA, arrows=[ARR_PULL], places=[OLDR]))),
)

chapter(
    P("P18",
      m(0, v(LA, highlight=[LAR], places=[OLDR, BR, NOLA])),
      photo("the same geologist who", PH_FISK7, "Fisk's 1944 map of the river's old courses"),
      stat("delivered a report on", "1952", "Fisk's report to the Mississippi River Commission", FISK),
      photo("He measured the trend", PH_DEPT_GULF, "The Atchafalaya Basin, Civil War-era map"),
      stat("Sometime between 1965 and", "1965-75", "When the Atchafalaya would reach a critical stage", FISK),
      stat("taking about forty percent", "~40 %", "Share of the flow at the critical stage", FISK),
      doc("After that, closure of", "closure of the Mississippi River below Old River will be rapid and diversion will be uncontrollable",
          FISK, highlight="uncontrollable", title="Fisk, 1952")),
    P("P19",
      stat(0, "BY ~1990", "When the Corps expected the river to change course (1953)", NASA),
      m("left unchecked, the Mississippi", v(LA, routes=[ATCH], places=[BR, NOLA])),
      photo("The Corps' own description", PH_NOLA_LOC, "The Mississippi winding through New Orleans"),
      sat("The old channel past", -90.55, 30.05, 0.40, "The river between Baton Rouge and New Orleans"),
      photo("The refineries, chemical plants,", PH_DOW2, "Taft, St. Charles Parish"),
      photo("Cities down to New", PH_NOLA_SKY, "New Orleans"),
      photo("And the Atchafalaya Basin", PH_SG_GUIDE, "A guide levee in the Atchafalaya Basin")),
    P("P20",
      stat(0, "3 SEP 1954", "Congress authorizes Old River Control", CORPS),
      photo("a project to hold", PH_ORCS_AIR, "Old River Control, 1999"),
      m("The rule was simple:", v(LA, routes=[MISS, ATCH], places=[OLDR])),
      chart("About seventy percent of", "The 1950 split, kept every year", " %", [["Mississippi", 70], ["Atchafalaya", 30]], CORPS,
            reveal=["and about thirty percent"], highlight=1)),
    P("P21",
      stat(0, "1955", "Construction begins at Old River", CORPS),
      sat("in a dry hole", -91.60, 31.08, 0.10, "Old River Control Complex"),
      stat("The Low Sill Structure", "11 GATES", "Low Sill Structure, each 44 ft wide", CORPS),
      photo("Next to it, the", PH_OR24_5, "Old River Control Complex, June 2024"),
      stat("seventy-three bays long,", "73 BAYS", "Overbank Structure, for flood years", CORPS),
      sat("Old River itself was", -91.62, 31.06, 0.10, "Old River"),
      stat("and a navigation lock", "1963", "Old River Lock opens", CORPS)),
    P("P22",
      stat(0, "$67 M", "Cost of the Old River complex by 1962", CORPS),
      sat("For the first time,", -91.58, 31.07, 0.22, "Old River Control"),
      photo("The Corps could decide", PH_SG_MORGAN, "The Atchafalaya at Morgan City"),
      sat("and for about ten", -91.75, 30.70, 0.30, "The Atchafalaya"),
      stat("Then came the spring", "1973", "The Great Flood of 1973", CORPS)),
)

chapter(
    P("P23",
      m(0, v(LA, highlight=[LAR], places=[OLDR, MORGANZA, MORGAN]), step("and the spring of", places=[NATCHEZ, BR])),
      doc("The river crested again", "The Mississippi crested several times that spring, and a prolonged flood fight raged up and down the big river, its tributaries and distributaries.",
          CORPS, highlight="crested several times", title="US Army Corps of Engineers"),
      doc("The federal photographers sent", "In the spring of 1973 the Mississippi River reached its highest level in more than 150 years.",
          "EPA DOCUMERICA caption, 1973 (NARA)", highlight="highest level in more than 150 years", title="EPA DOCUMERICA, 1973"),
      stat("reached its highest level", "150+ YEARS", "The river's highest level in that time (1973)", "EPA DOCUMERICA caption (NARA)"),
      sat("Across Louisiana, homes and", -91.65, 30.30, 0.40, "The Atchafalaya Basin")),
    P("P24",
      sat(0, -91.60, 31.075, 0.16, "Old River Control"),
      photo("By the Corps' account,", PH_BR_2011, "The Mississippi at Baton Rouge (2011)"),
      sat("could not carry as", -91.50, 30.95, 0.30, "The Mississippi below Old River"),
      photo("while the Atchafalaya had", PH_SG_AVOCA, "The Atchafalaya River"),
      doc("The gates did regulate", "The Low Sill Structure was designed to regulate flow, and it did so.", CORPS,
          highlight="and it did so", title="US Army Corps of Engineers")),
    P("P25",
      stat(0, "APRIL 1973", "The south wing wall of the Low Sill collapses", CORPS),
      stat("sixty-seven feet high on", "67 FT", "Height of the concrete wing wall", CORPS),
      doc("the wall that guided", "Flood waters undermine the south wing wall of the Low Sill Structure, causing it to collapse.",
          CORPS, highlight="causing it to collapse", title="US Army Corps of Engineers"),
      sat("Under the structure, it", -91.598, 31.077, 0.12, "The Low Sill Structure site"),
      doc("A large scour hole", "A large scour hole also developed in front of and beneath the structure, exposing approximately 50 feet of the 90-foot-long steel pilings",
          CORPS, highlight="exposing approximately 50 feet", title="US Army Corps of Engineers"),
      chart("The structure stood on", "Steel pilings under the Low Sill, 1973", " ft", [["Piling length", 90], ["Left exposed", 50]], CORPS,
            reveal=["and about fifty feet"], highlight=1)),
    P("P26",
      m(0, v(LA, places=[place("Low Sill", -91.598, 31.076, "Low Sill: undermined", icon="warning"), BR, NOLA]),
        step("with the river at", places=[MORGANZA])),
      photo("Downstream, the Corps opened", PH_MORG_1973, "The Morganza Floodway area, 5 May 1973 (Landsat 1)"),
      stat("Its one hundred and", "125 GATES", "Morganza Floodway: up to 600,000 ft³/s", "USACE; NASA EO"),
      m("into the Atchafalaya Basin,", v(LA, arrows=[ARR_MORG], places=[MORGANZA, BR, NOLA]))),
    P("P27",
      sat(0, -91.598, 31.077, 0.09, "Old River Control Structure"),
      doc("the Corps built a", "Emergency repairs involve construction of a stone dike at the end of the ramp to replace the failed wall.",
          CORPS, highlight="a stone dike", title="US Army Corps of Engineers"),
      sat("and pumped grout into", -91.60, 31.08, 0.10, "Old River Control Complex"),
      stat("the rehabilitation took until", "1981", "Repairs at the Low Sill finished", CORPS),
      chart("It had been designed", "Water-level difference allowed across the Low Sill", " ft", [["Designed for", 37], ["After 1973", 22]], CORPS,
            reveal=["After 1973, the Corps"], highlight=1)),
    P("P28",
      photo(0, PH_OR24_1, "The Auxiliary Structure, 2024"),
      stat("was started in July", "1981-86", "The Auxiliary Structure is built", CORPS),
      stat("for two hundred and", "$206 M", "Cost of the Auxiliary Structure: six 62-ft gates", CORPS),
      m("Here is the site", v(near(-91.60, 31.075, 0.15), compare=CMP_OLD), text="Old River Control"),
      sat("The new channel is", -91.615, 31.08, 0.10, "Old River Control Complex, 2025")),
    P("P29",
      sat(0, -91.61, 31.08, 0.12, "Old River Control Complex today"),
      m("It was built far", v(LA, places=[NOLA, OLDR]), step("then towed two hundred", arrows=[ARR_TOW])),
      photo("and went online in", PH_AUX, "Old River Auxiliary Structure, 2009"),
      sat("It turns the water", -91.605, 31.085, 0.08, "Old River Control Complex"),
      stat("into up to one", "192 MW", "Sidney A. Murray Jr. hydroelectric station, online 1990", CORPS),
      stat("Together, the structures here", "700,000 FT³/S", "Combined capacity of the Old River structures", CORPS)),
    P("P30",
      photo(0, PH_MORG11_A, "Morganza Floodway, May 2011"),
      photo("In May 2011, during", PH_MORG_NASA, "Morganza Floodway open, 15 May 2011 (NASA EO-1)"),
      photo("two bays on the", PH_MORG11_B, "Morganza Floodway, May 2011"),
      photo("In 2019 Morganza was", PH_BC_1, "Bonnet Carré Spillway, test opening, April 2025"),
      stat("had to be opened", "2 OPENINGS", "Bonnet Carré Spillway in 2019, a first", "USACE"),
      photo("Every big flood is", PH_BC_3, "Bonnet Carré Spillway, April 2025")),
)

chapter(
    P("P31",
      m(0, v(LA, highlight=[LAR], places=[OLDR, MORGAN]), step("The Atchafalaya still gets", routes=[ATCH])),
      photo("But thirty percent of", PH_SG_MORGAN, "The Atchafalaya at Morgan City"),
      photo("and it brings mud", PH_SG_FLANK, "The edge of the Atchafalaya delta"),
      sat("Follow it south to", -91.35, 29.50, 0.50, "Atchafalaya Bay")),
    P("P32",
      stat(0, "1941", "Wax Lake Outlet dug to protect Morgan City", NASA),
      sat("to lower flood levels", -91.20, 29.70, 0.12, "Morgan City"),
      sat("Today it carries about", -91.42, 29.62, 0.25, "Wax Lake Outlet", places=[WAXOUT]),
      photo("Mud began building up", PH_WAX_NASA, "Wax Lake delta, October 2014 (NASA, Landsat 8)"),
      photo("and after the great", PH_SG_DELTA, "The Atchafalaya delta")),
    P("P33",
      m(0, v(near(-91.35, 29.50, 0.46), compare=CMP_DELTA), step("And here it is", view=near(-91.35, 29.50, 0.46)),
        text="Atchafalaya Bay"),
      sat("We measured them on", -91.28, 29.46, 0.20, "The Atchafalaya delta"),
      chart("between 1985 and 2026,", "Land gained 1985-2026 (our Landsat measurement)", " km²", [["Wax Lake delta", 55], ["Atchafalaya delta", 60]], OWN,
            reveal=["and the Atchafalaya delta"], highlight=1),
      stat("That is roughly two", "2.8 KM²/YR", "Delta growth: our measurement matches LSU's estimate", OWN + "; NASA EO (LSU)"),
      photo("the same rate scientists", PH_SG_CHL, "The Atchafalaya delta")),
    P("P34",
      sat(0, -90.00, 29.45, 0.40, "Barataria Bay"),
      stat("The US Geological Survey", "~4,800 KM²", "Coastal Louisiana land lost, 1932-2016", USGS),
      photo("of land between 1932", PH_LANDLOSS, "Coastal Louisiana land, 1932 and 2011 (NOAA)"),
      sat("about a quarter of", -90.55, 29.40, 0.30, "Terrebonne marshes"),
      stat("At the worst of", "34 MIN", "A football field of land lost (1970s peak)", USGS),
      sat("And the river now", -89.25, 29.10, 0.35, "The river's mouth"),
      chart("about one hundred and", "Mud carried by the river", " Mt/yr", [["Today", 170], ["Historically", 400]], NASA,
            reveal=["down from about four"], highlight=0)),
    P("P35",
      photo(0, PH_SG_CHANNELS, "Channels of the Atchafalaya delta"),
      photo("It is a small", PH_SG_NORTH, "The Atchafalaya delta, looking north"),
      sat("thousands of years, and", -91.45, 29.50, 0.20, "The Wax Lake delta")),
)

chapter(
    P("P36",
      m(0, v(LA, highlight=[LAR], routes=[MISS], places=[NATCHEZ, NOLA])),
      stat("The bed of the", "BELOW SEA LEVEL", "The riverbed from Natchez to the Gulf", USACE24),
      m("When the river runs", v(GULF, arrows=[ARR_SALT], places=[MYRTLE, NOLA])),
      photo("to push back, and", PH_SALT_PRESS, "Salt-wedge briefing, New Orleans, September 2022"),
      sat("creeps upstream along the", -89.98, 29.63, 0.20, "The river at Myrtle Grove")),
    P("P37",
      photo(0, PH_SILL_4, "Sill construction, July 2023"),
      stat("in 1988, 1999, 2012,", "5 SILLS", "1988, 1999, 2012, 2022, 2023", USACE24),
      photo("That year the river", PH_SILL_6, "Sill construction, July 2023"),
      stat("on the twentieth of", "20 SEP 2023", "Salt water flows over the sill", "USACE"),
      photo("The Corps raised its", PH_SILL_AUG, "Raising the sill, 26 September 2023"),
      photo("and barges carried fresh", PH_BARGE07, "First water barge to Plaquemines Parish, 1 October 2023"),
      photo("where the salt had", PH_BARGE11, "Plaquemines Parish, October 2023")),
    P("P38",
      sat(0, -90.70, 30.08, 0.30, "Plants along the river"),
      stat("In the Corps' words,", "SALTWATER ESTUARY", "What the Corps says the old channel would become", CORPS),
      photo("right through the stretch", PH_GARYVILLE, "Garyville and Reserve, Louisiana"),
      stat("two hundred and seventeen", "217.5 M TONS", "Port of South Louisiana, 2023 (#1 in the US)", WCSC),
      photo("and where New Orleans", PH_NOLA_2019, "New Orleans")),
    P("P39",
      photo(0, PH_OR24_1, "Old River Control Complex, 2024"),
      sat("Atchafalaya its thirty percent", -91.58, 31.07, 0.22, "Old River Control"),
      m("But the shortcut is", v(LA, routes=[ATCH], places=[OLDR]), step("against three hundred and", routes=[MISS])),
      sat("Should the Corps keep", -91.60, 31.07, 0.30, "Old River"),
      ask=("Should the Corps keep", "Hold the river in place forever, or let it move?")),
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
    "title": "Why the Mississippi Wants to Leave New Orleans",
    "voice": "am_michael",
    "voice_speed": 1.15,
    "music": "procedural",
    "map_style": "satellite",
    "look": "none",
    "photo_upscale": True,
    "sources": ["episodes/mississippi-old-river/research.md and factcheck.md", "Contains modified Copernicus Sentinel data 2026", "Landsat imagery courtesy of the U.S. Geological Survey"],
    "thumbnail": {"text": "IT WANTS OUT"},
    "chapters": chapters,
    "youtube": {
        "title": "Why the Mississippi Wants to Leave New Orleans",
        "description": "Fifty miles northwest of Baton Rouge, the Mississippi River sits right next to a much shorter road to the sea: the Atchafalaya. This video follows how the river has moved across Louisiana again and again, how a steamboat captain's shortcut and a burned log jam opened the door, why a 1952 report gave the river a deadline, the night-and-day fight to save Old River Control in the flood of 1973, the only part of the coast that is still growing, and what the 2023 salt wedge showed about a Mississippi that leaves.",
        "tags": ["Mississippi River", "Atchafalaya River", "Old River Control Structure", "New Orleans", "Louisiana", "Army Corps of Engineers", "1973 flood", "Morganza Spillway", "Wax Lake delta", "river avulsion", "saltwater wedge", "geography", "satellite images"],
        "pinned_comment": "Should the Corps keep holding the Mississippi in place forever, or let it move and rebuild the coast?",
    },
}
out = HERE / "script.json"
out.write_text(json.dumps(script, ensure_ascii=False, indent=1) + chr(10), encoding="utf-8")
words = sum(len(p["text"].split()) for c in chapters for p in c["paragraphs"])
shots = [s for c in chapters for p in c["paragraphs"] for s in p["shots"]]
kinds = {k: sum(1 for s in shots if s["type"] == k) for k in ("map", "photo", "stat", "document", "chart")}
print(f"{words} words, {len(chapters)} chapters, {len(shots)} shots {kinds}")
