"""Builds script.json for scottish-highlands.  python build_script.py

Same production logic as episodes/olympic-peninsula (hand-placed shots, a photo or map frame at most twice,
60 s apart). The narration lives in drafts/narration.md; every sentence comes from research.md. Photos and satellite
tests: visuals.md.
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
SUMMER = "2025-07-01/2025-09-15"   # scratch op_sat 2026-11-23: clear on every test view

def sat(at, lon, lat, span, label=None, **kw):
    kw.setdefault("date", SUMMER)
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
SCOT = {"lon": -4.3, "lat": 57.2, "span": 8.0}        # Scotland
NORTH = {"lon": -4.8, "lat": 57.7, "span": 5.0}       # the Highland council area
NSEA = {"lon": 0.5, "lat": 59.0, "span": 20.0}        # Scotland and Norway
VEST = {"lon": 6.2, "lat": 60.9, "span": 6.0}         # Vestland
CENTRAL = {"lon": -3.8, "lat": 56.4, "span": 4.2}     # Highland Boundary Fault and Midland Valley
SUTH = {"lon": -4.3, "lat": 58.25, "span": 2.6}       # Sutherland
SKYEV = {"lon": -6.15, "lat": 57.3, "span": 2.6}      # Skye
HEB = {"lon": -7.0, "lat": 57.4, "span": 5.0}         # Hebrides to St Kilda
ATL = {"lon": -35.0, "lat": 52.0, "span": 75.0}       # Scotland to Nova Scotia
GLOBE = {"lon": 60.0, "lat": 5.0, "span": 250.0}      # Scotland to Australia
SPRING25 = "2025-04-01/2025-06-15"                    # scratch sh_sat: the record-sunny spring of 2025

# ------------------------------------------------------------------ sources (research.md)
NRS = "National Records of Scotland, Census 2022"
VOB = "Census tables on today's boundaries (A Vision of Britain)"
MET = "Met Office 1991-2020 averages"
BGN = "Bergen kommune, 1991-2020 normal"
HANS = "Deer forest returns, Hansard 17 Apr 1893"
SP = "ScotlandsPeople (NRS)"
RSPB = "RSPB"
UNESCO = "UNESCO"
WIGHT = "Andy Wightman, Who Owns Scotland (2024)"
SSB = "Statistics Norway (via citypopulation.de)"

# ------------------------------------------------------------------ photos (visuals.md)
PH_FULMAR = "File:Dividing the catch of fulmar, St Kilda - George Washington Wilson.jpg"
PH_KILDA7 = "File:Village Bay St Kilda7.jpg"
PH_KILDA10 = "File:Village Bay St Kilda10.jpg"
PH_KILDA_SHEEP = "File:Sheep Village Bay St Kilda.jpg"
PH_KILDA_DUN = "File:Village Bay Dùn Stac Levenish.jpg"
PH_KILDA_LOCH = "File:Loch Hiort Village Bay St Kilda.jpg"
PH_KILDA_PEOPLE = "File:With nature and a camera; being the adventures and observations of a field naturalist and an animal photographer (1898) (14779445535).jpg"
PH_EIGG = "File:Isle of Eigg - Flickr - Graham Grinner Lewis.jpg"
PH_EIGG_SGURR = "File:Sgurr of Eigg in Scotland 20060517 F.jpg"
PH_SHIELINGS = "File:Ruined Shielings - Flickr - Graham Grinner Lewis.jpg"
PH_ARDVRECK = "File:Loch Assynt - Ardvreck Castle.JPG"
PH_ASSYNT4 = "File:Loch Assynt 4.JPG"
PH_ASSYNT = "File:Loch Assynt.JPG"
PH_CANISP = "File:Canisp from the east.jpg"
PH_CULMOR_PATH = "File:CulMorPath.jpg"
PH_CULMOR = "File:Cul Mor.jpg"
PH_INCHNA = "File:Inchnadamph.jpg"
PH_LOCHINVER = "File:Lochinver, Sutherland, Scotland, 15 April 2011 - Flickr - PhillipC.jpg"
PH_QUINAG = "File:Quinag, Sutherland, Scotland, 14 April 2011 - Flickr - PhillipC.jpg"
PH_SUILVEN = "File:Suilven from the North West1.JPG"
PH_SUILVEN_CLOUD = "File:Suilven in cloud (23282141404).jpg"
PH_STOER = "File:Stoer peninsula (2498227507).jpg"
PH_ACHNAHAIRD = "File:Achnahaird Bay - Flickr - Graham Grinner Lewis (1).jpg"
PH_FOINAVEN = "File:Foinaven - Flickr - Graham Grinner Lewis.jpg"
PH_LOCHANS = "File:A Lot of Lochs and Lochans - Flickr - Graham Grinner Lewis.jpg"
PH_OLDSHORE = "File:Oldshoremore Bay - Flickr - Graham Grinner Lewis.jpg"
PH_BLACKHOUSE = "File:Gearranan Blackhouse Village.jpg"
PH_PEAT = "File:Peat-Stack in Ness, Outer Hebrides, Scotland.jpg"
PH_BLIGHT = "File:Phytophtora infestans-effects.jpg"
PH_DUNROBIN = "File:Dunrobin Castle -Sutherland -Scotland-26May2008 (2).jpg"
PH_CONIC = "File:Conic Hill with sheep.jpg"
PH_GLENCOE = "File:The Three Sisters Valley, Glencoe, Scotland - 53744377929.jpg"
PH_GLENCOE2 = "File:Lost Valley Trail, Glencoe, Scotland - 53737911447.jpg"
PH_QUIRAING = "File:The Quiraing, Isle of Skye, Scotland.jpg"
PH_PORTREE = "File:Portree Harbour, Isle of Skye, Scotland.jpg"
PH_CUILLIN = "File:Main ridge of the cuillin in skye arp.jpg"
PH_TORRIDON = "File:Torridon panoramic view June 2024.jpg"
PH_BEN_NEVIS = "File:Ben Nevis and Fort William from west.jpg"
PH_NESS_AIR = "File:Aerial view of Loch Ness.jpg"
PH_NESS_FA = "File:Great Glen Way - View of Loch Ness from Fort Augustus.JPG"
PH_INVERNESS = "File:From Inverness Castle towards the sea. - panoramio.jpg"
PH_INVERNESS2 = "File:Inverness - panoramio (13).jpg"
PH_CULLODEN = "File:The Battle of Culloden.jpg"
PH_LEANACH = "File:Culloden Battlefield- Leanach Cottage in Culloden Moor.jpg"
PH_ANSDELL = "File:Richard Ansdell - Collecting the sheep for clipping in the highlands (1881).jpg"
PH_HECTOR = "File:Hector (ship).jpg"
PH_CATTLE = "File:Highland cattle (14092287711).jpg"
PH_DEER1 = "File:Cervus elaphus (51307220686).jpg"
PH_DEER2 = "File:Cervus elaphus (51382686946).jpg"
PH_STALKER = "File:Professional stalker standing next to red deer stag Ardnamurchan Estate Scotland 01.png"
PH_SHEEP = "File:Curious - panoramio.jpg"
PH_PITLOCHRY = "File:Pitlochry Power Station.JPG"
PH_CRUACHAN = "File:Dam at Cruachan reservoir.jpg"
PH_BRYGGEN = "File:Bryggen - 5003 Bergen Norway.jpg"
PH_BRYGGEN_W = "File:Bryggen i Bergen - vinter 2025.jpg"
PH_BERGEN = "File:Bergen in the morning in june.JPG"
PH_BERGEN1910 = "File:Bergen (View from Fløyen) (Fylkesarkivet i Sogn og Fjordane).jpg"
PH_NAEROY = "File:Nærøyfjord - 49522345691.jpg"
PH_SOGNE = "File:Sognefjord-Norway-April-2011.jpg"
PH_DALSFJORD = "File:Dalsfjorden Rivedal.jpg"

# ------------------------------------------------------------------ places, routes and arrows
INVERNESS = place("Inverness", -4.22, 57.48, "Inverness", "city")
FORT_AUG = place("Fort Augustus", -4.68, 57.145, "Fort Augustus", "site")
EDINBURGH = place("Edinburgh", -3.19, 55.95, "Edinburgh", "capital")
GLASGOW = place("Glasgow", -4.25, 55.86, "Glasgow", "city")
ABERDEEN = place("Aberdeen", -2.10, 57.15, "Aberdeen", "city")
DUNDEE = place("Dundee", -2.97, 56.46, "Dundee", "city")
PERTH = place("Perth", -3.44, 56.40, "Perth", "city")
STIRLING = place("Stirling", -3.94, 56.12, "Stirling", "city")
DUNFERM = place("Dunfermline", -3.46, 56.07, "Dunfermline", "city")
BERGEN = place("Bergen", 5.32, 60.39, "Bergen", "city")
STONEHAVEN = place("Stonehaven", -2.21, 56.96, "Stonehaven", "site")
ARRAN = place("Arran", -5.25, 55.58, "Isle of Arran", "label")
CULLODEN = place("Culloden", -4.07, 57.48, "Culloden Moor, 1746", icon="warning")
STRATHNAVER = place("Strathnaver", -4.22, 58.40, "Strathnaver", "site")
GOLSPIE = place("Golspie", -3.98, 57.97, "Golspie", "site")
SKYE = place("Skye", -6.25, 57.30, "Isle of Skye", "label")
BRAES = place("Braes", -6.12, 57.35, "Braes, 1882", icon="warning")
KILDA = place("St Kilda", -8.57, 57.81, "St Kilda", "site")
EIGG = place("Eigg", -6.16, 56.90, "Isle of Eigg", "site")
ASSYNT = place("Assynt", -5.10, 58.17, "Assynt", "site")
MORAR = place("Morar", -5.82, 56.97, "River Morar, 1948", "site")
PITLOCHRY = place("Pitlochry", -3.73, 56.70, "Pitlochry", "site")
FORSINARD = place("Forsinard", -3.90, 58.36, "Flow Country", "site")
PICTOU = place("Pictou", -62.70, 45.68, "Pictou, Nova Scotia", "port")
SYDNEY = place("Australia", 144.96, -37.81, "Australia", "port")
MORAY = place("Moray Firth", -3.6, 57.75, "Moray Firth", "label")

HBF = {"from": [-5.29, 55.71], "via": [[-4.95, 55.92], [-4.60, 56.07], [-4.25, 56.22], [-3.95, 56.36], [-3.58, 56.56],
       [-3.20, 56.66], [-2.70, 56.82]], "to": [-2.21, 56.96], "mode": "line", "label": "Highland Boundary Fault",
       "color": "red", "seconds": 4.0}
TO_PICTOU = {"from": [-6.2, 57.3], "via": [[-20.0, 57.0], [-40.0, 52.0]], "to": [-62.7, 45.68], "mode": "line",
             "label": "Hector, 1773", "color": "accent", "seconds": 4.0}
TO_AUS = {"from": [-6.2, 57.3], "via": [[-15.0, 30.0], [10.0, -35.0], [80.0, -42.0]], "to": [144.96, -37.81], "mode": "line",
          "label": "To Australia, 1852-57", "color": "accent", "seconds": 4.5}
WINDS = [{"from": [-12.5, 56.2], "to": [-6.3, 56.9], "color": "blue", "label": "Atlantic winds", "bend": 0.1},
         {"from": [-12.0, 58.6], "to": [-6.0, 58.0], "color": "blue", "bend": -0.1}]
NORTH_SEA = [{"from": [-2.0, 58.0], "to": [4.6, 60.3], "color": "alt", "label": "Across the North Sea", "bend": 0.15}]
WESTERLIES_NO = [{"from": [-2.0, 61.5], "to": [4.9, 60.9], "color": "blue", "label": "The same storms", "bend": -0.1}]

H = "Highland@red"
V_RED = "file:vestland.geojson@red"
V_ALT = "file:vestland.geojson@alt"

chapters = []
heads = iter(HEADS)


def chapter(*paras):
    title, mood = next(heads)
    chapters.append({"title": title, "mood": mood, "paragraphs": list(paras)})


PH_GLENCOE3 = "File:Lost Valley Trail, Glencoe, Scotland - 53739047188.jpg"
PH_GLENCOE4 = "File:The Lost Valley, Glencoe, Scotland.jpg"
PH_QUIRAING2 = "File:The Quiraing, Isle of Skye, Scotland - 53718314137.jpg"
PH_QUIRAING3 = "File:The Quiraing, Isle of Skye, Scotland - 53727655796.jpg"
PH_CUILLIN2 = "File:The Cuillin Mountains of Skye (51148080435).jpg"
PH_LOMOND = "File:Loch Lomond (25052553995).jpg"
PH_EILEAN = "File:Eilean Donan castle - 95mm.jpg"
PH_URQUHART = "File:Urquhart Castle on Loch Ness.jpg"
PH_NESS2 = "File:Loch Ness (42064602492).jpg"
PH_GLENFINNAN = "File:Glenfinnan bay.jpg"
PH_LEWIS_ROAD = "File:Road from Stornoway to Callanish - Isle of Lewis, Scotland, UK - May 24, 1989.jpg"
PH_BERGEN_HARB = "File:Bergen harbour Bruvik.jpg"
PH_BRYGGEN11 = "File:Bryggen-Bergen-April-2011 01.jpg"
PH_NAEROY2 = "File:Nærøyfjord - 49534246726.jpg"
PH_HARDANGER = "File:Hardangerfjorden from krokavatn 2.jpg"
PH_ASSYNT2 = "File:Loch Assynt (187501557).jpeg"
PH_KYLESKU = "File:Kylesku Bridge (14859799060).jpg"
PH_SUTH_ROAD = "File:Drumbeg to Kylesku road, Sutherland, Scotland, 14 April 2011 - Flickr - PhillipC.jpg"
PH_EIGG2 = "File:Isle of Eigg in Scotland from north-east.jpg"
PH_DUN = "File:Dùn St Kilda.jpg"
PH_SHEEP2 = "File:Sheep in the highlands with shepard.jpg"
PH_DEER3 = "File:Cervo rosso - Red Deer.jpg"
PH_GLENCOE5 = "File:Lost Valley Trail, Glencoe, Scotland - 53744443330.jpg"
PH_GLENCOE6 = "File:Lost Valley Trail, Glencoe, Scotland - 53739259125.jpg"
PH_QUIRAING4 = "File:The Quiraing, Isle of Skye, Scotland - 53719571489.jpg"
PH_QUIRAING5 = "File:The Quiraing, Isle of Skye, Scotland - 53722135434.jpg"
PH_QUIRAING6 = "File:The Quiraing, Isle of Skye, Scotland - 53727735228.jpg"
PH_ASSYNT3 = "File:Loch Assynt 3.JPG"
PH_MACAULAY = "File:Macaulay Map of St Kilda, Published 1764.jpg"

S = SPRING25
chapter(
    P("P0",
      m(0, v(SCOT, highlight=[H])),
      m("The Highland council area", v({"lon": -4.9, "lat": 57.6, "span": 4.4}, highlight=[H], places=[INVERNESS])),
      photo("twenty-five and a half", PH_TORRIDON, "Torridon, Wester Ross"),
      stat("About two hundred and", "~235,000", "People in the Highland council area", NRS, note="On about 25,650 square kilometres"),
      photo("That is roughly nine", PH_SUILVEN, "Suilven, Assynt"),
      stat("Among Scotland's council areas,", "9 / KM²", "People per square kilometre, Highland, 2022", NRS)),
    P("P1",
      m(0, v(NSEA, highlight=[H, V_RED], arrows=NORTH_SEA)),
      photo("The county of Vestland", PH_NAEROY, "Nærøyfjord, Vestland"),
      m("It faces the same", v(VEST, highlight=[V_ALT], arrows=WESTERLIES_NO, places=[BERGEN])),
      photo("In fact, Bergen, its", PH_BERGEN, "Bergen"),
      stat("Yet Vestland has more", "~650,000", "People in Vestland, Norway", SSB, note="On about 33,900 square kilometres"),
      photo("and Bergen alone is", PH_BRYGGEN, "Bryggen, Bergen")),
    P("P1b",
      photo(0, PH_HARDANGER, "Hardangerfjord, Vestland"),
      chart("Vestland has about nineteen", "People per km²", "", [["Vestland", 19], ["Highland", 9]], "SSB; NRS (own division)"),
      photo("Both coasts are wet,", PH_SOGNE, "Sognefjord, Vestland"),
      photo("cut by long arms", PH_ARDVRECK, "Loch Assynt, Sutherland"),
      photo("The other emptied.", PH_SHIELINGS, "Ruined shielings, Sutherland")),
    P("P2",
      photo(0, PH_FOINAVEN, "Foinaven, Sutherland"),
      stat("In eighteen sixty-one, the", "253,534", "People in the Highland area, 1861", VOB, note="Today: about 235,000"),
      stat("About a century later,", "161,631", "People in the same area, 1971", VOB, note="More than a third fewer than in 1861")),
    P("P3",
      photo(0, PH_QUIRAING2, "The Quiraing, Skye"),
      photo("The answer runs through", PH_GLENCOE, "Glencoe"),
      photo("through a battle on", PH_LEANACH, "Leanach Cottage, Culloden Moor"),
      photo("through sheep and potatoes", PH_SHEEP2, "Sheep in the Highlands"),
      photo("through hunting estates the", PH_DEER1, "Red deer"),
      photo("and through a question", PH_EIGG, "Isle of Eigg"),
      photo("And it ends with", PH_QUIRAING, "The Quiraing, Skye")),
)

chapter(
    P("P4",
      m(0, v({"lon": -4.0, "lat": 56.9, "span": 6.5}, highlight=[H])),
      m("from the Isle of", v(CENTRAL, routes=[HBF], places=[ARRAN, STONEHAVEN])),
      photo("Geologists call it the", PH_CONIC, "Conic Hill, on the Highland Boundary Fault"),
      stat("It runs for more", "240+ KM", "Length of the Highland Boundary Fault", "British Geological Survey (via Wikipedia)"),
      m("South of it lies", v({"lon": -3.9, "lat": 56.0, "span": 2.8}, places=[GLASGOW, EDINBURGH])),
      photo("North of it, the", PH_LOMOND, "Loch Lomond, where the Highlands begin")),
    P("P4b",
      m(0, v({"lon": -3.6, "lat": 56.6, "span": 4.8}, places=[GLASGOW, EDINBURGH, DUNDEE, PERTH, STIRLING, DUNFERM]),
        step("Only two, Aberdeen and", places=[ABERDEEN, INVERNESS])),
      photo("and both sit on", PH_INVERNESS, "Inverness, looking to the Moray Firth")),
    P("P5",
      photo(0, PH_QUINAG, "Quinag, Sutherland"),
      photo("mountain chain that once", PH_CULMOR, "Cul Mor, Sutherland"),
      sat("Then, during the ice", -5.10, 58.17, 0.4, "Assynt: rock scraped by ice", date=S),
      photo("They carved the deep", PH_NESS_AIR, "Loch Ness from the air"),
      photo("What the ice left", PH_CULMOR_PATH, "Bare rock and thin ground, Sutherland")),
    P("P6",
      photo(0, PH_PEAT, "A stack of cut peat, Lewis"),
      photo("They piled up as", PH_LOCHANS, "Lochans and bog, Sutherland"),
      m("In the far north,", v(SUTH, places=[FORSINARD])),
      sat("It is called the", -3.85, 58.40, 0.6, "The Flow Country", date=S),
      stat("In July twenty twenty-four,", "190,000 HA", "The Flow Country World Heritage Site, 2024", UNESCO),
      sat("the first peatland World", -3.95, 58.45, 0.3, "Blanket bog, the Flow Country", date=S),
      stat("And that is only", "~400,000 HA", "The whole blanket bog", "The Flow Country Partnership")),
    P("P7",
      photo(0, PH_CANISP, "Bog moorland below Canisp"),
      photo("people tried to make", PH_SUTH_ROAD, "Sutherland"),
      sat("Tax breaks for commercial", -3.75, 58.30, 0.25, "Conifer blocks in the Flow Country", date=S),
      stat("The RSPB says nearly", "~20 %", "Of the Flow Country drained and planted", RSPB),
      stat("In March nineteen eighty-eight,", "1988", "Tax relief for commercial forestry ended", "UK budget, March 1988 (Hansard)"),
      sat("and today parts of", -3.88, 58.37, 0.15, "Forsinard: bog being restored", date=S)),
    P("P8",
      photo(0, PH_STOER, "Stoer, Sutherland"),
      photo("Norway's west coast is", PH_DALSFJORD, "Dalsfjorden, Vestland"),
      photo("Something else must be", PH_SUILVEN_CLOUD, "Suilven in cloud")),
)

chapter(
    P("P9",
      m(0, v({"lon": -6.0, "lat": 57.3, "span": 9.0}, arrows=WINDS)),
      photo("When those wet winds", PH_BEN_NEVIS, "Ben Nevis and Fort William"),
      photo("it cools, and it", PH_GLENCOE3, "Glencoe"),
      m("On the Met Office's", v({"lon": -4.0, "lat": 56.6, "span": 3.6}, places=[FORT_AUG, EDINBURGH])),
      photo("in the middle of", PH_NESS2, "Loch Ness, in the Great Glen"),
      stat("gets about one thousand", "1,359 MM", "Rain a year, Fort Augustus", MET),
      stat("Edinburgh, on the dry", "639 MM", "Rain a year, Edinburgh", MET)),
    P("P10",
      photo(0, PH_CUILLIN2, "The Cuillin, Skye"),
      sat("That is why the", -3.30, 57.60, 0.6, "Farmland along the Moray Firth", date=S),
      photo("around the Moray Firth", PH_INVERNESS2, "Inverness")),
    P("P11",
      m(0, v({"lon": 0.0, "lat": 58.5, "span": 15.0}, places=[BERGEN, FORT_AUG, EDINBURGH])),
      sat("Bergen's official average, by", 5.32, 60.39, 0.25, "Bergen and its fjords", date=S),
      chart("is about two thousand", "Rain a year", "mm", [["Bergen", 2495], ["Fort Augustus", 1359], ["Edinburgh", 639]],
            "Bergen kommune; Met Office 1991-2020", reveal=["That is nearly twice", "and four times that"]),
      photo("And Bergen became one", PH_BERGEN1910, "Bergen from Fløyen, about 1910")),
    P("P11b",
      sat(0, 5.32, 60.395, 0.1, "Bergen", date=S),
      photo("merchants of the Hanseatic", PH_BRYGGEN_W, "Bryggen, Bergen"),
      m("and shipped dried cod", v({"lon": 10.0, "lat": 62.5, "span": 20.0}, places=[BERGEN])),
      photo("Bryggen's wooden warehouses still", PH_BRYGGEN11, "Bryggen"),
      stat("and UNESCO listed them", "1979", "Bryggen on the World Heritage List", UNESCO)),
    P("P12",
      photo(0, PH_NAEROY2, "Nærøyfjord, Vestland"),
      photo("So the land made", PH_CUILLIN, "The Cuillin, Skye"),
      m("To understand what did,", v({"lon": -4.15, "lat": 57.6, "span": 2.8}, places=[CULLODEN]))),
)

chapter(
    P("P13",
      photo(0, PH_BLACKHOUSE, "A restored blackhouse village, Lewis"),
      photo("Glens that are silent", PH_GLENCOE4, "Glencoe"),
      photo("small clusters of stone", PH_SHIELINGS, "Ruined shielings, Sutherland"),
      photo("Families belonged to clans,", PH_EILEAN, "Eilean Donan Castle"),
      photo("the number of men", PH_ARDVRECK, "Ardvreck Castle, Loch Assynt")),
    P("P14",
      sat(0, -4.07, 57.48, 0.08, "Culloden Moor", date=S),
      photo("met government troops on", PH_CULLODEN, "The Battle of Culloden (18th-century painting)"),
      stat("By the National Trust", "< 1 HOUR", "The Battle of Culloden, 16 April 1746", "National Trust for Scotland; National Army Museum"),
      photo("between the first shots", PH_LEANACH, "Leanach Cottage, Culloden Moor"),
      stat("It was the last", "1746", "The last pitched battle on British soil", "Wikipedia (Battle of Culloden)")),
    P("P15",
      m(0, v({"lon": -3.9, "lat": 57.65, "span": 3.4}, places=[CULLODEN, INVERNESS])),
      photo("The government banned Highland", PH_GLENCOE2, "Glencoe"),
      photo("and pushed more military", PH_URQUHART, "Urquhart Castle, Loch Ness"),
      photo("But the biggest change", PH_DUNROBIN, "Dunrobin Castle, Sutherland"),
      photo("no longer needed hundreds", PH_GLENFINNAN, "Glenfinnan"),
      photo("What he needed was", PH_KYLESKU, "Kylesku, Sutherland"),
      photo("a glen full of", PH_ASSYNT4, "Loch Assynt")),
    P("P16",
      photo(0, PH_INCHNA, "Inchnadamph, Assynt"),
      photo("And the animal that", PH_SHEEP2, "Sheep in the Highlands")),
)

chapter(
    P("P17",
      photo(0, PH_QUIRAING2, "The Quiraing, Skye"),
      m("Sheep farmers from the", v({"lon": -4.6, "lat": 57.6, "span": 6.0}, places=[INVERNESS, STRATHNAVER])),
      photo("But families were already", PH_BLACKHOUSE, "A blackhouse village, Lewis"),
      photo("Over roughly a century,", PH_FOINAVEN, "Foinaven, Sutherland")),
    P("P18",
      sat(0, -5.24, 58.15, 0.12, "Lochinver: crofts on the coast", date=S),
      photo("so that they would", PH_LOCHINVER, "Lochinver"),
      photo("Others were simply told", PH_OLDSHORE, "Oldshoremore Bay, Sutherland")),
    P("P19",
      m(0, v(SUTH, places=[STRATHNAVER, GOLSPIE])),
      sat("In Strathnaver, the estate's", -4.22, 58.40, 0.3, "Strathnaver", date=S),
      stat("and the first removals", "28 FAMILIES", "The first Strathnaver removals, 1814", "Wikipedia (Patrick Sellar); NLS"),
      photo("Houses were burned so", PH_LOCHANS, "Sutherland"),
      stat("In April eighteen sixteen,", "1816", "Patrick Sellar tried at Inverness and acquitted", "Wikipedia (Patrick Sellar)"),
      sat("He was acquitted.", -4.22, 57.48, 0.2, "Inverness", date=S)),

    P("P19b",
      photo(0, PH_DUNROBIN, "Dunrobin Castle, seat of the Sutherland estates"),
      photo("later the first Duke", PH_ASSYNT2, "Loch Assynt"),
      sat("After his death in", -3.98, 57.98, 0.12, "Ben Bhraggie and Golspie", date=S),
      stat("The statue and its", "~30 M", "The Duke of Sutherland's monument, 1837", "Highland Historic Environment Record"),
      sat("and they still look", -3.99, 57.99, 0.08, "Ben Bhraggie", date=S),
      sat("It is one of", -3.96, 57.96, 0.3, "The Golspie coast", date=S)),
    P("P20",
      sat(0, -4.205, 58.45, 0.12, "Strathnaver: green fields along the river", date=S),
      photo("In glen after glen,", PH_CULMOR_PATH, "Sutherland"),
      photo("green patches of old", PH_STOER, "Stoer, Sutherland"),
      photo("Whole valleys were emptied", PH_ASSYNT, "Loch Assynt"),
      photo("Something else was coming", PH_QUIRAING5, "Skye")),
)

chapter(
    P("P21",
      photo(0, PH_PEAT, "Peat for the fire, Lewis"),
      photo("Then, in eighteen forty-six,", PH_LEWIS_ROAD, "Lewis"),
      stat("the same blight that", "1846", "Potato blight reaches the Highlands", "Wikipedia (Highland Potato Famine)"),
      m("and famine spread along", v(HEB, places=[SKYE]))),
    P("P22",
      photo(0, PH_PORTREE, "Portree, Skye"),
      stat("one charity, the Highland", "4,919", "People sent to Australia, 1852-1857", SP, note="Highland and Island Emigration Society"),
      photo("men, women and children", PH_QUIRAING6, "Skye"),
      m("Skye was the first", v(GLOBE, routes=[TO_AUS], places=[SYDNEY])),
      stat("In eighteen fifty-two alone,", "2,569", "Emigrants in 1852 alone", SP)),
    P("P22b",
      m(0, v(SKYEV, places=[SKYE])),
      photo("By the time the", PH_QUIRAING3, "The Quiraing, Skye"),
      stat("about six in ten", "59 %", "Of the Society's emigrants came from Skye", "Wikipedia (Highland and Island Emigration Society)")),
    P("P23",
      m(0, v(ATL, routes=[TO_PICTOU], places=[PICTOU])),
      photo("The road had been", PH_EILEAN, "Eilean Donan"),
      photo("In seventeen seventy-three, a", PH_HECTOR, "Replica of the Hector, Pictou"),
      m("in a colony with", v({"lon": -63.0, "lat": 45.3, "span": 6.0}, places=[PICTOU]))),
    P("P24",
      photo(0, PH_ACHNAHAIRD, "Achnahaird Bay"),
      chart("Measured on today's council", "Highland population", "", [["1801", 175368], ["1861", 253534], ["1911", 188667], ["1971", 161631], ["2021", 235336]],
            VOB, highlight=3, reveal=["peaked at about two", "By nineteen seventy-one it", "That is more than a"]),
      photo("while Scotland as a", PH_LOMOND, "Loch Lomond"),
      photo("So when the people", PH_TORRIDON, "Torridon")),
)

chapter(
    P("P25",
      photo(0, PH_CUILLIN2, "Skye"),
      photo("many Highland sheep farms", PH_GLENCOE5, "Glencoe"),
      photo("Landowners found a new", PH_STALKER, "A stalker and a red deer stag, Ardnamurchan"),
      photo("Wealthy Victorians would pay", PH_DEER3, "Red deer"),
      photo("and estate after estate", PH_DEER2, "Red deer stags"),
      photo("which, despite the name,", PH_CULMOR, "Open hill, Sutherland")),
    P("P26",
      photo(0, PH_GLENCOE4, "Glencoe"),
      stat("counted about one point", "1.98 M ACRES", "Deer forests, 1883", HANS),
      stat("By eighteen ninety-one, it", "2.57 M ACRES", "Deer forests, 1891", HANS),
      stat("That is nearly a", "+30 %", "Deer forests, 1883 to 1891", "Own: 2.57 / 1.98 = 1.30"),
      photo("A deer forest needs", PH_DEER1, "Red deer"),
      photo("a gamekeeper and a", PH_ASSYNT2, "Loch Assynt")),
    P("P26b",
      m(0, v({"lon": -4.2, "lat": 57.0, "span": 7.0}, highlight=[H])),
      stat("That is roughly an", "~1/8", "Of Scotland's land in deer forests, 1891", "Own: 2.57 M acres = 10,400 km² of 78,800 km²"),
      sat("given over to a", -4.00, 57.90, 0.6, "Open hill, Sutherland", date=S)),
    P("P27",
      m(0, v(SKYEV, places=[BRAES])),
      photo("in what became known", PH_PORTREE, "Portree, Skye"),
      stat("In March eighteen eighty-three,", "1883", "A royal commission under Lord Napier", "High Life Highland archives"),
      photo("which travelled the Highlands", PH_INCHNA, "Crofts at Inchnadamph"),
      stat("And in June eighteen", "1886", "The Crofters Act", "Crofters Holdings (Scotland) Act 1886"),
      stat("fair rents set by", "SECURE", "Tenure, fair rents and the right to inherit", "Crofters Holdings (Scotland) Act 1886"),
      photo("They could no longer", PH_KYLESKU, "Kylesku"),
      photo("But the act did", PH_CUILLIN, "The Cuillin, Skye")),
    P("P28",
      m(0, v(HEB, places=[KILDA])),
      photo("the islanders of St", PH_FULMAR, "Dividing the catch of fulmar, St Kilda, about 1886"),
      photo("After a hard winter,", PH_MACAULAY, "St Kilda, map of 1764"),
      photo("asking the government to", PH_DUN, "Dùn, St Kilda"),
      photo("Many of the young", PH_KILDA10, "Village Bay, St Kilda"),
      sat("On the twenty-ninth of", -8.57, 57.81, 0.08, "Hirta, St Kilda", date="2023-05-01/2023-09-15"),
      stat("the last thirty-six islanders", "36", "Islanders taken off St Kilda, 29 August 1930", "National Trust for Scotland"),
      photo("The island has had", PH_KILDA7, "The empty street, Village Bay, St Kilda"),
      photo("Today it belongs to", PH_KILDA_DUN, "Village Bay, St Kilda")),
)

chapter(
    P("P29",
      m(0, v({"lon": 0.0, "lat": 59.5, "span": 22.0}, highlight=[H, V_RED])),
      photo("Norway had the same", PH_HARDANGER, "Hardangerfjord"),
      photo("Why did its west", PH_SOGNE, "Sognefjord, Vestland")),
    P("P30",
      photo(0, PH_DALSFJORD, "Farms on Dalsfjorden, Vestland"),
      photo("tenant farmers there were", PH_NAEROY2, "Nærøyfjord"),
      stat("and that by about", "~1750", "Freeholders may be most of Norway's farmers", "Historians of Norway (1961 study)"),
      stat("Norway's constitution of eighteen", "1814", "The odal right in Norway's constitution", "Odelsrett (Wikipedia)"),
      photo("A farmer who owns", PH_BRYGGEN11, "Bryggen, Bergen")),
    P("P31",
      photo(0, PH_KILDA_SHEEP, "Village Bay, St Kilda"),
      photo("When the land became", PH_SUTH_ROAD, "Sutherland")),
    P("P32",
      photo(0, PH_PITLOCHRY, "Pitlochry Power Station"),
      stat("In August nineteen forty-three,", "1943", "North of Scotland Hydro-Electric Board", "Hydro-Electric Development (Scotland) Act 1943"),
      photo("Its motto was Gaelic:", PH_CRUACHAN, "Cruachan dam"),
      stat("power from the glens.", "NEART NAN GLEAN", "Power from the glens: the board's motto", "North of Scotland Hydro-Electric Board"),
      m("and electricity reached crofts", v({"lon": -4.6, "lat": 57.1, "span": 3.4}, places=[PITLOCHRY, MORAR])),
      photo("By the nineteen-seventies, the", PH_URQUHART, "Loch Ness"),
      photo("But the hydro schemes", PH_ASSYNT4, "Loch Assynt")),
    P("P32b",
      photo(0, PH_GLENFINNAN, "Glenfinnan"),
      stat("By most accounts, there", "54", "Power stations built by the Hydro Board", "North of Scotland Hydro-Electric Board (Wikipedia)"),
      stat("seventy-eight dams and some", "78", "Dams built by the Hydro Board", "North of Scotland Hydro-Electric Board (Wikipedia)"),
      sat("The first scheme to", -5.82, 56.97, 0.1, "Morar", date=S),
      sat("Many of those dams", -3.75, 56.70, 0.12, "Loch Faskally, Pitlochry", date=S)),
)

chapter(
    P("P33",
      photo(0, PH_GLENCOE3, "Glencoe"),
      stat("about four hundred owners", "~400", "Owners of half Scotland's private rural land", WIGHT),
      photo("Some estates cover tens", PH_DEER2, "Red deer"),
      photo("If you want to", PH_QUINAG, "Quinag, Sutherland"),
      sat("you often need the", -5.00, 57.05, 0.5, "Highland glens", date=S)),
    P("P34",
      m(0, v({"lon": -5.6, "lat": 57.6, "span": 3.2}, places=[ASSYNT, EIGG])),
      photo("In Assynt, in the", PH_SUILVEN, "Suilven, Assynt"),
      stat("about twenty-one thousand acres,", "£300,000", "The Assynt crofters' buyout, 1993", "The Scotsman"),
      photo("Four years later, in", PH_EIGG_SGURR, "The Sgurr of Eigg"),
      sat("the residents of the", -6.13, 56.88, 0.1, "Isle of Eigg", date=S)),
    P("P34b",
      sat(0, -6.16, 56.90, 0.25, "The Isle of Eigg", date=S),
      stat("of its sixty-five residents,", "65", "Residents who bought Eigg, 12 June 1997", "Isle of Eigg Heritage Trust"),
      photo("In two thousand and", PH_EIGG, "Isle of Eigg"),
      stat("switched on its own", "2008", "Eigg switches on its own island grid", "Eigg Electric (isleofeigg.org)"),
      photo("The people who had", PH_EIGG2, "Isle of Eigg")),
    P("P35",
      photo(0, PH_LOCHINVER, "Lochinver"),
      stat("The Land Reform Act", "2003", "Land Reform (Scotland) Act: a community right to buy", "Land Reform (Scotland) Act 2003"),
      photo("A community can register", PH_ACHNAHAIRD, "Achnahaird Bay"),
      photo("and when the owner", PH_OLDSHORE, "Oldshoremore"),
      sat("Since then, many more", -5.20, 58.20, 0.3, "North Assynt, community-owned since 1993", date=S),
      stat("And the Highland population", "~235,000", "Highland, Census 2022", NRS, note="1861: 253,534"),
      photo("in the last census.", PH_INVERNESS, "Inverness")),
    P("P36",
      photo(0, PH_NESS2, "Loch Ness"),
      sat("In the prettiest villages,", -6.19, 57.41, 0.08, "Portree", date=S),
      photo("and prices climb beyond", PH_INVERNESS2, "Inverness"),
      sat("The deer forests are", -5.30, 57.65, 0.4, "Highland hill ground", date=S)),
)

chapter(
    P("P37",
      photo(0, PH_BRYGGEN, "Bryggen, Bergen"),
      photo("old rock scraped bare", PH_CANISP, "Sutherland"),
      photo("But Norway shows that", PH_BERGEN, "Bergen"),
      photo("In the Highlands, the", PH_ASSYNT3, "Loch Assynt"),
      photo("After Culloden, they became", PH_QUIRAING3, "Skye"),
      photo("and deer forests kept", PH_STALKER, "Stalking on a Highland estate")),
    P("P38",
      photo(0, PH_GLENCOE, "Glencoe"),
      photo("In recent years, its", PH_GLENCOE5, "Glencoe"),
      photo("including splitting them into", PH_GLENCOE6, "Glencoe"),
      photo("Supporters say breaking them", PH_QUIRAING4, "Skye"),
      photo("Opponents say the land", PH_QUIRAING, "The Quiraing, Skye"),
      sat("and that the estates", -4.95, 57.27, 0.3, "Glen Affric", date=S)),
    P("P39",
      m(0, v({"lon": -5.0, "lat": 57.7, "span": 4.6}, highlight=[H])),
      photo("Should Scotland break up", PH_SUILVEN_CLOUD, "Suilven"),
      photo("or keep the hills", PH_ASSYNT, "Loch Assynt"),
      ask=("So here is the", "Break up the big estates, or keep the hills as they are?")),
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
    """Write the camera the pipeline would choose into the script. When places, arrows, routes or painted areas fall
    outside a hand-picked view, maps.py zooms out around them; render 1 then showed the edge of the imagery fetched
    for the hand-picked view (black vertical strips, 10 shots). With the fitted view written here, view and imagery
    agree. Views past 180 degrees get a second world image east of it (pipeline/maps.py)."""
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


TITLE = "Why Almost Nobody Lives in the Scottish Highlands"
script = {
    "title": TITLE,
    "voice": "am_michael",
    "voice_speed": 1.15,
    "music": "procedural",
    "map_style": "satellite",
    "look": "none",
    "photo_upscale": True,
    "sources": ["episodes/scottish-highlands/research.md and factcheck.md", "Contains modified Copernicus Sentinel data 2026",
                "Highland Boundary Fault and emigration routes drawn through main points (approximate)",
                "Vestland outline: Natural Earth (Hordaland + Sogn og Fjordane)"],
    "thumbnail": {"text": "EMPTIER THAN NORWAY"},
    "chapters": chapters,
    "youtube": {
        "title": TITLE,
        "description": "The Highland council area is bigger than Wales, yet only about 235,000 people live there, nine to a square kilometre. Across the North Sea, Norway's Vestland has the same ancient rock, the same Atlantic storms and even more rain, and twice the people. We follow the answer from orbit: the Highland Boundary Fault, ice, peat and the Flow Country, the rain, Culloden, the Highland Clearances and Strathnaver, the potato famine and the emigrant ships, the deer forests, St Kilda, Norway's freehold farmers, the Hydro Board, and who owns the glens today.",
        "tags": ["Scottish Highlands", "Highlands", "Scotland", "Highland Clearances", "Strathnaver", "Culloden", "St Kilda", "Flow Country",
                 "deer forests", "land reform", "Isle of Eigg", "Norway", "Bergen", "geography", "satellite images"],
        "pinned_comment": "Should Scotland break up the big Highland estates to bring people back to the glens?",
    },
}
out = HERE / "script.json"
out.write_text(json.dumps(script, ensure_ascii=False, indent=1) + chr(10), encoding="utf-8")
words = sum(len(p["text"].split()) for c in chapters for p in c["paragraphs"])
shots = [s for c in chapters for p in c["paragraphs"] for s in p["shots"]]
kinds = {k: sum(1 for s in shots if s["type"] == k) for k in ("map", "photo", "stat", "document", "chart")}
print(f"{words} words, {len(chapters)} chapters, {len(shots)} shots {kinds}")
