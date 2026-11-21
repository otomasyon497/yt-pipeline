"""Builds script.json for florida-big-bend.  python build_script.py

Same production logic as episodes/mississippi-old-river (hand-placed shots, a photo or map frame at most twice). The
narration lives in drafts/narration.md (one "Pnn:" line per paragraph, "## Title (mood)" per chapter); every sentence
comes from research.md (OK rows; CHECK rows only attributed). Photos and satellite tests: visuals.md. Painted regions:
geo/make_regions.py. Own measurements: shelf.json (ETOPO), the Cedar Key gauge chart (research.md).
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


CLEAR_DAY = "2025-04-17"  # MODIS Terra 2025-04-17: all of Florida and the Big Bend cloud-free (scratch modis.jpg, checked by eye)


def v(view, at=None, **kw):
    if view["span"] > 2.5 and not kw.get("highlight") and "date" not in kw and kw.get("layer") != "night":
        kw["date"] = CLEAR_DAY
    d = {"view": fresh(view), **kw}
    if at is not None:
        d["at"] = at
    return d


SAT_MIN_SPAN = 0.08  # Netherlands storyboard: narrower Sentinel views were soft
SPRING = "2025-03-01/2025-05-31"  # scratch bbsat.py 2026-11-21: clear scenes 2025-03-11 .. 2025-05-05 over every test view
CK_DAY = "2025-01-25/2025-01-25"  # Cedar Key at low tide: flats and channels exposed (spring 2025 was hazy there)
PRE_HELENE = "2024-09-01/2024-09-24"
POST_HELENE = "2024-09-28/2024-10-25"


def sat(at, lon, lat, span, label=None, **kw):
    kw.setdefault("date", SPRING)
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
USA_SE = {"lon": -85.5, "lat": 31.0, "span": 16.0}
FL = {"lon": -83.4, "lat": 27.9, "span": 8.6}
GULF_FL = {"lon": -84.6, "lat": 28.4, "span": 9.8}
BB = {"lon": -83.55, "lat": 29.65, "span": 2.9}
NFL = {"lon": -82.6, "lat": 29.6, "span": 4.6}  # north Florida: Fernandina to Cedar Key, the barge canal
CENTRAL = {"lon": -82.3, "lat": 28.8, "span": 4.4}  # Cedar Key to Tampa
FLR = "Florida@alt"
BBC = "file:bigbend_coast.geojson@red"
SHALLOW = "file:shallow10.geojson@blue"

# ------------------------------------------------------------------ sources (research.md)
OWN = "Own measurement: NOAA ETOPO 2022 seafloor model (60 arc-sec)"
USGS = "USGS Open-File Report 01-303 (Hine et al.)"
FDEP = "Florida DEP, Big Bend Seagrasses Aquatic Preserve"
CENSUS = "U.S. Census Bureau, population estimates, vintage 2024"
NWF = "Northwest Florida Water Management District"
FWS = "U.S. Fish and Wildlife Service"
NWS = "National Weather Service Tampa Bay"
UFLIB = "University of Florida Libraries"
FLMNH = "Florida Museum, University of Florida"
GP = "Georgia-Pacific, 18 September 2023"
IFAS = "UF/IFAS economic impact estimate, 2023"
NHC_I = "NHC Tropical Cyclone Report: Idalia"
NHC_D = "NHC Tropical Cyclone Report: Debby"
NHC_H = "NHC Tropical Cyclone Report: Helene"
NOS = "NOAA National Ocean Service"
GAUGE = "Own chart: NOAA CO-OPS 8727520 Cedar Key, monthly highest (ft above MHHW)"

# ------------------------------------------------------------------ photos (Commons, licence checked: visuals.md)
PH_NIGHT = "File:Florida Peninsula at night, 13 October 2014 (ISS041-E-74232).JPG"
PH_CK1 = "File:Cedar Key Florida01.jpg"
PH_CK2 = "File:Cedar Key Florida02.jpg"
PH_CK3 = "File:Cedar Key Florida03.jpg"
PH_CK4 = "File:Cedar Key Florida04.jpg"
PH_CK_ST = "File:Cedar Key SR 24 01.jpg"
PH_HAMMOCK = "File:Flickr - ggallice - Hammock.jpg"
PH_CK_IDALIA = "File:Hurricane Idalia’s damage around Faraway Inn, Cedar Key, Florida.jpg"
PH_ATSENA = "File:Atsena Otie Key Island.jpg"
PH_CK_MUSEUM = "File:Cedar Key Hist Museum Lutterloh01.jpg"
PH_CK_1884 = "File:Bird's eye view of Cedar-Key, Fla., Levy Co. LOC 77690244.jpg"
PH_CK_1884B = "File:Cedar Key 1884b small.jpg"
PH_CK_1861 = "File:Cedar Keys, Florida LOC 99447268.jpg"
PH_CK_1852 = "File:1852 U.S. Coast Survey Map of Cedar Key, Florida - Geographicus - CedarKey-uscs-1852.jpg"
PH_FL_1861 = "File:Birds eye view of Florida and part of Georgia and Alabama LOC 99447266.jpg"
PH_FL_RR = "File:Florida Railroad, from Cedar Key Extension to Tampa Bay - NARA - 102256504.jpg"
PH_YULEE = "File:David Levy Yulee - Brady-Handy.jpg"
PH_TAMPA_HOTEL = "File:Old Tampa Bay Hotel.jpg"
PH_SANBORN = "File:Sanborn Fire Insurance Map from Cedar Key, Levy County, Florida, 1909, Plate 0001.jpg"
PH_1896 = "File:After Great Hurricane of 1896 WDL4032.png"
PH_1896_MAP = "File:September 29, 1896 hurricane weather map.jpg"
PH_MOUND = "File:Indian mound, Cedar Key, Fla, from Robert N. Dennis collection of stereoscopic views.jpg"
PH_CK_AIR_OLD = "File:Florida - Brandenton through Clearwater - NARA - 23936569 (cropped).jpg"
PH_STM_LIGHT_MARSH = "File:A scenic view of white lighthouse.jpg"
PH_STM_LIGHT = "File:St Marks Light - Florida.jpg"
PH_STM_HABS = "File:St. Marks Light, at the mouth of the St. Marks River in the Apalachee Bay on Florida's panhandle LCCN2011632986.tif"
PH_BOARDWALK = "File:Refuge boardwalks.jpg"
PH_MARSH_FIRE = "File:Controlled burn in the salt marsh at St Marks NWR (7439799012).jpg"
PH_MARSH_FIRE2 = "File:St Marks NWR Rx Fire in salt water marsh (7439799476).jpg"
PH_SUWANNEE_PALMS = "File:Flickr - ggallice - Near lower Suwannee.jpg"
PH_PACE = "File:Hurricane Helene Stirs Up Gulf Coast Waters (153390 - pace 20240928 lrg).jpg"
PH_LANDSAT1 = "File:Apalachee Bay, Florida-Georgia, satellite image map - NASA LANDSAT-1, 1-500,000, N3015W08346 LOC 79695112.jpg"
PH_LEON = "File:Big Bend Scenic Byway - Leon Sinks Geological Site - NARA - 7717294.jpg"
PH_NATBRIDGE = "File:Natural Bridge Battlefield Historic State Park Pano.jpg"
PH_WAK1 = "File:Wakulla-springs 2009-05-03T23 48 20.jpg"
PH_WAK2 = "File:Wakulla-springs 2009-05-04T18 58 57.jpg"
PH_WAK3 = "File:Wakulla-springs 2009-05-04T19 12 53.jpg"
PH_SUW_TANNIC = "File:Suwanee River tannic acid.JPG"
PH_STM_RIVER = "File:St Marks River at Newport, Florida.jpg"
PH_CANAL_MAP = "File:Cross Florida Barge Canal ACoE.jpg"
PH_CANAL_E = "File:Cross Fla Barge canal SR19E-02.jpg"
PH_CANAL_W = "File:Cross Fla Barge canal SR19W-03.jpg"
PH_GREENWAY = "File:Santos CFBC trail 01.jpg"
PH_GREENWAY_I75 = "File:Florida I75sb Cross Florida Greenway Overpass.jpg"
PH_FENHOLLOWAY = "File:Fenholloway River east of Perry Florida.jpg"
PH_KEATON_NG = "File:Florida National Guard in Keaton Beach, Florida (Hurricane Helene).jpg"
PH_KEATON_STREET = "File:President Joe Biden surveys damage before receiving a briefing on Hurricane Helene response and recovery efforts on October 3, 2024, in the Keaton Beach neighborhood in Perry, Florida.jpg"
PH_STEIN_IDALIA1 = "File:Florida National Guard (Idalia response).jpg"
PH_STEIN_IDALIA2 = "File:Florida National Guard - 53155016685.jpg"
PH_STEIN_IDALIA3 = "File:Florida National Guard - 53154586186.jpg"
PH_PERRY_LINES = "File:Florida National Guard - 53153543735.jpg"
PH_IDALIA_CIRA = "File:Hurricane Idalia Makes Landfall Along the Coast of Florida’s Big Bend (CIRA 2023-08-30).png"
PH_HELENE_CIRA = "File:Hurricane Helene Approaches the Florida Coast (CIRA 2024-09-27).png"
PH_IDALIA_MODIS = "File:Hurricane Idalia Batters the Southeastern United States (MODIS).jpg"
PH_STEIN_RIVER = "File:Steinhatchee River from Fort Steinhatchee Pier.jpg"
PH_STEIN_RIVER_W = "File:Steinhatchee River looking west from Roy's Restaurant.jpg"
PH_STEIN_MARKER = "File:Deadman Bay, Stephensville and Steinhatchee historical marker.jpg"
PH_HELENE_ISS = "File:Iss072e001649 (Sept 25, 2024) -- Hurricane Helene is pictured from the International Space Station as it orbited 257 above the Gulf of Mexico off the coast of Mississippi.jpg"
PH_1896_MAP2 = "File:September 30, 1896 hurricane 4 weather map.jpg"
PH_SUW_PAN = "File:Along the Suwannee - panoramio.jpg"
PH_WAK4 = "File:Wakulla-springs 2009-05-04T19 01 40.jpg"
PH_STM_1831 = "File:Lighthouse built in 1831 of brick and mortar.jpg"
PH_SANBORN20 = "File:Sanborn Fire Insurance Map from Cedar Key, Levy County, Florida, 1920, Plate 0001.jpg"
PH_TAMPA_HOTEL3 = "File:Old Tampa Bay Hotel3.jpg"
PH_CANAL_E1 = "File:Cross Fla Barge canal SR19E-01.jpg"
PH_MARSHALL = "File:Marshall Swamp Trailhead; Cross Florida Greenway-01.jpg"
PH_STEIN_IDALIA4 = "File:Florida National Guard - 53154792319.jpg"
PH_STEIN_BRIDGE = "File:Capt Chad Allen Sr Memorial Bridge from Fort Steinhatchee Pier.jpg"

# ------------------------------------------------------------------ places
CEDAR = place("Cedar Key", -83.035, 29.138, "Cedar Key", "city")
KEATON = place("Keaton Beach", -83.594, 29.820, "Keaton Beach", "city")
STEIN = place("Steinhatchee", -83.387, 29.671, "Steinhatchee", "city")
HORSE = place("Horseshoe Beach", -83.289, 29.441, "Horseshoe Beach", "city")
STMARKS = place("St. Marks", -84.205, 30.160, "St. Marks", "city")
YANKEE = place("Yankeetown", -82.716, 29.030, "Yankeetown", "city")
PERRY = place("Perry", -83.582, 30.117, "Perry", "city")
CRYSTAL = place("Crystal River", -82.594, 28.902, "Crystal River", "city")
TALLY = place("Tallahassee", -84.28, 30.44, "Tallahassee", "city")
TAMPA = place("Tampa", -82.46, 27.95, "Tampa", "city")
STPETE = place("St. Petersburg", -82.64, 27.77, "St. Petersburg", "city")
MIAMI = place("Miami", -80.19, 25.77, "Miami", "city")
ORLANDO = place("Orlando", -81.38, 28.54, "Orlando", "city")
JAX = place("Jacksonville", -81.66, 30.33, "Jacksonville", "city")
PENSA = place("Pensacola Beach", -87.13, 30.33, "Pensacola Beach", "city")
MIAMIB = place("Miami Beach", -80.13, 25.79, "Miami Beach", "city")
PCB = place("Panama City Beach", -85.80, 30.18, "Panama City Beach", "city")
CLEAR = place("Clearwater", -82.80, 27.97, "Clearwater", "city")
NAPLES = place("Naples", -81.80, 26.14, "Naples", "city")
FERN = place("Fernandina", -81.46, 30.67, "Fernandina", "city")
WAKULLA = place("Wakulla Springs", -84.302, 30.235, "Wakulla Springs", icon="water")
AUCILLA = place("Aucilla River", -83.99, 30.09, "Aucilla River", icon="water")
FOLEY = place("Foley mill", -83.53, 30.07, "Foley mill (closed 2023)", icon="warning")
CANAL_END = place("Canal mouth", -82.80, 28.99, "Barge canal, Gulf end", icon="water")
GAUGE_PT = place("Cedar Key gauge", -83.03, 29.135, "Cedar Key tide gauge", icon="water")
L_IDALIA = place("Idalia landfall", -83.59, 29.82, "Idalia, 30 Aug 2023", icon="warning")
L_DEBBY = place("Debby landfall", -83.45, 29.70, "Debby, 5 Aug 2024", icon="warning")
L_HELENE = place("Helene landfall", -83.72, 29.99, "Helene, 27 Sep 2024", icon="warning")
L_1896 = place("1896 landfall", -83.05, 29.15, "Hurricane, 29 Sep 1896", icon="warning")

RR_FLA = {"from": [-81.46, 30.67], "via": [[-81.98, 30.30], [-82.11, 29.94], [-82.33, 29.65], [-82.64, 29.45]], "to": [-83.035, 29.138],
          "mode": "line", "color": "accent", "seconds": 2.5, "label": "Florida Railroad, 1861"}
RR_PLANT = {"from": [-81.27, 28.80], "via": [[-81.41, 28.29], [-81.95, 28.04]], "to": [-82.46, 27.95], "mode": "line", "color": "red",
            "seconds": 2.0, "label": "Plant's railroad to Tampa, 1884"}
CANAL = {"from": [-81.65, 29.65], "via": [[-81.63, 29.43], [-81.86, 29.26], [-82.10, 29.13], [-82.43, 29.05], [-82.62, 29.03]],
         "to": [-82.80, 28.99], "mode": "line", "color": "red", "seconds": 2.5, "label": "Cross Florida Barge Canal route"}
ARR_SHIP = {"from": [-82.2, 24.0], "to": [-79.7, 25.6], "color": "blue", "label": "The long way round", "bend": -0.35}
ARR_SURGE = {"from": [-84.4, 29.2], "to": [-83.65, 29.85], "color": "red", "label": "Wind pushes water over 15 miles of shallows", "bend": 0.1}
ARR_SHIP_BB = {"from": [-84.0, 29.25], "to": [-83.45, 29.65], "color": "blue", "label": "15 miles of shallows", "bend": 0.0}

CMP_KEATON = {"before": PRE_HELENE, "after": POST_HELENE, "seconds": 2.8, "until": "and this is the same coast",
              "label_before": "Early Sep 2024", "label_after": "After Helene"}
CMP_HORSE = {"before": PRE_HELENE, "after": POST_HELENE, "seconds": 2.8, "hold": 1.0,
             "label_before": "Early Sep 2024", "label_after": "After Helene"}

chapters = []
heads = iter(HEADS)


def chapter(*paras):
    title, mood = next(heads)
    chapters.append({"title": title, "mood": mood, "paragraphs": list(paras)})


chapter(
    P("P0",
      photo(0, PH_HELENE_ISS, "Hurricane Helene in the Gulf, 25 September 2024 (ISS)"),
      m("a tide gauge at", v(BB, highlight=[BBC], places=[GAUGE_PT, CEDAR])),
      stat("measured the sea nine", "9.3 FT", "Above the normal high-tide line, Cedar Key gauge", NHC_H),
      stat("That gauge had been", "SINCE 1914", "Never higher in all its years of records", NHC_H),
      photo("In all those years,", PH_CK4, "Cedar Key"),
      sat("And Cedar Key is", -83.03, 29.14, 0.14, "Cedar Key, Florida", date=CK_DAY),
      stat("It is a town", "736", "People in Cedar Key, 2024", CENSUS),
      photo("on a stretch of", PH_CK1, "The shore at Cedar Key")),
    P("P1",
      stat(0, "23.4 MILLION", "People in Florida, 2024", CENSUS),
      m("and long stretches of", v(FL, places=[MIAMI, TAMPA, STPETE, CLEAR, NAPLES])),
      stat("Pinellas County alone, around", "965,870", "People in Pinellas County (St. Petersburg), 2024", CENSUS),
      m("But follow the same", v(FL, highlight=[FLR, BBC], places=[TAMPA, TALLY]), step("to the long curve", view={"lon": -83.9, "lat": 29.3, "span": 4.6})),
      m("This is the Big", v(BB, highlight=[BBC], places=[STMARKS, KEATON, STEIN, CEDAR])),
      stat("Four counties along that", "103,143", "People in Jefferson, Taylor, Dixie and Levy counties, 2024", CENSUS),
      photo("hold about a hundred", PH_SUWANNEE_PALMS, "Near the lower Suwannee, Dixie County"),
      photo("Seen from space at", PH_NIGHT, "Florida at night from the ISS, 2014: north of Tampa (left), the Gulf coast goes dark"),
      m("this stretch of coast", v(GULF_FL, layer="night", places=[TAMPA, TALLY]))),
    P("P1b",
      photo(0, PH_CK_ST, "Main road into Cedar Key"),
      stat("Horseshoe Beach has a", "173", "People in Horseshoe Beach, 2024", CENSUS),
      sat("St. Marks, three hundred", -84.20, 30.15, 0.12, "St. Marks"),
      sat("Yankeetown, six hundred and", -82.72, 29.03, 0.12, "Yankeetown"),
      sat("The biggest town behind", -83.58, 30.11, 0.14, "Perry"),
      photo("There is no big", PH_HAMMOCK, "Salt marsh near Cedar Key"),
      sat("and for most of", -83.55, 29.75, 0.9, "The Big Bend coast: no beach")),
    P("P2",
      sat(0, -83.05, 29.12, 0.30, "Off Cedar Key at low tide", date=CK_DAY),
      photo("A town that once", PH_CK_1884, "Cedar Key, 1884"),
      photo("and lost it to", PH_TAMPA_HOTEL, "Tampa, where the railroad went instead"),
      sat("A canal across Florida", -82.72, 29.02, 0.32, "Where the barge canal meets the Gulf"),
      photo("And why that same", PH_KEATON_NG, "Keaton Beach the day after Helene, 27 September 2024"),
      m("sent the water at", v(near(-83.031, 29.134, 0.09), date=CK_DAY, places=[GAUGE_PT])),
      m("So why does a", v(FL, highlight=[FLR, BBC], places=[MIAMI, TAMPA])),
      photo("It isn't one thing.", PH_STM_LIGHT_MARSH, "St. Marks lighthouse and marsh"),
      m("The first reason is", v(GULF_FL, highlight=[SHALLOW], places=[CEDAR, TAMPA]))),
)

chapter(
    P("P3",
      m(0, v(GULF_FL, highlight=[SHALLOW], places=[PENSA, MIAMIB, CEDAR])),
      m("Off Pensacola Beach, we", v(near(-87.13, 30.2, 0.6), date=SPRING, places=[PENSA])),
      stat("about thirty-three feet, using", "10 METRES", "= 33 ft: the line we measured to", OWN),
      m("Off Miami Beach, about", v(near(-80.12, 25.80, 0.5), date=SPRING, places=[MIAMIB])),
      m("Off Panama City Beach,", v(near(-85.80, 30.15, 0.5), date=SPRING, places=[PCB]))),
    P("P4",
      m(0, v(BB, highlight=[SHALLOW], places=[KEATON, STEIN, STMARKS, CEDAR])),
      stat("Off Keaton Beach, the", "~13 MILES", "Keaton Beach to 10 m of water", OWN),
      stat("Off Steinhatchee and St.", "~16 MILES", "Steinhatchee and St. Marks to 10 m of water", OWN),
      stat("Off Crystal River, at", "~22 MILES", "Crystal River to 10 m of water", OWN),
      chart("Even Clearwater and Naples,", "Distance from shore to 10 m of water", " mi",
            [["Panama City Bch", 0.3], ["Pensacola Bch", 0.9], ["Miami Beach", 1.2], ["Clearwater", 7.5], ["Naples", 7.5],
             ["Keaton Beach", 13], ["Cedar Key", 15.5], ["Steinhatchee", 16], ["Crystal River", 22]], OWN, highlight=6)),
    P("P5",
      sat(0, -83.10, 29.10, 0.45, "Off Cedar Key", date=CK_DAY),
      stat("Off Cedar Key, our", "~5.5 FT", "Depth 3 miles off Cedar Key", OWN),
      chart("Off Keaton Beach, about", "Depth of water 3 miles out", " ft",
            [["Cedar Key", 5.5], ["Keaton Beach", 8], ["Pensacola", 72], ["Miami", 272]], OWN, highlight=0,
            reveal=["Off Pensacola, about", "Off Miami, about"]),
      m("And at thirty miles", v(GULF_FL, highlight=[SHALLOW], places=[CEDAR])),
      stat("the Gulf is still", "~50 FT", "Depth 30 miles off Cedar Key", OWN, note="Pensacola at 30 miles: over 300 ft"),
      m("out from Pensacola, it", v(near(-87.13, 29.95, 0.8), date=SPRING, places=[PENSA]), text="Thirty miles off Pensacola: over 300 ft deep"),
      m("These numbers come from", v(GULF_FL, highlight=[SHALLOW], places=[CEDAR, PENSA])),
      photo("but the pattern is", PH_LANDSAT1, "Apalachee Bay from Landsat 1, 1970s (false colour)")),
    P("P6",
      photo(0, PH_CK2, "The Gulf at Cedar Key"),
      stat("put a number on", "1 : 5,000", "Slope of the Big Bend's marsh coast", USGS),
      stat("That works out to", "~1 FT PER MILE", "Depth gained heading out to sea", USGS),
      sat("It is so flat,", -83.35, 29.55, 0.6, "Deadman Bay to Horseshoe Beach"),
      doc("described as an \"incipient", "such a low gradient (1:5,000) that it has been referred to as an incipient epicontinental sea",
          USGS, highlight="incipient epicontinental sea", title="USGS, Big Bend coast"),
      photo("a place where the", PH_CK3, "Where the land runs into the Gulf, Cedar Key")),
    P("P7",
      sat(0, -83.62, 29.85, 0.35, "Keaton Beach"),
      stat("It has almost no", "NO BEACH", "Marsh, not sand, for most of the Big Bend", USGS),
      photo("describes the marsh coast", PH_BOARDWALK, "Salt marsh, St. Marks refuge"),
      sat("than the sandy coast", -82.83, 27.98, 0.25, "Sandy coast to the south: Clearwater Beach"),
      doc("and the region as", "Big Bend region ... is considered sediment-starved", "Wood & Hine 2003, via USGS",
          highlight="sediment-starved"),
      photo("The Gulf in front", PH_SUWANNEE_PALMS, "Near the lower Suwannee"),
      photo("its waves are weak,", PH_STM_1831, "Calm water at St. Marks"),
      sat("So instead of a", -83.98, 30.06, 0.25, "Marsh coast at the Aucilla"),
      photo("and the marsh runs", PH_MARSH_FIRE, "Marsh meets the bay, St. Marks refuge")),
    P("P8",
      m(0, v(BB, highlight=["file:shallow10.geojson@alt"], places=[STMARKS, CEDAR])),
      photo("It is carpeted with", PH_PACE, "The shallow shelf off the Big Bend from orbit, 28 Sep 2024"),
      stat("The Big Bend Seagrasses", "984,325 ACRES", "Big Bend Seagrasses Aquatic Preserve", FDEP, note="The largest aquatic preserve in Florida"),
      sat("the largest aquatic preserve", -83.75, 29.85, 1.6, "The preserve: Apalachee Bay to the Withlacoochee"),
      sat("and one of the", -83.60, 29.60, 0.5, "Seagrass off Taylor and Dixie counties"),
      photo("Which raises a question", PH_STM_LIGHT, "St. Marks lighthouse"),
      photo("is this coast a", PH_STM_HABS, "St. Marks lighthouse"),
      sat("or one of the", -83.40, 29.62, 0.2, "Steinhatchee River mouth"),
      ask=("Tell me in the", "A failure to develop, or a coast Florida never ruined?")),
    P("P9",
      photo(0, PH_CK4, "Shallow water off Cedar Key"),
      m("A port needs deep", v(BB, arrows=[ARR_SHIP_BB], places=[KEATON, STEIN])),
      sat("Ships can't sail to", -83.55, 29.72, 0.45, "Shallows off Keaton Beach and Steinhatchee"),
      photo("And there was a", PH_MARSH_FIRE2, "Salt marsh, St. Marks refuge"),
      sat("because it's underneath the", -84.25, 30.20, 0.25, "St. Marks River")),
)

chapter(
    P("P10",
      m(0, v(BB, highlight=[BBC], places=[TALLY, WAKULLA, AUCILLA])),
      photo("sits on limestone, covered", PH_LEON, "Leon Sinks, south of Tallahassee"),
      photo("Rainwater soaks straight through", PH_NATBRIDGE, "Natural Bridge, on the St. Marks River"),
      sat("Over thousands of years,", -84.20, 30.28, 0.3, "Sinkhole ponds south of Tallahassee"),
      stat("Geologists call this kind", "KARST", "Ground dissolved into caves, sinkholes and underground channels", "Florida Geological Survey (via UF/IFAS)"),
      photo("and the Big Bend", PH_STM_RIVER, "The St. Marks River at Newport")),
    P("P11",
      photo(0, PH_WAK1, "Wakulla Springs"),
      m("Wakulla Springs, south of", v(near(-84.30, 30.30, 0.6), date=SPRING, places=[WAKULLA, TALLY])),
      stat("pours out about six", "623 FT³/S", "Average flow of Wakulla Springs", NWF, note="Roughly 400 million gallons a day"),
      photo("roughly four hundred million", PH_WAK4, "Wakulla Springs"),
      sat("according to the Northwest", -84.302, 30.235, 0.09, "Wakulla Springs from orbit"),
      photo("Its vent opens about", PH_WAK2, "Wakulla Springs"),
      stat("about a hundred and", "180 FT", "Depth of the spring's vent below the surface", NWF),
      photo("And it's not unique.", PH_WAK3, "Wakulla Springs"),
      stat("Florida has thirty-one springs", "31", "First-magnitude springs in Florida", NWF)),
    P("P12",
      photo(0, PH_SUW_PAN, "Along the Suwannee River"),
      m("The Aucilla River, which", v(near(-83.97, 30.20, 0.55), date=SPRING, places=[AUCILLA])),
      stat("disappears underground and comes", "~30 TIMES", "The Aucilla goes underground and rises again", "State water management plan (SRWMD)"),
      sat("according to a state", -83.96, 30.22, 0.25, "The lower Aucilla"),
      sat("before it rises for", -83.99, 30.10, 0.12, "The Aucilla's last stretch")),
    P("P13",
      sat(0, -84.08, 30.06, 0.35, "Where the rivers meet the Gulf"),
      sat("The rivers fray out", -83.97, 30.07, 0.10, "Marsh islands at the Aucilla mouth"),
      sat("and the shallow sea", -83.80, 29.95, 0.6, "Apalachee Bay"),
      photo("Low land, soft wet", PH_HAMMOCK, "Salt marsh near Cedar Key"),
      sat("and a sea you", -84.15, 29.98, 0.4, "Off St. Marks")),
    P("P14",
      m(0, v(BB, highlight=["file:bigbend_coast.geojson@alt"], places=[STMARKS, TALLY]), step("were not about building", view={"lon": -84.05, "lat": 30.0, "span": 2.6})),
      stat("In 1931, an executive", "1931", "Executive Order 5740 creates the St. Marks refuge", FWS),
      photo("as winter habitat for", PH_STM_LIGHT_MARSH, "St. Marks National Wildlife Refuge"),
      stat("Today it covers more", "86,000+ ACRES", "St. Marks National Wildlife Refuge", FWS, note="About 43 miles of Gulf coast"),
      photo("But seventy years before", PH_CK_1861, "Cedar Keys, a chart of 1861"),
      sat("And for a while,", -83.04, 29.14, 0.20, "Cedar Key", date=CK_DAY)),
)

chapter(
    P("P15",
      m(0, v(NFL, highlight=["Florida@alt"], places=[CEDAR, FERN])),
      photo("In the middle of", PH_FL_1861, "Florida in a bird's-eye view, 1861"),
      m("this was the spot", v(USA_SE, highlight=["Florida@alt"], places=[CEDAR, FERN])),
      photo("Federal surveyors charted its", PH_CK_1852, "U.S. Coast Survey chart of Cedar Key, 1852"),
      photo("and in 1861, according", PH_FL_RR, "Florida Railroad survey: the Cedar Key extension"),
      m("the first train arrived", v(NFL, routes=[RR_FLA], places=[FERN, CEDAR])),
      photo("Cedar Key became the", PH_YULEE, "David Levy Yulee, who built the Florida Railroad")),
    P("P16",
      photo(0, PH_CK_1884B, "Cedar Key, 1884"),
      stat("According to the town's", "PENCIL CEDAR", "Faber and Eagle Pencil mills", "Cedar Key local history"),
      photo("built mills on the", PH_MOUND, "Cedar Key in an old stereoscopic view"),
      sat("into pencil slats and", -83.05, 29.125, 0.08, "Atsena Otie, site of the first town", date=CK_DAY),
      photo("Here is Cedar Key", PH_CK_1884, "Cedar Key in 1884, a bird's-eye view"),
      photo("wharves, warehouses, a railroad", PH_SANBORN, "Cedar Key, Sanborn fire-insurance map, 1909")),
    P("P17",
      m(0, v(CENTRAL, places=[CEDAR, TAMPA])),
      stat("In 1883, the businessman", "1883", "Henry Plant takes over the South Florida Railroad", UFLIB),
      m("and pushed it all", v(CENTRAL, routes=[RR_PLANT], places=[CEDAR, TAMPA, ORLANDO]), step("with full service from", view={"lon": -82.0, "lat": 28.3, "span": 2.6})),
      photo("Tampa had what Cedar", PH_TAMPA_HOTEL, "Plant's Tampa Bay Hotel (now a museum)"),
      sat("a big, sheltered bay.", -82.55, 27.78, 0.9, "Tampa Bay"),
      photo("Census counts on record", PH_TAMPA_HOTEL3, "Plant's hotel in Tampa"),
      chart("Tampa growing from seven", "Tampa's population", "", [["1880", 720], ["1890", 5532]], "U.S. census counts", highlight=1,
            reveal=["more than five thousand"])),
    P("P18",
      photo(0, PH_1896_MAP, "Weather map, 29 September 1896"),
      m("a hurricane came ashore", v(BB, places=[L_1896, YANKEE])),
      stat("with winds of around", "~125 MPH", "Winds at landfall, 1896", NWS),
      stat("it pushed the water", "10.5 FT", "Above sea level at Cedar Key, 1896", NWS, note="About 12.5 ft at Yankeetown"),
      sat("and around twelve and", -82.72, 29.03, 0.3, "Yankeetown"),
      photo("About a hundred people", PH_1896_MAP2, "Weather map, 30 September 1896"),
      stat("most of them drowned", "~100", "Deaths, mostly from the surge", NWS)),
    P("P19",
      photo(0, PH_CK_AIR_OLD, "Cedar Key from the air (U.S. survey photograph)"),
      photo("and that Faber's mill", PH_SANBORN20, "Cedar Key, Sanborn fire-insurance map, 1920"),
      sat("The town rebuilt on", -83.04, 29.135, 0.10, "Cedar Key and Atsena Otie today", date=CK_DAY),
      photo("but it never became", PH_ATSENA, "Atsena Otie Key, where the old town stood"),
      photo("If you like stories", PH_CK_MUSEUM, "Cedar Key Historical Museum"),
      photo("subscribing is how you'll", PH_CK_1884B, "Cedar Key, 1884"),
      m("Because Cedar Key's collapse", v(FL, highlight=[FLR, BBC], places=[CEDAR, TAMPA]), step("Over the next century,", view={"lon": -82.9, "lat": 28.9, "span": 4.4}))),
)

chapter(
    P("P20",
      m(0, v(NFL, highlight=[BBC], places=[JAX, CEDAR, YANKEE])),
      photo("The Cross Florida Barge", PH_CANAL_W, "The barge canal west of SR 19"),
      m("so ships could cross", v(FL, arrows=[ARR_SHIP], places=[MIAMI, JAX])),
      m("Its western end was", v(NFL, routes=[CANAL], places=[YANKEE, CEDAR]))),
    P("P21",
      stat(0, "1930s", "A New Deal start; stalled after about three years", FLMNH),
      stat("In 1964 it started", "1964", "Work starts again", FLMNH),
      photo("Parts of it were", PH_CANAL_E, "The finished cut of the barge canal"),
      stat("Then, in 1971, President", "1971", "Construction halted for good", FLMNH),
      photo("citing the damage it", PH_CANAL_E1, "The barge canal today"),
      stat("By then the canal", "28%", "Of the canal complete when it was stopped", FLMNH),
      stat("and around seventy-five million", "$75 MILLION", "Spent by 1971", FLMNH),
      photo("according to the Florida", PH_MARSHALL, "Along the old canal route")),
    P("P22",
      m(0, v(near(-82.76, 29.00, 0.22), compare={"before": "1985-05-01/1985-09-30", "after": "2025-05-01/2025-09-30", "source": "landsat",
                                                                    "seconds": 2.4, "until": "This is where the", "label_before": "1985", "label_after": "2025"}),
        step("This is where the", view=near(-82.76, 29.00, 0.22)), text="Barge canal, Gulf end"),
      sat("Look how far the", -82.80, 28.99, 0.32, "The dredged channel"),
      sat("marked by a line", -82.86, 28.97, 0.45, "The channel and its spoil islands"),
      sat("before the water gets", -82.98, 28.94, 0.7, "The Gulf off the canal"),
      photo("The rest of the", PH_GREENWAY_I75, "The Cross Florida Greenway crossing I-75"),
      photo("Today it's the Marjorie", PH_GREENWAY, "Cross Florida Greenway"),
      stat("more than seventy thousand", "110 MILES", "Of greenway, more than 70,000 acres", FLMNH)),
    P("P23",
      m(0, v(BB, places=[PERRY, FOLEY, KEATON])),
      sat("Near Perry, the Foley", -83.53, 30.07, 0.10, "Foley pulp mill, near Perry"),
      photo("the biggest kind of", PH_FENHOLLOWAY, "The Fenholloway River, east of Perry"),
      stat("On the eighteenth of", "18 SEP 2023", "Georgia-Pacific: the Foley mill will close", GP),
      stat("with about five hundred", "~525", "Jobs at the mill", GP),
      stat("University of Florida economists", "1,879", "Potential jobs lost statewide", IFAS),
      sat("at up to one", -83.58, 30.11, 0.2, "Perry")),
    P("P24",
      m(0, v(BB, places=[FOLEY, L_IDALIA, PERRY])),
      photo("So which was the", PH_PERRY_LINES, "Clearing downed power lines outside Perry after Idalia"),
      photo("Have a think about", PH_STEIN_IDALIA2, "Steinhatchee after Idalia, 30 August 2023"),
      sat("Because the storms were", -83.50, 29.70, 0.8, "Keaton Beach to Horseshoe Beach"),
      ask=("So which was the", "Which hit harder: the storms or the jobs leaving?")),
)

chapter(
    P("P25",
      m(0, v(GULF_FL, highlight=[SHALLOW], places=[CEDAR, KEATON])),
      doc("caused by a storm", "Storm surge is the rise in seawater level caused solely by a storm.", NOS,
          highlight="caused solely by a storm"),
      photo("NOAA lists what decides", PH_IDALIA_MODIS, "Hurricane Idalia, 30 August 2023 (MODIS)"),
      m("its strength, its size,", v(USA_SE, date="2024-09-26"), text="Helene approaching, 26 September 2024 (MODIS)"),
      m("and the shape of", v({"lon": -84.2, "lat": 29.2, "span": 2.6}, highlight=[SHALLOW], places=[CEDAR])),
      m("On the Big Bend,", v(BB, highlight=[SHALLOW], arrows=[ARR_SURGE], places=[KEATON, STEIN]), step("to push before it", view={"lon": -83.75, "lat": 29.75, "span": 2.6}))),
    P("P26",
      photo(0, PH_STEIN_IDALIA3, "Steinhatchee, 30 August 2023"),
      m("Hurricane Idalia came ashore", v(BB, places=[L_IDALIA, STEIN, CEDAR])),
      stat("with winds of about", "~115 MPH", "Idalia at landfall (category 3)", NHC_I),
      stat("The National Hurricane Center", "3RD", "Strongest hurricane to hit the Big Bend", NHC_I, note="After the 1896 storm and Easy (1950)"),
      photo("behind only the Cedar", PH_1896_MAP, "The 1896 hurricane on the weather map"),
      photo("The surge flooded land", PH_STEIN_IDALIA1, "Steinhatchee after Idalia, 30 August 2023"),
      stat("eight to twelve feet", "8-12 FT", "Surge flooding, Keaton Beach to Steinhatchee", NHC_I),
      stat("and the Cedar Key", "6.89 FT", "Cedar Key gauge during Idalia: a record at the time", NHC_I),
      photo("above the high-tide line,", PH_CK1, "Cedar Key"),
      stat("Idalia caused an estimated", "$3.6 BILLION", "Idalia's damage in the United States", NHC_I)),
    P("P27",
      m(0, v(BB, places=[L_IDALIA, L_DEBBY, STEIN])),
      photo("a category one storm,", PH_STEIN_RIVER, "The Steinhatchee River"),
      stat("And seven weeks after", "7 WEEKS", "From Debby to Helene", NHC_H)),
    P("P28",
      photo(0, PH_HELENE_ISS, "Helene over the Gulf, 25 September 2024 (ISS)"),
      m("Six hours before landfall,", v(GULF_FL, places=[L_HELENE, TAMPA])),
      stat("winds of around a", "~140 MPH", "Helene at its peak, 6 hours before landfall", NHC_H),
      m("It came ashore about", v(BB, places=[L_HELENE, PERRY, KEATON, L_IDALIA, L_DEBBY])),
      stat("The Hurricane Center calls", "STRONGEST", "Big Bend landfall since records began around 1900", NHC_H),
      sat("since reliable records began", -83.62, 29.85, 0.3, "Keaton Beach after Helene, 2024", date=POST_HELENE),
      stat("the surge put twelve", "12-16 FT", "Surge flooding, Keaton Beach to Steinhatchee", NHC_H),
      sat("South of there, through", -83.25, 29.40, 0.45, "Horseshoe Beach to Cedar Key")),
    P("P29",
      m(0, v(near(-83.595, 29.82, 0.10), compare=CMP_KEATON), step("and this is the same coast", view=near(-83.595, 29.82, 0.10)),
        text="Keaton Beach"),
      m("Further south, at Horseshoe", v(near(-83.29, 29.44, 0.10), compare=CMP_HORSE), text="Horseshoe Beach"),
      photo("On the ground, the", PH_KEATON_NG, "Air National Guard clearing roads, Keaton Beach, 27 September 2024"),
      photo("was clearing the roads", PH_KEATON_STREET, "Keaton Beach, 3 October 2024")),
    P("P30",
      stat(0, "14", "Deaths in Helene's storm surge, all in Florida", NHC_H),
      stat("The storm went on", "175+", "Direct deaths across the United States", NHC_H),
      m("across the southeastern United", v(USA_SE, date="2024-09-27"), text="Helene over the Southeast, 27 September 2024 (MODIS)"),
      sat("Media reports cited by", -83.035, 29.137, 0.09, "Cedar Key after Helene, 2024", date=POST_HELENE),
      stat("about a quarter of", "~25%", "Of Cedar Key's homes destroyed (media reports cited by NHC)", NHC_H),
      m("Three hurricanes had come", v(BB, places=[L_IDALIA, L_DEBBY, L_HELENE]))),
    P("P31",
      m(0, v(near(-83.04, 29.13, 0.25), date=CK_DAY, places=[GAUGE_PT])),
      chart("Here they are.", "Highest water of the year, Cedar Key", " ft",
            [["Typical year", 1.9], ["1966", 4.0], ["1972", 4.2], ["1993", 5.1], ["1996", 5.1], ["2016", 6.0],
             ["2023 Idalia", 6.8], ["2024 Helene", 9.3]], GAUGE, highlight=7,
            reveal=["A few storms in", "the 1990s and 2016", "Then Idalia, at nearly", "And Helene, at nine"]),
      stat("The two highest water", "2023 + 2024", "The two highest years in 101 years of records", GAUGE),
      photo("thirteen months apart, in", PH_CK2, "Cedar Key")),
    P("P32",
      photo(0, PH_PACE, "The Gulf off the Big Bend, 28 September 2024 (NASA PACE)"),
      m("Along the Big Bend,", v({"lon": -83.6, "lat": 29.5, "span": 2.6}, date="2024-09-28"), text="The Big Bend, 28 September 2024 (MODIS)"),
      sat("The storm's winds and", -83.70, 29.60, 1.2, "The Big Bend shelf, calm"),
      m("That day, the shelf", v(GULF_FL, highlight=[SHALLOW], places=[CEDAR]))),
)

chapter(
    P("P33",
      m(0, v(BB, highlight=[BBC], places=[CEDAR, STMARKS, PERRY])),
      sat("A seafloor too shallow", -83.06, 29.11, 0.18, "Cedar Key at low tide", date=CK_DAY),
      photo("Ground made of soft,", PH_LEON, "Leon Sinks"),
      photo("A boomtown that lost", PH_CK_1852, "Cedar Key, 1852"),
      photo("Plans like the barge", PH_GREENWAY_I75, "Cross Florida Greenway over I-75"),
      photo("And a shelf that", PH_STEIN_IDALIA3, "Steinhatchee, August 2023")),
    P("P34",
      photo(0, PH_STEIN_BRIDGE, "Steinhatchee"),
      stat("Cedar Key grew from", "685 → 736", "People in Cedar Key, 2020 to 2024", CENSUS),
      photo("to seven hundred and", PH_CK_MUSEUM, "Cedar Key"),
      stat("Levy County grew by", "+4,852", "Levy County, 2020 to 2024", CENSUS, note="Wakulla County: +3,349"),
      photo("Much of the coast", PH_STM_HABS, "St. Marks lighthouse"),
      sat("and the same shallow", -83.50, 29.55, 0.7, "The Big Bend seagrass shelf")),
    P("P35",
      photo(0, PH_STEIN_RIVER_W, "The Steinhatchee River"),
      m("the part of Florida", v(FL, highlight=[BBC], places=[TAMPA, MIAMI, CEDAR])),
      photo("So here's the question", PH_STEIN_MARKER, "Deadman Bay, Steinhatchee"),
      m("Should Florida keep the", v(GULF_FL, layer="night", places=[CEDAR, TAMPA])),
      ask=("Should Florida keep the", "Keep the Big Bend empty, or build on it?")),
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
    "title": "Why Almost Nobody Lives on Florida's Big Bend Coast",
    "voice": "am_michael",
    "voice_speed": 1.15,
    "music": "procedural",
    "map_style": "satellite",
    "look": "none",
    "photo_upscale": True,
    "sources": ["episodes/florida-big-bend/research.md and factcheck.md", "Contains modified Copernicus Sentinel data 2026",
                "Landsat imagery courtesy of the U.S. Geological Survey", "Seafloor depth: NOAA NCEI ETOPO 2022"],
    "thumbnail": {"text": "NO BEACH NO TOWNS"},
    "chapters": chapters,
    "youtube": {
        "title": "Why Almost Nobody Lives on Florida's Big Bend Coast",
        "description": "Florida has 23.4 million people and a coastline lined with beach towns, yet the long curve where the peninsula meets the Panhandle is almost empty. We measured the seafloor off the Big Bend and compared it with Pensacola and Miami, then follow the karst ground full of springs and sinking rivers, Cedar Key's railroad boom and its fall, the Cross Florida Barge Canal stopped at 28 percent, the Foley mill closure, and the three hurricanes in thirteen months that sent the Cedar Key tide gauge to its highest level since 1914.",
        "tags": ["Florida", "Big Bend", "Florida Big Bend", "Cedar Key", "Steinhatchee", "Keaton Beach", "Hurricane Helene", "Hurricane Idalia",
                 "storm surge", "continental shelf", "Cross Florida Barge Canal", "karst", "Wakulla Springs", "geography", "satellite images"],
        "pinned_comment": "Should Florida keep the Big Bend mostly empty, or try once more to build on it?",
    },
}
out = HERE / "script.json"
out.write_text(json.dumps(script, ensure_ascii=False, indent=1) + chr(10), encoding="utf-8")
words = sum(len(p["text"].split()) for c in chapters for p in c["paragraphs"])
shots = [s for c in chapters for p in c["paragraphs"] for s in p["shots"]]
kinds = {k: sum(1 for s in shots if s["type"] == k) for k in ("map", "photo", "stat", "document", "chart")}
print(f"{words} words, {len(chapters)} chapters, {len(shots)} shots {kinds}")
