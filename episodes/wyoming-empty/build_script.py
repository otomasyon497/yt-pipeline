"""Builds script.json for wyoming-empty.  python build_script.py

Same production logic as episodes/uruguay-empty (hand-placed shots, a photo or map frame at most twice, 60 s apart,
every reason opens on a painted map). The narration lives in drafts/narration.md; every sentence comes from
research.md. Photos and satellite tests: visuals.md. Regions: geo/make_regions.py; the railway band: geo/measure_rail.py.
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
SU = "2025-07-01/2025-09-20"    # northern summer 2025: scratch wysat.py 2026-11-27, clear on every view used
L24 = "2024-07-01/2024-09-15"   # Laramie: the 2025 summer scene had cloud over the town


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
US = {"lon": -97.0, "lat": 39.5, "span": 62.0}         # the lower 48
WYV = {"lon": -107.55, "lat": 42.76, "span": 16.0}     # Wyoming (prefit size; fresh() reframes each use)
WEST = {"lon": -108.0, "lat": 41.5, "span": 21.0}      # Wyoming with Colorado, Utah, Idaho, Montana
FARW = {"lon": -112.0, "lat": 42.0, "span": 34.0}      # Oregon to Nebraska
SOUTH = {"lon": -107.6, "lat": 41.75, "span": 7.2}     # the railway corridor
NORTH = {"lon": -106.4, "lat": 44.0, "span": 3.6}      # Johnson County, Buffalo to Casper
TETONV = {"lon": -110.95, "lat": 43.6, "span": 2.8}    # Jackson Hole and the Idaho side
FRONT = {"lon": -105.2, "lat": 40.45, "span": 7.2}      # Laramie to Denver
ATL = {"lon": -50.0, "lat": 46.0, "span": 105.0}       # Britain to Wyoming
CIRC10 = {"lon": -103.0, "lat": 38.5, "span": 24.0}    # the six states of the 10th Circuit

WY_RED, WY_ALT = "Wyoming@red", "Wyoming@alt"
CO_RED, CO_ALT = "Colorado@red", "Colorado@alt"
UK_ON = "file:uk_on_wy.geojson@red"
FED_RED, FED_ALT = "file:federal.geojson@red", "file:federal.geojson@alt"
BLM_RED = "file:blm.geojson@red"
PARKS_RED = "file:parks.geojson@red"
LINE_RED = "file:line1868.geojson@red"
BAND_RED, BAND_ALT = "file:rail20.geojson@red", "file:rail20.geojson@alt"
JOHNSON_RED = "file:county_johnson.geojson@red"
TETON_RED = "file:county_teton.geojson@red"
CARBON_RED = "file:county_carbon.geojson@red"
CAMPBELL_RED = "file:county_campbell.geojson@red"
NATRONA_ALT = "file:county_natrona.geojson@alt"
CHECKER = "file:checker.geojson@red"
TENTH = [s + "@red" for s in ("Wyoming", "Colorado", "Utah", "New Mexico", "Kansas", "Oklahoma")]


# ------------------------------------------------------------------ sources (research.md)
CENSUS = "US Census Bureau, Vintage 2025 estimates"
OWN_RAIL = "Own count: 2020 census block groups vs the 1868 line (geo/measure_rail.py)"
OWN_SMA = "Own measurement: BLM Surface Management Agency data (geo/make_regions.py)"
NPS = "National Park Service"
WYOHIST = "WyoHistory.org (Wyoming State Historical Society)"
WYDOT = "Wyoming Department of Transportation"
WYOFILE = "WyoFile"

# ------------------------------------------------------------------ photos (visuals.md; all PD / CC0 / CC BY, checked 2026-11-27)
PH_SADDLE = "This broad open saddle called South Pass in Wyoming located on the continental divide is one of the high points along the Oregon (f87089a1-155d-451f-67c6-1277b1f30ec3).JPG"
PH_SP_ACEC = "South Pass Area of Critical Environmental Concern, Wyoming (15472769319).jpg"
PH_SP_OVER = "B-14. South Pass Overlook (west of South Pass City) on the California, Mormon Pioneer, and Oregon National Historic Trails (2003) (49008a89-8329-4aac-93d1-cd43c3407933).JPG"
PH_RUTS1 = "Oregon Trail ruts Guernsey Wy.jpg"
PH_RUTS2 = "Oregon Trail Wagon Ruts - panoramio.jpg"
PH_BEDLAM = "A-12. The Bedlam Ruts (west of Fort Laramie National Historic Site) on the California, Mormon Pioneer, and Oregon National Historic Trails (2006) (a3b55225-3e5d-4675-8d62-e97ef09219a1).jpg"
PH_FTLAR_1868 = "Fort Laramie. Post as it appeared in 1868. Orginally located as a fur trading post in 1834, known as Fort William... - NARA - 516878.jpg"
PH_MILLER = "Alfred Jacob Miller - Fort Laramie - Walters 37194049.jpg"
PH_BRIDGER = "An afternoon of croquet. Ladies, gentlemen, and children on the lawn at Fort Bridger, Wyo. Terr., ca. 1873. Officers' qu - NARA - 530927.jpg"
PH_WAGON1 = "Emigrant National Historic Trail, Wyoming (36346399930).jpg"
PH_WAGON2 = "Emigrant National Historic Trail, Wyoming (36346409040).jpg"
PH_REGISTER = "Register Cliff - panoramio.jpg"
PH_CASEMENT = "Captain Andrew Joseph Russell - General John S. Casement and His Outfit - Google Art Project.jpg"
PH_CITADEL = "CitadelRockGreenRiverWyoming1868.jpg"
PH_CHURCHB = "Andrew J. Russell - Church Buttes, 1868.jpg"
PH_DALE = "Dale Creek Bridge Union Pacific Railroad Company by Andrew J Russell.jpg"
PH_SANDERS = "Generals Grant, Sherman, Sheridan, Hooker, Harney, Dodge, Gibbon, and Potter at Fort Sanders LCCN2013647598.jpg"
PH_CHEY_1876 = "\"Cheyenne, Wyo., 1876.\" General view of this town on the Oregon Trail - NARA - 531115.tif"
PH_BEARRIVER = "Railroad restaurant in Bear River City, Wyoming - DPLA - f952f358c59683fed05088ecc8973626.jpg"
PH_LAR_DEPOT = "1885 Picture of the Laramie Depot.jpg"
PH_CHEY_DEPOT = "Cheyenne WY UP depot.JPG"
PH_GRANITE = "Granite cut, near Dale Creek bridge, West Cheyenne. Albany County, Wyoming. - NARA - 516612.jpg"
PH_BRANDING = "Cattle branding (Grabill 1888).jpg"
PH_COWBOY = "Cowboy1902.jpg"
PH_DRIVE = "Cattle Drive near Pinedale, WY (14963962303).jpg"
PH_INVADERS = "Invaders.gif"
PH_TAMAP = "TAranch.jpg"
PH_SUFFRAGE = "Woman suffrage in Wyoming Territory. - Scene at the polls in Cheyenne - from a photo. by Kirkland. LCCN92516129.jpg#crop=0.12,0.22,0.12,0.06"
PH_MOULTON = "Looking northwest past Ranch House and Barn toward Grand Teton - T. A. Moulton Ranch, Mormon Row Road, Kelly, Teton County, WY HABS WYO,20-KEL.V,2-9.tif"
PH_HAYDEN = "Hayden Survey by W.H.Jackson.jpg"
PH_JACKSON = "Downtown Jackson Wyoming.jpg"
PH_BARN = "Barns grand tetons.jpg"
PH_ELKREF = "National Elk Refuge (7467049882).jpg"
PH_HORSES = "BLM Wyoming- Salt Wells Creek Herd Management Area (19834956313).jpg"
PH_REDDESERT = "Red Desert.jpg"
PH_BIKE = "Bikepacking through Great Divide Basin, Wyoming, USA.jpg"
PH_PRONGHORN = "PronghornAntelopeHerdYNP2009.jpg"
PH_I80 = "I-80 toward Rawlins and Laramie - Wyoming (53577131945).jpg"
PH_MUDDY = "Muddy Water Red desert.jpg"
PH_GROUSE = "Greater Sage-Grouse in Red Desert, WY (7487155676).jpg"
PH_SEEDS = "Seedskadee nwr sunset.jpg"
PH_SAGESNOW = "Artemesia tridentata var wyomingensis Wyoming big sagebrush (52752054243).jpg"
PH_TEAPOT = "OIL WELLS NEAR TEAPOT DOME, WYOMING - NARA - 549208 (restored).jpg"
PH_FALL = "Albert B. Fall.jpg"
PH_SINCLAIR = "Harry F. Sinclair, multimillionaire oil magnate (left) and his counsel Martin W. Littleton. Teapot Dome hearing LCCN2016893277.jpg"
PH_FALL_GUILTY = "Former Secretary of Interior found guilty of bribery. Albert B. Fall, former Secretary of Interior, leaving the District and Supreme Court in Washington today surrounded by members of his LCCN2016889499.jpg"
PH_JC1 = "Jeffrey City, Wyoming 1.JPG"
PH_JC2 = "Jeffrey City, Wyoming 2.JPG"
PH_TRUCK = "Coal Haul Truck at North Antelope Rochelle.png"
PH_NARM = "New Antelope Rochelle Coal Mine.png"
PH_DRAGLINE = "Coal Mining Dragline.png"
PH_RS_1919 = "Front Street, downtown Rock Springs in 1919.jpg"
PH_HANNA = "2009-0722-Hanna.jpg"
PH_GIL_POST = "Postcard - Aeroplane View, Gillette, Wyoming. (front).jpg"
PH_GIL_NOW = "Downtown Gillette Wyoming in Summer (54271653951).jpg"
PH_WIND = "Wind Power 4892597382.jpg"
PH_LAR_NOW = "Downtown Laramie Wyoming (52953967558).jpg"
PH_UW = "Arts and Sciences Building - University of Wyoming - Laramie (52040416492).jpg"
PH_UNION = "Wyoming Union 2009.jpg"
PH_CASPER = "Natrona County Courthouse.JPG"

# ------------------------------------------------------------------ places, routes and arrows
CHEYENNE = place("Cheyenne", -104.82, 41.14, "Cheyenne", "capital")
LARAMIE = place("Laramie", -105.59, 41.31, "Laramie", "city")
RAWLINS = place("Rawlins", -107.24, 41.79, "Rawlins", "city")
ROCKSPR = place("Rock Springs", -109.22, 41.59, "Rock Springs", "city")
GREENR = place("Green River", -109.47, 41.53, "Green River", "city")
EVANSTON = place("Evanston", -110.96, 41.27, "Evanston", "city")
CASPER = place("Casper", -106.31, 42.85, "Casper", "city")
GILLETTE = place("Gillette", -105.50, 44.29, "Gillette", "city")
JACKSON = place("Jackson", -110.76, 43.48, "Jackson", "city")
VICTOR = place("Victor", -111.11, 43.60, "Idaho side", "city")
KEMMERER = place("Kemmerer", -110.54, 41.79, "Kemmerer", "site", icon="factory")
JEFFREY = place("Jeffrey City", -107.83, 42.50, "Jeffrey City", "site")
BENTON = place("Benton", -107.03, 41.80, "Benton, 1868", "site")
ELKMTN = place("Elk Mountain", -106.41, 41.69, "Elk Mountain", "site")
TEAPOT = place("Teapot Dome", -106.23, 43.27, "Teapot Dome", "site", icon="factory")
HANNA = place("Hanna", -106.56, 41.87, "Hanna", "site", icon="factory")
SOUTHPASS = place("South Pass", -108.90, 42.35, "South Pass", "site")
FTLARAMIE = place("Fort Laramie", -104.56, 42.21, "Fort Laramie", "site")
FTBRIDGER = place("Fort Bridger", -110.39, 41.32, "Fort Bridger", "site")
GUERNSEY = place("Guernsey", -104.75, 42.26, "Guernsey ruts", "site")
DIVIDE = place("Great Divide Basin", -108.20, 42.00, "GREAT DIVIDE BASIN", "label")
KC = place("KC Ranch", -106.64, 43.71, "KC Ranch", "site", icon="conflict")
BUFFALO = place("Buffalo", -106.70, 44.35, "Buffalo", "city")
TA = place("TA Ranch", -106.62, 44.27, "TA Ranch", "site", icon="conflict")
FTMCK = place("Fort McKinney", -106.78, 44.34, "Fort McKinney", "site")
CHOKE = place("Chokecherry", -107.20, 41.60, "Wind farm site", "site", icon="factory")
DENVER = place("Denver", -104.99, 39.74, "Denver", "city")
FTCOLLINS = place("Fort Collins", -105.08, 40.59, "Fort Collins", "city")
SLC = place("Salt Lake City", -111.89, 40.76, "Salt Lake City", "city")
DC = place("Washington", -77.04, 38.90, "Washington, D.C.", "capital")
LONDON = place("London", -0.13, 51.51, "London", "capital")
L_OREGON = place("Oregon", -122.6, 44.9, "OREGON", "label")
L_CALIF = place("California", -121.0, 38.8, "CALIFORNIA", "label")
L_UTAH = place("Utah", -111.9, 40.4, "SALT LAKE", "label")

TRAIL = [{"from": [-104.05, 41.95], "via": [[-104.56, 42.21], [-105.40, 42.55], [-106.32, 42.85], [-107.13, 42.49], [-108.90, 42.35], [-110.39, 41.32]],
          "to": [-111.05, 41.40], "mode": "line", "label": "Emigrant trails (approx.)", "color": "accent", "seconds": 3.0}]
TRAIL_US = [{"from": [-95.9, 41.2], "via": [[-104.56, 42.21], [-108.90, 42.35]], "to": [-122.6, 45.4], "mode": "line",
             "label": "Oregon Trail (approx.)", "color": "accent", "seconds": 3.0}]
THREE = [{"from": [-108.9, 42.35], "to": [-122.6, 44.9], "color": "red", "bend": 0.12},
         {"from": [-108.9, 42.35], "to": [-121.0, 38.8], "color": "red", "bend": -0.1},
         {"from": [-108.9, 42.35], "to": [-111.9, 40.8], "color": "red", "bend": 0.15}]
RAIL1868 = [{"from": [-104.05, 41.18], "via": [[-104.82, 41.14], [-105.59, 41.31], [-106.20, 41.90], [-107.24, 41.79], [-108.78, 41.68],
             [-109.22, 41.59], [-109.97, 41.60]], "to": [-111.05, 41.25], "mode": "line", "label": "Union Pacific, 1868", "color": "accent", "seconds": 3.0}]
TRAIN = {"from": [-104.82, 41.14], "via": [[-105.40, 42.30]], "to": [-106.31, 42.85], "mode": "line", "label": "Special train, April 1892", "color": "red", "seconds": 2.5}
RIDE = [{"from": [-106.31, 42.85], "to": [-106.64, 43.71], "color": "red", "label": "On horseback", "bend": 0.1}]
POSSE = [{"from": [-106.70, 44.35], "to": [-106.62, 44.29], "color": "blue", "bend": 0.3}]
CAVALRY = [{"from": [-106.78, 44.34], "to": [-106.63, 44.28], "color": "blue", "bend": -0.3}]
MONEY = [{"from": [-0.13, 51.51], "to": [-104.82, 41.14], "color": "red", "label": "British money", "bend": 0.12}]
LEAVERS = [{"from": [-105.59, 41.31], "to": [-104.99, 39.74], "color": "red", "label": "The young leave", "bend": 0.2},
           {"from": [-105.59, 41.31], "to": [-105.08, 40.59], "color": "red", "bend": -0.2},
           {"from": [-107.5, 42.6], "to": [-111.89, 40.76], "color": "red", "bend": 0.15}]
TETONPASS = {"from": [-111.11, 43.60], "via": [[-110.95, 43.50]], "to": [-110.76, 43.48], "mode": "line", "label": "Over Teton Pass", "color": "red", "seconds": 2.5}

chapters = []
heads = iter(HEADS)


def chapter(*paras):
    title, mood = next(heads)
    chapters.append({"title": title, "mood": mood, "paragraphs": list(paras)})


# ================================================================== Hook
chapter(
    P("P0",
      m(0, v(US, highlight=[WY_RED])),
      m("on the way west.", v(US, highlight=[WY_RED], routes=TRAIL_US)),
      photo("Almost none of them", PH_WAGON1, "Emigrant trail country, Wyoming")),
    P("P1",
      m(0, v(WYV, highlight=[WY_ALT, UK_ON]), text="The United Kingdom at the same scale"),
      chart("But fewer people live", "People, July 2025", "", [["Wyoming", 588753], ["Washington, D.C.", 693645]], CENSUS, highlight=0)),
    P("P2",
      photo(0, PH_CHEY_DEPOT, "The old Union Pacific depot, Cheyenne"),
      sat("has about sixty-five thousand", -104.80, 41.14, 0.2, "Cheyenne"),
      photo("Drive west from it", PH_I80, "Interstate 80, Wyoming"),
      sat("and the houses run", -105.00, 41.17, 0.12, "West of Cheyenne")),
    P("P3",
      photo(0, PH_DRIVE, "A cattle drive near Pinedale"),
      m("once hired gunmen to", v(WYV, highlight=[JOHNSON_RED])),
      sat("Where four hunters were", -106.42, 41.69, 0.6, "Elk Mountain", highlight=[CHECKER]),
      photo("And where a whole", PH_JC1, "Jeffrey City today"),
      sat("emptied in a few", -107.83, 42.495, 0.08, "Jeffrey City")),
    P("P4",
      m(0, v(WYV, highlight=[WY_RED])),
      photo("There are six reasons,", PH_SEEDS, "Seedskadee National Wildlife Refuge"),
      sat("still shows on the", -108.30, 41.95, 0.4, "The Great Divide Basin"),
      photo("The first is the", PH_WAGON2, "On the emigrant trails, Wyoming")),
)

# ================================================================== 1. A Road, Not a Destination
chapter(
    P("P5",
      m(0, v(WYV, highlight=[WY_RED], routes=TRAIL)),
      photo("not a place to", PH_SP_OVER, "South Pass overlook")),
    P("P6",
      stat(0, "~500,000", "Emigrants on the Oregon, California and Mormon trails, 1840-1869", NPS),
      photo("crossed it on the", PH_MILLER, "Fort Laramie, painted by Alfred Jacob Miller, 1850s"),
      m("Almost all of them", v(WYV, places=[SOUTHPASS], routes=TRAIL)),
      photo("South Pass.", PH_SP_ACEC, "South Pass")),
    P("P7",
      photo(0, PH_SADDLE, "South Pass, on the Continental Divide"),
      sat("wagons could roll over", -108.90, 42.35, 0.25, "South Pass from orbit"),
      stat("It is also more", "7,412 FT", "South Pass, the emigrants' crossing", "WyoHistory; NPS")),
    P("P7b",
      m(0, v(WYV, places=[FTLARAMIE, FTBRIDGER], routes=TRAIL)),
      sat("Fort Laramie, on the", -104.56, 42.21, 0.1, "Fort Laramie and the North Platte"),
      photo("and later an army", PH_FTLAR_1868, "Fort Laramie as it was in 1868"),
      sat("Fort Bridger, in the", -110.39, 41.32, 0.1, "Fort Bridger"),
      photo("These were service stations,", PH_REGISTER, "Register Cliff, where emigrants carved their names")),
    P("P7c",
      photo(0, PH_RUTS1, "The Oregon Trail ruts at Guernsey"),
      sat("near today's town of", -104.752, 42.255, 0.08, "Guernsey and the North Platte"),
      photo("in places five feet", PH_RUTS2, "The Guernsey ruts"),
      photo("You can still walk", PH_BEDLAM, "Wagon ruts west of Fort Laramie")),
    P("P8",
      m(0, v(WYV, highlight=[WY_RED])),
      stat("The average height of", "6,700 FT", "Wyoming's average elevation", "USGS"),
      m("Only Colorado sits higher.", v(WEST, highlight=[WY_ALT, CO_RED]))),
    P("P9",
      photo(0, PH_GROUSE, "The Red Desert"),
      photo("In the high basins,", PH_SAGESNOW, "Sagebrush in winter"),
      stat("On average the state", "~13 IN", "Rain and snow a year, Wyoming average (1961-1990)", "National Atlas of the United States"),
      photo("In the western basins", PH_MUDDY, "The Red Desert"),
      m("Iowa's farms get more", v(US, highlight=["Iowa@red", WY_ALT])),
      sat("more than twice as", -93.60, 42.00, 0.15, "Farmland in Iowa")),
    P("P10",
      m(0, v(WYV, places=[DIVIDE])),
      sat("where the Continental Divide", -108.30, 41.95, 0.5, "The Great Divide Basin"),
      photo("Rain that falls here", PH_BIKE, "Inside the Great Divide Basin"),
      photo("It sinks into the", PH_REDDESERT, "The Red Desert")),
    P("P10b",
      m(0, v(SOUTH, places=[CHEYENNE, LARAMIE, RAWLINS, ROCKSPR])),
      photo("On Interstate 80, gusts", PH_I80, "Interstate 80"),
      stat("of sixty miles an", "60 MPH", "Gusts that close I-80 to light, high-profile vehicles", WYDOT),
      stat("Even so, the wind", "~47 A YEAR", "Vehicles blown over on I-80 (five-year average)", WYDOT)),
    P("P11",
      photo(0, PH_WAGON1, "A replica wagon on the emigrant trail"),
      m("Oregon had rain.", v(FARW, places=[L_OREGON, L_CALIF, L_UTAH], arrows=THREE)),
      m("Wyoming was the hard", v(FARW, highlight=[WY_RED]))),
    P("P12",
      photo(0, PH_WAGON2, "The emigrant trail"),
      sat("What finally made some", -108.90, 42.30, 0.6, "South Pass country"),
      photo("It was a railway.", PH_CASEMENT, "A Union Pacific track crew, 1868")),
)

# ================================================================== 2. The Railway Drew the Map
chapter(
    P("P13",
      m(0, v(WYV, highlight=[WY_ALT], routes=RAIL1868)),
      m("They were placed, one", v(SOUTH, highlight=[LINE_RED], places=[CHEYENNE, LARAMIE, RAWLINS]))),
    P("P14",
      photo(0, PH_GRANITE, "The Union Pacific cut west of Cheyenne, about 1869"),
      stat("In November the tracks", "~4,000", "People in Cheyenne when the tracks arrived, November 1867", WYOHIST),
      sat("were living there in", -104.82, 41.15, 0.35, "Crow Creek and Cheyenne"),
      photo("They called it Cheyenne,", PH_CHEY_1876, "Cheyenne in 1876"),
      sat("the Magic City of", -104.82, 41.135, 0.12, "Cheyenne today")),
    P("P15",
      photo(0, PH_CITADEL, "Citadel Rock and the new line near Green River, 1868"),
      m("Laramie.", v(SOUTH, highlight=[LINE_RED], places=[CHEYENNE, LARAMIE]),
        step("Rawlins.", places=[CHEYENNE, LARAMIE, RAWLINS]),
        step("Rock Springs.", places=[CHEYENNE, LARAMIE, RAWLINS, ROCKSPR]),
        step("Green River.", places=[CHEYENNE, LARAMIE, RAWLINS, ROCKSPR, GREENR]),
        step("Evanston.", places=[CHEYENNE, LARAMIE, RAWLINS, ROCKSPR, GREENR, EVANSTON]))),
    P("P15b",
      sat(0, -107.10, 41.78, 0.4, "The desert east of Rawlins"),
      m("Benton, in the desert", v(SOUTH, highlight=[LINE_RED], places=[BENTON, RAWLINS])),
      stat("For a few weeks", "~3,000", "People in Benton, summer 1868", "Carbon County Museum; WyoHistory"),
      m("Then the tracks moved", v(SOUTH, routes=RAIL1868, places=[BENTON])),
      sat("Today there is nothing", -107.03, 41.80, 0.1, "Near the Benton site, by today's Sinclair")),
    P("P15c",
      photo(0, PH_DALE, "Dale Creek Bridge, Union Pacific, 1868"),
      photo("They were the railway's", PH_SANDERS, "Grant, Sherman and the railway's engineer Dodge at Fort Sanders, 1868")),
    P("P16",
      m(0, v(WYV, highlight=[LINE_RED])),
      m("A band twelve miles", v(WYV, highlight=[BAND_RED])),
      chart("More than a third", "Within 20 km of the 1868 line", "%", [["Share of the land", 9.9], ["Share of the people", 35.3]], OWN_RAIL, highlight=1),
      m("Most of the rest", v(WYV, highlight=[BAND_ALT], places=[CASPER, GILLETTE]))),
    P("P16b",
      m(0, v(WYV, layer="night")),
      m("A line of towns", v(WYV, layer="night", routes=RAIL1868)),
      m("and in the north", v(WYV, layer="night")),
      m("mostly mine and oil", v(WYV, layer="night", places=[GILLETTE, CASPER]))),
    P("P17",
      m(0, v(SOUTH, routes=RAIL1868)),
      m("Congress gave the Union", v({"lon": -107.0, "lat": 41.9, "span": 10.8}, highlight=[LINE_RED])),
      stat("for twenty miles on", "20 MILES", "Railroad grant on each side of the track: every other square mile", "Pacific Railway Acts, 1862 and 1864"),
      sat("The government kept the", -106.47, 41.63, 0.7, "Elk Mountain: the grant pattern (illustration)", highlight=[CHECKER])),
    P("P18",
      m(0, v({"lon": -107.0, "lat": 42.4, "span": 17.5}, highlight=[BLM_RED])),
      sat("Private square, public square,", -106.39, 41.71, 0.55, "Railroad squares (illustration)", highlight=[CHECKER]),
      stat("They touch only at", "CORNER LOCKED", "Public squares meet only at their corners", "BLM; onX")),
    P("P19",
      photo(0, PH_PRONGHORN, "Pronghorn"),
      sat("Can you step from", -106.50, 41.61, 0.8, "One corner, Elk Mountain (illustration)", highlight=[CHECKER])),
    P("P20",
      stat(0, "2021", "Four Missouri hunters cross a corner at Elk Mountain", WYOFILE),
      sat("on Elk Mountain, using", -106.40, 41.70, 0.35, "Elk Mountain"),
      photo("The ranch belonged to", PH_HORSES, "Public range in southern Wyoming"),
      stat("claiming the step had", "$7.75 M", "Damage the ranch's company claimed", "Court filings, via WyoFile")),
    P("P21",
      stat(0, "2023 / 2025", "District court, then the 10th Circuit, rule for the hunters", "Iron Bar Holdings v. Cape"),
      stat("In October 2025 the", "20 OCT 2025", "The Supreme Court declines the case (No. 25-64)", "US Supreme Court docket"),
      m("Across the West, about", v(FARW, highlight=[WY_ALT])),
      stat("about eight million acres", "~8 MILLION ACRES", "Public land locked behind corners in the West", "onX, 2022")),
    P("P21b",
      m(0, v(WYV, highlight=[CARBON_RED])),
      stat("In April 2022 a", "NOT GUILTY", "Carbon County jury, 29 April 2022, after under two hours", WYOFILE),
      photo("after deliberating for less", PH_HANNA, "Carbon County from the air")),
    P("P22",
      photo(0, PH_CHEY_1876, "Cheyenne, 1876"),
      sat("But who would own", -105.90, 42.70, 0.3, "Grassland, central Wyoming"),
      photo("Cattle, and the men", PH_BRANDING, "Branding cattle, 1888")),
)

# ================================================================== 3. The Cattle Kings
chapter(
    P("P23",
      m(0, v(WYV, highlight=[JOHNSON_RED])),
      photo("by a few very", PH_DRIVE, "Cattle on the open range, Pinedale")),
    P("P24",
      sat(0, -106.00, 42.80, 0.15, "Open range, central Wyoming"),
      sat("Anyone could graze it.", -106.20, 42.90, 0.4, "Open range, central Wyoming"),
      m("Investors in Britain and", v(ATL, places=[LONDON, CHEYENNE], arrows=MONEY)),
      photo("In Cheyenne, their managers", PH_CHEY_DEPOT, "Cheyenne's Union Pacific depot")),
    P("P25",
      stat(0, "~900,000", "Cattle in Wyoming, late 1886", "Wyoming SHPO"),
      sat("far more than the", -106.05, 42.75, 0.25, "Grassland, central Wyoming"),
      photo("Then came the winter", PH_SAGESNOW, "Sagebrush under snow"),
      stat("Storm after storm buried", "1886-87", "The winter that ended the open range", "Wyoming SHPO")),
    P("P26",
      photo(0, PH_MOULTON, "A homestead in Jackson Hole"),
      m("Small ranchers and homesteaders", v(NORTH, highlight=[JOHNSON_RED], places=[BUFFALO])),
      stat("The big outfits called", "\"RUSTLERS\"", "What the big outfits called many small ranchers", WYOHIST)),
    P("P27",
      sat(0, -104.83, 41.13, 0.5, "Cheyenne, where the special train left"),
      m("A special train left", v(WYV, places=[CHEYENNE, CASPER], routes=[TRAIN])),
      stat("about fifty armed men,", "~50", "Armed men on the train, two dozen hired in Texas", WYOHIST),
      m("They carried a list", v(WYV, places=[CASPER, KC], routes=[TRAIN], arrows=RIDE))),
    P("P28",
      sat(0, -106.64, 43.71, 0.12, "Kaycee, by the old KC Ranch"),
      stat("Inside was Nate Champion,", "9 APRIL 1892", "Nate Champion besieged at the KC Ranch", WYOHIST),
      m("He held them off", v(NORTH, places=[KC, BUFFALO])),
      stat("His last line was", "NATHAN D. CHAMPION", "How his diary ends, 9 April 1892", "Champion's diary, published 1894"),
      sat("That evening they set", -106.62, 43.72, 0.3, "The Powder River country near Kaycee")),
    P("P29",
      m(0, v(NORTH, places=[KC, BUFFALO])),
      m("and a posse of", v(NORTH, places=[KC, BUFFALO, TA], arrows=POSSE)),
      sat("They trapped the invaders", -106.62, 44.27, 0.15, "The TA Ranch, on Crazy Woman Creek")),
    P("P30",
      stat(0, "13 APRIL 1892", "President Harrison orders the cavalry in", WYOHIST),
      m("sent the cavalry from", v(NORTH, places=[FTMCK, TA], arrows=CAVALRY)),
      stat("None of them was", "NO CONVICTIONS", "None of the invaders was ever convicted", WYOHIST)),
    P("P31",
      m(0, v(WYV, highlight=[WY_RED])),
      stat("The census of 1890", "62,555", "People in Wyoming, 1890 census", "US Census 1890"),
      sat("In the place where", -106.30, 44.10, 0.35, "Ranch country, Johnson County")),
    P("P31b",
      photo(0, PH_SUFFRAGE, "Women at the polls in Cheyenne, 1888"),
      stat("In December 1869, Wyoming", "10 DEC 1869", "Women's vote in Wyoming Territory, the first in the US", WYOHIST),
      m("where women could vote", v(US, highlight=[WY_RED])),
      photo("Men far outnumbered women", PH_SANDERS, "Fort Sanders, near Laramie, 1868"),
      photo("Others hoped it would", PH_BARN, "A homestead barn, Mormon Row"),
      m("It did not make", v(WYV, highlight=[WY_RED]))),
    P("P32",
      stat("A federal homestead was", "160 ACRES", "A homestead under the 1862 Act", "Homestead Act, 1862"),
      sat("In Iowa that was", -93.70, 42.05, 0.08, "Iowa: farms on 160-acre squares"),
      sat("In Wyoming's dry grass,", -105.95, 42.85, 0.1, "Wyoming range")),
    P("P33",
      m(0, v(WYV, highlight=[FED_RED])),
      sat("And that is where", -108.60, 41.90, 0.4, "Federal range, Red Desert"),
      photo("gets bigger than any", PH_HORSES, "BLM range, Salt Wells Creek")),
    P("P33b",
      photo(0, PH_LAR_NOW, "Laramie"),
      m("still decide where people", v(WYV, highlight=[BAND_RED, FED_ALT]))),
)

# ================================================================== 4. The Land Nobody Can Buy
chapter(
    P("P34",
      m(0, v(WYV, highlight=[FED_RED])),
      stat("Almost half of Wyoming", "48 %", "Federal share of Wyoming's land (our own count: 47 %)", "CRS 2012; BLM SMA")),
    P("P35",
      sat(0, -110.40, 44.40, 0.6, "Yellowstone"),
      m("when Congress set aside", v(WYV, highlight=[PARKS_RED])),
      sat("as the world's first", -110.60, 44.45, 0.4, "Yellowstone Lake")),
    P("P36",
      photo(0, PH_SP_ACEC, "BLM land near South Pass"),
      m("became public grazing land,", v(WYV, highlight=[BLM_RED])),
      stat("Today it holds more", "18.3 M ACRES", "BLM land in Wyoming", "Bureau of Land Management"),
      photo("in Wyoming alone.", PH_REDDESERT, "BLM land in the Red Desert")),
    P("P36b",
      stat(0, "1934", "Taylor Grazing Act", "US Congress"),
      photo("put the remaining open", PH_GROUSE, "Open range in the Red Desert"),
      sat("and within a year", -108.50, 41.60, 0.3, "Public range, southern Wyoming"),
      photo("The last great chance", PH_MOULTON, "A homestead in Jackson Hole")),
    P("P37",
      photo(0, PH_PRONGHORN, "Pronghorn"),
      m("But you cannot build", v({"lon": -108.1, "lat": 43.1, "span": 18.6}, highlight=[BLM_RED], places=[ROCKSPR, RAWLINS, LARAMIE])),
      sat("Most of the land", -109.22, 41.59, 0.15, "Rock Springs")),
    P("P38",
      m(0, v(WYV, highlight=[TETON_RED])),
      stat("More than nine-tenths of", "92 %", "Federal land in Teton County", OWN_SMA),
      sat("The private land is", -110.75, 43.55, 0.35, "Jackson Hole", date=L24)),
    P("P39",
      photo(0, PH_JACKSON, "Jackson"),
      photo("and the sliver became", PH_ELKREF, "The National Elk Refuge beside Jackson"),
      stat("Teton County has the", "#1", "Income per person, of all US counties", "Bureau of Economic Analysis"),
      sat("Many of the people", -110.76, 43.48, 0.1, "Jackson"),
      m("and drive in over", v(TETONV, places=[JACKSON, VICTOR], routes=[TETONPASS]))),
    P("P40",
      photo(0, PH_MUDDY, "The Red Desert"),
      photo("Under that land lies", PH_NARM, "Coal at North Antelope Rochelle"),
      m("And that is where", v(WYV, places=[GILLETTE, CASPER, ROCKSPR]))),
)

# ================================================================== 5. Boom and Bust Underground
chapter(
    P("P41",
      m(0, v(WYV, highlight=[CAMPBELL_RED, NATRONA_ALT])),
      photo("and take them away", PH_JC2, "Jeffrey City")),
    P("P42b",
      photo(0, PH_CITADEL, "The Union Pacific line at Green River, 1868"),
      m("and it opened mines", v(SOUTH, places=[ROCKSPR, HANNA])),
      stat("In the early 1950s", "DIESEL", "Union Pacific trades steam for diesel, early 1950s", WYOHIST),
      stat("It closed its Hanna", "1954", "Union Pacific shuts its Hanna mines", WYOHIST),
      sat("and its last Rock", -109.24, 41.60, 0.25, "Rock Springs"),
      photo("and the towns around", PH_HANNA, "Hanna from the air")),
    P("P42",
      sat(0, -106.25, 43.25, 0.15, "Teapot Dome"),
      photo("the Secretary of the", PH_FALL, "Albert Fall, Secretary of the Interior"),
      m("north of Casper, called", v(WYV, places=[CASPER, TEAPOT])),
      photo("to an oil tycoon", PH_SINCLAIR, "Harry Sinclair at the Teapot Dome hearings"),
      photo("Albert Fall became the", PH_FALL_GUILTY, "Albert Fall after the guilty verdict, 1929")),
    P("P43",
      m(0, v(WYV, places=[JEFFREY])),
      sat("and Jeffrey City grew", -107.82, 42.49, 0.12, "Jeffrey City"),
      stat("By 1980 more than", "4,000+", "People in Jeffrey City, 1980", WYOHIST),
      photo("with a school, a", PH_JC1, "Jeffrey City")),
    P("P44",
      stat(0, "1979", "Three Mile Island; uranium prices fall", WYOHIST),
      photo("In the early 1980s", PH_JC2, "Jeffrey City"),
      sat("By 1988 Jeffrey City", -107.84, 42.50, 0.2, "Jeffrey City and the empty plain"),
      stat("In 2010 the census", "58", "People in Jeffrey City, 2010 census", "US Census 2010")),
    P("P45",
      m(0, v(WYV, highlight=[CAMPBELL_RED])),
      sat("In the Powder River", -105.25, 43.68, 0.25, "North Antelope Rochelle mine"),
      photo("so thick and so", PH_NARM, "North Antelope Rochelle"),
      photo("machines the size of", PH_DRAGLINE, "A dragline, Powder River Basin")),
    P("P46",
      sat(0, -105.52, 44.27, 0.35, "Gillette and its mines"),
      stat("a psychologist gave the", "1974", "\"Gillette Syndrome\": a psychologist names the boomtown's troubles", WYOHIST),
      sat("Crime, drinking, broken marriages,", -105.50, 44.29, 0.15, "Gillette")),
    P("P47",
      chart(0, "Wyoming coal output (million tons)", "", [["2008", 466.3], ["2024", 190]], "Wyoming State Geological Survey; EIA", highlight=1),
      m("By 2024 it had", v(WYV, highlight=[CAMPBELL_RED])),
      sat("the lowest since 1992.", -105.28, 43.66, 0.6, "Coal country, Campbell County"),
      photo("Power plants across America", PH_WIND, "Wind turbines")),
    P("P48",
      photo(0, PH_TRUCK, "A haul truck at North Antelope Rochelle"),
      sat("The machines did the", -105.22, 43.70, 0.4, "North Antelope Rochelle mine"),
      stat("dug about sixty-five million", "65 M TONS", "North Antelope Rochelle, 2025", "Peabody Energy"),
      stat("It did it with", "~1,100", "Workers at the mine", "Peabody Energy")),
    P("P49",
      photo(0, PH_GIL_NOW, "Gillette"),
      stat("Wyoming has no state", "NO INCOME TAX", "Wyoming levies no state income tax", "Wyoming Department of Revenue"),
      sat("But the jobs did", -105.48, 44.30, 0.25, "Gillette"),
      photo("And the people who", PH_UNION, "The Wyoming Union, University of Wyoming")),
)

# ================================================================== 6. The Children Leave
chapter(
    P("P50",
      m(0, v(FRONT, places=[LARAMIE, FTCOLLINS, DENVER], arrows=LEAVERS[:2]))),
    P("P51",
      photo(0, PH_UW, "University of Wyoming, Laramie"),
      sat("in Laramie, a town", -105.59, 41.31, 0.15, "Laramie", date=L24),
      photo("There is no big", PH_CASPER, "Casper")),
    P("P52",
      stat(0, "2024", "Harvard Growth Lab: Wyoming growth diagnostic", "Harvard Growth Lab"),
      stat("By their thirties, nearly", "2 IN 3", "Born in Wyoming, gone by their thirties", "Harvard Growth Lab, 2024"),
      m("That is one of", v(US, highlight=[WY_RED]))),
    P("P53",
      m(0, v(FRONT, places=[LARAMIE, FTCOLLINS, DENVER])),
      stat("but a metro of", "~3 MILLION", "People in the Denver metro area", "US Census Bureau"),
      m("and jobs that do", v(WEST, highlight=[CO_RED, WY_ALT], places=[DENVER]))),
    P("P53b",
      m(0, v(WEST, highlight=[CO_ALT, WY_ALT])),
      stat("But it found gold", "1858", "Gold found near today's Denver", "History Colorado"),
      m("and gained federal offices,", v(FRONT, places=[DENVER, LARAMIE])),
      chart("Colorado now has just", "People, July 2025 (millions)", "", [["Colorado", 6.01], ["Wyoming", 0.59]], CENSUS, highlight=0),
      m("on a state not", v(WEST, highlight=[CO_RED, WY_RED]))),
    P("P54",
      m(0, v(WYV, highlight=[WY_RED])),
      photo("Few employers means the", PH_LAR_NOW, "Laramie"),
      photo("And when they leave,", PH_SEEDS, "Seedskadee, at dusk")),
)

# ================================================================== Ending
chapter(
    P("P55",
      m(0, v(WYV, highlight=[WY_RED])),
      photo("so the travellers kept", PH_SADDLE, "South Pass"),
      m("The railway put the", v(WYV, highlight=[LINE_RED])),
      photo("The cattle kings fought", PH_BRANDING, "Branding cattle, 1888"),
      m("The government kept the", v(WYV, highlight=[FED_RED])),
      photo("The minerals came and", PH_TRUCK, "North Antelope Rochelle"),
      photo("And the young leave", PH_UW, "University of Wyoming")),
    P("P55b",
      sat(0, -106.36, 41.66, 0.9, "Elk Mountain (squares: illustration)", highlight=[CHECKER]),
      m("in six western states.", v(CIRC10, highlight=TENTH)),
      stat("The men who rode", "1892", "The invaders were never punished", WYOHIST),
      photo("and the big ranches", PH_BARN, "Ranch land under the Tetons"),
      sat("And Jeffrey City, the", -107.80, 42.48, 0.3, "Jeffrey City in the sagebrush")),
    P("P56",
      m(0, v(SOUTH, highlight=[CARBON_RED], places=[CHOKE, RAWLINS])),
      sat("In Carbon County, on", -107.30, 41.70, 0.6, "Carbon County range"),
      sat("a wind farm of", -107.20, 41.60, 0.35, "The Chokecherry and Sierra Madre site"),
      stat("about six hundred turbines.", "~600 TURBINES", "Chokecherry and Sierra Madre wind project", "Power Company of Wyoming"),
      photo("It will be the", PH_WIND, "Wind turbines")),
    P("P57",
      m(0, v(WYV, places=[KEMMERER])),
      sat("construction began in 2026", -110.60, 41.76, 0.12, "Kemmerer: the Naughton coal plant"),
      stat("on a new kind", "NATRIUM", "TerraPower's reactor: construction permit 4 March 2026", "US Nuclear Regulatory Commission")),
    P("P58",
      sat(0, -107.15, 41.55, 0.5, "The wind farm site, Carbon County"),
      stat("But once they run,", "114", "Permanent jobs at the wind farm (developer's estimate)", "Power Company of Wyoming"),
      stat("The reactor, about two", "~250", "Permanent jobs at the Natrium plant (estimate)", "TerraPower / Bechtel"),
      m("Wind and atoms will", v(WYV, highlight=[WY_RED]))),
    P("P59",
      photo(0, PH_SP_OVER, "South Pass"),
      photo("and many of the", PH_BIKE, "The Great Divide Basin"),
      m("Would you take that", v(US, highlight=[WY_RED])),
      ask=("Would you take that", "Would you take that much space, three hours from the nearest city?")),
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



TITLE = "Why Almost Nobody Lives in Wyoming"
script = {
    "title": TITLE,
    "voice": "am_michael",
    "voice_speed": 1.15,
    "music": "procedural",
    "map_style": "satellite",
    "look": "none",
    "photo_upscale": True,
    "sources": ["episodes/wyoming-empty/research.md and factcheck.md", "Contains modified Copernicus Sentinel data 2024-2025",
                "Railway band: own count from 2020 census block groups (US Census Bureau) (geo/measure_rail.py)",
                "Federal land: BLM Surface Management Agency; counties: US Census Bureau; states and countries: Natural Earth (geo/make_regions.py)",
                "Checkerboard squares at Elk Mountain: illustration of the 1862 grant pattern, not surveyed parcels",
                "Trail, railway, train and route lines drawn through main points (approximate)"],
    "thumbnail": {"text": "ALMOST EMPTY"},
    "chapters": chapters,
    "youtube": {
        "title": TITLE,
        "title_candidates": [TITLE, "Why Wyoming Is Bigger Than Britain but Almost Empty", "Why Wyoming Has Fewer People Than Washington, D.C."],
        "description": "Wyoming is bigger than the United Kingdom, yet fewer people live in the whole state than in Washington, D.C. Half a million emigrants crossed it on the way west and almost none stayed. We follow the answer on the map and in the archives: South Pass and the emigrant trails, the 1868 Union Pacific line that still holds a third of the people on a tenth of the land, the checkerboard and the corner-crossing hunters, the cattle kings and the Johnson County War, the federal land nobody can buy, Teapot Dome, Jeffrey City and the Powder River coal, and the young people who leave for Colorado.",
        "tags": ["Wyoming", "Cheyenne", "Wyoming geography", "Union Pacific", "Oregon Trail", "South Pass", "corner crossing",
                 "Johnson County War", "Teapot Dome", "Jeffrey City", "Powder River Basin", "Jackson Hole", "geography", "satellite images"],
        "pinned_comment": "Would you take that much space, if the nearest city were three hours away?",
    },
}
out = HERE / "script.json"
out.write_text(json.dumps(script, ensure_ascii=False, indent=1) + chr(10), encoding="utf-8")
words = sum(len(p["text"].split()) for c in chapters for p in c["paragraphs"])
shots = [s for c in chapters for p in c["paragraphs"] for s in p["shots"]]
kinds = {k: sum(1 for s in shots if s["type"] == k) for k in ("map", "photo", "stat", "document", "chart")}
print(f"{words} words, {len(chapters)} chapters, {len(shots)} shots {kinds}")
