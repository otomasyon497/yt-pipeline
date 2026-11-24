"""Builds script.json for canadian-shield.  python build_script.py

Same production logic as episodes/scottish-highlands (hand-placed shots, a photo or map frame at most twice, 60 s
apart, every reason opens on a painted map). The narration lives in drafts/narration.md; every sentence comes from
research.md. Photos and satellite tests: visuals.md. Regions: geo/make_regions.py.
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


def v(view, at=None, **kw):
    d = {"view": fresh(view), **kw}
    if at is not None:
        d["at"] = at
    return d


SAT_MIN_SPAN = 0.08
SU = "2025-07-01/2025-08-31"    # northern summer 2025: scratch cssat 2026-11-24, clear on the Ontario/Quebec/Finland views
S24 = "2024-07-01/2024-08-31"   # summer 2024: Churchill, Pine Point, Churchill Falls (2025 had wildfire smoke there)


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
CANADA = {"lon": -96.0, "lat": 61.0, "span": 72.0}     # the whole country
SHIELD_V = {"lon": -86.0, "lat": 56.0, "span": 46.0}   # the horseshoe around Hudson Bay
HUDSON = {"lon": -85.0, "lat": 59.0, "span": 28.0}     # Hudson Bay
ATL = {"lon": -35.0, "lat": 58.0, "span": 140.0}       # Canada to Finland
FIN = {"lon": 26.0, "lat": 64.0, "span": 16.0}         # Finland
NEUROPE = {"lon": 12.0, "lat": 58.0, "span": 46.0}     # the North Atlantic to Finland
CLAY = {"lon": -80.8, "lat": 48.9, "span": 6.0}        # the Great Clay Belt
TIMISK = {"lon": -79.8, "lat": 47.6, "span": 3.0}      # Lake Timiskaming
SOUTH_ON = {"lon": -76.5, "lat": 45.3, "span": 15.0}   # Windsor to Quebec City
PRAIRIE_V = {"lon": -104.0, "lat": 51.5, "span": 24.0}  # the prairies
QUE_N = {"lon": -68.0, "lat": 52.5, "span": 14.0}      # Schefferville to the coast
GSL = {"lon": -114.4, "lat": 61.2, "span": 5.0}        # Great Slave Lake
RAIL_V = {"lon": -97.5, "lat": 56.4, "span": 11.0}     # the line to Churchill
JAMES = {"lon": -74.0, "lat": 53.5, "span": 16.0}      # James Bay and La Grande
LAB = {"lon": -63.5, "lat": 53.4, "span": 8.0}         # Churchill Falls
SOUTH_EDGE = {"lon": -80.0, "lat": 47.5, "span": 22.0}  # the Shield's southern edge, Thunder Bay to Saguenay

SHIELD_RED, SHIELD_ALT = "file:shield.geojson@red", "file:shield.geojson@alt"
MIXED_RED, MIXED_BLUE = "file:mixedwood.geojson@red", "file:mixedwood.geojson@blue"
PRAIRIE_RED, PRAIRIE_ALT = "file:prairie.geojson@red", "file:prairie.geojson@alt"
CLAY_RED = "file:claybelt.geojson@red"
FIN_RED, FIN_ALT = "Finland@red", "Finland@alt"

# ------------------------------------------------------------------ sources (research.md)
OWN_POP = "Own count: Kontur Population 2023 in AAFC Shield ecozones"
OWN_T = "Own calculation: ERA5 daily means 1991-2020 (Open-Meteo)"
TCE = "The Canadian Encyclopedia"
SF = "Statistics Finland"
SC = "Statistics Canada, 2021 census"
OHT = "Ontario Heritage Trust"
HQ = "Hydro-Québec"

# ------------------------------------------------------------------ photos (visuals.md; sharpness checked: scratch cs_q.txt)
PH_SHIELD_CUT = "Canadian Shield.jpg"
PH_SHIELD_ON = "Canadian Shield Ontario.jpg"
PH_TONNERRE = "Riviere au Tonnerre 032.jpg"
PH_BOG = "Bog in Northern Ontario.jpg"
PH_STRAIGHT = "Straight Lake, Timiskaming District, Ontario.jpg"
PH_TBAY_SUNSET = "Thunder Bay Ontario.jpg"
PH_SUPERIOR = "North Shore of Lake Superior (35840825081).jpg"
PH_SLAVE = "UtsingiPoint-GreatSlaveLake.JPG"
PH_STRIAE = "Glacial striations (Straight Lake West roadcut, north of Temagami, Ontario, Canada) (40859886953).jpg"
PH_HEL_AIR = "Aerial photograph of Helsinki, Finland, 2020 May.jpg"
PH_HEL_AIR2 = "Aerial view of Helsinki. 2025-07-23.jpg"
PH_OULU = "View of Oulu 20240904 01.jpg"
PH_OULU_BRIDGE = "Tuira Bridges Oulu 20130715.JPG"
PH_SAIMAA = "Lake Saimaa morning.jpg"
PH_MODIS_HB = "Sea ice in Hudson Bay (MODIS 2016-07-13).jpg"
PH_ICE_CAPE = "Sea ice on Hudson Bay near Cape Churchill.JPG"
PH_HB_SHORE = "Hudson Bay - Churchill, Manitoba (27426253488).jpg"
PH_CHURCHILL_WINTER = "Churchill, Manitoba (16885476409).jpg"
PH_CHURCHILL_2010 = "Churchill, Manitoba (2010).jpg"
PH_PORT = "Port of Churchill aerial view.JPG"
PH_BEAR_WATER = "Polar Bear in Hudson Bay - Churchill, Manitoba (27426282558).jpg"
PH_BEAR_JAIL = "Polar Bear Jail (6360633055).jpg"
PH_BEAR_JAIL2 = "Bear jail (6360643033).jpg"
PH_AURORA = "Aurora Borealis - Churchill, Manitoba (27426660778).jpg"
PH_NUSHKA = "Nushka (Val Gagné), Ontario (1916).jpg"
PH_MORGUE = "Temporary morgue at Matheson, Ontario (1916).jpg"
PH_CLEARING = "Ontario Sessional Papers, 1918, No.47-49 (1918) (14583495169).jpg"
PH_STREET_1918 = "Ontario Sessional Papers, 1918, No.47-49 (1918) (14790006293).jpg"
PH_KAP_AIR = "Kapuskasing, Ontario.jpg"
PH_MATHESON_AIR = "Black River-Matheson, Ontario.jpg"
PH_TIMMINS_1915 = "Timmins, Ontario by Charles A See (16809126075).jpg"
PH_TIMMINS_AIR = "Timmins, Ontario.jpg"
PH_TORONTO = "Toronto skyline 2025.jpg"
PH_KENORA = "Kenora, Ontario.jpg"
PH_YK = "Yellowknife, Northwest Territories.jpg"
PH_SCHEFF = "Downtown Schefferville, QC.jpg"
PH_EMERIL = "Emeril station, Labrador.jpg"
PH_PINE_ORE = "Dolomite-sphalerite-galena (Pine Point Mine, Northwest Territories, Canada) (40704477664).jpg"
PH_END_LINE = "End of the line, Churchill Manitoba (30352378547).jpg"
PH_VIA = "Hudsonbayvia2.JPG"
PH_DINER = "WinnipegChurchillDiningCar2015.jpg"
PH_HARBOUR_1927 = "Hudson Bay Route Plan of Churchill Harbour (1927).jpg"
PH_CF_STATION = "Churchill Falls Generating Station.jpg"
PH_CF_TOWN = "Churchill Falls, Labrador.jpg"
PH_GRAND_FALLS = "Grand or McLean Falls Hamilton River.png"
PH_BRINK = "At the Brink of the Grand Falls.png"
PH_RB_SPILL = "Déversoir, Centrale hydro-électrique Robert-Bourassa.jpg"
PH_RB_RES = "Réservoir R-B.jpg"
PH_RB_EVAC = "Évacuateur de crues R-B.jpg"
PH_RB_TRANSF = "Transformateur CentraleR-B.jpg"
PH_RADISSON = "Radisson, Quebec, Canada.jpg"
PH_TBAY_1929 = "Thunder Bay and Lake Superior 1929.jpg"
PH_GNEISS = "Gneiss (Archean; Windy Lake Northwest roadcut, Sudbury Impact Structure, Ontario, Canada) 1 (32792412377).jpg"
PH_ABITIBI = "Lake Abitibi2.jpg"
PH_SUPERIOR_MN = "Lake Superior North Shore Minnesota Tony Webster 19283970576.jpg"
PH_HEL_2015 = "Suomen Ilmakuva - Aerial photograph from the center of Helsinki to the sea in 2015.jpg"
PH_OULU3 = "View of Oulu 20240904 03.jpg"
PH_MS_OULU = "MS Oulu Toppila 20241020 02.jpg"
PH_ICE2026 = "Ice on Hudson Bay (MODIS 2026-05-06).jpg"
PH_SESS1913 = "Ontario Sessional Papers, 1913, No.49-113 (1913) (14594606530).jpg"
PH_COCHRANE = "Cochrane Ontario.jpg"
PH_REGINA_1910 = "Regina, Saskatchewan, Canada (1910) (14595380219).jpg"
PH_WEST_MAP = "Canada west - 350,000,000 bushels wheat in 1915 - Manitoba, Saskatchewan, Alberta (1916) (14591304049).jpg"
PH_TBAY_MILL = "Thunder Bay Pulp and Paper.jpg"
PH_MONTREAL = "Montreal skyline from Milton-Parc.jpg"
PH_YK2 = "Yellowknife 201809.jpg"
PH_YK_WINTER = "Yellowknife -27 (25302183098).jpg"
PH_CH_RIVER = "Churchill River - Churchill, Manitoba (39488866070).jpg"
PH_HB_AIR = "Hudson Bay - Churchill, Manitoba (40402865225).jpg"
PH_SHORELINE = "Hudson Bay Shoreline - Churchill, Manitoba (39488969890).jpg"
PH_WATERFRONT = "Waterfront Park - Churchill, Manitoba (26427327227).jpg"
PH_BEAR_BUGGY = "Polar Bear and Tundra Buggy - Churchill, Manitoba (26427267077).jpg"
PH_CF_SIGN = "Churchill Falls, Labrador welcome sign.jpg"
PH_CANON = "The Canon a Quarter of a Mile below the Grand Falls.png"

# ------------------------------------------------------------------ places, routes and arrows
CHURCHILL = place("Churchill", -94.17, 58.77, "Churchill", "port")
HELSINKI = place("Helsinki", 24.94, 60.17, "Helsinki", "capital")
STOCKHOLM = place("Stockholm", 18.07, 59.33, "Stockholm", "capital")
OULU = place("Oulu", 25.47, 65.01, "Oulu", "city")
PARIS = place("Paris", 2.35, 48.86, "Paris", "capital")
TIMMINS = place("Timmins", -81.33, 48.48, "Timmins", "city")
SUDBURY = place("Greater Sudbury", -81.00, 46.49, "Greater Sudbury", "city")
TBAY = place("Thunder Bay", -89.25, 48.38, "Thunder Bay", "city")
SAGUENAY = place("Saguenay", -71.07, 48.43, "Saguenay", "city")
MATHESON = place("Matheson", -80.47, 48.53, "Matheson", "site", icon="fire")
NUSHKA = place("Nushka (Val Gagné)", -80.67, 48.62, "Nushka", "site", icon="fire")
HAILEYBURY = place("Haileybury", -79.64, 47.45, "Haileybury", "site", icon="fire")
KAPUSKASING = place("Kapuskasing", -82.43, 49.42, "Kapuskasing", "site", icon="farm")
TORONTO = place("Toronto", -79.38, 43.65, "Toronto", "city")
MONTREAL = place("Montreal", -73.57, 45.50, "Montreal", "city")
OTTAWA = place("Ottawa", -75.70, 45.42, "Ottawa", "capital")
QUEBEC = place("Quebec City", -71.21, 46.81, "Quebec City", "city")
WINDSOR = place("Windsor", -83.03, 42.31, "Windsor", "city")
WINNIPEG = place("Winnipeg", -97.14, 49.90, "Winnipeg", "city")
SCHEFF = place("Schefferville", -66.83, 54.80, "Schefferville", "site", icon="mine")
SEPT_ILES = place("Sept-Îles", -66.38, 50.21, "Sept-Îles", "port")
PINE = place("Pine Point", -114.45, 60.84, "Pine Point", "site", icon="mine")
HAY = place("Hay River", -115.80, 60.82, "Hay River", "site")
FORTRES = place("Fort Resolution", -113.68, 61.17, "Fort Resolution", "site")
YK = place("Yellowknife", -114.37, 62.45, "Yellowknife", "city")
GILLAM = place("Gillam", -94.71, 56.35, "Gillam", "site")
THE_PAS = place("The Pas", -101.25, 53.83, "The Pas", "site")
RADISSON = place("Robert-Bourassa", -77.55, 53.79, "Robert-Bourassa station", "site", icon="power")
CANIAP = place("Caniapiscau reservoir", -69.5, 54.4, "Caniapiscau reservoir", "site", icon="water")
CFALLS = place("Churchill Falls", -64.30, 53.53, "Churchill Falls", "site", icon="power")
CHISASIBI = place("Chisasibi", -78.91, 53.79, "Chisasibi", "site")
CREE = {"lon": -77.0, "lat": 53.0, "span": 8.0}       # the Cree towns of James Bay
KINGSTON = place("Kingston", -76.48, 44.23, "Kingston", "city")

HB_RAIL = {"from": [-101.25, 53.83], "via": [[-98.6, 54.9], [-97.86, 55.74], [-94.71, 56.35], [-94.2, 57.6]], "to": [-94.17, 58.77],
           "mode": "line", "label": "Hudson Bay line", "color": "accent", "seconds": 4.0}
ORE_RAIL = {"from": [-66.83, 54.80], "via": [[-66.6, 53.6], [-66.4, 52.95], [-66.5, 51.6]], "to": [-66.38, 50.21],
            "mode": "line", "label": "Ore railway to the coast", "color": "accent", "seconds": 3.5}
POWER_LG = {"from": [-77.55, 53.79], "via": [[-76.5, 51.0], [-75.0, 48.5]], "to": [-73.57, 45.50],
            "mode": "line", "label": "Power lines south (approx.)", "color": "blue", "seconds": 4.0}
POWER_CF = {"from": [-64.30, 53.53], "via": [[-67.0, 51.5], [-70.0, 48.5]], "to": [-73.57, 45.50],
            "mode": "line", "label": "Churchill Falls power to Quebec (approx.)", "color": "blue", "seconds": 4.0}
LAT_HEL = {"from": [-94.17, 58.77], "to": [24.94, 60.17], "mode": "line", "label": "Almost the same latitude",
           "color": "accent", "seconds": 3.5}
LAT_PARIS = {"from": [-81.33, 48.48], "to": [2.35, 48.86], "mode": "line", "label": "The latitude of Paris",
             "color": "accent", "seconds": 3.5}
ICE_PUSH = [{"from": [-80.0, 60.0], "to": [-80.5, 47.0], "color": "blue", "label": "Ice pushed the soil south", "bend": 0.05},
            {"from": [-95.0, 60.0], "to": [-97.0, 49.5], "color": "blue", "bend": -0.05}]
WEST_WIND = [{"from": [-30.0, 52.0], "to": [8.0, 60.0], "color": "red", "label": "Winds off the Atlantic", "bend": -0.1},
             {"from": [8.0, 60.0], "to": [24.0, 62.5], "color": "red", "bend": 0.05}]
LAND_WIND = [{"from": [-112.0, 63.0], "to": [-96.0, 57.0], "color": "blue", "label": "Air off the continent", "bend": 0.1},
             {"from": [-86.0, 60.0], "to": [-82.0, 50.5], "color": "blue", "label": "Air off the frozen bay", "bend": -0.05}]
SETTLERS = [{"from": [-79.4, 44.0], "to": [-97.0, 50.0], "color": "red", "label": "Settlers ride past the Shield", "bend": -0.12}]

chapters = []
heads = iter(HEADS)


def chapter(*paras):
    title, mood = next(heads)
    chapters.append({"title": title, "mood": mood, "paragraphs": list(paras)})


# ================================================================== Hook
chapter(
    P("P0",
      m(0, v(CANADA, highlight=["Canada@alt"])),
      m("Look at it from", v(CANADA, layer="night")),
      m("And the darkest part", v(SHIELD_V, highlight=[SHIELD_RED]),
        step("from the Arctic down", places=[CHURCHILL, TBAY]))),
    P("P1",
      photo(0, PH_SHIELD_CUT, "The Canadian Shield, Ontario"),
      stat("It covers about five", "5 MILLION KM²", "Area of the Canadian Shield, about half of Canada", TCE),
      sat("We counted the people", -90.50, 50.50, 0.8, "Lakes of the Shield, north-western Ontario"),
      stat("About three point four", "3.4 MILLION", "People on the Shield's forest belt: 8.7 % of Canadians", OWN_POP)),
    P("P2",
      photo(0, PH_ABITIBI, "Lake Abitibi, Ontario-Quebec border"),
      m("On the other side", v(ATL, highlight=[SHIELD_ALT, FIN_RED])),
      photo("Ancient, hard, scraped bare", PH_SAIMAA, "Lake Saimaa, Finland"),
      stat("More than five and", "5.6 MILLION", "People in Finland, end of 2024", SF),
      sat("Finland has a city", 25.47, 65.01, 0.25, "Oulu, Finland"),
      photo("Canada's Shield has nothing", PH_SLAVE, "Great Slave Lake, Northwest Territories")),
    P("P3",
      m(0, v(SHIELD_V, places=[CHURCHILL]), step("a frozen sea in", highlight=["file:hudsonbay.geojson@blue"])),
      photo("a farming dream that", PH_NUSHKA, "Nushka, Ontario, after the fire of 1916"),
      sat("a town whose houses", -114.455, 60.835, 0.1, "Pine Point, Northwest Territories", date=S24),
      photo("a railway that vanished", PH_END_LINE, "End of the line, Churchill"),
      photo("and a river of", PH_CF_STATION, "Churchill Falls, Labrador"),
      photo("The first reason is", PH_SHIELD_ON, "The Canadian Shield, Ontario")),
)

# ================================================================== 1. Rock Without Soil
chapter(
    P("P4",
      m(0, v(SHIELD_V, highlight=[SHIELD_RED])),
      photo("In most places, the", PH_TONNERRE, "Rivière au Tonnerre, Quebec"),
      photo("Here, those layers are", PH_GNEISS, "Gneiss, near Sudbury"),
      m("What you stand on", v(SOUTH_EDGE, places=[SUDBURY, TBAY])),
      photo("is Precambrian rock, more", PH_SUPERIOR, "North shore of Lake Superior"),
      stat("more than five hundred", "500 MILLION+", "Years since the Shield's youngest rock formed", TCE)),
    P("P5",
      m(0, v(CANADA)),
      photo("As it crept outward,", PH_STRIAE, "Scratches left by the ice, near Temagami"),
      photo("and ground across the", PH_SUPERIOR_MN, "Ice-scoured rock, Lake Superior"),
      m("It scraped off the", v(CANADA, arrows=ICE_PUSH))),
    P("P6",
      photo(0, PH_STRAIGHT, "Straight Lake, Timiskaming District"),
      sat("a thin layer of", -94.49, 49.77, 0.3, "Lake of the Woods at Kenora"),
      sat("That is why the", -90.50, 50.50, 0.4, "North-western Ontario from orbit"),
      photo("Rock, black spruce, and", PH_BOG, "Bog in northern Ontario"),
      sat("Lakes beyond counting.", -69.50, 54.50, 1.2, "Lakes of northern Quebec")),
    P("P7",
      m(0, v(FIN, highlight=[FIN_RED])),
      photo("Its bedrock is part", PH_HEL_AIR2, "Helsinki"),
      photo("The soil there is", PH_SAIMAA, "Lake Saimaa"),
      sat("So the rock cannot", 24.94, 60.17, 0.3, "Helsinki from orbit"),
      photo("Something else must make", PH_TBAY_SUNSET, "Thunder Bay, Ontario")),
)

# ================================================================== 2. The Freezer in the Middle
chapter(
    P("P8",
      m(0, v(HUDSON, highlight=["file:hudsonbay.geojson@blue"])),
      photo("Together with James Bay", PH_HB_AIR, "Hudson Bay at Churchill"),
      stat("Hudson Bay covers more", "1.2 MILLION KM²", "Hudson Bay with James Bay", "Wikipedia; Britannica (wider definition)"),
      photo("For most of the", PH_MODIS_HB, "Hudson Bay from orbit, July 2016")),
    P("P9",
      m(0, v(RAIL_V, places=[CHURCHILL])),
      sat("on its western shore,", -94.17, 58.77, 0.12, "Churchill, Manitoba", date=S24),
      photo("and to freeze again", PH_ICE_CAPE, "Ice on Hudson Bay near Cape Churchill"),
      stat("That leaves about eight", "~8 MONTHS", "Ice on the route to Churchill, 1981-2014 average", "Own arithmetic, from Arctic journal dates"),
      photo("When the ice melts,", PH_BEAR_WATER, "Polar bear, Churchill"),
      photo("fasting, for about four", PH_HB_SHORE, "Hudson Bay shore at Churchill")),
    P("P9b",
      photo(0, PH_CHURCHILL_WINTER, "Churchill in winter"),
      stat("Since 1983, the town", "SINCE 1983", "Churchill's Polar Bear Alert program", "Polar Bears International"),
      photo("Anyone who sees a", PH_CHURCHILL_2010, "Churchill, Manitoba"),
      photo("Bears that keep coming", PH_BEAR_JAIL, "The polar bear holding facility, Churchill"),
      photo("opened in 1982,", PH_BEAR_JAIL2, "The holding facility"),
      photo("until the bay freezes", PH_BEAR_BUGGY, "Waiting for the ice, Churchill")),
    P("P10",
      m(0, v(ATL, places=[CHURCHILL, HELSINKI]), step("Churchill sits a little", places=[STOCKHOLM], routes=[LAT_HEL])),
      photo("We pulled thirty years", PH_HEL_AIR, "Helsinki"),
      photo("from a global weather", PH_HEL_2015, "Helsinki")),
    P("P11",
      chart(0, "Days a year below freezing, 1991-2020", "", [["Helsinki", 93], ["Churchill", 214]], OWN_T, highlight=1),
      stat("In January, Helsinki sits", "-26 °C", "Churchill in January; Helsinki: -4 °C (1991-2020 averages)", OWN_T),
      photo("Churchill spends more than", PH_AURORA, "Churchill in the dark season"),
      photo("Helsinki spends fewer than", PH_HEL_AIR2, "Helsinki")),
    P("P12",
      m(0, v(SOUTH_EDGE, places=[TIMMINS])),
      photo("Timmins, a mining city", PH_TIMMINS_AIR, "Timmins, Ontario"),
      m("lies at about the", v(ATL, places=[TIMMINS, PARIS], routes=[LAT_PARIS]), step("Oulu, in Finland, lies", places=[OULU])),
      photo("And yet, over a", PH_OULU, "Oulu, Finland"),
      chart("slightly warmer than Timmins.", "Average temperature over the year (°C)", "", [["Oulu, 65° N", 3.3], ["Timmins, 48° N", 2.7]], OWN_T, highlight=0)),
    P("P13",
      photo(0, PH_MS_OULU, "Oulu harbour"),
      m("Northern Europe gets its", v(NEUROPE, arrows=WEST_WIND)),
      photo("Scientists still argue about", PH_OULU_BRIDGE, "Oulu, Finland"),
      sat("comes from ocean currents", 25.30, 65.05, 0.6, "The Gulf of Bothnia at Oulu"),
      photo("But the result is", PH_OULU3, "Oulu"),
      sat("Finland's air comes off", 25.47, 65.01, 0.12, "Oulu on the Gulf of Bothnia")),
    P("P14",
      m(0, v(SHIELD_V, arrows=LAND_WIND)),
      photo("and off a bay", PH_ICE2026, "Hudson Bay, still frozen in May 2026"),
      photo("The same rock, at", PH_KENORA, "Kenora, Ontario"),
      sat("And that difference decided", -80.47, 48.53, 0.25, "Farms near Matheson, Ontario")),
)

# ================================================================== 3. The Farm Dream That Burned
chapter(
    P("P15",
      m(0, v(SOUTH_EDGE, highlight=[CLAY_RED])),
      photo("At the end of", PH_ABITIBI, "Lake Abitibi"),
      m("sat against the ice", v(CLAY, places=[TIMMINS])),
      m("When it drained, it", v(CLAY, highlight=[CLAY_RED], places=[KAPUSKASING, MATHESON])),
      sat("It became known as", -82.43, 49.42, 0.2, "Fields around Kapuskasing, on the clay", date=S24)),
    P("P16",
      photo(0, PH_STREET_1918, "Northern Ontario, about 1918"),
      stat("A geologist named Alfred", "1899", "Alfred Barlow's report praises the Clay Belt", "Clay Belt histories (TCE; Wikipedia)"),
      photo("The next year, the", PH_TIMMINS_1915, "Timmins, about 1915"),
      stat("Pamphlets promised the great", "15,000,000 ACRES", "The Clay Belt, as promoted around 1901", "Pamphlet, c. 1901 (Canadiana)")),
    P("P17",
      photo(0, PH_CLEARING, "Clearing land in northern Ontario, 1918"),
      photo("They cut the forest", PH_SESS1913, "Cleared land, northern Ontario, 1913"),
      m("In the summer of", v(CLAY, places=[MATHESON, NUSHKA])),
      stat("On the twenty-ninth of", "29 JULY 1916", "Clearing fires join into one", "CBC; Ontario Heritage Trust")),
    P("P18",
      photo(0, PH_NUSHKA, "Nushka, after the fire"),
      sat("Matheson was almost destroyed.", -80.47, 48.53, 0.12, "Matheson today"),
      photo("people ran from the", PH_MORGUE, "Temporary morgue at Matheson, 1916"),
      stat("The official count was", "223", "Official death toll of the 1916 fire; the real number is unknown", "Alexander 2010; CBC"),
      photo("It is often called", PH_MATHESON_AIR, "Black River-Matheson today")),
    P("P19",
      m(0, v(TIMISK, places=[HAILEYBURY])),
      sat("fires in the smaller", -79.64, 47.45, 0.2, "Haileybury on Lake Timiskaming"),
      stat("Within hours, about ninety", "90 %", "Share of Haileybury destroyed, 4 October 1922", OHT),
      stat("Around forty-three people died", "3,500", "People left homeless by the 1922 fire", OHT),
      photo("The fire stopped only", PH_STRAIGHT, "Timiskaming District")),
    P("P20",
      m(0, v(CLAY, highlight=[CLAY_RED], places=[KAPUSKASING])),
      photo("After the First World", PH_COCHRANE, "Cochrane station, on the Clay Belt railway"),
      sat("in the heart of", -82.43, 49.42, 0.2, "Kapuskasing on the clay", date=S24),
      photo("for soldiers coming home", PH_KAP_AIR, "Kapuskasing today"),
      stat("The scheme was dropped", "1920", "Ontario drops its soldier settlement scheme at Kapuskasing", OHT),
      photo("left for the cities", PH_REGINA_1910, "Threshing on the prairies, 1910")),
    P("P20b",
      sat(0, -80.60, 48.60, 0.5, "Clay Belt farms near Matheson"),
      photo("and the rain came", PH_SESS1913, "Northern Ontario, 1913"),
      photo("The Clay Belt became", PH_TBAY_MILL, "Paper mill, Thunder Bay"),
      photo("And there was another", PH_KENORA, "Kenora")),
)

# ================================================================== 4. Somewhere Better to Go
chapter(
    P("P21",
      m(0, v(CANADA, places=[TORONTO, MONTREAL])),
      m("South of the Shield", v(SOUTH_ON, highlight=[MIXED_RED]), step("from Windsor through Toronto", places=[WINDSOR, TORONTO]),
        step("to Montreal and Quebec", places=[MONTREAL, QUEBEC])),
      sat("The soil the ice", -76.40, 44.40, 0.6, "Where the Shield meets the farmland, near Kingston")),
    P("P22",
      photo(0, PH_TORONTO, "Toronto"),
      photo("the band of mixed", PH_MONTREAL, "Montreal"),
      stat("It covers only about", "2 %", "Share of Canada's land in the Great Lakes-St Lawrence lowlands", OWN_POP),
      stat("More than half of", "51 %", "Share of Canadians living there", OWN_POP)),
    P("P23",
      m(0, v(PRAIRIE_V, highlight=[PRAIRIE_RED], places=[WINNIPEG])),
      photo("Under the Dominion Lands", PH_WEST_MAP, "Canada West, a settlers' guide, 1916"),
      stat("a hundred and sixty", "160 ACRES", "A homestead under the Dominion Lands Act, 1872, for a $10 fee", TCE),
      m("Much of the prairies", v(CANADA, highlight=[PRAIRIE_RED], arrows=SETTLERS)),
      photo("and the railways carried", PH_REGINA_1910, "Regina, Saskatchewan, 1910"),
      photo("For a family looking", PH_SUPERIOR, "The railway's way across the Shield, Lake Superior"),
      photo("Why fight the rock", PH_SHIELD_CUT, "Shield rock, Ontario")),
    P("P24",
      m(0, v(FIN, highlight=[FIN_RED], places=[HELSINKI, OULU])),
      photo("People cleared fields wherever", PH_OULU_BRIDGE, "Oulu, Finland"),
      sat("built their towns along", 25.47, 65.01, 0.4, "Oulu on the Gulf of Bothnia"),
      photo("Canada did have somewhere", PH_YK2, "Yellowknife"),
      photo("so the Shield was", PH_YK_WINTER, "Yellowknife in winter")),
    P("P24b",
      m(0, v(SOUTH_EDGE), step("The largest are Greater", places=[SUDBURY]),
        step("Saguenay, with about a", places=[SAGUENAY]), step("and Thunder Bay, with", places=[TBAY])),
      sat("All three sit close", -81.00, 46.49, 0.35, "Greater Sudbury"),
      photo("on a railway, a", PH_TBAY_1929, "Thunder Bay and Lake Superior, chart of 1929"),
      m("Not one city of", v(SHIELD_V, layer="night"))),
)

# ================================================================== 5. Towns That Live as Long as the Mine
chapter(
    P("P25",
      m(0, v(SHIELD_V, places=[SCHEFF, PINE])),
      photo("The rock that is", PH_PINE_ORE, "Zinc and lead ore, Pine Point mine"),
      photo("copper, zinc and uranium.", PH_GNEISS, "Shield rock near Sudbury"),
      sat("So towns grew where", -81.33, 48.47, 0.25, "Timmins and its mines"),
      photo("And when the ore", PH_YK, "Yellowknife, a gold-mining town")),
    P("P26",
      m(0, v(QUE_N, places=[SCHEFF])),
      sat("They called it Schefferville.", -66.83, 54.80, 0.15, "Schefferville and its old pits"),
      m("A railway hundreds of", v(QUE_N, places=[SCHEFF, SEPT_ILES], routes=[ORE_RAIL])),
      photo("carried the ore south", PH_EMERIL, "On the ore railway, Labrador"),
      stat("By its peak, around", "~5,000", "People in Schefferville at its peak, late 1960s", "Wikipedia (secondary)")),
    P("P27",
      stat(0, "2 NOV 1982", "The Iron Ore Company announces the mine will close", "Canadian Historical Review"),
      photo("Mining stopped the next", PH_SCHEFF, "Schefferville today"),
      sat("In 2021, the census", -66.80, 54.85, 0.5, "The empty pits around Schefferville"),
      stat("two hundred and forty-four", "244", "People in Schefferville, 2021 census", SC)),
    P("P28",
      m(0, v(GSL, places=[PINE, YK])),
      sat("It was a zinc", -114.45, 60.84, 0.2, "Pine Point townsite", date=S24),
      stat("a school, an arena", "1,915", "People in Pine Point, 1976", "Wikipedia (secondary)"),
      sat("The mine closed in", -114.30, 60.85, 0.35, "Pine Point's open pits", date=S24)),
    P("P29",
      m(0, v(GSL, places=[PINE]), step("many of them to", places=[HAY, FORTRES])),
      stat("Other buildings were knocked", "9", "People left in Pine Point, 1991", "Wikipedia (secondary)"),
      sat("From above, you can", -114.455, 60.835, 0.06, "The streets of Pine Point", date=S24)),
    P("P30",
      sat(0, -114.30, 60.85, 0.6, "Pine Point's pits", date=S24),
      photo("But a town built", PH_YK, "Yellowknife"),
      photo("and the Shield is", PH_YK_WINTER, "Yellowknife in winter"),
      m("Which brings us to", v(SHIELD_V, places=[CHURCHILL]))),
)

# ================================================================== 6. One Line to the Sea
chapter(
    P("P31",
      m(0, v(RAIL_V, places=[CHURCHILL])),
      photo("and many places have", PH_CH_RIVER, "Mouth of the Churchill River"),
      photo("Churchill, on Hudson Bay,", PH_PORT, "Churchill and its port"),
      photo("For almost a century,", PH_HB_AIR, "The coast near Churchill"),
      m("its link to the", v(RAIL_V, places=[CHURCHILL, THE_PAS], routes=[HB_RAIL]))),
    P("P32",
      stat(0, "29 MARCH 1929", "The railway reaches Churchill", "Manitoba Heritage Council plaque"),
      photo("A crew of about", PH_SHORELINE, "Wet ground on Hudson Bay, Churchill"),
      photo("across frozen muskeg, the", PH_BOG, "Muskeg and spruce"),
      photo("The port was finished", PH_HARBOUR_1927, "Plan of Churchill Harbour, 1927"),
      sat("to ship prairie grain", -94.19, 58.78, 0.05, "The grain port at Churchill", date=S24)),
    P("P33",
      m(0, v(RAIL_V, places=[CHURCHILL, GILLAM])),
      stat("washed out the track", "~20", "Places where floods cut the line, May 2017", "CBC"),
      photo("The owner of the", PH_END_LINE, "The end of the line, Churchill"),
      photo("The trains stopped.", PH_CHURCHILL_WINTER, "Churchill"),
      photo("Food and fuel had", PH_WATERFRONT, "Churchill waterfront")),
    P("P34",
      stat(0, "18 MONTHS", "Churchill without its railway, 2017-2018", "CBC; Government of Canada"),
      sat("except by air.", -94.17, 58.77, 0.4, "Churchill from orbit", date=S24),
      stat("and the federal government", "$117 MILLION", "Federal money to buy and repair the line", "Government of Canada"),
      photo("When the first passenger", PH_VIA, "The train at Churchill"),
      photo("people came out to", PH_DINER, "On the Winnipeg-Churchill train")),
    P("P35",
      photo(0, PH_SLAVE, "Great Slave Lake"),
      sat("and the one thin", -94.25, 58.60, 0.5, "The railway across the muskeg near Churchill", date=S24),
      photo("Yet the most important", PH_CF_SIGN, "Power lines at Churchill Falls"),
      photo("They carry electricity.", PH_RB_TRANSF, "Robert-Bourassa station, James Bay")),
)

# ================================================================== 7. The Empty Half Lights the Full Half
chapter(
    P("P36",
      m(0, v(JAMES, places=[RADISSON])),
      sat("The ice that scraped", -77.50, 53.78, 0.6, "La Grande River and its reservoir"),
      photo("Canada is the third", PH_GRAND_FALLS, "Grand Falls, Labrador, 1896"),
      stat("and more than half", "53 %", "Quebec's share of Canada's hydroelectricity, 2021", TCE)),
    P("P37",
      stat(0, "30 APRIL 1971", "Quebec announces the James Bay project", TCE),
      sat("announced what he called", -77.60, 53.75, 1.5, "La Grande reservoirs", date=S24),
      m("Huge dams on the", v(JAMES, places=[RADISSON, CANIAP])),
      photo("The Cree and Inuit", PH_RB_RES, "Robert-Bourassa reservoir"),
      photo("They went to court", PH_RADISSON, "Radisson, the town built for the dams")),
    P("P38",
      stat(0, "11 NOV 1975", "The James Bay and Northern Quebec Agreement is signed", TCE),
      m("the Cree, the Inuit,", v(CREE, places=[CHISASIBI, RADISSON])),
      sat("The Cree and Inuit gave", -78.91, 53.79, 0.8, "The mouth of La Grande River", date=S24),
      stat("in return for two", "$225 MILLION", "Compensation under the 1975 agreement", TCE),
      sat("and rights over hunting,", -78.91, 53.79, 0.3, "Chisasibi, a Cree town on La Grande", date=S24),
      photo("It is known as", PH_RB_EVAC, "Robert-Bourassa spillway")),
    P("P39",
      stat(0, "~17,000 MW", "La Grande complex, close to half of Hydro-Québec's capacity", HQ),
      photo("close to half of", PH_RB_TRANSF, "Robert-Bourassa station"),
      photo("The largest station alone,", PH_RB_SPILL, "Robert-Bourassa spillway"),
      stat("can deliver more than", "5,616 MW", "Robert-Bourassa generating station", HQ),
      m("The power travels about", v(JAMES, places=[RADISSON, MONTREAL], routes=[POWER_LG]))),
    P("P39b",
      sat(0, -77.55, 53.79, 0.25, "Robert-Bourassa dam", date=S24),
      m("In September 1984, thousands", v(QUE_N, places=[CANIAP])),
      stat("Quebec officials first estimated", "10,000+", "Caribou drowned, September 1984 (early official estimate)", "Time; The New York Times"),
      sat("Inuit leaders blamed water", -69.50, 54.50, 1.2, "Caniapiscau reservoir"),
      photo("Fences were later built", PH_BRINK, "Falls in Labrador, 1892")),
    P("P39c",
      sat(0, -69.50, 54.50, 0.5, "Flooded forest, Caniapiscau"),
      stat("Hydro-Québec's own monitoring found", "2-8×", "Mercury in fish after the reservoirs filled", "Hydro-Québec monitoring 1978-2012"),
      photo("to between two and", PH_CANON, "Labrador river canyon, 1892"),
      photo("and took twenty to", PH_RB_RES, "Robert-Bourassa reservoir"),
      photo("The Cree, who fish", PH_RADISSON, "Radisson")),
    P("P40",
      m(0, v(LAB, places=[CFALLS])),
      photo("In 1969, Newfoundland signed", PH_CF_STATION, "Churchill Falls Generating Station"),
      photo("until 2041, at a", PH_CF_SIGN, "Churchill Falls"),
      stat("That price was about", "0.2 ¢", "Price per kilowatt-hour under the 1969 contract", "Government of Newfoundland and Labrador"),
      sat("For decades, Hydro-Québec earned", -64.80, 53.70, 1.2, "The reservoir behind Churchill Falls", date=S24),
      photo("and the contract became", PH_CF_TOWN, "Churchill Falls, Labrador")),
    P("P41",
      stat(0, "1.8 ¢", "Starting price per kilowatt-hour from 2027 under the 2026 deal", "Hydro-Québec; NL Hydro"),
      sat("Under it, the price", -64.80, 53.70, 2.0, "Labrador's reservoirs", date=S24),
      sat("and rises from there.", -64.30, 53.53, 0.2, "Churchill Falls from orbit", date=S24),
      m("But the pattern stays", v(QUE_N, places=[CFALLS, MONTREAL], routes=[POWER_CF])),
      m("where almost nobody lives,", v(CANADA, layer="night", places=[MONTREAL, TORONTO]))),
)

# ================================================================== Ending
chapter(
    P("P42",
      m(0, v(SOUTH_EDGE, places=[MATHESON, TIMMINS])),
      photo("The ice took the", PH_STRIAE, "Ice scratches, Ontario"),
      photo("A frozen sea in", PH_MODIS_HB, "Hudson Bay"),
      photo("The farms burned and", PH_MORGUE, "Matheson, 1916"),
      photo("The country had better", PH_TORONTO, "Toronto"),
      photo("Its towns live and", PH_EMERIL, "The ore railway, Labrador"),
      photo("Every place is a", PH_VIA, "The train to Churchill"),
      photo("often joined by a", PH_DINER, "On the Churchill train"),
      photo("And its greatest wealth,", PH_GRAND_FALLS, "Grand Falls, Labrador, 1896"),
      photo("can be taken south", PH_MONTREAL, "Montreal")),
    P("P43",
      photo(0, PH_HEL_AIR, "Helsinki"),
      photo("Canada never had to.", PH_TBAY_SUNSET, "Thunder Bay"),
      m("Would you move to", v(SHIELD_V, layer="night", places=[SUDBURY, TBAY, SCHEFF])),
      ask=("Would you move to", "Would you move to a Shield town for double the pay?")),
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


TITLE = "Why Almost Nobody Lives on Half of Canada"
script = {
    "title": TITLE,
    "voice": "am_michael",
    "voice_speed": 1.15,
    "music": "procedural",
    "map_style": "satellite",
    "look": "none",
    "photo_upscale": True,
    "sources": ["episodes/canadian-shield/research.md and factcheck.md", "Contains modified Copernicus Sentinel data 2026",
                "Shield, lowlands, prairies and Clay Belt: Ecological Framework of Canada (AAFC) ecozones/ecoregion 96 (geo/)",
                "People on the Shield: own count, Kontur Population 2023 (CC BY 4.0) in Boreal + Taiga Shield ecozones (geo/measure_population.py)",
                "Temperatures: own calculation from ERA5 reanalysis 1991-2020 via Open-Meteo (data/era5_normals.py)",
                "Railway, power-line and wind arrows drawn through main points (approximate)"],
    "thumbnail": {"text": "HALF OF CANADA EMPTY"},
    "chapters": chapters,
    "youtube": {
        "title": TITLE,
        "title_candidates": [TITLE, "Why Almost Nobody Lives on the Canadian Shield", "Why Half of Canada Is Still Empty"],
        "description": "The Canadian Shield covers about half of Canada, yet fewer than one Canadian in ten lives on it. Finland stands on the same kind of ancient rock, scraped by the same ice, and holds 5.6 million people. We follow the answer from orbit: the frozen sea in the middle of the continent, the Great Clay Belt and the fires of 1916 and 1922, the prairies that pulled settlers past the rock, the mining towns of Schefferville and Pine Point, the single railway to Churchill, and the James Bay and Churchill Falls power that flows south.",
        "tags": ["Canadian Shield", "Canada", "Hudson Bay", "Finland", "Churchill Manitoba", "Clay Belt", "Matheson fire",
                 "Schefferville", "Pine Point", "James Bay project", "Churchill Falls", "northern Ontario", "geography", "satellite images"],
        "pinned_comment": "Would you move to a town on the Shield, with its lakes and its winters, if the job paid twice as much?",
    },
}
out = HERE / "script.json"
out.write_text(json.dumps(script, ensure_ascii=False, indent=1) + chr(10), encoding="utf-8")
words = sum(len(p["text"].split()) for c in chapters for p in c["paragraphs"])
shots = [s for c in chapters for p in c["paragraphs"] for s in p["shots"]]
kinds = {k: sum(1 for s in shots if s["type"] == k) for k in ("map", "photo", "stat", "document", "chart")}
print(f"{words} words, {len(chapters)} chapters, {len(shots)} shots {kinds}")
