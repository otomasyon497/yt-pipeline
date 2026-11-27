"""Builds script.json for florida-keys.  python build_script.py

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
SU = "2025-01-01/2025-04-30"    # dry season 2025: scratch fksat.py 2026-11-27, clear on the views used


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
FLA = {"lon": -82.0, "lat": 26.6, "span": 9.5}        # the Florida peninsula and the Keys
SFLA = {"lon": -81.0, "lat": 25.15, "span": 3.6}      # Miami to Key West
KEYS = {"lon": -81.05, "lat": 24.85, "span": 2.8}     # the whole chain
STRAITS = {"lon": -81.6, "lat": 24.2, "span": 6.5}    # Key West, the Straits, Havana
CARIB = {"lon": -80.5, "lat": 17.5, "span": 30.0}     # Key West to Panama
EAST = {"lon": -81.0, "lat": 28.2, "span": 8.5}       # the Florida East Coast line
USE = {"lon": -79.0, "lat": 33.0, "span": 26.0}       # New York to Havana
UPPER = {"lon": -80.62, "lat": 25.0, "span": 2.6}     # Florida City to Long Key
LOWER = {"lon": -81.45, "lat": 24.68, "span": 2.6}    # Marathon to Key West

KEYS_RED = "file:keys.geojson@red"
KEYS_ALT = "file:keys.geojson@alt"
UPMID_RED = "file:upper_mid.geojson@red"
LOWER_RED = "file:lower.geojson@red"
KW_RED = "file:keywest.geojson@red"
DADE_RED = "file:dade_south.geojson@red"

# ------------------------------------------------------------------ sources (research.md)
CENSUS = "US Census Bureau"
OWN_SEA = "Own calculation: NOAA monthly mean sea level, Key West, 1913-2025 (geo/measure_sealevel.py)"
OWN_ROAD = "Own count: 2020 census blocks vs US 1 (geo/measure_road.py)"
OWN_HEIGHT = "Own sample: 1,500 land points, USGS 3DEP elevations (geo/measure_height.py)"
MONROE = "Monroe County, Florida"
FKAA = "Florida Keys Aqueduct Authority"
NWS = "National Weather Service"
FLSTAT = "Florida Statutes 380.0552"

# ------------------------------------------------------------------ photos (visuals.md; all PD / CC0 / CC BY, checked 2026-11-27)
PH_7MILE_AIR = "Seven Mile Bridge, Florida Keys aerial (2003).jpg"
PH_7MILE_SUN = "7 Mile Bridge www.florida-infos.com - panoramio (1).jpg"
PH_HWY = "Overseas Highway to Key West - panoramio.jpg"
PH_LOWERKEYS = "The Lower Keys.jpg"
PH_SUGARLOAF = "001 Key West Bay Point - Lower Sugarloaf Channel aerial view.jpg"
PH_1935_A = "1935 hurricane effects in the Florida Keys MM00003786x (15479759252).jpg"
PH_1935_B = "1935 hurricane effects in the Florida Keys MM00005619 (7841218628).jpg"
PH_1935_CHURCH = "Islamorada church after the 1935 Labor Day hurricane.jpg"
PH_1935_ROAD = "Overseas Highway on Upper Matecumbe Key after the 1935 Labor Day hurricane.jpg"
PH_1935_STATION = "Platform of railway station on Long Key after the 1935 Labor Day hurricane.jpg"
PH_1935_CARIBEE = "Caribee Colony after 1935 Labor Day hurricane.jpg"
PH_1935_BLDG = "Destroyed building on the Florida Keys after the 1935 Labor Day hurricane.jpg"
PH_VET_MAP = "Veterans Storm Relief Map.jpg"
PH_KW_1884 = "Bird's eye view of Key West, Fla., Key West Island, C.S. Monroe Co., 1884 LOC 83693954.jpg"
PH_KW_HARBOR = "MM00032290 (5837195542).jpg"
PH_CIGAR = "Key West Florida - Ann Street - Cortez Cigar Factory.jpg"
PH_POHALSKI = "Pohalski City Key West Florida 1889.jpg"
PH_CUBA_BOAT = "Arrival of boat from Cuba ... LCCN97504618.jpg"
PH_TRAM = "Duval and Front with Horse Tram, Key West Florida.jpg"
PH_LIGHT = "Key West Lighthouse 20080728.jpg"
PH_SPONGE = "Key West Florida Sponge Wagon 1930s.jpg"
PH_FLAGLER = "Henry Morrison Flagler (1830-1913) portrait.jpg"
PH_OPENING = "Opening of Florida Keys Railway - J.R. Parott, H. M. Flagler LCCN2014680212.jpg"
PH_FIRST_TRAIN = "Florida East Coast Railway first Key West Train 1912.JPG"
PH_LONGKEY_TRAIN = "H.M. Flagler's Special, first train crossing Long Key Viaduct, 2.7 miles long, Long Key, Fla. LCCN2005694817.jpg"
PH_GUIDE1912 = "A guide to Florida for tourists, sportsmen and settlers (1912) (14576579758).jpg"
PH_ARCHES = "Long Key Viaduct, view showing typical method of construction for all concrete arches in 7-Mile Bridge (-214). - Seven Mile Bridge, Linking Florida Keys, Marathon, Monroe County HAER FLA,44-KNIKE,1-52.tif"
PH_KK_GIRDERS = "Knight's Key Bridge, View of steel girders in place and on barge (-571). - Seven Mile Bridge, Linking Florida Keys, Marathon, Monroe County, FL HAER FLA,44-KNIKE,1-44.tif"
PH_KK_PIERS = "Knight's Key Bridge, finishing concrete piers w-view of temporary wood trestle in right (-2534). - Seven Mile Bridge, Linking Florida Keys, Marathon, Monroe County, FL HAER FLA,44-KNIKE,1-48.tif"
PH_KK_COFFER = "Knight's Key Bridge, view of derrick lowering cofferdam (Lindenberg Collection -1569). - Seven Mile Bridge, Linking Florida Keys, Marathon, Monroe County, FL HAER FLA,44-KNIKE,1-53.tif"
PH_KK_FIRST = "Knight's Key Bridge, view of first span, 1909 (-2518). - Seven Mile Bridge, Linking Florida Keys, Marathon, Monroe County, FL HAER FLA,44-KNIKE,1-51.tif"
PH_KK_PIGEON = "Knight's Key Bridge approaching Pigeon Key, 12-22-26 (Matlack 138-40). - Seven Mile Bridge, Linking Florida Keys, Marathon, Monroe County, FL HAER FLA,44-KNIKE,1-58.tif"
PH_KK_TRAIN = "Knight's Key Bridge, passenger train crossing bridge, no date (Bramson Collection, X-336-1). - Seven Mile Bridge, Linking Florida Keys, Marathon, Monroe County, FL HAER FLA,44-KNIKE,1-72.tif"
PH_KK_LONG = "Knight's Key Bridge, long side perspective, 12-22-26 (Matlack 141-40). - Seven Mile Bridge, Linking Florida Keys, Marathon, Monroe County, FL HAER FLA,44-KNIKE,1-59.tif"
PH_MOSER = "Moser Channel Bridge, draw span partially open, no date (Kyle K-32). - Seven Mile Bridge, Linking Florida Keys, Marathon, Monroe County, FL HAER FLA,44-KNIKE,1-68.tif"
PH_CONV_1937 = "Construction view of concrete bridge meeting railroad bridge, 10-28-37 (Matlack 247-13). - Seven Mile Bridge, Linking Florida Keys, Marathon, Monroe County, FL HAER FLA,44-KNIKE,1-62.tif"
PH_PIGEON_1938 = "Pigeon Key Bridge, aerial view w-auto traffic, April 23, 1938 (Matlack 397-13-7). - Seven Mile Bridge, Linking Florida Keys, Marathon, Monroe County, FL HAER FLA,44-KNIKE,1-66.tif"
PH_BH_POST = "Bahia Honda Bridge, highest span of Overseas Highway on way to Key West, Florida.jpg"
PH_BH_FDR = "FDR in an open car by the Bahia Honda Bridge on February 19, 1939 (8150911081).jpg"
PH_BH_NOW = "Baihia Honda Bridge - Flickr - daniel.chodusov.jpg"
PH_BH_RAIL = "Bahia Honda Rail Bridge(js).jpg"
PH_BH_GAP = "Florida Keys Broken Railroad Bridge (17060736207).jpg"
PH_US1_SIGN = "Photograph of a road sign along the highway in Key West, Florida, announcing the beginning of U.S. Route 1 to Fort... - NARA - 200542.jpg"
PH_LONGKEY_PARK = "AERIAL VIEW OF STATE PARK ON LONG KEY, MIDWAY BETWEEN KEY LARGO AND KEY WEST. VIEW SHOWS A SEGMENT OF THE OVERSEAS... - NARA - 548628.jpg"
PH_FOSSIL = "Fossil Reef Windley Key 1.jpg"
PH_CISTERN = "3-4 VIEW TO NORTHEAST - Naval Air Station Key West, Truman Annex, Fresh Water Cistern, Intersection of Front and Eaton Streets, Key West, Monroe County, FL HABS fl-530-C-4.tif"
PH_CISTERNS2 = "CISTERNS AT REAR, LOOKING SOUTHEAST - Tift and Company, Ships Chandlery and Icehouse, Mallory Square, Key West, Monroe County, FL HABS FLA,44-KEY,8-3.tif"
PH_NAVY_1939 = "Naval Station Key West, Florida (USA), on 11 February 1939 (80-G-463399).jpg"
PH_NAVY_HOSP = "Sally Rand Visits Key West Naval Hospital.jpg"
PH_TRUMBO_AIR = "Aerial photo of Trumbo Point Annex of Naval Air Station Key West in April 2016.JPG"
PH_KW_NARA = "Florida - Key West - NARA - 23936667.jpg"
PH_KW_NARA2 = "Florida - Key West - NARA - 23936663.jpg"
PH_AIR_1950 = "Aerial photographs of Florida MM00004535 (5967441175).jpg"
PH_TRAILER = "TRAILER PARK UNDER CONSTRUCTION AT MARATHON IN THE CENTRAL FLORIDA KEYS. THIS IS ONE OF MANY SUCH PARKS SPRINGING UP... - NARA - 548762.jpg"
PH_POSTOFFICE = "Old Post Office and Customshouse, Key West.jpg"
PH_PINKHOUSE = "Pink and Blue House in Key West, Florida.jpg"
PH_MARIEL_BOAT = "Boat with Cuban refugees during Mariel Boatlift (7164182641).jpg"
PH_MARIEL_PIER = "Pier B during Mariel Boatlift (7164183301).jpg"
PH_MARIEL_TONY = "El Tony and others during Mariel Boatlift (7349394034).jpg"
PH_MARIEL_CENTER = "Mariel Boatlift refugee center (7164017325).jpg"
PH_CONCH_FOUND = "The founding of the Conch Republic.jpg"
PH_CONCH_FLAG = "The Conch Republic Flag, Key West, Florida, June 2021.jpg"
PH_CONCH_PASS = "Key West Florida 2014 - Conch Republic Passport Office.jpg"
PH_IRMA_DEBRIS = "Debris (36884162550).jpg"
PH_IRMA_19 = "Hurricane Irma 19 (36977734710).jpg"
PH_IRMA_VISIT = "170914-H-OD937-209 (37474487341).jpg"
PH_IRMA_NIGHT = "Florida night-time satellite image before-and-after Hurricane Irma.jpg"
PH_DONNA = "Hurricane Donna effects in the Florida Keys MM00030997 (4934987453).jpg"
PH_ELKHORN = "Elkhorn coral 8 Molasses Reef 20080309.jpg"
PH_STAGHORN = "Staghorn Looe Key 2010.jpg"
PH_FRED = "Fred the Tree 2025-05-18.jpg"
PH_FRED2 = "Christmastime Fred the Tree.jpg"
PH_MARATHON = "“Welcome to Marathon,” Marathon, Florida Keys.jpg"
PH_1909 = "1909 hurricane effects in Key West MM00000841x (15413985922).jpg"
PH_1910 = "1910 hurricane effects in Key West MM00011137x (26387467093).jpg"

PH_KW2008 = "Key West 2008 (2338775214).jpg"
PH_HARBORHOUSE = "The Harbor House, Front Street, Key West, Florida.jpg"
PH_NAS2016 = "Aerial view of Naval Air Station Key West - Boca Chica Field in April 2016.JPG"
PH_WX1935 = "Labor Day hurricane weather analysis (Enlarged), Sep 2, 1935.jpg"
PH_PATH1935 = "1935 Labor Day hurricane path.png"
PH_WX0904 = "Labor Day hurricane weather map, September 4, 1935 (high quality) (3099770).jpg"
PH_BURIAL = "Burial of 1935 hurricane victims at Woodlawn Cemetery, Miami, FL.jpg"
PH_FKEAST = "Fkeast 2000.jpg"
PH_KW_NARA3 = "Florida - Key West - NARA - 23936671.jpg"
PH_USCG = "USCGC Active (WMEC 618) Mariel Boatlift (7352293542).jpg"
PH_CITYHALL = "Key West City Hall.jpg"
PH_MALLORY = "Mallory Square, Key West - panoramio (5).jpg"
PH_WILMA = "Flood102405.JPG"
PH_IRMA_SAT = "Irma 2017-09-10 1315Z.jpg"

PH_HEMHOUSE = "Hemingwayhouse.jpg"
PH_SUNSETKEY = "Sunset Key and Sailboats, Florida, 2025.jpg"
PH_WX0901 = "Labor Day hurricane weather map (enlarged), September 1, 1935 (4399800).jpg"

# ------------------------------------------------------------------ places, routes and arrows
KEYWEST = place("Key West", -81.78, 24.555, "Key West", "city")
HAVANA = place("Havana", -82.37, 23.13, "Havana", "capital")
MIAMI = place("Miami", -80.19, 25.77, "Miami", "city")
HOMESTEAD = place("Homestead", -80.48, 25.47, "Homestead", "city")
FLCITY = place("Florida City", -80.48, 25.45, "Florida City", "city")
JAX = place("Jacksonville", -81.66, 30.33, "Jacksonville", "city")
TAMPA = place("Tampa", -82.46, 27.95, "Tampa", "city")
PANAMA = place("Panama Canal", -79.75, 9.1, "Panama Canal", "site")
NYC = place("New York", -74.0, 40.71, "New York", "city")
KEYLARGO = place("Key Largo", -80.43, 25.10, "Key Largo", "city")
LAKESURP = place("Lake Surprise", -80.39, 25.175, "Lake Surprise", "site")
ISLAMORADA = place("Islamorada", -80.63, 24.92, "Islamorada", "city")
LONGKEY = place("Long Key", -80.82, 24.82, "Long Key", "site")
LMATE = place("Lower Matecumbe", -80.75, 24.86, "Lower Matecumbe Key", "site")
WINDLEY = place("Windley Key", -80.67, 24.955, "Windley Key camp", "site")
MARATHON = place("Marathon", -81.07, 24.72, "Marathon", "city")
PIGEON = place("Pigeon Key", -81.156, 24.704, "Pigeon Key", "site")
BAHIA = place("Bahia Honda", -81.27, 24.66, "Bahia Honda", "site")
NONAME = place("No Name Key", -81.32, 24.70, "No Name Key", "site")
CUDJOE = place("Cudjoe Key", -81.50, 24.67, "Cudjoe Key", "site")
TRUMBO = place("Trumbo Point", -81.79, 24.568, "Trumbo Point", "site")
MILE74 = place("Mile 74", -80.78, 24.85, "Washouts", "site")
MARIEL = place("Mariel", -82.76, 23.01, "Mariel", "city")
STRAITS_L = place("Straits", -81.0, 24.0, "STRAITS OF FLORIDA", "label")
GULF_L = place("Gulf", -84.5, 25.6, "GULF OF MEXICO", "label")

ROAD_PTS = [[-80.43, 25.12], [-80.63, 24.92], [-80.83, 24.82], [-81.05, 24.72], [-81.20, 24.68], [-81.27, 24.66],
            [-81.37, 24.67], [-81.50, 24.66], [-81.62, 24.60]]
ROAD = [{"from": [-80.48, 25.45], "via": ROAD_PTS, "to": [-81.78, 24.56], "mode": "line", "label": "US 1", "color": "red", "seconds": 3.0}]
RAIL = [{"from": [-80.48, 25.45], "via": ROAD_PTS, "to": [-81.79, 24.57], "mode": "line", "label": "Railway, 1912", "color": "accent", "seconds": 3.0}]
PIPE = [{"from": [-80.50, 25.43], "via": ROAD_PTS, "to": [-81.77, 24.56], "mode": "line", "label": "Water main", "color": "blue", "seconds": 3.0}]
FEC = [{"from": [-81.66, 30.33], "via": [[-81.31, 29.90], [-80.05, 26.70], [-80.19, 25.77]], "to": [-80.48, 25.47], "mode": "line",
        "label": "Florida East Coast Railway", "color": "accent", "seconds": 3.0}]
ROAD1928 = [{"from": [-80.48, 25.45], "via": [[-80.43, 25.12], [-80.63, 24.92]], "to": [-80.75, 24.86], "mode": "line", "label": "Road, 1928", "color": "red", "seconds": 2.0}]
FERRY = [{"from": [-80.75, 24.86], "to": [-81.32, 24.70], "color": "blue", "label": "Ferry, ~4 hours", "bend": 0.25}]
TRAIN35 = [{"from": [-80.19, 25.77], "via": [[-80.48, 25.45], [-80.43, 25.12]], "to": [-80.63, 24.92], "mode": "line", "label": "Rescue train", "color": "red", "seconds": 2.5}]
STORM35 = [{"from": [-78.6, 24.1], "to": [-80.84, 24.84], "color": "red", "label": "Labor Day storm, 2 Sep 1935", "bend": 0.08}]
IRMA = [{"from": [-79.6, 23.1], "to": [-81.50, 24.66], "color": "red", "label": "Irma, 10 Sep 2017", "bend": -0.1}]
LANE = [{"from": [-86.0, 24.6], "to": [-79.6, 25.2], "color": "blue", "label": "Gulf - Atlantic shipping", "bend": -0.12}]
CANAL = [{"from": [-79.75, 9.1], "to": [-81.78, 24.55], "color": "red", "label": "Canal trade?", "bend": 0.1}]
PAST = [{"from": [-79.75, 9.1], "to": [-75.5, 20.0], "color": "blue", "label": "Ships kept their routes", "bend": -0.15}]
TOTAMPA = [{"from": [-81.78, 24.56], "to": [-82.46, 27.95], "color": "red", "label": "Cigar makers move", "bend": 0.12}]
CARFERRY = [{"from": [-81.78, 24.56], "to": [-82.37, 23.13], "color": "blue", "label": "Car ferry, 1915", "bend": 0.15}]
NY_HAV = [{"from": [-74.0, 40.71], "via": [[-81.66, 30.33], [-80.19, 25.77], [-81.78, 24.56]], "to": [-82.37, 23.13], "mode": "line",
           "label": "By rail and ferry", "color": "accent", "seconds": 3.0}]
MARIELA = [{"from": [-82.76, 23.01], "to": [-81.78, 24.55], "color": "red", "label": "Mariel boatlift, 1980", "bend": 0.1}]
OUT = [{"from": [-81.0, 24.72], "to": [-80.48, 25.45], "color": "red", "label": "Everyone out", "bend": 0.15}]

chapters = []
heads = iter(HEADS)


def chapter(*paras):
    title, mood = next(heads)
    chapters.append({"title": title, "mood": mood, "paragraphs": list(paras)})


# ================================================================== Hook
chapter(
    P("P0",
      m(0, v(FLA, highlight=[KEYS_RED])),
      m("It runs more than", v(SFLA, highlight=[KEYS_RED], routes=ROAD)),
      m("farther than New York", v(USE, places=[NYC], highlight=[KEYS_RED]))),
    P("P1",
      photo(0, PH_7MILE_AIR, "The Seven Mile Bridge"),
      sat("Everything the islands need", -81.17, 24.70, 0.2, "The Seven Mile Bridge from orbit"),
      photo("And most of it", PH_HWY, "The Overseas Highway")),
    P("P2",
      m(0, v(KEYS, highlight=[KEYS_RED], routes=ROAD)),
      photo("and can Florida keep", PH_LOWERKEYS, "The Lower Keys from the air")),
    P("P3",
      photo(0, PH_1935_A, "The Keys after the storm of 1935"),
      photo("A city on it", PH_KW2008, "Key West"),
      photo("And keeping the road", PH_SUGARLOAF, "Lower Sugarloaf Channel"),
      stat("now has a price", "$1.8 BILLION", "To raise the county's roads above future tides", MONROE)),
    P("P4",
      m(0, v(KEYS, places=[KEYWEST])),
      sat("with the town that", -81.78, 24.56, 0.15, "Key West")),
)

# ================================================================== 1. A Town Worth the Trip
chapter(
    P("P5",
      m(0, v(STRAITS, highlight=[KW_RED], places=[KEYWEST, STRAITS_L])),
      photo("the biggest in Florida.", PH_KW_1884, "Key West in 1884")),
    P("P6",
      m(0, v(STRAITS, places=[GULF_L], arrows=LANE)),
      photo("between the Gulf of", PH_KW_HARBOR, "Ships at Key West"),
      m("Cuba is about ninety", v(STRAITS, places=[HAVANA]))),
    P("P7",
      photo(0, PH_HARBORHOUSE, "Front Street, Key West"),
      photo("Ships wrecked on the", PH_1909, "Key West's waterfront"),
      photo("under a federal court", PH_POSTOFFICE, "The old federal building, Key West"),
      photo("Later it rolled cigars", PH_CIGAR, "A cigar factory on Ann Street"),
      photo("and the Navy kept", PH_NAS2016, "Naval Air Station Key West today")),
    P("P8",
      chart(0, "People, 1890 census", "", [["Key West", 18080], ["Jacksonville", 17201]], "US Census 1890", highlight=0),
      photo("and more than any", PH_POHALSKI, "Pohalski's cigar works, Key West, 1889")),
    P("P8b",
      photo(0, PH_SPONGE, "A sponge wagon, Key West"),
      photo("Lighthouses made the reef", PH_LIGHT, "The Key West lighthouse"),
      m("Then most of the", v(FLA, places=[KEYWEST, TAMPA], arrows=TOTAMPA))),
    P("P9",
      m(0, v(KEYS, places=[KEYWEST, MIAMI])),
      sat("Everything came and went", -81.805, 24.56, 0.08, "Key West harbour")),
    P("P10",
      m(0, v(CARIB, places=[KEYWEST, PANAMA, HAVANA])),
      m("Key West was the", v(CARIB, arrows=CANAL))),
    P("P11",
      photo(0, PH_OPENING, "Henry Flagler and his railway men, 1912"),
      m("His Florida East Coast", v(EAST, places=[JAX, MIAMI, HOMESTEAD], routes=FEC)),
      m("If he could carry", v(USE, places=[NYC, HAVANA], routes=NY_HAV)),
      m("the trade of the", v(STRAITS, places=[HAVANA, KEYWEST]))),
    P("P12",
      stat(0, "128 MILES", "Homestead to Key West by the railway's route", "Florida East Coast Railway, 1912"),
      sat("Most of it was", -80.95, 24.78, 0.6, "The Middle Keys")),
    P("P13",
      photo(0, PH_ARCHES, "Building the concrete arches"),
      photo("And the railroad was", PH_KK_COFFER, "Lowering a cofferdam, Knight's Key")),
)

# ================================================================== 2. A Railroad First
chapter(
    P("P14",
      m(0, v(KEYS, highlight=[KEYS_ALT], routes=RAIL)),
      photo("there was a railroad", PH_GUIDE1912, "The line over the sea, 1912 guidebook")),
    P("P15",
      photo(0, PH_KK_FIRST, "The first span at Knight's Key, 1909"),
      photo("dredged fill out of", PH_KK_GIRDERS, "Steel girders on a barge"),
      sat("and poured concrete into", -81.12, 24.71, 0.1, "Knight's Key")),
    P("P16",
      m(0, v(UPPER, places=[KEYLARGO, LAKESURP])),
      sat("they found a lake", -80.41, 25.18, 0.25, "Key Largo"),
      sat("and they named it", -80.39, 25.17, 0.12, "Lake Surprise, with US 1 across it")),
    P("P17",
      stat(0, "OCT 1906", "A hurricane tears loose a floating workers' barracks", "Wikipedia: Overseas Railroad", note="about 100 workers died"),
      photo("from its moorings, and", PH_1910, "Key West after the 1910 hurricane"),
      photo("More hurricanes hit in", PH_1909, "Storm damage at Key West, 1909")),
    P("P18",
      sat(0, -80.87, 24.80, 0.08, "The Long Key Viaduct's arches today"),
      photo("and the railway put", PH_KK_TRAIN, "A passenger train on the Knight's Key bridge")),
    P("P19",
      m(0, v(LOWER, places=[BAHIA])),
      sat("they built a steel", -81.27, 24.66, 0.1, "Bahia Honda"),
      m("West of Marathon came", v(LOWER, places=[MARATHON, PIGEON])),
      photo("crossed by the Seven", PH_KK_LONG, "The Seven Mile Bridge, 1926"),
      sat("Its builders lived under", -81.155, 24.704, 0.08, "Pigeon Key")),
    P("P19b",
      sat(0, -81.79, 24.57, 0.08, "Key West"),
      m("so a dredging company", v(KEYS, places=[TRUMBO])),
      photo("at Trumbo Point.", PH_TRUMBO_AIR, "Trumbo Point today")),
    P("P19c",
      photo(0, PH_ARCHES, "Arches under construction"),
      sat("because few stayed more", -81.10, 24.72, 0.15, "Knight's Key and Marathon")),
    P("P20",
      stat(0, "22 JAN 1912", "The first train arrives in Key West", "Library of Congress"),
      photo("Flagler was on board.", PH_OPENING, "Flagler at the opening, 1912"),
      sat("He was eighty-two years", -81.79, 24.57, 0.1, "Trumbo Point, the end of the line")),
    P("P20b",
      m(0, v(STRAITS, places=[KEYWEST, HAVANA], arrows=CARFERRY)),
      m("so a wagon loaded", v(USE, places=[NYC, HAVANA], routes=NY_HAV))),
    P("P21",
      m(0, v(CARIB, places=[KEYWEST, PANAMA], arrows=PAST)),
      stat("The canal opened in", "1914", "The Panama Canal opens", "Panama Canal Authority"),
      m("Freight on the single", v(KEYS, routes=RAIL))),
    P("P22",
      photo(0, PH_US1_SIGN, "US 1 begins at Key West"),
      m("In 1928 a road", v(UPPER, places=[LMATE], routes=ROAD1928)),
      m("From there, cars went", v(KEYS, places=[NONAME], arrows=FERRY)),
      sat("to the next stretch", -81.32, 24.70, 0.12, "No Name Key")),
    P("P23",
      sat(0, -80.82, 24.82, 0.15, "Long Key"),
      m("Then the sea decided", v(KEYS, highlight=[UPMID_RED]))),
)

# ================================================================== 3. The Sea Took the Railroad
chapter(
    P("P24",
      m(0, v(UPPER, highlight=[UPMID_RED])),
      photo("the sea destroyed the", PH_WX0901, "Weather map, 1 September 1935")),
    P("P24b",
      photo(0, PH_SPONGE, "Key West in the 1930s"),
      stat("The Navy had closed", "80 %", "Share of Key West on relief, 1934", "Florida Trend; KWAHS"),
      stat("In July 1934 the", "JULY 1934", "Key West hands its powers to the state", "Florida Trend; KWAHS"),
      photo("Federal relief officials took", PH_KW_NARA, "Key West"),
      photo("and they decided Key", PH_POSTOFFICE, "Old Post Office and Customs House, Key West"),
      m("The tourists would need", v(KEYS, places=[KEYWEST], arrows=FERRY))),
    P("P25",
      m(0, v(UPPER, places=[WINDLEY, LMATE])),
      photo("They lived in camps", PH_VET_MAP, "Veterans' camps and the storm, 1936 relief map"),
      sat("and built bridges to", -80.74, 24.86, 0.15, "Lower Matecumbe Key")),
    P("P26",
      m(0, v(SFLA, places=[LONGKEY], arrows=STORM35)),
      stat("Its central pressure was", "892 mb", "Lowest pressure of any US landfall on record", NWS),
      sat("in the United States", -80.82, 24.81, 0.12, "Long Key, where the eye crossed")),
    P("P27",
      stat(0, "185 MPH", "Estimated one-minute winds", "Landsea et al., NOAA reanalysis 2014"),
      photo("The sea rose over", PH_PATH1935, "The storm's track, 1935")),
    P("P28",
      m(0, v(SFLA, places=[MIAMI, ISLAMORADA], routes=TRAIN35)),
      m("It was held at", v(EAST, places=[MIAMI])),
      sat("and reached Islamorada late,", -80.63, 24.92, 0.12, "Islamorada")),
    P("P29",
      photo(0, PH_1935_A, "After the surge, 1935"),
      m("Everyone on the train", v(UPPER, places=[WINDLEY, LMATE], highlight=[UPMID_RED]))),
    P("P30",
      stat(0, "408", "Official count of the dead", NWS, note="later counts went higher"),
      photo("More than half of", PH_BURIAL, "Burial of storm victims, Miami, September 1935"),
      stat("About half of the", "~350 OF 718", "Camp veterans away in Miami that weekend", "Florida Historical Society"),
      sat("or the toll would", -80.73, 24.86, 0.3, "The Matecumbe Keys")),
    P("P31",
      m(0, v(UPPER, highlight=[UPMID_RED], routes=RAIL)),
      photo("The railway was already", PH_WX0904, "Weather map, 4 September 1935")),
    P("P32",
      photo(0, PH_KK_LONG, "The railway's bridges"),
      stat("with its bridges, for", "$640,000", "Price of the railway right-of-way and bridges, 1936", "Keys historian J. Wilkinson; Fla. Supreme Court 1936")),
    P("P33",
      photo(0, PH_PIGEON_1938, "Cars on the new highway, April 1938"),
      m("In 1938 the Overseas", v(UPPER, routes=ROAD)),
      m("and for the first", v(KEYS, routes=ROAD))),
    P("P34",
      photo(0, PH_BH_POST, "The Bahia Honda bridge, road on top"),
      photo("So the road was", PH_BH_FDR, "President Roosevelt at the Bahia Honda bridge, 1939"),
      photo("sixty-five feet above the", PH_BH_RAIL, "The Bahia Honda bridge today")),
    P("P34b",
      photo(0, PH_HEMHOUSE, "Hemingway's house in Key West"),
      sat("published an article about", -81.80, 24.553, 0.1, "Key West"),
      stat("Its title was a", "SEPT 1935", "Hemingway: \"Who Murdered the Vets?\"", "New Masses, 17 September 1935"),
      sat("He blamed Washington for", -80.72, 24.87, 0.25, "The low islands of the Matecumbe Keys")),
    P("P35",
      sat(0, -80.632, 24.918, 0.08, "Islamorada, where the memorial stands"),
      photo("The remains of some", PH_VET_MAP, "The 1936 relief map of the storm")),
    P("P36",
      photo(0, PH_BH_NOW, "The old Bahia Honda bridge"),
      sat("The islands it joined", -80.95, 24.76, 0.15, "Grassy Key")),
)

# ================================================================== 4. Islands With No Water
chapter(
    P("P37",
      m(0, v(SFLA, highlight=[KEYS_RED, DADE_RED], places=[FLCITY])),
      photo("because they have no", PH_FKEAST, "The Keys from orbit")),
    P("P38",
      photo(0, PH_FOSSIL, "Fossil coral, Windley Key"),
      sat("Rain sinks straight through", -80.655, 24.96, 0.08, "Windley Key")),
    P("P39",
      photo(0, PH_PINKHOUSE, "A Key West house"),
      photo("Every house caught water", PH_CISTERNS2, "Cisterns behind a Key West warehouse")),
    P("P40",
      photo(0, PH_CISTERN, "A Navy fresh-water cistern, Key West"),
      photo("It did not work", PH_NAVY_HOSP, "The Key West naval hospital, 1940s")),
    P("P41",
      m(0, v(SFLA, places=[FLCITY], highlight=[DADE_RED])),
      m("It laid a pipe", v(SFLA, routes=PIPE)),
      sat("island by island,", -81.05, 24.72, 0.15, "Marathon")),
    P("P42",
      stat(0, "22 SEP 1942", "Mainland water reaches Key West for the first time", "Florida Keys Aqueduct Authority history"),
      m("reached Key West for", v(SFLA, routes=PIPE, places=[KEYWEST])),
      photo("It took about six", PH_KW_NARA2, "Key West")),
    P("P43",
      photo(0, PH_KW_NARA3, "Key West"),
      photo("With water you could", PH_SUNSETKEY, "Sunset Key off Key West"),
      chart("In 1940, about fourteen", "People in Monroe County", "", [["1940", 14078], ["1950", 29957], ["1960", 47921]], "US Census", highlight=2),
      photo("Twenty years later, nearly", PH_MARATHON, "Marathon")),
    P("P44",
      sat(0, -80.50, 25.46, 0.2, "Florida City, where the wells are"),
      m("It runs down the", v(KEYS, routes=PIPE)),
      sat("all the way to", -81.17, 24.70, 0.08, "The pipe crosses on the bridges")),
    P("P44b",
      stat(0, "17 MILLION", "Gallons of water a day down the pipe", FKAA),
      photo("The whole system now", PH_7MILE_SUN, "The Seven Mile Bridge")),
    P("P45",
      m(0, v(KEYS, routes=ROAD)),
      photo("So does the fuel,", PH_KW2008, "Key West")),
    P("P45b",
      m(0, v(KEYS, highlight=[KEYS_RED], routes=ROAD)),
      m("We took every block", v(KEYS, highlight=[KEYS_ALT])),
      sat("and measured how far", -81.07, 24.72, 0.12, "Marathon along US 1")),
    P("P45c",
      stat(0, "49 %", "Keys residents within a quarter mile of US 1", OWN_ROAD),
      sat("within a quarter of", -80.63, 24.93, 0.1, "Islamorada along US 1"),
      stat("More than nine in", "93 %", "Keys residents within one mile of US 1", OWN_ROAD)),
    P("P45d",
      sat(0, -81.735, 24.572, 0.08, "Stock Island"),
      photo("After Irma, they were", PH_IRMA_DEBRIS, "After Irma, 2017"),
      stat("makes about four million", "4 MILLION", "Gallons a day from the Stock Island seawater plant (2025)", FKAA)),
    P("P46",
      sat(0, -80.45, 25.30, 0.2, "Where the road leaves the mainland"),
      photo("And a strip that", PH_HWY, "The Overseas Highway")),
)

# ================================================================== 5. One Road, One Door
chapter(
    P("P47",
      m(0, v(SFLA, highlight=[DADE_RED], places=[FLCITY], routes=ROAD)),
      sat("In 1982, somebody shut", -80.47, 25.40, 0.08, "US 1 south of Florida City")),
    P("P48",
      m(0, v(STRAITS, places=[MARIEL, KEYWEST], arrows=MARIELA)),
      stat("had crossed the Straits", "125,000+", "Cubans in the Mariel boatlift, 1980", "Britannica"),
      photo("Most of them landed", PH_MARIEL_CENTER, "A refugee centre, 1980"),
      stat("On one day in", "4,588", "Cubans arriving at Key West on 11 May 1980", "Miami Herald"),
      m("The Border Patrol now", v(SFLA, places=[FLCITY], routes=ROAD))),
    P("P49",
      m(0, v(UPPER, places=[FLCITY], routes=ROAD)),
      sat("just south of Florida", -80.47, 25.42, 0.1, "The highway at Florida City"),
      photo("Every car leaving the", PH_LOWERKEYS, "The Lower Keys")),
    P("P50",
      sat(0, -80.44, 25.20, 0.2, "The road onto Key Largo"),
      photo("Key West's leaders went", PH_CITYHALL, "Key West City Hall")),
    P("P51",
      stat(0, "23 APR 1982", "Key West declares itself the Conch Republic", "Florida Historical Society"),
      photo("The city had left", PH_CONCH_FLAG, "The Conch Republic flag, Key West")),
    P("P52",
      photo(0, PH_MALLORY, "Mallory Square, Key West"),
      photo("and the Keys still", PH_CONCH_PASS, "A Conch Republic 'passport office'")),
    P("P53",
      sat(0, -81.20, 24.69, 0.12, "One road in, one road out"),
      m("And in a hurricane,", v(KEYS, routes=ROAD, arrows=OUT))),
    P("P54",
      m(0, v(SFLA, highlight=[KEYS_RED], places=[FLCITY])),
      sat("All the permanent residents", -80.60, 24.95, 0.3, "The Upper Keys"),
      stat("in no more than", "24.5 HOURS", "Legal limit to evacuate the Keys' permanent residents", FLSTAT)),
    P("P54b",
      stat(0, "24 → 24.5", "Hours allowed, before and after the 2025 law", "Laws of Florida, ch. 2025-190"),
      sat("and ordered a new", -80.40, 25.10, 0.15, "Key Largo")),
    P("P55",
      sat(0, -81.40, 24.66, 0.2, "Big Pine Key"),
      sat("so the state hands", -80.55, 24.98, 0.12, "Plantation Key")),
    P("P56",
      sat(0, -81.52, 24.665, 0.08, "Cudjoe Key"),
      photo("because they are ordered", PH_IRMA_DEBRIS, "After Irma, 2017")),
    P("P57",
      m(0, v(SFLA, places=[KEYWEST], arrows=IRMA)),
      photo("Hurricane Irma was heading", PH_IRMA_SAT, "Irma over the Keys, 10 September 2017"),
      stat("On the morning of", "6 SEP 2017", "Visitors ordered out at 7 a.m., residents at 7 p.m.", MONROE),
      m("That evening, the order", v(KEYS, routes=ROAD, arrows=OUT))),
    P("P58",
      m(0, v(LOWER, places=[CUDJOE], highlight=[LOWER_RED])),
      sat("in the Lower Keys,", -81.50, 24.67, 0.15, "Cudjoe Key")),
    P("P59",
      stat(0, "1,179", "Homes destroyed by Irma in the Keys", MONROE),
      photo("were mobile homes and", PH_IRMA_19, "After Irma, 2017")),
    P("P60",
      photo(0, PH_IRMA_VISIT, "Officials in the Keys after Irma"),
      m("Two short stretches of", v(UPPER, places=[MILE74])),
      sat("and had to be", -80.78, 24.85, 0.1, "The highway near mile 74")),
    P("P61",
      photo(0, PH_IRMA_NIGHT, "Florida's lights before and after Irma"),
      m("But the homes that", v(LOWER, highlight=[LOWER_RED])),
      sat("and with permits capped,", -81.36, 24.69, 0.08, "Big Pine Key")),
    P("P62",
      sat(0, -80.83, 24.82, 0.12, "Long Key"),
      m("It is the sea", v(KEYS, highlight=[KEYS_RED]))),
)

# ================================================================== 6. The Sea Is Coming Up the Road
chapter(
    P("P63",
      m(0, v(KEYS, places=[KEYWEST], highlight=[KEYS_RED])),
      photo("The sea is no", PH_PIGEON_1938, "The highway, 1938")),
    P("P63b",
      m(0, v(KEYS, highlight=[KEYS_ALT])),
      sat("mangrove islands included,", -81.45, 24.70, 0.3, "Mangrove islands of the Lower Keys")),
    P("P63c",
      chart(0, "Share of the Keys' land", "%", [["Under 3 ft", 81], ["Under 5 ft", 91], ["Under 10 ft", 98.5]], OWN_HEIGHT, highlight=0),
      sat("The highest ground is", -80.66, 24.96, 0.1, "Windley Key")),
    P("P64",
      sat(0, -81.808, 24.553, 0.08, "The Key West tide gauge"),
      photo("We took NOAA's monthly", PH_KW_HARBOR, "Key West harbour")),
    P("P65",
      chart(0, "Sea level at Key West vs 1913-22", "in", [["1913-22", 0], ["2016-25", 11.6]], OWN_SEA, highlight=1),
      stat("And over the last", "2.4×", "Rise since 1996 vs the 1913-2025 rate (6.4 vs 2.65 mm a year)", OWN_SEA),
      sat("as fast as the", -81.79, 24.548, 0.12, "Key West's south shore")),
    P("P66",
      photo(0, PH_WILMA, "A flooded street in Key West"),
      m("on days with no", v(UPPER, places=[KEYLARGO])),
      sat("In the autumn of", -80.42, 25.14, 0.08, "Stillwright Point, Key Largo"),
      stat("stayed under the tide", "94 DAYS", "Streets under the king tides, autumn 2019", "Keys Weekly; WLRN")),
    P("P67",
      m(0, v(KEYS, highlight=[KEYS_RED])),
      sat("about a hundred and", -81.06, 24.725, 0.18, "Streets of Marathon"),
      stat("The answer was about", "$1.8 BILLION", "To raise about 150 miles of county roads", MONROE)),
    P("P68",
      sat(0, -80.44, 25.08, 0.08, "Twin Lakes, Key Largo"),
      stat("Less than a mile", "$22 MILLION", "Twin Lakes road project, under one mile", MONROE)),
    P("P68b",
      photo(0, PH_7MILE_SUN, "The Seven Mile Bridge"),
      stat("In the early 1980s", "37 OF 44", "Old bridges replaced in the early 1980s", "Florida Memory"),
      photo("most of them Flagler's", PH_KK_TRAIN, "One of Flagler's railway bridges"),
      sat("The new Seven Mile", -81.12, 24.71, 0.12, "The new and old Seven Mile Bridges")),
    P("P69",
      m(0, v(LOWER, routes=ROAD)),
      photo("Its longest bridge, the", PH_7MILE_AIR, "The Seven Mile Bridge"),
      stat("and the state's early", "$677 MILLION", "Early estimate for a new Seven Mile Bridge", "FDOT, via Miami Herald 2024")),
    P("P69b",
      photo(0, PH_ELKHORN, "Elkhorn coral, Molasses Reef, 2008"),
      sat("In the summer of", -80.375, 25.01, 0.12, "Molasses Reef, off Key Largo"),
      stat("grew hotter than it", "150+ YEARS", "Hottest water on Florida's reef in the record", "Science, 2025"),
      stat("and nearly all the", "97.8-100 %", "Of the remaining elkhorn and staghorn corals died, 2023", "Science, 2025"),
      stat("Scientists now call both", "FUNCTIONALLY EXTINCT", "Elkhorn and staghorn coral in Florida after 2023", "Science, 2025")),
    P("P70",
      stat(0, "~80,000", "People in the Keys", CENSUS),
      sat("Every road raised and", -81.06, 24.725, 0.1, "Marathon")),
    P("P71",
      photo(0, PH_FRED, "The old Seven Mile Bridge"),
      photo("Its first two miles", PH_FRED2, "The old bridge, now a footpath"),
      sat("out to Pigeon Key.", -81.155, 24.704, 0.08, "Pigeon Key"),
      photo("Further on, a span", PH_BH_NOW, "A missing span: the old Bahia Honda bridge")),
)

# ================================================================== Ending
chapter(
    P("P72",
      m(0, v(FLA, highlight=[KEYS_RED]))),
    P("P73",
      photo(0, PH_KW_1884, "Key West, 1884"),
      photo("A railroad reached it,", PH_GUIDE1912, "The line over the sea, 1912"),
      photo("The islands had no", PH_CISTERN, "A Key West cistern"),
      m("And because it is", v(KEYS, routes=ROAD, arrows=OUT)),
      photo("the reason the Keys", PH_SUNSETKEY, "Key West")),
    P("P74",
      photo(0, PH_CONCH_FLAG, "The Conch Republic flag"),
      photo("The storm of 1935", PH_PATH1935, "The storm's track, 1935"),
      sat("The price of keeping", -81.17, 24.70, 0.25, "The Seven Mile Bridge")),
    P("P74b",
      sat(0, -80.63, 24.92, 0.25, "Islamorada"),
      stat("Nine in ten people", "93 %", "Within one mile of US 1", OWN_ROAD),
      stat("Four-fifths of the land", "81 %", "Of the land under 3 feet", OWN_HEIGHT),
      stat("And that sea is", "+1 FT", "Sea level at Key West since the gauge began", OWN_SEA),
      sat("when the gauge at", -81.808, 24.553, 0.14, "Key West")),
    P("P74c",
      photo(0, PH_BH_RAIL, "Old and new bridges at Bahia Honda"),
      sat("The next rebuild will", -80.95, 24.78, 0.6, "The Middle Keys")),
    P("P75",
      photo(0, PH_SUGARLOAF, "The Lower Keys"),
      m("or should the Keys", v(SFLA, highlight=[KEYS_RED], routes=ROAD)),
      ask=("Would you keep paying", "Keep paying to hold the road above the sea, or go back to boats?")),
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


TITLE = "Why the Florida Keys Hang on a Single Road"
script = {
    "title": TITLE,
    "voice": "am_michael",
    "voice_speed": 1.15,
    "music": "procedural",
    "map_style": "satellite",
    "look": "none",
    "photo_upscale": True,
    "sources": ["episodes/florida-keys/research.md and factcheck.md", "Contains modified Copernicus Sentinel data 2025",
                "Sea level: own calculation from NOAA CO-OPS monthly means, Key West 8724580 (geo/measure_sealevel.py)",
                "People near US 1: own count from 2020 census blocks (US Census Bureau) and TIGER/Line roads (geo/measure_road.py)",
                "Land height: own sample of 1,500 points, USGS 3DEP via EPQS (geo/measure_height.py)",
                "Islands: 2020 census land blocks minus TIGER area water (geo/make_regions.py)",
                "Road, railway, pipe, ferry, train and storm lines drawn through main points (approximate)"],
    "thumbnail": {"text": "ONE ROAD"},
    "chapters": chapters,
    "youtube": {
        "title": TITLE,
        "title_candidates": [TITLE, "Why America Built a Highway Across the Sea", "Why the Florida Keys Have Only One Way Out"],
        "description": "The Florida Keys hang on one road, more than a hundred miles of highway and bridges over the sea. Their people, their drinking water and their only way out all depend on it. We follow why it was built and whether it can be kept: Key West, once the biggest city in Florida; Flagler's railroad across the sea; the Labor Day hurricane of 1935 that destroyed it and left the road; the 1942 Navy pipe that still carries every drop of water; the 1982 roadblock and the Conch Republic; the 24.5-hour evacuation rule that caps new homes; Hurricane Irma; and the rising sea, measured at the Key West tide gauge since 1913.",
        "tags": ["Florida Keys", "Key West", "Overseas Highway", "Seven Mile Bridge", "Overseas Railroad", "Henry Flagler",
                 "1935 Labor Day hurricane", "Conch Republic", "Hurricane Irma", "sea level rise", "US 1", "Florida geography",
                 "geography", "satellite images"],
        "pinned_comment": "Would you keep paying to hold a road above a rising sea, or should the Keys one day go back to boats?",
    },
}
out = HERE / "script.json"
out.write_text(json.dumps(script, ensure_ascii=False, indent=1) + chr(10), encoding="utf-8")
words = sum(len(p["text"].split()) for c in chapters for p in c["paragraphs"])
shots = [s for c in chapters for p in c["paragraphs"] for s in p["shots"]]
kinds = {k: sum(1 for s in shots if s["type"] == k) for k in ("map", "photo", "stat", "document", "chart")}
print(f"{words} words, {len(chapters)} chapters, {len(shots)} shots {kinds}")
