"""Builds script.json for australia-west-coast.  python build_script.py

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
SO = "2025-01-01/2025-03-31"   # southern summer: scratch awcsat 2026-11-23, clear on every southern test view
NO = "2025-06-01/2025-09-30"   # northern dry season: clear on every northern test view
ABR = "2024-10-01/2025-05-31"  # the Abrolhos: the summer window had cumulus over the reefs


def sat(at, lon, lat, span, label=None, **kw):
    kw.setdefault("date", SO if lat < -26.5 else NO)
    return m(at, v(near(lon, lat, max(span, SAT_MIN_SPAN)), **kw), text=label)


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
AUS = {"lon": 134.0, "lat": -27.5, "span": 58.0}       # the continent
WA = {"lon": 121.5, "lat": -25.5, "span": 27.0}        # Western Australia
WEST = {"lon": 116.5, "lat": -25.5, "span": 17.0}      # the west coast
SW = {"lon": 116.2, "lat": -32.2, "span": 4.6}         # Perth and the south-west corner
GLOBE_S = {"lon": 45.0, "lat": -22.0, "span": 260.0}   # the southern subtropics, Chile to Australia
EASTC = {"lon": 150.5, "lat": -26.5, "span": 14.0}     # Queensland coast and the Great Dividing Range
PILB = {"lon": 118.6, "lat": -21.8, "span": 5.5}       # the Pilbara
NW = {"lon": 118.0, "lat": -20.3, "span": 10.5}        # Broome to Exmouth
SHARKB = {"lon": 113.9, "lat": -25.9, "span": 3.2}     # Shark Bay
MIDW = {"lon": 114.4, "lat": -28.6, "span": 3.0}       # Geraldton and the Abrolhos
INDIAN = {"lon": 68.0, "lat": -22.0, "span": 115.0}    # Cape of Good Hope to Java
GOLD = {"lon": 118.8, "lat": -31.3, "span": 7.5}       # Perth to Kalgoorlie
WIND_WA = {"lon": 108.0, "lat": -33.0, "span": 26.0}   # winter storms off the south-west

WA_RED, WA_ALT = "Western Australia@red", "Western Australia@alt"
COAST_RED = "file:wa_coast.geojson@red"
CYC_RED = "file:cyclone_coast.geojson@red"
PERTH_RED = "file:perth.geojson@red"
RIDGE_ALT = "file:ridge.geojson@alt"
HAM_RED, HAM_ALT = "file:hamersley.geojson@red", "file:hamersley.geojson@alt"
RANGE_ALT = "file:range.geojson@alt"
DRY_RED = "file:dry_coast.geojson@red"

# ------------------------------------------------------------------ sources (research.md)
GA = "Geoscience Australia"
WAPOP = "Population Statement 2025, WA (Centre for Population)"
BOM = "Bureau of Meteorology"
WC = "Water Corporation"
WAG = "WA Government"
WAM = "WA Museum"
PP = "Pilbara Ports (WA Government, July 2025)"

# ------------------------------------------------------------------ photos (visuals.md)
PH_PERTH_GOLD = "AUS Perth, Central Business District, Kings Park, View 005.jpg"
PH_PERTH_DUSK = "AUS Perth, Central Business District, Kings Park, View 002.jpg"
PH_PERTH_NIGHT = "AUS Perth, Central Business District, Kings Park, View 015.jpg"
PH_PERTH_NIGHT2 = "AUS Perth, Central Business District, Kings Park, View 014.jpg"
PH_PERTH_DAY = "AUS Perth, Central Business District, Kings Park, View 022.jpg"
PH_PERTH_DAY2 = "AUS Perth, Central Business District, Kings Park, View 021.jpg"
PH_PERTH_RIVER = "AUS Perth, Central Business District, Kings Park, View 023.jpg"
PH_PERTH_SWAN = "Perth skyline from the Swan River, August 2024.jpg"
PH_PERTH_ISS = "Perth, Australia, is split by the Swan River (iss074e0376130).jpg"
PH_COTTESLOE = "AUS Perth, Cottesloe, Cottesloe Beach 002.jpg"
PH_BRIS_RIVER = "AUS Brisbane, South Brisbane, Clem Jones Promenade, View 002.jpg"
PH_BRIS_GREEN = "Brisbane - City view 4 (4028603547).jpg"
PH_BRIS_CBD = "AUS Brisbane, Central Business District, Brisbane River 007.jpg"
PH_CARAVAN = "Little yellow caravan on the prairie.JPG"
PH_SANDY_BAY = "Australia exmouth sandy bay.jpg"
PH_YARDIE = "Australia exmouth yardie creek gorge.jpg"
PH_SNORKEL = "Exmouth, Australia (Unsplash hIyWlsCKjkQ).jpg"
PH_WHALESHARK = "Exmouth, Australia (Unsplash SiLz-4N33sk).jpg"
PH_EXMOUTH_CLOUDS = "Clouds above Exmouth WA.jpg"
PH_KALBARRI_RED = "Kalbarri (2052465296).jpg"
PH_KALBARRI_GORGE = "In the Kalbarri National Park (15003005389).jpg"
PH_KALBARRI_COAST = "In the Kalbarri National Park (15167082876).jpg"
PH_KALBARRI_BEND = "Kalbarri (2051678983).jpg"
PH_ATAC_WASTE = "A challenging wasteland (img 0285-cc).jpg"
PH_ATAC_COAST = "A portion of the Atacama Desert along Peru’s southern Pacific coast (iss074e0315662).jpg"
PH_SKELETON = "Huge Dunes at Skeleton Coast (37714628376).jpg"
PH_LEEUWIN_SUNSET = "Sunset at Cape Leeuwin (January 2005).jpg"
PH_LEEUWIN_LH = "CapeLeeuwinLighthouse gobeirne.jpg"
PH_SPINIFEX = "147 Nr Pt Hedland, July 1976 (51764953624).jpg"
PH_KARIJINI_HILL = "Karijini National Park (2052475590).jpg"
PH_KARIJINI_GORGE = "Karijini National Park (2052472982).jpg"
PH_BIF = "Banded iron formation Dales Gorge.jpg"
PH_GASC_DRY = "Dry Gascoyne River Bed - panoramio.jpg"
PH_GASC_CROSSING = "Gascoyne River Crossing - panoramio.jpg"
PH_GASC_SOAK = "Gascoyne soakage pool.png"
PH_PLANT_TANK = "Bathing in the big tank on Perret's plantation, Carnarvon (full).png"
PH_BANANAS = "Margaret Hall and Les Skipworth, Carnarvon (cropped).png"
PH_CARN_1969 = "69-1362 Carnarvon, Australia 1969 (51216478649).jpg"
PH_CARN_FASCINE = "69-1364 Carnarvon, Australia 1969 (51216478639).jpg"
PH_HAMELIN1 = "Hamelin Pool (39922169782).jpg"
PH_HAMELIN2 = "Hamelin Pool (Stromatolites) (2051681949).jpg"
PH_HAMELIN_WALK = "Hamelin Pool (Stromatolites) (2051681681).jpg"
PH_SHELL = "Shelly Beach - panoramio - Halooch (1).jpg"
PH_RED_TRACK = "Monkey Mia (2052469310).jpg"
PH_SHARK_CLIFF = "- panoramio - Halooch.jpg"
PH_SHARK_UNSPLASH = "Shark Bay, Australia (Unsplash).jpg"
PH_SHARK_ISS = "ISS006-E-35196 - View of Western Australia.jpg"
PH_SHARK_MODIS = "Shark Bay (MODIS 2021-06-21).jpg"
PH_CHART_1835 = "Admiralty Chart No 1056 West Coast of Australia. Sheet VIII, Published 1835.jpg"
PH_CHART_ABR = "Admiralty Chart No 1723 The Houtman Rocks, Published 1845.jpg"
PH_REPLICA_SAIL = "De BATAVIA voor de film onderweg als de NIEUW HOORN (01).jpg"
PH_REPLICA_SAIL2 = "De BATAVIA voor de film onderweg als de NIEUW HOORN (03).jpg"
PH_PLATES = "Drik hartog's plate, 1616 and vlaming's plate, 1697 - cyclopedia of western australia.jpg"
PH_RIJKS = "Rijksmuseum (tram cables digitally removed) (5821431193).jpg"
PH_BAT1 = "Batavia Pl.1 State Library of New South Wales FL3726277.jpg"
PH_BAT2 = "Batavia Pl.2 State Library of New South Wales FL3726280.jpg"
PH_BAT3 = "Batavia Pl.3 State Library of New South Wales M DSM C530.jpg"
PH_BAT4 = "Batavia Pl.4 State Library of New South Wales FL3726284.jpg"
PH_BAT6 = "Batavia Pl.6 State Library of New South Wales FL3726288.jpg"
PH_MASSACRE = "AMH-6776-KB Massacre after the shipwreck of the Batavia in 1629.jpg"
PH_ABR_ISS = "STS107-E-5578 - View of Western Australia.jpg"
PH_HULL = "WTF Marlene Oostryck Maritime Museum Batavia from above.jpg"
PH_HULL_STERN = "WTF Marlene Oostryck Maritime Museum Batavia stern.jpg"
PH_DAMPIER = "Schrijver William Dampier in een kleine open prauw op reis naar Aceh (Indonesië), Caspar Luyken, Abraham de Hondt, 1698 - Rijksmuseum.jpg"
PH_DAMPIER_MAP = "Map-dampier-roebuck-1699.jpg"
PH_BROOME_CLIFFS = "Broomewestern Australia.JPG"
PH_FREMANTLE_1832 = "View of Freemantle (Western Australia) From Church Hill E. of the Town.jpg"
PH_MORRELL = "Fremantle, 1832 from original sketch by r morrell - cyclopedia of western australia.jpg"
PH_STATUE = "Porcelli with O'Connor statue.png"
PH_MUNDARING_69 = "69-1380 Mundaring Weir, Australia 1969 (51215929778).jpg"
PH_MUNDARING_PUMP = "2000 Mundaring Weir-04.jpg"
PH_MUNDARING_LOW = "2000 Mundaring Weir-09.jpg"
PH_MUNDARING_LOW2 = "2000 Mundaring Weir-08.jpg"
PH_MUNDARING_2025 = "Mundaring Weir - April 2025.jpg"
PH_PIPE_MERREDIN = "CSIRO ScienceImage 6380 Section of the Perth Kalgoorlie water supply pipeline near Merredin WA 1976.jpg"
PH_PIPE_AIR = "E37 Clackline Lion Park - Goldfields pipeline.JPG"
PH_PIPE_SMC = "Goldfields Pipeline SMC.JPG"
PH_SERPENTINE = "Serpentine Dam View.jpg"
PH_CANNING = "Canningdam spillway.jpg"
PH_VANCE = "Vance 1999-03-21 0425Z.png"
PH_VANCE2 = "Vance 1999-03-20 2332Z.png"
PH_VANCE_TRACK = "Vance 1999 track.png"
PH_MARBLE_76 = "151 Marble Bar, July 1976 (51772923349).jpg"
PH_MARBLE_PUB = "69-07 Centralian Tours 306 Marble Bar, Australia 1969 (51240178409).jpg"
PH_LUGGER = "Pearlingluggerpenguin.JPG"
PH_JAP_CEM = "Japanese Cemetery, Broome, WA, Australia 01.jpg"
PH_JAP_CEM_1939 = "Japanese Cemetery Broome 1939 SLNSW FL18913679.jpg"
PH_CABLE = "Dusk at Cable Beach, Broome, WA, Australia 01.jpg"
PH_CABLE2 = "Dusk at Cable Beach, Broome, WA, Australia 04.jpg"
PH_HEDLAND_76 = "149b Pt Hedland, July 1976 (51765181505).jpg"
PH_NEWMAN_MINE = "Mount Newman Mining Co. - panoramio.jpg"
PH_SHIPLOADER = "Port Headland - panoramio.jpg"
PH_ORE_TRAIN = "Iron train loading paraburdoo mine.jpg"
PH_PARA_MINE = "Mining operations paraburdoo mine.jpg"
PH_WING = "CG Gainer Pilbara Visit September 2020 (50351659681).jpg"
PH_DAMPIER_PORT = "Dampier Port panorama Nov06 SMC.jpg"
PH_WITT_1966 = "1966 WITTENOOM (3371782555).jpg"
PH_WITT_MILL = "69-07 Centralian Tours 328 Wittenoom Gorge, Australia 1969 (51240464100).jpg"
PH_WITT_HUT = "Quonsett hut at wittenoom.jpg"
PH_WITT_ROAD = "Deserted traffic island wittenoom.jpg"
PH_WITT_TAILINGS = "Asbestos tailings wittenoom gorge.jpg"
PH_WITT_GORGE = "Tree in the rock wittenoom gorge.jpg"

# ------------------------------------------------------------------ places, routes and arrows
PERTH = place("Perth", 115.86, -31.95, "Perth", "city")
FREMANTLE = place("Fremantle", 115.75, -32.05, "Fremantle", "site")
CARNARVON = place("Carnarvon", 113.66, -24.88, "Carnarvon", "city")
BRISBANE = place("Brisbane", 153.03, -27.47, "Brisbane", "city")
SYDNEY = place("Sydney", 151.21, -33.87, "Sydney", "city")
EXMOUTH = place("Exmouth", 114.13, -21.93, "Exmouth", "site")
BROOME = place("Broome", 122.24, -17.96, "Broome", "city")
HEDLAND = place("Port Hedland", 118.60, -20.31, "Port Hedland", "port")
DAMPIER = place("Dampier", 116.71, -20.66, "Dampier", "port")
TOM_PRICE = place("Tom Price", 117.79, -22.69, "Tom Price", "site")
WITTENOOM = place("Wittenoom", 118.34, -22.24, "Wittenoom", "site", icon="warning")
MEHARRY = place("Mount Meharry", 118.59, -22.98, "Mount Meharry, 1,249 m", "site")
KALGOORLIE = place("Kalgoorlie", 121.47, -30.75, "Kalgoorlie", "city")
COOLGARDIE = place("Coolgardie", 121.17, -30.95, "Coolgardie", "site")
MUNDARING = place("Mundaring Weir", 116.16, -31.95, "Mundaring Weir", "site")
GERALDTON = place("Geraldton", 114.61, -28.78, "Geraldton", "city")
ABROLHOS = place("Houtman Abrolhos", 113.80, -28.60, "Houtman Abrolhos", "site", icon="warning")
HAMELIN = place("Hamelin Pool", 114.20, -26.40, "Hamelin Pool", "site")
HARTOG = place("Dirk Hartog Island", 113.05, -25.60, "Dirk Hartog Island, 1616", "site")
ATACAMA = place("Atacama", -69.9, -24.0, "Atacama", "label")
NAMIB = place("Namib", 15.0, -24.0, "Namib", "label")
CAPE = place("Cape of Good Hope", 18.47, -34.36, "Cape of Good Hope", "port")
JAVA = place("Batavia (Jakarta)", 106.82, -6.13, "Batavia (Jakarta)", "port")

LAT_LINE = {"from": [113.66, -24.88], "to": [153.03, -27.47], "mode": "line", "label": "Almost the same distance from the equator",
            "color": "accent", "seconds": 3.0}
BROUWER = {"from": [18.47, -34.36], "via": [[45.0, -38.5], [80.0, -38.5], [104.0, -36.0], [107.0, -20.0]], "to": [106.82, -6.13],
           "mode": "line", "label": "The Dutch route to Java", "color": "accent", "seconds": 4.5}
PIPE = {"from": [116.16, -31.95], "via": [[116.67, -31.65], [118.28, -31.48], [119.33, -31.23]], "to": [121.47, -30.75],
        "mode": "line", "label": "Goldfields pipeline, 566 km", "color": "blue", "seconds": 4.0}
TOO_LATE = [{"from": [104.0, -36.0], "to": [113.3, -28.5], "color": "red", "label": "Turn too late", "bend": -0.15}]
SE_PACIFIC = [{"from": [165.0, -20.0], "to": [153.8, -26.0], "color": "blue", "label": "Moist Pacific air", "bend": 0.1},
              {"from": [163.0, -29.0], "to": [153.6, -31.0], "color": "blue", "bend": -0.05}]
ACROSS = [{"from": [146.0, -24.0], "to": [128.0, -23.5], "color": "alt", "label": "Over dry land", "bend": 0.08},
          {"from": [128.0, -23.5], "to": [114.5, -24.5], "color": "red", "label": "Arrives dry", "bend": 0.05}]
LEEUWIN = [{"from": [113.2, -21.5], "to": [113.6, -28.0], "color": "red", "label": "Leeuwin Current", "bend": 0.08},
           {"from": [113.6, -28.0], "to": [115.0, -34.6], "color": "red", "bend": 0.1}]
WINTER = [{"from": [98.0, -40.0], "to": [114.8, -33.0], "color": "blue", "label": "Winter storms", "bend": -0.12}]

chapters = []
heads = iter(HEADS)


def chapter(*paras):
    title, mood = next(heads)
    chapters.append({"title": title, "mood": mood, "paragraphs": list(paras)})


# ------------------------------------------------------------------ photos added in pass 2 (sharpness checked: scratch awc_q.py)
PH_CAPE_ROAD = "Cape Ranges National Park - Flickr - GregTheBusker.jpg"
PH_KALBARRI_GLOW = "Kalbarri (2052466486).jpg"
PH_KALBARRI_2 = "In the Kalbarri National Park (15003350020).jpg"
PH_KALBARRI_3 = "In the Kalbarri National Park (15002665629).jpg"
PH_KALBARRI_4 = "In the Kalbarri National Park (15003540857).jpg"
PH_KARIJINI_2 = "Karijini National Park (2052473138).jpg"
PH_KARIJINI_3 = "Karijini National Park (2051689193).jpg"
PH_KARIJINI_GUM = "Karijini National Park (2051688725).jpg"
PH_JOFFRE = "Joffre Gorge, Karijini National Park.jpg"
PH_DALES = "Dales Gorge, WA.jpg"
PH_NAMIB = "Namibie Skeleton Coast 01.JPG"
PH_NINGALOO_MODIS = "Ningaloo Coast and Lake Macleod, Western Australia (MODIS 2021-10-01).jpg"
PH_MONKEY_MIA = "Monkey Mia from the water - panoramio.jpg"
PH_BRIS_MERIVALE = "AUS Brisbane, Central Business District, Merivale Bridge 002.jpg"
PH_ROCKY_POOL = "Rocky Pool - Gascoyne River - panoramio.jpg"
PH_KYBRA = "Kybra alongside jetty slwa b2392712 1.png"
PH_CARN_STREET = "Street in Carnarvon.png"
PH_FASCINE = "Still morning at the Fascine, Carnarvon (cropped).png"
PH_SHARK_ISS2 = "ISS014-E-18727 - View of Western Australia.jpg"
PH_BAT5 = "Batavia Pl.5 State Library of New South Wales FL3726286.jpg"
PH_ABR_ISS2 = "STS107-E-5575 - View of Western Australia.jpg"
PH_MOLL = "Moll - A map of the world shewing the course of Mr Dampiers voyage round it from 1679 to 1691.png"
PH_REPLICA_DOCK = "20140612 Batavia replica2 Lelystad.jpg"
PH_ROEBUCK = "Low tide at Roebuck Bay, Broome, WA, Australia 01.jpg"
PH_LAKE_OCONNOR = "Lake O'Connor SMC.jpg"
PH_STATUE2 = "CY O'Connor statue at sunset.jpg"
PH_PERTH_7 = "AUS Perth, Central Business District, Kings Park, View 007.jpg"
PH_PERTH_9 = "AUS Perth, Central Business District, Kings Park, View 009.jpg"
PH_PERTH_19 = "AUS Perth, Central Business District, Kings Park, View 019.jpg"
PH_PERTH_20 = "AUS Perth, Central Business District, Kings Park, View 020.jpg"
PH_APPLECROSS = "Applecross viewed from Kings Park (cropped).jpg"
PH_COTTESLOE2 = "AUS Perth, Cottesloe, Cottesloe Beach 011.jpg"
PH_SERP_TOWER = "Serpentine Dam Intake Tower.jpg"
PH_CANNING_PANO = "Canningdam panorama2.jpg"
PH_PILBARA_76 = "146 Nr Pt Hedland, July 1976 (51765181685).jpg"
PH_HEDLAND_76B = "149c Pt Hedland, July 1976 (51764307101).jpg"
PH_STOCKYARD = "CG Gainer Pilbara Visit September 2020 (50350968938).jpg"
PH_RECLAIMER = "CG Gainer Pilbara Visit September 2020 (50350969378).jpg"
PH_CSIRO_LOADER = "CSIRO ScienceImage 11678 A Rio Tinto iron ore shiploader in operation in the Pilbara.jpg"
PH_NEWMAN_MINE2 = "Mount Newman Mining Co. - panoramio - Seko Naotomo.jpg"
PH_HEDLAND_ISS = "ISS045-E-3246 - View of Western Australia.jpg"
PH_WITT_GORGE69 = "69-07 Centralian Tours 330 Wittenoom Gorge, Australia 1969 (51239610298).jpg"
PH_EXMOUTH_BASE = "Exmouth WA ex US Base.JPG"
PH_YARDI = "Yardi Creek - Flickr - GregTheBusker.jpg"
LACEPEDE = place("Lacepede Islands", 122.12, -16.85, "Lacepede Islands", "site", icon="warning")
KIMB = {"lon": 122.4, "lat": -17.6, "span": 3.2}       # Broome and the Lacepede Islands

# ================================================================== Hook
chapter(
    P("P0",
      m(0, v(WA, highlight=[WA_RED])),
      stat("nearly thirteen thousand kilometres", "12,889 KM", "Mainland coastline of Western Australia", GA),
      m("Fly along it at", v(WA, layer="night"))),
    P("P1",
      m(0, v(SW, layer="night", places=[PERTH])),
      photo("About eight in every", PH_PERTH_NIGHT, "Perth"),
      stat("live in and around", "80 %", "Western Australians living in Greater Perth, 2023-24", WAPOP),
      photo("Leave it behind and", PH_CARAVAN, "Near Exmouth"),
      photo("drive for days along", PH_CAPE_ROAD, "Cape Range, near Exmouth"),
      photo("mining ports and empty", PH_SANDY_BAY, "Sandy Bay, Cape Range")),
    P("P2",
      m(0, v(AUS, layer="night")),
      m("And Carnarvon, on the", v(AUS, places=[CARNARVON]),
        step("as Brisbane does on", places=[BRISBANE], routes=[LAT_LINE])),
      photo("Brisbane gets about a", PH_BRIS_RIVER, "Brisbane"),
      chart("Carnarvon gets about two", "Rain in an average year (mm)", "", [["Brisbane", 1031], ["Carnarvon", 230]],
            "Bureau of Meteorology", highlight=1)),
    P("P3",
      photo(0, PH_FASCINE, "Carnarvon, about 1930"),
      photo("More than four times", PH_BRIS_GREEN, "Brisbane"),
      photo("And now even Perth,", PH_PERTH_GOLD, "Perth"),
      photo("is losing the rain", PH_LAKE_OCONNOR, "Mundaring Weir, in the hills above Perth")),
    P("P4",
      m(0, v(WEST, highlight=[COAST_RED])),
      photo("a wind that blows", PH_KALBARRI_GLOW, "Kalbarri"),
      photo("a river that hides", PH_GASC_DRY, "The dry bed of the Gascoyne"),
      photo("a Dutch shipwreck and", PH_BAT1, "The Batavia, from Pelsaert's journal (1647)"),
      photo("one of the strongest", PH_VANCE_TRACK, "Cyclone Vance, March 1999"),
      photo("a town that was", PH_WITT_1966, "Wittenoom, 1966"),
      sat("and a city that", 115.765, -32.20, 0.12, "Kwinana desalination plant, Perth")),
)

# ================================================================== 1. The Wrong Side of the Wind
chapter(
    P("P5",
      m(0, v(WEST, highlight=[DRY_RED])),
      m("Australia lies under a", v(GLOBE_S, highlight=[RIDGE_ALT]),
        v({"lon": 95.0, "lat": -26.0, "span": 150.0}, at="circles the globe at")),
      photo("Air in that belt", PH_ATAC_WASTE, "Atacama Desert, Chile"),
      m("It is the same", v(GLOBE_S, highlight=[RIDGE_ALT], places=[ATACAMA, NAMIB, CARNARVON])),
      photo("two deserts that also", PH_ATAC_COAST, "The Atacama meets the Pacific")),
    P("P6",
      m(0, v(AUS, highlight=["Queensland@alt"]), step("On the east coast,", arrows=SE_PACIFIC)),
      m("and hit a long", v(EASTC, highlight=[RANGE_ALT], places=[BRISBANE])),
      photo("The air rises, cools", PH_BRIS_CBD, "Brisbane"),
      photo("That is why Brisbane", PH_BRIS_GREEN, "Brisbane")),
    P("P7",
      m(0, v(AUS, arrows=ACROSS[:1]), step("it has crossed thousands", arrows=ACROSS[1:])),
      photo("It arrives from the", PH_SPINIFEX, "Near Port Hedland"),
      photo("And there are no", PH_KALBARRI_GORGE, "Murchison River gorge, Kalbarri"),
      photo("to squeeze out what", PH_KALBARRI_2, "Kalbarri"),
      m("The highest peak in", v(PILB, highlight=[HAM_ALT], places=[MEHARRY])),
      stat("reaches only about twelve", "1,249 M", "Mount Meharry, highest point of Western Australia", GA),
      photo("and it sits far", PH_KARIJINI_HILL, "Hamersley Range")),
    P("P8",
      photo(0, PH_SKELETON, "Skeleton Coast, Namibia"),
      photo("cold water wells up", PH_NAMIB, "Skeleton Coast, Namibia"),
      m("Off Western Australia, something", v(WEST), step("the Leeuwin Current, flows", arrows=LEEUWIN)),
      photo("Scientists describe it as", PH_WHALESHARK, "Ningaloo, off Exmouth"),
      photo("an eastern boundary current", PH_NINGALOO_MODIS, "The Ningaloo coast from orbit"),
      photo("carries tropical heat towards", PH_LEEUWIN_LH, "Cape Leeuwin")),
    P("P9",
      photo(0, PH_MONKEY_MIA, "Shark Bay"),
      stat("four to six degrees", "+4-6 °C", "Sea off Western Australia, against other desert coasts at its latitude", "CSIRO"),
      photo("That warmth gives Perth", PH_COTTESLOE, "Cottesloe, Perth"),
      photo("It feeds coral reefs", PH_SNORKEL, "Ningaloo Reef"),
      sat("North of Perth, the", 114.10, -22.10, 0.45, "North West Cape")),
)

# ================================================================== 2. Rivers That Hide
chapter(
    P("P10",
      m(0, v(WEST, highlight=[DRY_RED], places=[CARNARVON])),
      photo("The east coast has", PH_BRIS_MERIVALE, "The Brisbane River"),
      photo("Most rivers in the", PH_GASC_CROSSING, "Gascoyne River crossing")),
    P("P11",
      sat(0, 113.68, -24.87, 0.2, "The Gascoyne reaches the sea at Carnarvon"),
      photo("For most of the", PH_GASC_DRY, "The dry bed of the Gascoyne"),
      photo("Locals call it the", PH_ROCKY_POOL, "Rocky Pool, Gascoyne River"),
      sat("in the sand and", 113.86, -24.89, 0.1, "The dry bed of the Gascoyne")),
    P("P12",
      photo(0, PH_PLANT_TANK, "A plantation water tank, Carnarvon, about 1930"),
      sat("Since about the nineteen", 113.74, -24.86, 0.14, "Plantations along the Gascoyne"),
      photo("and Carnarvon became a", PH_KYBRA, "MV Kybra at Carnarvon jetty, 1930s"),
      stat("In the nineteen sixties,", "1960s", "Limits on pumping after the plantations failed", "WA Government, Lower Gascoyne"),
      photo("and many of the", PH_CARN_STREET, "Carnarvon, about 1920"),
      photo("Since then the state", "Gascoyne River Outflow (51225476925).png", "The Gascoyne in flood, 2021, from orbit")),
    P("P12b",
      m(0, v(SHARKB, places=[HAMELIN, CARNARVON])),
      sat("In a shallow arm", 114.20, -26.40, 0.25, "Hamelin Pool"),
      stat("the sea is about", "2×", "Salt in Hamelin Pool, against normal seawater", "DBCA, Shark Bay World Heritage"),
      photo("Few of the animals", PH_HAMELIN1, "Stromatolites, Hamelin Pool"),
      photo("So on its floor,", "Hamelin Pool (26081546618).jpg", "Hamelin Pool"),
      photo("the same kind of", PH_HAMELIN2, "Stromatolites, Hamelin Pool"),
      photo("They survive here because", PH_HAMELIN_WALK, "Hamelin Pool"),
      stat("Shark Bay became a", "1991", "Shark Bay on the World Heritage List", "UNESCO")),
    P("P13",
      photo(0, PH_SHELL, "Shell Beach, Shark Bay"),
      photo("That is roughly the", PH_RED_TRACK, "Peron Peninsula, Shark Bay"),
      photo("And for a long", PH_CHART_1835, "The west coast on an Admiralty chart, 1835"),
      photo("decided it could not", PH_KALBARRI_3, "Kalbarri")),
)

# ================================================================== 3. The Ships That Kept Going
chapter(
    P("P14",
      m(0, v(INDIAN, highlight=[WA_RED])),
      photo("The first Europeans known", PH_REPLICA_SAIL, "A Dutch East India ship (replica)"),
      m("Their ships sailed from", v(INDIAN, places=[CAPE]),
        step("on the strong westerly", routes=[BROUWER]),
        step("then turned north towards", places=[JAVA]),
        step("Turn too late, and", arrows=TOO_LATE))),
    P("P15",
      m(0, v(SHARKB, places=[HARTOG])),
      sat("He landed on an", 113.05, -25.85, 0.5, "Dirk Hartog Island"),
      photo("nailed a flattened pewter", PH_PLATES, "Hartog's plate (1616) and Vlamingh's plate (1697)"),
      stat("It is the oldest", "1616", "Hartog's plate: the oldest European object known from Australia", WAM),
      photo("Then he sailed on.", PH_SHARK_CLIFF, "Shark Bay coast")),
    P("P15b",
      photo(0, PH_SHARK_ISS, "Shark Bay from orbit"),
      photo("On the same island", PH_SHARK_ISS2, "Shark Bay from orbit"),
      stat("He put up a", "1697", "Vlamingh replaces Hartog's plate and takes the original", WAM),
      photo("It ended up in", PH_RIJKS, "The Rijksmuseum, Amsterdam"),
      photo("Two visits, eighty years", PH_KALBARRI_4, "The coast south of Shark Bay")),
    P("P16",
      m(0, v(MIDW, places=[ABROLHOS, GERALDTON])),
      photo("one of the Dutch", PH_REPLICA_SAIL2, "A replica of the Batavia"),
      sat("struck a reef in", 113.80, -28.47, 0.15, "Wallabi Group, Houtman Abrolhos", date=ABR),
      photo("Most of the people", PH_BAT1, "The wreck, from Pelsaert's journal (1647)")),
    P("P17",
      photo(0, PH_BAT2, "From Pelsaert's journal (1647)"),
      photo("While he was gone,", PH_BAT5, "From Pelsaert's journal (1647)"),
      photo("took control of the", PH_BAT3, "From Pelsaert's journal (1647)"),
      stat("According to the Western", "~125", "Men, women and children killed by the mutineers", WAM),
      photo("When Pelsaert returned with", PH_BAT6, "The trial and executions (1647)"),
      photo("Almost four hundred years", PH_ABR_ISS, "The Abrolhos from orbit"),
      photo("where most of the", PH_ABR_ISS2, "The Abrolhos from orbit"),
      photo("Two young mutineers were", PH_KALBARRI_COAST, "The mainland opposite the Abrolhos"),
      photo("The wreck itself was", PH_HULL, "Part of the Batavia's hull, Fremantle"),
      photo("and part of its", PH_HULL_STERN, "WA Shipwreck Galleries, Fremantle"),
      sat("a short drive from", 115.75, -32.05, 0.1, "Fremantle")),
    P("P18",
      photo(0, PH_DAMPIER, "William Dampier (print, 1698)"),
      photo("In the account he", PH_DAMPIER_MAP, "Dampier's voyage of 1699, chart by Emanuel Bowen"),
      photo("with no water unless", PH_MOLL, "Map of Dampier's voyage round the world"),
      photo("His bleak picture of", PH_ROEBUCK, "Roebuck Bay, Broome")),
    P("P19",
      photo(0, PH_CHART_ABR, "The Houtman Rocks, Admiralty chart, 1845"),
      photo("and sailed past it.", PH_REPLICA_DOCK, "A Dutch East India ship (replica)"),
      m("When Britain finally did", v(AUS, places=[SYDNEY, PERTH]))),
)

# ================================================================== 4. A Colony on Sand
chapter(
    P("P20",
      m(0, v(SW, highlight=[PERTH_RED], places=[PERTH, FREMANTLE])),
      stat("In May eighteen twenty-nine,", "1829", "The Swan River Colony is founded", "Swan River Colony (via Wikipedia)"),
      photo("Its founders had expected", PH_FREMANTLE_1832, "Fremantle, 1832")),
    P("P21",
      sat(0, 115.85, -31.95, 0.6, "The Swan River and the coastal plain"),
      photo("The good farmland was", PH_PERTH_ISS, "The Swan River from orbit"),
      photo("Gardens failed. Twenty-one years", PH_MORRELL, "Fremantle, 1832 (sketch)"),
      stat("still had fewer than", "5,886", "Settlers in the colony, 1850", "Swan River Colony records (via Wikipedia)")),
    P("P22",
      m(0, v(GOLD, places=[PERTH, KALGOORLIE, COOLGARDIE])),
      photo("So the colony did", PH_STATUE, "Pietro Porcelli at work on O'Connor's statue, about 1910"),
      m("planned a steel pipeline", v(GOLD, places=[MUNDARING]),
        step("all the way to", routes=[PIPE], places=[KALGOORLIE])),
      stat("five hundred and sixty-six", "566 KM", "Mundaring Weir to Kalgoorlie, eight pumping stations", "WA Government heritage record")),
    P("P23",
      photo(0, PH_MUNDARING_PUMP, "Mundaring Weir"),
      photo("O'Connor did not see", PH_PIPE_AIR, "The Goldfields pipeline at Clackline"),
      photo("after fierce attacks on", PH_STATUE2, "O'Connor's statue"),
      photo("His pipeline still runs", PH_PIPE_MERREDIN, "The pipeline near Merredin, 1976")),
    P("P24",
      sat(0, 116.16, -31.955, 0.1, "Mundaring Weir"),
      photo("And the water to", PH_PIPE_SMC, "The Goldfields pipeline"),
      photo("The city became the", PH_PERTH_DAY, "Perth")),
    P("P24b",
      photo(0, PH_PERTH_19, "Perth"),
      chart("In nineteen eleven, about", "People of WA living in Perth", "%", [["1911", 33], ["1947", 50], ["2024", 80]],
            "Engineers Australia; WA Population Statement 2025 (about one third in 1911)",
            reveal=["By nineteen forty-seven it", "Today it is eight"], highlight=2),
      photo("Every decade, a larger", PH_PERTH_SWAN, "Perth"),
      photo("moved to the one", PH_PERTH_20, "Perth")),
)

# ================================================================== 5. The Cyclone Coast
chapter(
    P("P25",
      m(0, v(NW),
        step("According to the Bureau", highlight=[CYC_RED]),
        step("between Broome and Exmouth", places=[BROOME, EXMOUTH])),
      photo("Tropical cyclones cross it", PH_EXMOUTH_CLOUDS, "Exmouth"),
      stat("else on the continent,", "DEC-APR", "Cyclone season on the north-west coast", BOM)),
    P("P26",
      photo(0, PH_VANCE, "Cyclone Vance, 21 March 1999"),
      sat("Just before midday on", 114.09, -22.24, 0.12, "Learmonth, south of Exmouth"),
      stat("recorded a gust of", "267 KM/H", "Gust at Learmonth, 22 March 1999", BOM, note="Listed by the Bureau as a mainland record"),
      photo("The Bureau listed it", PH_VANCE_TRACK, "The track of Cyclone Vance")),
    P("P27",
      photo(0, PH_PILBARA_76, "The Pilbara, 1976"),
      sat("the Pilbara town of", 119.74, -21.17, 0.12, "Marble Bar"),
      stat("on one hundred and", "160 DAYS", "In a row at 37.8 °C or more, Marble Bar, 1923-24", "Bureau of Meteorology (original records)"),
      photo("from the end of", PH_KARIJINI_GUM, "The Pilbara")),
    P("P27b",
      sat(0, 122.23, -17.96, 0.2, "Broome"),
      photo("and hundreds of small", PH_LUGGER, "A pearling lugger (museum ship)"),
      photo("many crewed by Japanese", PH_JAP_CEM_1939, "Japanese cemetery, Broome, 1939"),
      m("In March nineteen thirty-five,", v(KIMB, places=[BROOME, LACEPEDE])),
      sat("near the Lacepede Islands.", 122.12, -16.85, 0.25, "The Lacepede Islands"),
      stat("Twenty-one luggers were lost.", "21 LUGGERS", "Lost in the cyclone of March 1935", "Bureau of Meteorology; Federal Cabinet report, April 1935",
           note="About 140 men drowned")),
    P("P28",
      photo(0, PH_CABLE, "Cable Beach, Broome"),
      photo("you get a place", PH_HEDLAND_76B, "Port Hedland, 1976"),
      photo("Yet some of the", PH_BIF, "Banded iron, Karijini")),
)

# ================================================================== 6. Rich, But No Cities
chapter(
    P("P29",
      m(0, v(PILB, places=[HEDLAND, DAMPIER]),
        step("Inland from the cyclone", highlight=[HAM_RED], places=[TOM_PRICE])),
      photo("with some of the", PH_NEWMAN_MINE, "An iron ore mine, Pilbara"),
      photo("In the year to", PH_RECLAIMER, "Iron ore machinery, Pilbara"),
      stat("shipped about seven hundred", "730.8 MT", "Iron ore shipped from Pilbara ports, 2024-25", PP),
      stat("The state says that", "~43 %", "Of the world's seaborne iron ore trade", PP),
      photo("and about four fifths", PH_CSIRO_LOADER, "Loading iron ore, Pilbara")),
    P("P30",
      sat(0, 118.59, -20.31, 0.15, "Port Hedland"),
      stat("Port Hedland shipped almost", "577.7 MT", "Iron ore through Port Hedland, 2024-25", PP),
      photo("more than any other", PH_SHIPLOADER, "Loading ore, Port Hedland"),
      photo("Yet the town around", "Admiralty Chart No 1437 Australia - North West coast Port Hedland, Published 1897.jpg", "Port Hedland on an Admiralty chart, 1897"),
      stat("had only about fifteen", "~15,300", "People in Port Hedland, incl. South Hedland, 2021", "ABS Census 2021")),
    P("P31",
      photo(0, PH_ORE_TRAIN, "An ore train loading, Paraburdoo"),
      photo("not on large crowds", PH_PARA_MINE, "Paraburdoo mine"),
      photo("Many workers do not", PH_NEWMAN_MINE2, "An iron ore mine, Pilbara"),
      photo("They fly in from", PH_WING, "Landing in the Pilbara"),
      sat("The money is made", 118.62, -20.36, 0.35, "Port Hedland and South Hedland"),
      photo("The families, the schools", PH_PERTH_DAY2, "Perth")),
    P("P32",
      m(0, v(PILB, places=[TOM_PRICE]),
        step("In the gorges of", highlight=[HAM_ALT], places=[WITTENOOM])),
      photo("a town called Wittenoom", PH_WITT_1966, "Wittenoom, 1966"),
      photo("The company closed the", PH_WITT_GORGE69, "Wittenoom Gorge, 1969"),
      photo("and the government later", PH_WITT_HUT, "Wittenoom")),
    P("P33",
      stat(0, "1978-2007", "Wittenoom wound down, its power cut (2006), then removed from the map", WAG),
      photo("In two thousand and", PH_WITT_ROAD, "Wittenoom"),
      sat("the town was officially", 118.34, -22.25, 0.12, "Wittenoom today"),
      photo("More than two thousand", PH_KARIJINI_3, "The Hamersley gorges"),
      stat("of the roughly twenty", "2,000+", "Former workers and residents dead of asbestos diseases",
           "Asbestos Diseases Society; WA Government", note="Of roughly 20,000"),
      photo("according to health groups", PH_KARIJINI_HILL, "Hamersley Range"),
      photo("The last resident left", PH_DALES, "Dales Gorge, Hamersley Range"),
      photo("About three million tonnes", PH_WITT_TAILINGS, "Asbestos tailings, Wittenoom Gorge"),
      photo("and the road signs", PH_JOFFRE, "Gorges of the Hamersley Range")),
)

# ================================================================== 7. The One City Runs Dry
chapter(
    P("P34",
      m(0, v(WA, places=[PERTH]),
        step("and from the same", highlight=[PERTH_RED]),
        v(WIND_WA, at="Perth was built on", arrows=WINTER)),
      photo("The south-west corner is", PH_LEEUWIN_SUNSET, "Cape Leeuwin"),
      photo("and that is exactly", PH_PERTH_7, "Perth"),
      photo("Its water came from", PH_SERPENTINE, "Serpentine Dam")),
    P("P35",
      photo(0, PH_CANNING, "Canning Dam"),
      photo("According to Perth's water", PH_SERP_TOWER, "Serpentine Dam"),
      stat("rainfall in the dam", "−15-20 %", "Rain in Perth's dam catchments since the mid-1970s", WC),
      stat("But the flow of", "−80 %", "Water flowing into Perth's dams", WC),
      photo("because dry ground soaks", PH_MUNDARING_LOW2, "Mundaring Weir")),
    P("P36",
      chart(0, "Into Perth's dams (billion litres a year)", "",
            [["Before 1975", 420], ["Last decade", 75], ["2026", 12.5]], WC,
            reveal=["In the last decade,", "This year, after a"], highlight=2),
      photo("little more than twelve", PH_CANNING_PANO, "Canning Dam")),
    P("P37",
      sat(0, 115.765, -32.20, 0.1, "Kwinana desalination plant, 2006"),
      sat("and a second one", 115.71, -33.15, 0.1, "Southern Seawater plant, Binningup"),
      stat("Together, the plants can", "~1/2", "Of Perth's drinking water made from the sea", "BoM National Water Account 2025"),
      stat("The southern plant alone", "~30 %", "From the Southern Seawater plant, on average", WC),
      sat("A third plant, at", 115.66, -31.62, 0.1, "Alkimos, north of Perth"),
      stat("is due to add", "+50 GL", "A year from the Alkimos plant, from 2028", WC)),
    P("P37b",
      sat(0, 115.86, -31.66, 0.3, "Gnangara, north of Perth"),
      stat("levels have fallen by", "UP TO 10 M", "Fall in Gnangara groundwater levels since 1980", WAG),
      stat("The state estimates about", "~1,000 GL", "Groundwater storage lost", WAG),
      sat("So Perth now cleans", 115.77, -31.79, 0.1, "Craigie: recycled water pumped underground"),
      stat("up to twenty-eight billion", "28 GL", "A year recharged into the aquifers", WC)),
    P("P38",
      photo(0, PH_PERTH_DUSK, "Perth"),
      photo("now makes a large", PH_APPLECROSS, "Perth and the Swan River"),
      photo("The coast's only success", PH_PERTH_RIVER, "Perth and the Swan River"),
      photo("that kept the rest", PH_YARDI, "Yardie Creek, Cape Range")),
)

# ================================================================== Ending
chapter(
    P("P39",
      m(0, v(WA, places=[PERTH, CARNARVON, BROOME]), step("The wind comes from", arrows=ACROSS[1:])),
      photo("The rivers hide underground.", PH_GASC_CROSSING, "The Gascoyne"),
      photo("The first Europeans who", PH_BAT4, "From Pelsaert's journal (1647)"),
      photo("The soil was sand.", PH_KALBARRI_BEND, "Kalbarri"),
      photo("The north is a", PH_VANCE, "Cyclone Vance, 1999"),
      photo("And the wealth that", PH_DAMPIER_PORT, "Dampier port"),
      photo("without building towns to", PH_HEDLAND_ISS, "Port Hedland from orbit")),
    P("P40",
      photo(0, PH_PERTH_NIGHT2, "Perth"),
      photo("and then because everything", PH_PERTH_9, "Perth"),
      photo("Now even that corner", PH_MUNDARING_2025, "Mundaring Weir, April 2025")),
    P("P41",
      photo(0, "Lighthouse (7893989706).jpg", "Vlamingh Head lighthouse, Exmouth"),
      photo("with new ports, new", PH_CSIRO_LOADER, "Loading iron ore, Pilbara"),
      photo("Others say the coast", PH_YARDIE, "Yardie Creek, Cape Range"),
      photo("that the money is", PH_COTTESLOE2, "Cottesloe, Perth")),
    P("P41b",
      photo(0, PH_KARIJINI_GORGE, "Karijini"),
      photo("The wind will still", PH_KARIJINI_2, "Karijini"),
      photo("And the one city", PH_CABLE2, "Cable Beach, Broome"),
      photo("what it has done", PH_PERTH_DAY, "Perth"),
      m("finding water where the", v(WA, layer="night", places=[PERTH]))),
    P("P42",
      m(0, v(WEST, places=[CARNARVON, HEDLAND]), step("or leave it as", places=[PERTH])),
      ask=("Should Australia try to", "A second big city on the west coast, or leave it as it is?")),
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
            if h.startswith("file:ridge"):
                continue  # a schematic belt around the globe: the hand-picked view shows the part that matters
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


TITLE = "Why Australia's West Coast Has Only One City"
script = {
    "title": TITLE,
    "voice": "am_michael",
    "voice_speed": 1.15,
    "music": "procedural",
    "map_style": "satellite",
    "look": "none",
    "photo_upscale": True,
    "sources": ["episodes/australia-west-coast/research.md and factcheck.md", "Contains modified Copernicus Sentinel data 2026",
                "Dutch route, pipeline and wind arrows drawn through main points (approximate)",
                "Coast strip, cyclone coast and Greater Perth: geo/make_regions.py (Natural Earth, buffers; approximate)",
                "Share of WA in Perth, 1911: 'about one third' shown as 33 %"],
    "thumbnail": {"text": "ONLY ONE CITY"},
    "chapters": chapters,
    "youtube": {
        "title": TITLE,
        "title_candidates": [TITLE, "Why Almost Nobody Lives on Australia's West Coast", "Why Perth Is the Only City on Australia's West Coast"],
        "description": "Western Australia has nearly 13,000 km of mainland coast, yet eight in ten Western Australians live in one city, Perth. Carnarvon sits almost as far from the equator as Brisbane and gets less than a quarter of its rain. We follow the answer from orbit: the wind that blows the wrong way, the Leeuwin Current, the upside-down Gascoyne River and Shark Bay's stromatolites, Dirk Hartog's plate and the Batavia massacre, the Swan River Colony and C. Y. O'Connor's pipeline, Cyclone Vance and the Broome pearling fleet, Port Hedland's iron ore and the erased town of Wittenoom, and the city that now makes its water from the sea.",
        "tags": ["Western Australia", "Australia", "Perth", "west coast", "Carnarvon", "Shark Bay", "Batavia", "Houtman Abrolhos",
                 "Port Hedland", "Pilbara", "Wittenoom", "Cyclone Vance", "Broome", "desalination", "geography", "satellite images"],
        "pinned_comment": "Should Australia try to build a second big city on its west coast, or leave it as it is?",
    },
}
out = HERE / "script.json"
out.write_text(json.dumps(script, ensure_ascii=False, indent=1) + chr(10), encoding="utf-8")
words = sum(len(p["text"].split()) for c in chapters for p in c["paragraphs"])
shots = [s for c in chapters for p in c["paragraphs"] for s in p["shots"]]
kinds = {k: sum(1 for s in shots if s["type"] == k) for k in ("map", "photo", "stat", "document", "chart")}
print(f"{words} words, {len(chapters)} chapters, {len(shots)} shots {kinds}")
