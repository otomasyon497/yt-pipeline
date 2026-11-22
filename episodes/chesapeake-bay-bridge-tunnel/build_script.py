"""Builds script.json for chesapeake-bay-bridge-tunnel.  python build_script.py

Same production logic as episodes/permian-basin (hand-placed shots, a photo or map frame at most twice, 60 s apart).
The narration lives in drafts/narration.md; every sentence comes from research.md. Photos and satellite tests:
visuals.md. Painted crater outline (approximate circle): geo/make_regions.py.
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


CLEAR_DAY = "2025-10-31"  # Sentinel-2 single day clear over every test view (scratch cbsat.py 2026-11-22)


def v(view, at=None, **kw):
    d = {"view": fresh(view), **kw}
    if at is not None:
        d["at"] = at
    return d


SAT_MIN_SPAN = 0.08
DRY = "2025-10-01/2025-11-30"  # scratch cbsat.py: 10-31 (bay), 10-21 (Norfolk), 10-06 (Fisherman), 10-16 (Kiptopeke)
SPRING = "2025-04-01/2025-05-31"


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
USA = {"lon": -80.0, "lat": 36.5, "span": 22.0}
EAST = {"lon": -76.8, "lat": 37.6, "span": 6.0}   # Virginia and the whole bay
BAY = {"lon": -76.3, "lat": 37.6, "span": 3.4}    # lower bay, crater, Eastern Shore, Norfolk
CRATER = "file:crater_outer.geojson@red"
CRATER_IN = "file:crater_inner.geojson@accent"
VA = "Virginia@alt"

# ------------------------------------------------------------------ sources (research.md)
USGS15 = "USGS Fact Sheet 2015-3071"
USGS23 = "U.S. Geological Survey"
NPS = "National Park Service"
NOAA = "NOAA Ocean Service"
NOAAT = "NOAA tide gauges (sea level trends, 1927-2025)"
NOAA_CC = "NOAA tide gauge, Chesapeake Channel, 1975-2025"
OWNNOAA = "Own ranking of NOAA tide gauge trends"
CBBT = "Chesapeake Bay Bridge-Tunnel District"
VP = "Virginia Places (virginiaplaces.org)"
ASCE = "American Society of Civil Engineers"
NAVFAC = "U.S. Navy (NAVFAC)"
HRNM = "Hampton Roads Naval Museum"
SANFORD = "Sanford et al. 2013, Nature (USGS)"
BEKAERT = "Bekaert et al. 2017, Scientific Reports"
USGSVA = "USGS, land subsidence in coastal Virginia"

# ------------------------------------------------------------------ photos (Commons, licence checked: visuals.md)
PAN = "File:Chesapeake Bay Bridge–Tunnel connects Virginia Beach Hampton Roads to the Delmarva Peninsula - panoramio{}.jpg"
PH_BEACH = "File:Chesapeake Bay Bridge-Tunnel, Virginia Beach Area.jpg"
PH_ROAD = PAN.format("")
PH_ROAD1 = PAN.format(" (1)")
PH_ROAD2 = PAN.format(" (2)")
PH_ROAD3 = PAN.format(" (3)")
PH_TRES9 = PAN.format(" (9)")
PH_ROAD10 = PAN.format(" (10)")
PH_TRES11 = PAN.format(" (11)")
PH_TRES12 = PAN.format(" (12)")
PH_TRES13 = PAN.format(" (13)")
PH_ROAD14 = PAN.format(" (14)")
PH_ROAD15 = PAN.format(" (15)")
PH_ROAD16 = PAN.format(" (16)")
PH_ROAD17 = PAN.format(" (17)")
PH_ROAD4 = PAN.format(" (4)")
PH_PORTAL5 = PAN.format(" (5)")
PH_ISLAND6 = PAN.format(" (6)")
PH_PORTAL7 = PAN.format(" (7)")
PH_PORTAL8 = PAN.format(" (8)")
PH_NIGHT_ISLAND = "File:Island 1 and Western Section of Bridge - panoramio.jpg"
PH_PIER = "File:FishingPierontheChesapeakeBayBridgeTunnel.jpg"
PH_BRUN1 = "File:Virginia Brunnel01.jpg"
PH_BRUN2 = "File:Virginia Brunnel02.jpg"
PH_BRUN4 = "File:Virginia Brunnel04.jpg"
PH_BRUN5 = "File:Virginia Brunnel05.jpg"
PH_BRUN6 = "File:Virginia Brunnel06.jpg"
PH_CONCRETE_SHIPS = "File:Aerial of concrete ships in Bay (12680358583).jpg"
PH_HRBT_IKE = "File:USS Dwight D. Eisenhower departs Norfolk, crossing over the - Hampton Roads Bridge Tunnel 130221-N-GC639-125.jpg"
PH_YANCEY = "File:USS Yancey (AKA-93) underway c1952.jpg"
PH_AMPHIB_1964 = "File:US Navy Amphibious Group underway in April 1964.jpg"
PH_FERRY = "File:The S. S. Princess Anne Ferry Boat between Kiptopeke Beach and Norfolk, Virginia (8618851013).jpg"
PH_CRATER_MAP = "File:Boundaries of the Chesapeake Bay impact crater.png"
PH_BAY_LANDSAT = "File:Chesapeakelandsat.jpeg"
PH_BEDIASITE = "File:Bediasite (35 Ma, Late Eocene; southeastern Texas) 3.jpg"
PH_FLATTOPS = "File:9 Flattops at Norfolk naval base, December 20, 2012.jpg"
PH_NAVSTA_AIR = "File:US Navy 110707-N-XZ912-104 An aerial view of Norfolk Naval Station, the largest naval base in the world.jpg"
PH_KITE = "File:Tight and Light - Kite Over The Chesapeake Bay Bridge Tunnel.jpg"

# ------------------------------------------------------------------ places
NORFOLK = place("Norfolk", -76.29, 36.85, "Norfolk", "city")
VBEACH = place("Virginia Beach", -76.00, 36.85, "Virginia Beach", "city")
CAPE_CHARLES = place("Cape Charles", -76.01, 37.265, "Cape Charles", "city")
RICHMOND = place("Richmond", -77.44, 37.54, "Richmond", "city")
BALTIMORE = place("Baltimore", -76.61, 39.29, "Baltimore", "city")
WASHINGTON = place("Washington", -77.04, 38.90, "Washington, D.C.", "city")
NAVSTA = place("Naval Station Norfolk", -76.31, 36.945, "Naval Station Norfolk", icon="warning")
SEWELLS = place("Sewells Point gauge", -76.33, 36.947, "Sewells Point tide gauge (1927)", icon="water")
CC_GAUGE = place("Chesapeake Channel gauge", -76.083, 37.033, "Bridge-tunnel tide gauge (1975)", icon="water")
THIMBLE = place("Thimble Shoal Channel", -76.10, 36.977, "Thimble Shoal Channel", icon="water")
CHESCH = place("Chesapeake Channel", -76.08, 37.04, "Chesapeake Channel", icon="water")
KIPTOPEKE = place("Kiptopeke", -75.99, 37.165, "Kiptopeke ferry landing", "site")
LITTLE_CREEK = place("Little Creek", -76.18, 36.92, "Little Creek ferry landing", "site")
HRBT = place("HRBT", -76.30, 36.99, "Hampton Roads Bridge-Tunnel (1957)", "site")
ORANGE = place("Orange, Texas", -93.74, 30.09, "Orange, Texas", "city")
CRATER_C = place("Crater centre", -76.017, 37.283, "Buried crater (approximate)", icon="warning")
SUSQ = place("Susquehanna", -76.09, 39.55, "Susquehanna River", icon="water")

THIMBLE_V = (-76.105, 36.975)
CHES_V = (-76.08, 37.04)

PH_CARRIER = "File:US Navy 031109-N-6278K-002 The USS George Washington (CVN 73), sails past the Chesapeake Bay Bridge Tunnel on the way to sea, as it prepares for the Composite Training Unit Exercise (COMPTUEX) in the Atlantic Ocean.jpg"
PH_CARRIER2 = "File:US Navy 040120-N-6278K-001 USS George Washington (CVN 73) sails past the Chesapeake Bay Bridge tunnel into the Atlantic Ocean to start her deployment.jpg"
PH_CC_1853 = "File:1853 U.S.C.S. Map of Cape Charles and Vicinity, Virginia - Geographicus - CapeCharles-uscs-1853.jpg"
PH_FISH1 = "File:Fisherman Island National Wildlife Refuge, VA. Credit- USFWS (11804450384).jpg"
PH_FISH2 = "File:Fisherman Island National Wildlife Refuge, VA. Credit- USFWS (11804792806).jpg"
PH_MDBRIDGE1 = "File:Aerial view of the Chesapeake Bay Bridge, connecting Annapolis with Maryland's Eastern Shore LCCN2011635445.tif"
PH_MDBRIDGE2 = "File:Aerial view of the Chesapeake Bay Bridge, officially the William Preston Lane, Jr. Memorial Bridge, connecting the Maryland capital city, Annapolis, with Maryland's Eastern Shore in Queen Anne County LCCN2011631712.tif"
PH_TANGIER = "File:Tangier Island flooding.jpg"
PH_HENRY_NEW = "File:New Cape Henry Lighthouse (28482794045).jpg"
PH_HENRY_OLD = "File:Old Cape Henry Lighthouse (27866899213).jpg"
PH_IKE_DEPART = "File:CVN 69 departs Naval Station Norfolk with the USS Dwight D. Eisenhower Carrier Strike Group (CSG). 160601-N-XG464-054.jpg"
PH_KIP_AERIAL = "File:Aerial (12680379975).jpg"
PH_SUSQ_PAINT = "File:A Ferry Scene on the Susquehanna at Wright's Ferry, near Havre de Grace MET DT1813.jpg"

chapters = []
heads = iter(HEADS)


def chapter(*paras):
    title, mood = next(heads)
    chapters.append({"title": title, "mood": mood, "paragraphs": list(paras)})


X0, Y0 = -76.03, 37.02  # the whole crossing
TX, TY = THIMBLE_V
CX, CY = CHES_V

chapter(
    P("P0",
      photo(0, PH_BEACH, "Virginia Beach and the Chesapeake Bay Bridge-Tunnel"),
      sat(8, -76.115, 36.93, 0.08, "The south end, Virginia Beach"),
      photo("Low concrete, a few", PH_ROAD14, "The Chesapeake Bay Bridge-Tunnel"),
      photo("After a few miles", PH_TRES12, "Miles out in the bay"),
      sat("Ahead, the highway runs", TX, TY, 0.09, "Two islands at Thimble Shoal Channel"),
      sat("and sand in the", TX + 0.005, TY - 0.01, 0.08, "An island of rock and sand"),
      photo("And then the road", PH_PORTAL7, "Thimble Shoal Channel Tunnel")),
    P("P1",
      sat(0, X0, Y0, 0.34, "The Chesapeake Bay Bridge-Tunnel from orbit"),
      stat("Seventeen point six miles from", "17.6 MILES", "Shore to shore across the mouth of the bay", CBBT),
      m("across the mouth of", v(EAST, places=[NORFOLK, CAPE_CHARLES, BALTIMORE])),
      photo("Twice on the way", PH_PORTAL5, "Into the tunnel"),
      sat(36, -76.07, 37.06, 0.08, "Chesapeake Channel"),
      photo("a cargo ship or", PH_CARRIER, "USS George Washington passing the crossing, 2003 (U.S. Navy)")),
    P("P2",
      photo(0, PH_KITE, "The crossing from a kite, 2010"),
      photo(13, PH_TRES13, "Why build it like this?"),
      sat("Why is there seventeen", -76.10, 37.10, 1.2, "The mouth of the Chesapeake Bay"),
      sat("with two deep channels", X0 - 0.02, Y0 - 0.01, 0.5, "Two shipping channels"),
      photo("Why would anyone pay", PH_PORTAL8, "Where the road leaves the surface"),
      sat(47, -76.12, 36.96, 0.09, "Under the shipping lane"),
      sat("The answers go back", -75.98, 37.22, 1.3, "Under the mouth of the bay"),
      photo("and the largest naval", PH_FLATTOPS, "Carriers at Naval Station Norfolk, 2012 (U.S. Navy)"),
      photo("And there is one", PH_NIGHT_ISLAND, "Island 1 at night"),
      sat("There is a tide", -76.083, 37.033, 0.08, "The bridge-tunnel's tide gauge, Chesapeake Channel"),
      stat("Since nineteen seventy-five, the", "~1 FOOT", "Sea level rise at the bridge-tunnel's gauge since 1975", NOAA_CC)),
)

chapter(
    P("P3",
      sat(0, -76.30, 37.25, 1.5, "The lower Chesapeake today"),
      m(10, v(EAST, places=[RICHMOND, WASHINGTON, BALTIMORE])),
      m("and everything east of", v(EAST, places=[RICHMOND]), step(30, view=near(-76.6, 37.4, 3.0))),
      stat("Then, according to the", "35 MILLION YEARS", "Since an asteroid or comet hit the lower bay", USGS15),
      sat(46, -75.90, 37.30, 2.4, "Where it came down"),
      m("right about where the", v(BAY, highlight=[CRATER], places=[NORFOLK, CAPE_CHARLES]))),
    P("P4",
      photo(0, PH_CRATER_MAP, "The buried Chesapeake Bay impact crater"),
      stat(6, "TOP 20", "Among the largest known impact structures on Earth", USGS15),
      photo("Glassy drops of melted", PH_BEDIASITE, "Bediasite: impact glass found in Texas"),
      m("Tsunamis spread across most", v(USA, places=[CRATER_C])),
      sat("over millions of years,", -76.00, 37.25, 0.8, "The crater filled in", date="2025-10-16"),
      stat("Today the crater lies", "1,000-1,500 FT", "Of sediment and rock now cover the crater", USGS23),
      sat("You cannot see it", -76.017, 37.283, 0.25, "Above the crater today: Cape Charles", date="2025-10-16"),
      photo("But it never really", PH_CC_1853, "Cape Charles, 1853 survey chart")),
    P("P5",
      m(0, v(BAY, highlight=[CRATER, CRATER_IN])),
      sat("kept settling for millions", -76.10, 37.35, 1.1, "Over the buried crater", date="2025-10-16"),
      m("little lower than the", v(BAY, highlight=[CRATER], places=[NORFOLK, RICHMOND])),
      stat("The National Park Service", "THE LOW SPOT", "\"Helped determine the location of the Chesapeake Bay\"", NPS),
      sat(45, -76.25, 37.45, 1.4, "Where the bay would form", date="2025-10-16"),
      m("of years later. The", v(EAST, highlight=[CRATER], places=[BALTIMORE])),
      sat("The rock from space", -76.6, 37.45, 1.8, "Rivers of the lower bay"),
      sat("left a low spot,", -76.45, 37.20, 0.9, "The James and the York bend toward the bay")),
    P("P6",
      photo(0, PH_HENRY_OLD, "Cape Henry, the south cape of the bay"),
      stat("About twenty thousand years", "~20,000 YEARS AGO", "Height of the last ice age", NPS),
      m("so much water was", v(EAST, places=[SUSQ, BALTIMORE])),
      sat("The shore lay far", -75.85, 37.05, 1.4, "Today's shore; the ice-age coast lay far offshore"),
      m("Where the bay is", v(EAST, places=[SUSQ, WASHINGTON, RICHMOND]), step("The Susquehanna River ran", view=near(-76.3, 38.3, 3.0))),
      photo("joined by the Potomac,", PH_SUSQ_PAINT, "The Susquehanna near Havre de Grace (19th-century painting)"),
      sat("and flowed out across", -76.10, 37.10, 1.6, "Where the old river left the land")),
    P("P7",
      photo(0, PH_HENRY_NEW, "Cape Henry"),
      stat("By about ten thousand", "~10,000 YEARS AGO", "The sea floods the lower river valley", NPS),
      m("The water kept climbing", v(EAST, places=[SUSQ, BALTIMORE, WASHINGTON])),
      stat("three thousand years ago", "~3,000 YEARS AGO", "The bay reaches roughly its present shape", NPS),
      photo("A drowned river system,", PH_BAY_LANDSAT, "The Chesapeake Bay, the largest estuary in the U.S.")),
    P("P8",
      sat(0, -76.08, 37.12, 0.9, "The gap at the mouth of the bay"),
      sat("The Geological Survey notes", -76.20, 37.40, 0.9, "The bay's deep channel", date="2025-10-16"),
      photo("Big ships need deep", PH_CARRIER2, "USS George Washington heading for sea, 2004 (U.S. Navy)"),
      sat("The road had to", X0, Y0 + 0.01, 0.28, "Seventeen miles of water"),
      sat("and it had to", TX - 0.01, TY + 0.005, 0.14, "A deep path for ships"),
      photo("Which raises the next", PH_ROAD16, "The crossing today")),
)

chapter(
    P("P9",
      m(0, v(EAST, places=[CAPE_CHARLES, NORFOLK, BALTIMORE])),
      sat("Its southern tip is", -75.95, 37.30, 0.9, "The Eastern Shore of Virginia"),
      sat("two counties of farms,", -75.99, 37.19, 0.12, "Farms on the Eastern Shore"),
      photo("To reach the rest", PH_ROAD1, "The road south"),
      m("Drive north and all", v(EAST, places=[CAPE_CHARLES, NORFOLK, BALTIMORE, WASHINGTON])),
      photo("Or take a boat.", PH_FERRY, "Princess Anne, one of the bay ferries (postcard)")),
    P("P10",
      sat(0, -76.10, 37.03, 0.55, "The ferry route across the mouth"),
      sat("late years of the", -76.18, 36.92, 0.12, "Little Creek, the southern ferry landing"),
      sat("to Kiptopeke, near Cape", -75.99, 37.165, 0.12, "Kiptopeke, the northern landing"),
      stat("A ferry could carry", "90 MINUTES", "For the 18-mile ferry crossing", VP, note="Up to about 60 cars a trip"),
      photo("In fog or a", PH_CONCRETE_SHIPS, "Old concrete ships sunk as a breakwater at Kiptopeke")),
    P("P11",
      stat(0, "1954", "Virginia creates a commission to take over the ferries", "Encyclopedia Virginia"),
      photo(13, PH_KIP_AERIAL, "Kiptopeke today"),
      sat("Could the mouth of", -76.10, 37.06, 0.7, "The mouth of the bay"),
      m("A few miles to", v(BAY, places=[HRBT, NORFOLK, NAVSTA])),
      sat("In nineteen fifty-seven, the", -76.30, 36.99, 0.10, "Hampton Roads Bridge-Tunnel (1957)"),
      sat("three and a half", -76.31, 37.00, 0.18, "Trestles, then a tunnel"),
      photo("It proved a road", PH_HRBT_IKE, "A carrier passing over the Hampton Roads tunnel, 2013 (U.S. Navy)"),
      sat("The Chesapeake crossing would", X0, Y0, 0.40, "Two channels to cross")),
    P("P12",
      photo(0, PH_ROAD10, "The open bay"),
      photo("Engineers built tall bridges", PH_MDBRIDGE1, "Maryland's Chesapeake Bay Bridge, opened 1952 (LoC)"),
      sat("Here, though, someone else", -76.31, 36.96, 0.22, "Naval Station Norfolk")),
)

chapter(
    P("P13",
      m(0, v(BAY, places=[NAVSTA, NORFOLK, HRBT])),
      sat(13, -76.32, 36.98, 0.35, "Hampton Roads"),
      sat("And on its southern", -76.31, 36.945, 0.10, "Naval Station Norfolk"),
      sat("nineteen-oh-seven world's fair, the", -76.305, 36.955, 0.08, "The piers of the naval base"),
      photo("It grew into Naval", PH_NAVSTA_AIR, "Naval Station Norfolk, 2011 (U.S. Navy)"),
      photo("home port of aircraft", PH_FLATTOPS, "Nine carriers at Norfolk, December 2012 (U.S. Navy)")),
    P("P14",
      sat(0, -76.20, 36.98, 0.45, "From the base to the open sea"),
      sat("one deep, dredged path,", TX, TY, 0.10, "Thimble Shoal Channel"),
      photo("In the middle of", PH_AMPHIB_1964, "Navy ships off Virginia, April 1964"),
      photo("According to histories of", PH_CARRIER, "The channel the Navy needed open"),
      sat("If a bridge collapsed,", -76.15, 36.98, 0.30, "One channel between the fleet and the Atlantic"),
      m("storm or through sabotage,", v(BAY, places=[NAVSTA, THIMBLE]))),
    P("P15",
      sat(0, CX, CY, 0.10, "Chesapeake Channel"),
      m("ships up the bay", v(EAST, places=[BALTIMORE, CAPE_CHARLES, NORFOLK])),
      photo("So the plan became", PH_TRES11, "Long, low trestles"),
      photo("Two higher bridges over", PH_ROAD17, "A high bridge over a smaller channel"),
      sat("And at the two", X0, Y0 - 0.01, 0.26, "Two tunnels, four islands"),
      photo("where the big ships", PH_PORTAL5, "The road goes under")),
    P("P16",
      photo(0, PH_ISLAND6, "An island at the mouth of a tunnel"),
      sat("There is no land", -76.09, 37.05, 0.08, "Islands built in open water"),
      photo("So before anyone could", PH_BRUN4, "The fishing pier on island 1, 2004"),
      sat("Four islands, in the", TX + 0.006, TY + 0.004, 0.08, "Thimble Shoal: islands 1 and 2")),
)

chapter(
    P("P17",
      sat(0, -76.11, 36.94, 0.09, "The trestle leaving Virginia Beach"),
      stat("In nineteen sixty, the", "$200 MILLION", "In revenue bonds sold to private investors, 1960", CBBT),
      photo("to be paid back", PH_ROAD2, "Paid for by tolls"),
      stat("According to the crossing's", "$0", "Local, state or federal tax money in the construction", CBBT),
      photo("If the road failed", PH_ROAD3, "The crossing")),
    P("P18",
      stat(0, "1960", "Construction begins", ASCE),
      sat("To make each island,", -76.07, 37.03, 0.09, "Islands of sand and rock"),
      sat("sand into the middle", TX - 0.004, TY - 0.008, 0.08, "Pumped sand"),
      photo("Then they covered the", PH_BRUN2, "Granite armour and a plaque on an island"),
      sat("Granite boulders of two", -76.095, 36.965, 0.08, "Armour of granite"),
      stat("Each island ended up", "~5.25 ACRES", "Each of the four islands", ASCE)),
    P("P19",
      photo(0, PH_PORTAL8, "A tunnel under a shipping channel"),
      m("Steel tubes, each about", v(USA, places=[ORANGE, NORFOLK])),
      stat("were made at a", "300 FT", "Each steel tube section; 35 feet across", VP),
      m("they would float, and", v(USA, places=[ORANGE, NORFOLK]), step(48, view=near(-82.0, 29.0, 16.0))),
      stat("Thirty-seven of them for", "37", "Steel tube sections for each tunnel", VP),
      m("two broke away from", v(USA, places=[ORANGE]), step("were caught again.", view=near(-88.0, 27.5, 9.0)))),
    P("P20",
      sat(0, -76.29, 36.86, 0.12, "Norfolk"),
      sat("Then, one by one,", TX + 0.01, TY, 0.12, "The tubes lie under the channel"),
      photo("When it was done,", PH_CARRIER2, "Ships pass over the tunnels"),
      sat("with no idea that", -76.10, 36.97, 0.15, "A highway under the channel")),
    P("P21",
      photo(0, PH_TRES9, "Trestle piles in the bay"),
      m("Under the bay is", v(BAY, highlight=[CRATER])),
      sat(23, -76.00, 37.10, 0.7, "The bay mouth lies over the crater"),
      stat("solid rock lies more", "6,000+ FT", "Down to bedrock under the bay mouth", VP),
      photo("So the concrete piles", PH_ROAD4, "Held up by friction"),
      stat("The longest was driven", "172 FT", "The deepest pile", VP)),
    P("P22",
      stat(0, "MARCH 1962", "The Ash Wednesday Storm", "Weather Bureau records"),
      sat("A nor'easter stalled off", -75.70, 37.00, 2.0, "Off the Atlantic coast"),
      sat("Tides ran high through", -76.27, 36.87, 0.20, "Norfolk"),
      sat("and according to reporting", -76.10, 37.00, 0.5, "The work sites at the mouth of the bay"),
      photo("knocked over a tunnel", PH_BRUN5, "An island today"),
      photo(64, PH_TRES13, "The trestle in open water")),
    P("P23",
      stat(0, "15 APRIL 1964", "The bridge-tunnel opens, 42 months after work began", CBBT),
      sat(9, -76.04, 37.04, 0.45, "The whole crossing"),
      photo("The ferries were retired.", PH_FISH1, "Fisherman Island, at the crossing's north end (USFWS)"),
      stat("The next year, a", "1965", "Named one of the Seven Engineering Wonders of the Modern World", CBBT),
      sat(33, -75.99, 37.10, 0.14, "The north end of the crossing"),
      photo("Accounts of the project", PH_BRUN1, "On the crossing, 2004")),
    P("P24",
      sat(0, -75.97, 37.10, 0.10, "Fisherman Island, the Eastern Shore end"),
      photo("But the bay had", PH_ROAD15, "Open water on both sides")),
)

chapter(
    P("P25",
      sat(0, -76.06, 37.00, 0.5, "Ships anchor around the crossing"),
      stat("In the night of", "21 JAN 1970", "A gale over the mouth of the bay", HRNM),
      photo("According to a later", PH_AMPHIB_1964, "Navy ships off Virginia"),
      sat(44, -76.15, 36.99, 0.35, "The anchorage off the crossing"),
      photo("One of them was", PH_YANCEY, "USS Yancey, about 1952 (U.S. Navy)")),
    P("P26",
      sat(0, X0 - 0.03, Y0 - 0.02, 0.30, "Across the bay, stern first"),
      stat("at one thirty-seven in", "1:37 AM", "First impact; at 3:30 she went through", HRNM),
      sat(26, -76.07, 36.98, 0.12, "The trestle"),
      stat("She left a gap", "~400 FT", "Of trestle knocked out", HRNM),
      photo("The crossing had stockpiled", PH_TRES12, "Spans of 75 feet"),
      sat("in the cold and", -76.09, 36.95, 0.10, "The south trestle"),
      photo("It was not the", PH_FISH2, "Fisherman Island (USFWS)")),
    P("P27",
      photo(0, PH_ROAD, "Open water, no shelter"),
      sat(11, -76.02, 37.08, 0.20, "Nothing breaks the wind"),
      sat("So it has rules", -76.06, 37.06, 0.6, "Wind off the Atlantic"),
      stat("At thirty-five miles an", "35 MPH WIND", "Speed limit 45, no passing", CBBT),
      stat("At forty, motorcycles, campers,", "40 MPH", "Motorcycles, campers, towed loads, box trucks, buses, empty trucks banned", CBBT),
      stat("At fifty, only cars,", "50 MPH", "Only cars, empty pickups, minivans and SUVs", CBBT, note="At 60 mph the crossing closes")),
    P("P28",
      photo(0, PH_TRES11, "No shoulder, low railing"),
      sat(11, -76.08, 36.96, 0.13, "Low trestle, open water"),
      stat("By one count, at", "20+", "People killed in over-the-side crashes, by one count to 2023", VP),
      sat("Some crashes came in", -76.05, 37.07, 0.12, "Open trestle"),
      photo("Others came on calm", PH_ROAD10, "Calm days too")),
    P("P29",
      stat(0, "35 YEARS", "One two-lane road, one lane each way", CBBT),
      sat(10, -76.00, 37.09, 0.10, "Two lanes for 35 years"),
      photo("In nineteen ninety-nine, a", PH_ROAD17, "Two parallel trestles since 1999"),
      sat("But not its own", TX - 0.006, TY + 0.006, 0.08, "Four lanes, then one tunnel"),
      photo("So even today, when", PH_PORTAL7, "Into a single tube"),
      photo("and you drive under", PH_BRUN6, "Island 1, 2004"),
      sat(70, -76.09, 37.00, 0.09, "One tube under each channel")),
)

chapter(
    P("P30",
      sat(0, TX + 0.012, TY - 0.004, 0.09, "Thimble Shoal: the new tunnel runs beside the old one"),
      stat("In twenty sixteen, the", "$757 MILLION", "Contract for a second tunnel under Thimble Shoal Channel, 2016", CBBT),
      sat(18, -76.12, 36.97, 0.10, "Under Thimble Shoal Channel"),
      photo("This time it would", PH_HRBT_IKE, "Navy ships use the channels above"),
      stat("It would be bored", "43 FT", "Across the cutterhead; the machine is 308 ft long", CBBT),
      sat(58, -76.13, 36.96, 0.08, "Island 1, where the machine started"),
      sat("Its name, chosen by", -76.11, 36.965, 0.09, "Island 1, where the new tunnel begins")),
    P("P31",
      stat(0, "FEB 2023", "Chessie starts mining", CBBT),
      sat("In May, it hit", -76.11, 36.98, 0.13, "Somewhere under the channel"),
      stat("It turned out to", "1900s", "A ship's anchor made in England, buried in the channel", CBBT),
      sat(28, -76.10, 36.99, 0.11, "Near the old tube"),
      sat("Some ship lost it", -76.05, 36.97, 0.4, "The mouth of a busy harbor"),
      photo(51, PH_HENRY_NEW, "Cape Henry, at the harbor mouth")),
    P("P32",
      stat(0, "8 MONTHS", "Of extra work to remove the anchor", CBBT),
      stat("Tunnelling only resumed in", "~50 FT A DAY", "From May 2024", CBBT),
      stat("On January twenty-seventh, twenty", "6,300+ FT", "Mined before breakthrough, 27 January 2025", CBBT),
      sat(38, -76.09, 36.98, 0.10, "Breakthrough at Two Island"),
      stat("The crossing's current forecast", "EARLY 2028", "Forecast opening of the new tunnel", CBBT)),
    P("P33",
      sat(0, CX, CY + 0.01, 0.12, "Chesapeake Channel: still one tube"),
      photo("So the bay keeps", PH_ROAD16, "The crossing"),
      sat("Which brings us back", -76.083, 37.033, 0.14, "Back to the tide gauge")),
)

chapter(
    P("P34",
      sat(0, -76.33, 36.947, 0.08, "Sewells Point, Naval Station Norfolk"),
      stat("It has measured the", "1927", "The Sewells Point tide gauge starts recording", NOAAT),
      stat("Over that time, according", "+1.90 IN", "Per decade, Sewells Point, 1927-2025", NOAAT),
      sat(46, -76.30, 36.93, 0.12, "The naval base"),
      sat("That adds up to", -76.32, 36.95, 0.16, "Norfolk's waterfront"),
      stat(66, "~1.5 FEET", "Since 1927 (1.90 in per decade x 9.8 decades)", NOAAT)),
    P("P35",
      m(0, v(USA, places=[SEWELLS])),
      chart("There are twenty-three.", "Sea level trend, long-record U.S. Atlantic gauges", "inches per decade",
            [("Sewells Point, VA", 1.90), ("Sandy Hook, NJ", 1.68), ("Atlantic City, NJ", 1.67), ("Annapolis, MD", 1.52),
             ("Charleston, SC", 1.38), ("Baltimore, MD", 1.30), ("Boston, MA", 1.17), ("New York (Battery)", 1.16),
             ("Key West, FL", 1.04), ("Portland, ME", 0.78)], OWNNOAA, highlight=0),
      sat("Faster than New York,", -74.02, 40.69, 0.15, "New York harbor"),
      sat("And the gauge on", -76.09, 37.02, 0.09, "The bridge-tunnel's own gauge"),
      stat("About a foot in", "+2.42 IN", "Per decade at the bridge-tunnel gauge, 1975-2025", NOAA_CC)),
    P("P36",
      photo(0, PH_ROAD15, "Water close to the road"),
      stat("The U.S. Geological Survey", "HIGHEST", "Relative sea level rise on the Atlantic coast: coastal Virginia", USGSVA),
      sat(26, -76.30, 37.00, 0.5, "Hampton Roads"),
      photo("because the ground is", PH_TANGIER, "Tangier Island, Virginia: high water in the streets, 2023"),
      sat("Much of it comes", -76.55, 36.75, 0.9, "Suffolk and Franklin: wells and sinking ground"),
      sat("and as the water", -76.92, 36.68, 0.30, "Franklin, Virginia"),
      stat("the clay layers squeeze", "1.5-3.7 MM/YR", "Measured sinking, Franklin and Suffolk, 1979-1995", BEKAERT),
      m("Part of it is", v(EAST, places=[BALTIMORE, NORFOLK])),
      m("And researchers studying the", v(BAY, highlight=[CRATER], places=[NORFOLK])),
      sat("ongoing shifts in the", -76.05, 37.27, 0.6, "Over the crater", date="2025-10-16")),
    P("P37",
      photo(0, PH_CRATER_MAP, "The buried crater"),
      stat("Deep under the bay,", "2x", "As salty as today's ocean: water deep in the crater", SANFORD),
      sat(18, -76.10, 37.20, 1.0, "The crater under the bay", date="2025-10-16"),
      stat("In twenty thirteen, USGS", "100-145 MILLION YEARS", "Age of the seawater trapped in the crater", SANFORD),
      photo(42, PH_CC_1853, "Cape Charles, above the crater (1853 chart)"),
      sat("trapped and kept in", -76.017, 37.283, 0.5, "Above the crater", date="2025-10-16")),
)

chapter(
    P("P38",
      sat(0, X0, Y0, 0.36, "The Chesapeake Bay Bridge-Tunnel"),
      m("A rock from space", v(BAY, highlight=[CRATER])),
      m("An ice age carved", v(EAST, places=[SUSQ])),
      sat("The deepest parts of", TX, TY - 0.006, 0.12, "The channels"),
      photo("And a navy that", PH_NAVSTA_AIR, "Naval Station Norfolk")),
    P("P39",
      sat(0, -76.09, 37.03, 0.10, "Islands built in the early 1960s"),
      photo("Since then the water", PH_NIGHT_ISLAND, "Island 1"),
      sat("and the ground under", -76.28, 36.90, 0.25, "Norfolk"),
      sat("The next tunnel under", CX, CY, 0.18, "Chesapeake Channel"),
      photo("So here is the", PH_KITE, "The crossing"),
      sat(64, -76.03, 37.00, 0.5, "The mouth of the bay"),
      ask=("So here is the", "Should the next tunnel be built for today's sea, or the sea of 2100?")),
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


TITLE = "Why This American Highway Dives Under the Sea"
script = {
    "title": TITLE,
    "voice": "am_michael",
    "voice_speed": 1.15,
    "music": "procedural",
    "map_style": "satellite",
    "look": "none",
    "photo_upscale": True,
    "sources": ["episodes/chesapeake-bay-bridge-tunnel/research.md and factcheck.md", "Contains modified Copernicus Sentinel data 2026",
                "Sea level trends: NOAA CO-OPS (tidesandcurrents.noaa.gov)", "Crater outline: approximate, after USGS and the Earth Impact Database"],
    "thumbnail": {"text": "THE ROAD GOES UNDER"},
    "chapters": chapters,
    "youtube": {
        "title": TITLE,
        "description": "At the mouth of the Chesapeake Bay, a highway runs 17.6 miles out to sea, onto islands built in open water, and twice dives under the shipping channels. Why build it like that? We follow the answer from orbit: an asteroid crater buried under the bay 35 million years ago, the drowned valley of the Susquehanna, the ferries of the Eastern Shore, the Navy's fear of a fallen bridge, four man-made islands and steel tubes towed from Texas, the 1962 storm, the night USS Yancey went through the trestle, the tunnel machine Chessie and the century-old anchor it hit, and the tide gauges that show the sea rising faster here than anywhere else on the U.S. Atlantic coast.",
        "tags": ["Chesapeake Bay Bridge-Tunnel", "Chesapeake Bay", "Virginia", "Norfolk", "Virginia Beach", "Eastern Shore", "Naval Station Norfolk",
                 "Chesapeake Bay impact crater", "Thimble Shoal tunnel", "Chessie TBM", "sea level rise", "engineering", "geography", "satellite images"],
        "pinned_comment": "Should the next tunnel be built for today's sea, or the sea of 2100?",
    },
}
out = HERE / "script.json"
out.write_text(json.dumps(script, ensure_ascii=False, indent=1) + chr(10), encoding="utf-8")
words = sum(len(p["text"].split()) for c in chapters for p in c["paragraphs"])
shots = [s for c in chapters for p in c["paragraphs"] for s in p["shots"]]
kinds = {k: sum(1 for s in shots if s["type"] == k) for k in ("map", "photo", "stat", "document", "chart")}
print(f"{words} words, {len(chapters)} chapters, {len(shots)} shots {kinds}")
