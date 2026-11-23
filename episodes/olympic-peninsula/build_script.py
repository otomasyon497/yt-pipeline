"""Builds script.json for olympic-peninsula.  python build_script.py

Same production logic as episodes/russia-far-east (hand-placed shots, a photo or map frame at most twice,
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
PEN = {"lon": -123.75, "lat": 47.75, "span": 3.4}       # the whole peninsula
PNW = {"lon": -122.8, "lat": 47.4, "span": 7.5}         # peninsula and Puget Sound
WA = {"lon": -120.6, "lat": 47.3, "span": 9.5}          # Washington state
WEST = {"lon": -122.0, "lat": 44.0, "span": 22.0}       # West Coast, Cascadia
JAPAN = {"lon": 141.6, "lat": 39.5, "span": 7.0}        # Sanriku coast
PACIFIC_W = {"lon": 160.0, "lat": 38.0, "span": 60.0}   # Japan side of the Pacific
SOUTH = {"lon": -123.9, "lat": 46.95, "span": 2.8}      # Grays Harbor and Willapa Bay
ELWHA = {"lon": -123.58, "lat": 48.03, "span": 0.5}
SUMMER25 = "2025-07-01/2025-09-15"

# ------------------------------------------------------------------ sources (research.md)
NPS = "National Park Service"
NOAA = "NOAA 1991-2020 climate normals"
PNSN = "Pacific Northwest Seismic Network"
USGS_P = "USGS, as cited by PNSN"
DNR = "Washington Dept. of Natural Resources"
WDFW = "Washington Dept. of Fish and Wildlife (via Restoration of the Elwha River)"
ATW = "Atwater et al. 2005; Satake et al. 1996"
CENSUS = "U.S. Census 2020"

# ------------------------------------------------------------------ photos (Commons, licence checked: visuals.md)
PH_HOH_MOSS = "File:Hall of Mosses, Hoh Rainforest, Olympic National Park, Washington (2015).jpg"
PH_HOH_LOG = "File:Hoh Rainforest, mossy log tree NPS Photo (16680304244).jpg"
PH_HOH_COL = "File:Hoh rainforest colanade 0090 (22453931843).jpg"
PH_HOH_HALL = "File:Hoh rainforest hall of mosses 0096 (22656775187).jpg"
PH_HOH_STUMP = "File:Stair step moss stump hoh rainforest c bubar july 2014 (17302171651).jpg"
PH_HOH_SPRUCE = "File:Visitor big spruce tree fallen hoh rainforest c bubar march 05 2015 (22972414455).jpg"
PH_HOH_STREAM = "File:Fallen mossy logs stream hoh rainforest d archuleta march 05 2015 (23086722282).jpg"
PH_HOH_BRANCH = "File:Hanging mossy branch hoh rainforest c bubar march 05-2015 (22656700368).jpg"
PH_HOH_F1 = "File:Hoh Rain Forest - 54018538707.jpg"
PH_HOH_F2 = "File:Hoh Rain Forest - 54019461571.jpg"
PH_DUNG = "File:Dungeness Spit NWR.jpg"
PH_DUNG_HEAD = "File:Dungeness Spit Headland.jpg"
PH_DUNG_TRAIL = "File:Dungeness Spit Trail (7638331612).jpg"
PH_OLYMPUS = "File:2016. Mt. Olympus. Olympic National Park, Washington. (38897209971).jpg"
PH_RIALTO1 = "File:Rialto Beach - 54018507487.jpg"
PH_RIALTO2 = "File:Rialto Beach - 54019636128.jpg"
PH_RIALTO_PANO = "File:Rialto Beach - 54019732359.jpg"
PH_RUBY_DOOR = "File:Doorway to Ruby Beach in Washington.jpg"
PH_RUBY_ROCKS = "File:Ruby Beach rocks and waves.jpg"
PH_RUBY_SUN = "File:Sunset at Ruby Beach (Olympic Peninsula, Washinton, USA).jpg"
PH_ELK = "File:Bull Roosevelt elk (36904820472).jpg"
PH_ELK_CALF = "File:Roosevelt elk cow & calf (36904812482).jpg"
PH_LOGRAFTS = "File:EDIZ HOOK AND LOG RAFTS - NARA - 552170.jpg"
PH_FORKS_MUSEUM = "File:Forks timber museum.JPG"
PH_FORKS_DOWN = "File:Forks WA Downtown.JPG"
PH_TWILIGHT = 'File:"Welcome Twilight fans" in Forks, Washington.jpg'
PH_FORKS_1981 = "File:Forks Washington 1981.jpg"
PH_ISS_OZETTE = "File:View from ISS Expedition 71, Ozette Lake, Forks, Washington, June 7, 2024 (ISS071-E-176451).jpg"
PH_ELWHA_1913 = "File:Historic Elwha Dam Power House, circa 1913.jpg"
PH_ELWHA_2011 = "File:2011-06-01, Elwha River Dam.jpg"
PH_ELWHA_BITE = "File:Elwha Dam Removal - first bite of removal process.jpg"
PH_GLINES_NOTCH = "File:Glines canyon dam removal notching NPS Photo 11-30-11 from spillway (16703097944).jpg"
PH_GLINES_CRANE = "File:Glines canyon dam removal crane NPS Photo 3-1-12 NPS photo J Burger (2) (17139325269).jpg"
PH_ELWHA_SILT = "File:Elwha river nearshore silt drift NPS Photo 2012 (17137801028).jpg"
PH_ALDWELL = "File:Aldwell Delta tree stump elwha river silt deposit NPS Photo 3-6-12 (21) (17137799068).jpg"
PH_PA_1973 = "File:PORT ANGELES HARBOR ON THE OLYMPIC PENINSULA - NARA - 552155.jpg"
PH_PA_1910 = "File:Water-Front and Harbor, Port Angeles, Wash.jpg"
PH_MAKAH = "File:Makah Tribal Cemetery in Neah Bay, Washington.jpg"
PH_FLATTERY = "File:Cape Flattery (4301328607).jpg"
PH_FLATTERY_N = "File:Cape Flattery looking north.JPG"
PH_QUINAULT = "File:Dense forest canopy quinault rainforest c bubar march 05 2015 (22655664738).jpg"
PH_QUINAULT2 = "File:Quinault Rainforest.jpg"
PH_ONP2023 = "File:Olympic National Park, 2023 - 002.jpg"
PH_WESTPORT_NARA = "File:WASHINGTON-WESTPORT - NARA - 545162.jpg"
PH_LAKECRES = "File:Lake Crescent Recreation.JPG"

# ------------------------------------------------------------------ places
HOH = place("Hoh", -123.93, 47.86, "Hoh rainforest", icon="water")
SEQUIM = place("Sequim", -123.10, 48.08, "Sequim", "city")
FORKS = place("Forks", -124.39, 47.95, "Forks", "city")
PA = place("Port Angeles", -123.43, 48.12, "Port Angeles", "port")
SEATTLE = place("Seattle", -122.33, 47.61, "Seattle", "city")
TACOMA = place("Tacoma", -122.44, 47.25, "Tacoma", "city")
OLYMPIA = place("Olympia", -122.90, 47.04, "Olympia", "capital")
OLYMPUS = place("Mount Olympus", -123.71, 47.80, "Mount Olympus", icon="mountain")
ELWHA_DAM = place("Elwha Dam", -123.553, 48.093, "Elwha Dam (1913)", icon="warning")
GLINES = place("Glines Canyon Dam", -123.600, 48.000, "Glines Canyon Dam (1927)", icon="warning")
COPALIS = place("Copalis", -124.17, 47.12, "Copalis River ghost forest", icon="warning")
NCOVE = place("North Cove", -124.07, 46.73, "North Cove (Washaway Beach)", icon="warning")
WESTPORT = place("Westport", -124.10, 46.88, "Westport", "city")
LAPUSH = place("La Push", -124.64, 47.91, "La Push", "site")
NEAH = place("Neah Bay", -124.62, 48.37, "Neah Bay", "site")
ABERDEEN = place("Aberdeen", -123.81, 46.98, "Aberdeen", "port")
OTSUCHI = place("Otsuchi", 141.88, 39.36, "Otsuchi", "site")
KUWA = place("Kuwagasaki", 141.96, 39.64, "Kuwagasaki (Miyako)", "site")
VANC_I = place("Vancouver Island", -125.5, 49.5, "Vancouver Island", "label")
NCAL = place("N. California", -123.8, 40.5, "Northern California", "label")

US101 = {"from": [-122.90, 47.04], "via": [[-123.10, 47.40], [-122.90, 47.70], [-122.95, 48.00], [-123.10, 48.08],
         [-123.43, 48.12], [-123.85, 48.06], [-124.39, 47.95], [-124.20, 47.55], [-124.10, 47.30], [-123.81, 46.98]],
         "to": [-123.10, 47.05], "mode": "line", "label": "Highway 101", "color": "accent", "seconds": 5.0}
CSZ = {"from": [-127.0, 50.0], "via": [[-126.0, 48.5], [-125.3, 47.0], [-125.0, 45.0], [-124.9, 43.0]], "to": [-124.6, 40.4],
       "mode": "line", "label": "Cascadia subduction zone", "color": "red", "seconds": 4.0}
STORMS = [{"from": [-126.2, 47.3], "to": [-124.3, 47.8], "color": "blue", "label": "Pacific storms", "bend": 0.1},
          {"from": [-126.0, 48.4], "to": [-124.4, 48.1], "color": "blue", "bend": -0.1}]
DRY_AIR = [{"from": [-123.6, 47.85], "to": [-123.1, 48.05], "color": "alt", "label": "Dry air sinking", "bend": 0.15}]

chapters = []
heads = iter(HEADS)


def chapter(*paras):
    title, mood = next(heads)
    chapters.append({"title": title, "mood": mood, "paragraphs": list(paras)})


chapter(
    P("P0",
      photo(0, PH_HOH_HALL, "Hoh rainforest, Olympic National Park"),
      photo("moss hangs from the", PH_HOH_BRANCH, "Moss on bigleaf maple, Hoh rainforest (NPS)"),
      stat("The National Park Service", "140-167 IN", "Rain a year in Olympic's rainforest valleys", NPS, note="12 to 14 feet of water"),
      photo("a hundred and sixty-seven", PH_HOH_MOSS, "Hall of Mosses, Hoh rainforest"),
      sat("That is twelve to", -123.93, 47.86, 0.3, "The Hoh valley from orbit", date=SUMMER25)),
    P("P1",
      m(0, v(PEN, places=[HOH]), step("to the small town", places=[SEQUIM])),
      sat("Here, the official average", -123.10, 48.08, 0.3, "Sequim from orbit", date=SUMMER25),
      stat("about seventeen inches a", "~17 IN", "Rain a year in Sequim, 1991-2020", NOAA, note="About as dry as Los Angeles"),
      photo("Irrigation canals first brought", PH_DUNG_TRAIL, "The dry side: Dungeness, near Sequim"),
      sat("and the town still", -123.12, 48.07, 0.12, "Sequim's farm fields", date=SUMMER25),
      m("And the two places", v(PEN, places=[HOH, SEQUIM]), text="About 40 miles apart")),
    P("P2",
      m(0, v(PEN, places=[OLYMPUS, HOH, SEQUIM])),
      m("Washington is home to", v(WA, places=[SEATTLE, TACOMA, OLYMPIA])),
      photo("Yet the state's ocean", PH_RIALTO_PANO, "Rialto Beach, Olympic coast"),
      photo("There are no beach", PH_RUBY_ROCKS, "Ruby Beach"),
      stat("and seventy-three miles of", "73 MILES", "Of wilderness coast in Olympic National Park", NPS)),
    P("P3",
      photo(0, PH_RUBY_SUN, "Ruby Beach at sunset"),
      photo("The answer runs through", PH_FORKS_1981, "Forks, 1981"),
      photo("through two dams on", PH_ELWHA_2011, "The Elwha Dam, 2011"),
      sat("and back to one", -124.17, 47.12, 0.15, "The Copalis River, Washington coast", date=SUMMER25),
      m("a night that was", v(JAPAN, places=[OTSUCHI, KUWA])),
      photo("And it ends with", PH_RIALTO1, "Rialto Beach")),
)

chapter(
    P("P4",
      m(0, v(WEST, places=[SEATTLE])),
      m("To the west is", v(PNW, places=[SEATTLE, TACOMA, OLYMPIA, PA])),
      sat("To the east is", -122.40, 47.55, 0.4, "Seattle and Puget Sound", date=SUMMER25)),
    P("P5",
      m(0, v(PEN, places=[OLYMPUS])),
      sat("They rise from near", -123.71, 47.80, 0.3, "Mount Olympus and its glaciers", date=SUMMER25),
      photo("and they sit right", PH_OLYMPUS, "Mount Olympus, 2016"),
      m("the storms that roll", v(PEN, arrows=STORMS))),
    P("P6",
      photo(0, PH_QUINAULT, "Rainforest canopy, Quinault valley (NPS)"),
      m("As it rises, it", v(PEN, arrows=STORMS, places=[HOH])),
      photo("So the clouds drop", PH_QUINAULT2, "Quinault rainforest"),
      sat("The Olympic Mountains carry", -123.68, 47.78, 0.15, "Glaciers on Mount Olympus", date=SUMMER25)),
    P("P6b",
      photo(0, PH_ONP2023, "Olympic National Park, 2023"),
      sat("and studies cited on", -123.72, 47.82, 0.6, "The Olympic high country", date=SUMMER25),
      photo("When they go, the", PH_LAKECRES, "Lake Crescent")),
    P("P7",
      m(0, v(PEN, arrows=DRY_AIR, places=[SEQUIM])),
      sat("comes down the other", -123.30, 48.00, 0.4, "The dry northeast foothills", date=SUMMER25),
      photo("As it sinks, it", PH_DUNG_HEAD, "Dungeness, in the rain shadow"),
      m("The land behind the", v({"lon": -123.25, "lat": 48.0, "span": 3.0}, places=[SEQUIM])),
      sat("That is where Sequim", -123.13, 48.16, 0.2, "Dungeness Spit, north of Sequim", date=SUMMER25)),
    P("P8",
      m(0, v(PEN, places=[HOH, SEQUIM])),
      chart("On the wet side,", "Rain a year", "inches",
            [["Hoh rainforest", 140], ["Forks", 120], ["Seattle", 39], ["Sequim", 17]], "NPS; NOAA 1991-2020 normals",
            reveal=["On the dry side,", "and a town that", "And notice where the"]),
      m("Highway 101, the only", v(PEN, routes=[US101])),
      m("It can't. It loops", v(PNW, routes=[US101], places=[PA, FORKS, ABERDEEN])),
      m("Everything on the outer", v(PEN, routes=[US101], places=[FORKS]))),
)

chapter(
    P("P9",
      photo(0, PH_HOH_COL, "Hoh rainforest (NPS)"),
      sat("the Queets and the", -124.10, 47.55, 0.3, "The Queets valley", date=SUMMER25),
      photo("The park service describes", PH_HOH_SPRUCE, "A fallen Sitka spruce, Hoh rainforest (NPS)"),
      photo("that are hundreds of", PH_HOH_F1, "Hoh rainforest"),
      photo("It rarely freezes here,", PH_HOH_STREAM, "Hoh rainforest stream (NPS)")),
    P("P10",
      sat(0, -124.39, 47.95, 0.2, "Forks", date=SUMMER25),
      stat("records about a hundred", "~120 IN", "Rain a year in Forks, 1991-2020", NOAA, note="Seattle: about 39"),
      sat("That is roughly three", -122.30, 47.45, 0.3, "Seattle", date=SUMMER25),
      photo("Rivers here rise fast.", PH_HOH_F1, "Hoh rainforest"),
      photo("Everything that people build", PH_FORKS_DOWN, "Forks, 2007")),
    P("P10b",
      photo(0, PH_HOH_STUMP, "A nurse stump, Hoh rainforest (NPS)"),
      photo("and young trees sprout", PH_HOH_LOG, "Nurse log, Hoh rainforest (NPS)"),
      photo("Roosevelt elk graze the", PH_ELK, "Roosevelt elk, Olympic Peninsula"),
      photo("It looks untouched because,", PH_HOH_F2, "Hoh rainforest")),
    P("P11",
      photo(0, PH_RIALTO2, "Rialto Beach"),
      photo("battered by some of", PH_RUBY_DOOR, "Ruby Beach"),
      m("Further south, the land", v(SOUTH, places=[NCOVE, WESTPORT, ABERDEEN])),
      sat("At North Cove on", -124.07, 46.73, 0.15, "North Cove, August 1994", date="1994-08-23"),
      sat("and called it the", -124.06, 46.735, 0.16, "North Cove, July 2025", date=SUMMER25)),
    P("P12",
      stat(0, "2,000+ ACRES", "Lost to the sea at North Cove by 2016, by one local count", "WA Coastal Hazards Resilience Network (via Wikipedia)"),
      sat("sixty homes and more", -124.075, 46.725, 0.1, "North Cove", date=SUMMER25),
      sat("People call it Washaway", -124.08, 46.74, 0.3, "Washaway Beach, Willapa Bay", date=SUMMER25)),
    P("P13",
      m(0, v(PEN, places=[OLYMPUS])),
      photo("and a coast that", PH_FLATTERY, "Cape Flattery"),
      sat("But nature is only", -124.72, 48.38, 0.15, "Cape Flattery", date=SUMMER25),
      photo("The other half is", PH_FLATTERY_N, "Cape Flattery, looking north")),
)

chapter(
    P("P14",
      stat(0, "1909", "Mount Olympus National Monument, by Theodore Roosevelt", NPS),
      photo("To this day, one", PH_ELK_CALF, "Roosevelt elk, cow and calf"),
      photo("permanent protection for its", PH_ELK, "Roosevelt elk, Olympic Peninsula")),
    P("P15",
      stat(0, "1938", "Olympic National Park", NPS),
      m("Over the years, a", v(PEN, places=[LAPUSH, OLYMPUS])),
      stat("the park covers about", "922,651 ACRES", "Olympic National Park; 95 % designated wilderness", NPS),
      sat("and ninety-five percent of", -123.75, 47.70, 1.2, "Olympic wilderness", date=SUMMER25)),
    P("P16",
      photo(0, PH_RIALTO1, "Rialto Beach"),
      sat("You walk. Hikers carry", -124.64, 47.92, 0.15, "La Push and Rialto Beach", date=SUMMER25),
      photo("Sea stacks stand offshore,", PH_RUBY_SUN, "Sea stacks, Ruby Beach")),
    P("P17",
      m(0, v(PEN, places=[NEAH, LAPUSH, FORKS])),
      photo("In nineteen eighty-one, the", PH_QUINAULT2, "Quinault rainforest"),
      sat("The emptiness of this", -124.40, 47.60, 0.6, "The Kalaloch coast", date=SUMMER25),
      photo("And it was chosen", PH_MAKAH, "Neah Bay, Makah Reservation"),
      sat("over the one thing", -124.20, 47.80, 0.4, "Logged land outside the park", date=SUMMER25)),
)

chapter(
    P("P18",
      photo(0, PH_LOGRAFTS, "Log rafts at Port Angeles, 1973 (NARA)"),
      m("Mills, logging camps and", v({"lon": -123.8, "lat": 47.6, "span": 3.8}, places=[PA, FORKS, ABERDEEN])),
      photo("Ports like Port Angeles", PH_PA_1910, "Port Angeles waterfront, about 1910")),
    P("P19",
      photo(0, PH_FORKS_MUSEUM, "Forks Timber Museum"),
      photo("The boom ran from", PH_FORKS_1981, "Forks, 1981"),
      sat("On satellite images today,", -124.30, 47.95, 0.5, "Clear-cuts meet the park forest near Forks", date=SUMMER25),
      photo("ending sharply at the", PH_ISS_OZETTE, "Ozette Lake and Forks from the ISS, 2024 (NASA)")),
    P("P20",
      photo(0, PH_PA_1973, "Port Angeles harbor, 1973 (NARA)"),
      sat("Much of the old", -124.25, 47.70, 0.4, "Second-growth forest", date=SUMMER25),
      stat("Forks, a town of", "3,335", "People in Forks, 2020 census", CENSUS)),
    P("P21",
      photo(0, PH_TWILIGHT, "Forks welcomes Twilight fans, 2010"),
      photo("set her Twilight novels", PH_FORKS_DOWN, "Forks"),
      sat("And suddenly, the wettest", -124.385, 47.948, 0.08, "Forks", date=SUMMER25),
      sat("But the timber years", -123.62, 47.98, 0.6, "The Elwha valley", date=SUMMER25)),
)

chapter(
    P("P22",
      m(0, v(PEN, places=[PA, ELWHA_DAM])),
      stat("Washington's fish and wildlife", "~392,000", "Fish a year returning up the Elwha before the dams (estimate)", WDFW),
      sat("once came back up", -123.55, 48.10, 0.15, "The lower Elwha", date=SUMMER25)),
    P("P23",
      photo(0, PH_ELWHA_1913, "Elwha Dam powerhouse, about 1913"),
      m("to make electricity for", v({"lon": -123.5, "lat": 48.05, "span": 2.6}, places=[PA, ELWHA_DAM])),
      m("The Glines Canyon Dam,", v(ELWHA, places=[ELWHA_DAM, GLINES])),
      photo("The fish that had", PH_ELWHA_2011, "The Elwha Dam, 2011"),
      sat("for thousands of years", -123.60, 47.96, 0.3, "The upper Elwha valley", date=SUMMER25)),
    P("P23b",
      photo(0, PH_GLINES_NOTCH, "Glines Canyon Dam during removal, 2011 (NPS)"),
      stat("By most published figures,", "210 FT", "Glines Canyon Dam (Elwha Dam: about 108 ft)", "Restoration of the Elwha River (Wikipedia)"),
      photo("For almost a century,", PH_ALDWELL, "Old stumps in Lake Aldwell's silt, 2012 (NPS)"),
      photo("and the beaches at", PH_PA_1973, "The strait at Port Angeles, 1973 (NARA)")),
    P("P24",
      stat(0, "<3,000", "Fish returning by the late 20th century", WDFW),
      sat("The Lower Elwha Klallam", -123.56, 48.13, 0.2, "The Elwha River reaches the strait", date=SUMMER25),
      stat("In nineteen ninety-two, Congress", "1992", "Elwha River Ecosystem and Fisheries Restoration Act", "Restoration of the Elwha River (Wikipedia)"),
      sat("which allowed the government", -123.555, 48.095, 0.1, "The Elwha Dam site", date=SUMMER25)),
    P("P25",
      photo(0, PH_ELWHA_BITE, "First bite of the Elwha Dam removal, 2011"),
      stat("what the park service", "2011-2014", "The largest dam removal in U.S. history", NPS),
      sat("Within six months, the", -123.552, 48.092, 0.08, "Where the Elwha Dam stood", date=SUMMER25),
      photo("The Glines Canyon Dam", PH_GLINES_CRANE, "Glines Canyon Dam removal, 2012 (NPS)"),
      sat("Behind them, a century", -123.60, 47.99, 0.15, "Old Lake Mills: the river runs through it again", date=SUMMER25),
      sat("and on satellite images", -123.56, 48.14, 0.12, "Elwha mouth, July 2010", date="2010-07-25")),
    P("P26",
      sat(0, -123.548, 48.142, 0.13, "Elwha mouth, July 2025", date=SUMMER25),
      photo("The park says eleven", PH_ELWHA_SILT, "Sediment drifting off the Elwha mouth, 2012 (NPS)"),
      stat("A study published in", "2024 STUDY", "Fish numbers rose once the way upstream was open", "Pess et al. 2024, Frontiers in Ecology and Evolution"),
      photo("It is one of", PH_ONP2023, "Olympic National Park")),
)

chapter(
    P("P27",
      sat(0, -124.18, 47.14, 0.12, "The Copalis River marshes", date=SUMMER25),
      m("For a long time,", v(SOUTH, places=[COPALIS]))),
    P("P28",
      m(0, v(WEST, places=[VANC_I, NCAL])),
      stat("The ground had dropped", "1-2 METERS", "Sudden drop of the coast, killing the ghost forests", PNSN),
      m("Something enormous had happened", v(WEST, routes=[CSZ]))),
    P("P29",
      m(0, v(PACIFIC_W, places=[OTSUCHI])),
      m("Old records from villages", v(JAPAN, places=[OTSUCHI, KUWA])),
      m("Because nothing had shaken", v({"lon": 141.9, "lat": 39.5, "span": 3.0}, places=[OTSUCHI, KUWA]))),
    P("P29b",
      stat(0, "27-28 JAN 1700", "Genroku 12, 12th month, 8th-9th days: the tsunami in Japan", ATW),
      m("and they give the", v({"lon": 141.95, "lat": 39.5, "span": 2.6}, places=[OTSUCHI, KUWA])),
      stat("The waves were probably", "2-5 M", "Estimated tsunami height in Japan", ATW)),
    P("P30",
      stat(0, "~9 HOURS", "For the tsunami to cross the Pacific", PNSN),
      m("scientists worked backwards.", v(WEST, places=[COPALIS, NCOVE])),
      stat("The parent earthquake must", "26 JAN 1700", "About 9 pm, Cascadia", PNSN),
      photo("on the twenty-sixth of", PH_FLATTERY, "The outer coast at night's edge: Cape Flattery"),
      sat("Tree rings agreed: the", -124.16, 47.10, 0.1, "Copalis ghost forest site", date=SUMMER25),
      stat("The magnitude was probably", "M 8.7-9.2", "The 1700 Cascadia earthquake", PNSN)),
    P("P30b",
      m(0, v(WEST, routes=[CSZ])),
      stat("Scientists estimate that the", "~1,000 KM", "Of fault that broke, ~20 m average slip", ATW),
      m("from Vancouver Island to", v(WEST, places=[VANC_I, NCAL]))),
    P("P31",
      photo(0, PH_MAKAH, "Neah Bay"),
      m("Makah stories describe a", v(PEN, places=[NEAH, LAPUSH])),
      photo("A Quileute story tells", PH_RIALTO_PANO, "Near La Push, Quileute land"),
      photo("They had remembered for", PH_FLATTERY_N, "Cape Flattery")),
)

chapter(
    P("P32",
      m(0, v(WEST, routes=[CSZ], places=[SEATTLE])),
      m("where the ocean floor", v({"lon": -125.5, "lat": 46.5, "span": 6.0}, routes=[CSZ])),
      stat("at least nineteen great", "19", "Great (M8+) Cascadia earthquakes in ~10,000 years", PNSN, note="About every 500 years on average"),
      photo("The last one was", PH_QUINAULT, "Rainforest canopy, Quinault valley (NPS)")),
    P("P33",
      stat(0, "10-15 %", "Chance of a full-margin ~M9 in the next 50 years", USGS_P),
      photo("The United States Geological", PH_ISS_OZETTE, "The outer coast from the ISS, 2024 (NASA)"),
      m("When it comes, the", v(SOUTH, places=[WESTPORT, NCOVE, ABERDEEN])),
      stat("Washington's natural resources department", "TENS OF MINUTES", "To reach high ground after a Cascadia quake", DNR),
      sat("to get to high", -124.10, 46.95, 0.6, "Ocean Shores and Westport: low, flat ground", date=SUMMER25)),
    P("P34",
      photo(0, PH_WESTPORT_NARA, "Westport (NARA)"),
      sat("and why the towns", -124.15, 47.00, 0.4, "Ocean Shores", date=SUMMER25),
      sat("In twenty sixteen, at", -124.10, 46.88, 0.2, "Westport", date=SUMMER25),
      stat("a reinforced platform above", "1,000 PEOPLE", "Ocosta school tsunami refuge, Westport, 2016", DNR)),
    P("P34b",
      sat(0, -124.105, 46.885, 0.08, "Westport and the open coast", date=SUMMER25),
      photo("On a coast where", PH_RIALTO2, "Rialto Beach"),
      stat("a roof may be", "53 FT", "Height of the Ocosta refuge above sea level", "Seattle Times 2016, via Wikipedia")),
)

chapter(
    P("P35",
      m(0, v(PEN, arrows=STORMS, places=[HOH, SEQUIM])),
      photo("It pulls the rain", PH_HOH_BRANCH, "Moss and rain, Hoh rainforest (NPS)"),
      photo("more than twelve feet", PH_HOH_MOSS, "Hoh rainforest"),
      photo("while the other side", PH_DUNG, "Dungeness Spit, in the rain shadow"),
      m("Add a shore of", v(PEN, routes=[US101])),
      photo("a park drawn around", PH_GLINES_NOTCH, "Glines Canyon Dam coming down, 2011 (NPS)"),
      m("and a fault that", v(WEST, routes=[CSZ]))),
    P("P36",
      photo(0, PH_RUBY_DOOR, "Ruby Beach"),
      sat("where the land looks", -124.42, 47.66, 0.3, "The Olympic coast", date=SUMMER25),
      sat("So here is the", -124.17, 47.13, 0.4, "The Copalis coast", date=SUMMER25),
      photo("would you build your", PH_RUBY_ROCKS, "Ruby Beach"),
      photo("Tell me in the", PH_HOH_HALL, "Hoh rainforest"),
      ask=("So here is the", "Would you build on this coast, or keep it wild?")),
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


TITLE = "Why Almost Nobody Lives on Washington's Wild Coast"
script = {
    "title": TITLE,
    "voice": "am_michael",
    "voice_speed": 1.15,
    "music": "procedural",
    "map_style": "satellite",
    "look": "none",
    "photo_upscale": True,
    "sources": ["episodes/olympic-peninsula/research.md and factcheck.md", "Contains modified Copernicus Sentinel data 2026",
                "Landsat imagery courtesy of NASA/USGS", "Highway 101 and the Cascadia fault drawn through main points (approximate)"],
    "thumbnail": {"text": "RAINFOREST NEXT TO A DESERT"},
    "chapters": chapters,
    "youtube": {
        "title": TITLE,
        "description": "On Washington's Olympic Peninsula, the Hoh rainforest gets 12 to 14 feet of rain a year, while Sequim, about 40 miles away, is as dry as Los Angeles. The same mountains help explain why the state's Pacific coast is almost empty. We follow the answer from orbit: the rain shadow, the rainforest and a coast that will not stay still, Olympic National Park and its 73 miles of wilderness shore, the timber boom of Forks, the Elwha dams and the largest dam removal in U.S. history, and the night of 26 January 1700, when a Cascadia earthquake sent a tsunami to Japan.",
        "tags": ["Olympic Peninsula", "Olympic National Park", "Hoh Rainforest", "Sequim", "rain shadow", "Washington coast", "Forks",
                 "Elwha River", "dam removal", "Cascadia earthquake", "1700 tsunami", "ghost forest", "geography", "satellite images"],
        "pinned_comment": "Would you build on this coast, or keep it wild?",
    },
}
out = HERE / "script.json"
out.write_text(json.dumps(script, ensure_ascii=False, indent=1) + chr(10), encoding="utf-8")
words = sum(len(p["text"].split()) for c in chapters for p in c["paragraphs"])
shots = [s for c in chapters for p in c["paragraphs"] for s in p["shots"]]
kinds = {k: sum(1 for s in shots if s["type"] == k) for k in ("map", "photo", "stat", "document", "chart")}
print(f"{words} words, {len(chapters)} chapters, {len(shots)} shots {kinds}")
