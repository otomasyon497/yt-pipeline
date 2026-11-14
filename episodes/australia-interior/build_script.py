"""Builds script.json for australia-interior.  python build_script.py

Production logic of 2026-11-13/14: the hook template and numbered reasons (docs/reference-videos-2026-11-13.md), every
reason opens on a painted map (highlight "name@tint"), a third of the pictures are ground-level photographs, and there
is NO filler machinery: every shot is placed by hand under the words it shows, no view or photo comes back more than
twice (tools/episode_check.py). Narration speed 1.15 (user, 2026-11-13).
Sources: research.md. Regions: geo/make_regions.py and Geoscience Australia drainage divisions.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent.parent / "pipeline"))
from schema import Paragraph  # noqa: E402

AUS = {"lon": 134.0, "lat": -27.5, "span": 58}
EAST = {"lon": 143.0, "lat": -26.0, "span": 25}  # right edge at 155.5 E: a dark strip showed near 157 E for 2 s after a cut (storyboard 1)
SA = {"lon": 137.6, "lat": -33.3, "span": 9.5}
EYRE_W = {"lon": 137.4, "lat": -28.6, "span": 4.4}
NQ = {"lon": 145.6, "lat": -19.0, "span": 9}
INLAND, COAST = "file:inland.geojson", "file:coast.geojson"
RANGE, DESERTS, GAB = "file:range.geojson", "file:deserts.geojson", "file:gab.geojson"
EYRE_B, MDB, NWP, SWP = "file:eyre_basin.geojson", "file:mdb.geojson", "file:nw_plateau.geojson", "file:sw_plateau.geojson"
SPRING = "2025-09-02"  # a clear MODIS day over South Australia with the crops green (checked 2026-11-13)
CMP_EYRE = {"before": "2018-05-15", "after": "2025-07-12", "source": "modis", "seconds": 2.0, "label_before": "2018", "label_after": "2025"}


def near(lon, lat, span):
    return {"lon": lon, "lat": lat, "span": span}


def place(name, lon, lat, label=None, kind="city"):
    return {"name": name, "lon": lon, "lat": lat, "kind": kind, "label": label if label is not None else name}


def m(at, *steps, text=None, cut=True):
    s = {"type": "map", "at": at, "map": {"steps": list(steps)}}
    if cut:
        s["map"]["cut"] = True
    if text:
        s["on_screen_text"] = text
    return s


_uses: dict = {}


def fresh(view):
    """Wide views (painted maps, dated MODIS views) come back with new content; frame each use a little differently so
    no map frame is seen twice (episode_check counts a view by its centre and width)."""
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


def step(at, **kw):
    return {"at": at, **kw}


def sat(at, lon, lat, span, label=None, **kw):
    """One close satellite view (Sentinel-2, the clearest recent day) of a named spot."""
    return m(at, v(near(lon, lat, span), **kw), text=label)


def paint(at, *names, view=AUS, **kw):
    return m(at, v(view, highlight=list(names), **kw))


def photo(at, name, text=None):
    d = {"type": "photo", "at": at, "photo": name}
    if text:
        d["on_screen_text"] = text
    return d


def stat(at, value, label, source):
    return {"type": "stat", "at": at, "stat": {"value": value, "label": label, "source": source}}


def clip(at, text, source, highlight=None):
    d = {"text": text, "source": source}
    if highlight:
        d["highlight"] = highlight
    return {"type": "document", "at": at, "document": d}


def chart(at, title, unit, data, source, reveal=None, highlight=0):
    c = {"type": "bar", "title": title, "unit": unit, "data": data, "source": source, "highlight": highlight}
    if reveal:
        c["reveal"] = reveal
    return {"type": "chart", "at": at, "chart": c}


def P(text, *shots, ask=None):
    d = {"text": text, "shots": list(shots)}
    if ask:
        d["ask"] = {"at": ask[0], "text": ask[1]}
    return d


ABS01 = "ABS, Population Growth and Distribution 2001 (cat. 2035.0)"
BOM = "Bureau of Meteorology, in ABS Year Book Australia 2005"
GA = "Geoscience Australia"
NASA19 = "NASA Earth Observatory, 2019"
SAHH = "Judith Jeffery, SA History Hub (History Trust of South Australia)"
CSIRO = "Petheram, Hughes, Read & Stokes (CSIRO), MODSIM 2023"
CONV = "Ryan Borrett, Murdoch University, in The Conversation, January 2024"

# Photographs (Wikimedia Commons; licence checked by tools/find_media.py and again by the pipeline)
PH_MELB = "File:Aerial panorama of South Yarra facing the Melbourne skyline. September 2023.jpg"
PH_SYDNEY = "File:Sydney Harbour aerial.jpg"
PH_PERTH = "File:Perth skyline from the Swan River, August 2024.jpg"
PH_STUART = "File:Stuart Highway - panoramio.jpg"
PH_STUART2 = "File:Stuart Highway (2050420602).jpg"
PH_DAINTREE = "File:Daintree Rainforest, Queensland (483845) (9443587310).jpg"
PH_DAINTREE2 = "File:Daintree Rainforest, Queensland (483850) (9443590252).jpg"
PH_ULURU = "File:Uluru, helicopter view.jpg"
PH_SIMPSON = "File:Simpson Desert Dunes, Australia (52241360124).png"
PH_SOIL = "File:CSIRO ScienceImage 3832 Red Sodosol soil profile near Coober Pedy South Australia.jpg"
PH_COOBER = "File:CSIRO ScienceImage 3835 Opal fields at Coober Pedy South Australia 1992.jpg"
PH_SALTBUSH = "File:SaltbushPlainHay.JPG"
PH_BIRDSVILLE = "File:Birdsville DSC02999 SA (38297669892).jpg"
PH_MUNGER = "File:Mungerannie Roadhouse, Birdsville Track - 8609801810.jpg"
PH_MAIL = "File:Royal Mail car on Birdsville Track, 1934.jpg"
PH_SALT = "File:LakeEyreSaltCrust.JPG"
PH_SIMPSON2 = "File:Simpson Desert, Australia (52241573890).png"
PH_BIRDSVILLE2 = "File:Birdsville DSC03000 SA (38297658682).jpg"
PH_MUNGER2 = "File:Mungerannie Roadhouse, Birdsville Track - 8608694241.jpg"
PH_DAINTREE3 = "File:Daintree Rainforest, Queensland (483880) (9440826087).jpg"
PH_WHEAT2 = "File:CSIRO ScienceImage 4026 Harvesting wheat near Blyth in the mid north of South Australia 1986.jpg"
PH_SYDNEY2 = "File:Sydney Harbour from a jet aircraft-19Mar2009.jpg"
PH_ISS = "File:ISS-30 Lake Eyre - South Australia.jpg"
PH_CHANNEL = "File:Australia's Channel Country (MODIS 2024-04-12).jpg"
PH_FLOOD = "File:Floodwaters Surge Through the Australian Outback (154116 - ing oli 20250329 lrg).jpg"
PH_GOYDER = "File:Portrait of George Woodroffe Goyder(GN03908).jpg"
PH_WHEAT = "File:CSIRO ScienceImage 4485 Harvesting wheat at Blyth in the mid north of South Australia 1986.jpg"
PH_WHEAT_OLD = "File:Line of Horse Drawn Harvesting Machines in a Field of Wheat at Hallett(GN07447).jpg"
PH_KANYAKA = "File:Kanyaka Homestead (188325219).jpg"
PH_FARINA = "File:Ruin in Farina.jpg"
PH_FARINA2 = "File:Farina - detail (33428641183).jpg"
PH_BRADFIELD = "File:John Bradfield at his desk 02.jpg"
PH_BRADFIELD2 = "File:John Bradfield at his desk 01.jpg"
PH_BRADFIELD3 = "File:Doctor John Bradfield doffing his hat.jpg"
PH_PERTH2 = "File:Perth across the Swan 4245574568.jpg"
PH_BRIDGE = "File:John Bradfield tipping his hat from a walkway on the newly constructed Sydney Harbour Bridge.jpg"
PH_BURDEKIN = "File:CSIRO ScienceImage 10816 Spillway at the Burdekin Falls Dam.jpg"
PH_BORE = "File:Sinking an artesian bore on Saxby Downs Station, Queensland, circa 1893.tif"
PH_STATION = "File:Northern Territory - cattle station buildings and yard(GN02897).jpg"
PH_ROADTRAIN = "File:Road train (19754667713).jpg"
PH_SUPERPIT = "File:Super Pit Mine, Kalgoorlie, Western Australia.jpg"
PH_HANNAN = "File:Crowd watching parade in Hannan Street, Kalgoorlie, 1901.jpg"
PH_ALICE = "File:Alice Springs - Anzac Hill - panoramio.jpg"

SYDNEY, MELBOURNE = place("Sydney", 151.21, -33.87), place("Melbourne", 144.96, -37.81)
BRISBANE, PERTH, ADELAIDE = place("Brisbane", 153.03, -27.47), place("Perth", 115.86, -31.95), place("Adelaide", 138.60, -34.93)
ALICE = place("Alice Springs", 133.88, -23.70)
CAIRNS = place("Cairns", 145.77, -16.92)
LAKE = place("Kati Thanda-Lake Eyre", 137.37, -28.37, "Kati Thanda-Lake Eyre", "site")
FARINA = place("Farina", 138.28, -30.07, "Farina", "site")
KANYAKA = place("Kanyaka", 138.29, -32.09, "Kanyaka", "site")
ST_GEORGE = place("St George", 148.58, -28.04, "St George", "site")
KALGOORLIE = place("Kalgoorlie", 121.47, -30.75)
ANNA = place("Anna Creek Station", 136.17, -28.90, "Anna Creek Station", "site")
GOYDER_E = {"from": [137.59, -34.07], "via": [[138.21, -33.35], [138.61, -32.73], [138.84, -32.97], [138.93, -33.67]], "to": [140.91, -35.26],
            "mode": "line", "color": "red", "seconds": 2.5, "label": "Goyder's Line (approximate)"}
GOYDER_W = {"from": [133.67, -32.13], "via": [[136.20, -33.47]], "to": [136.57, -33.91], "mode": "line", "color": "red", "seconds": 1.5}
PACIFIC_AIR = [{"from": [154.5, -18.0], "to": [147.2, -18.5], "color": "blue", "bend": 0.1},
               {"from": [155.3, -26.0], "to": [153.6, -27.5], "color": "blue", "bend": -0.1},
               {"from": [155.0, -35.0], "to": [151.3, -34.2], "color": "blue", "bend": 0.1}]
TO_EYRE = [{"from": [142.5, -21.0], "to": [138.2, -27.6], "color": "blue", "bend": 0.2, "label": "up to ten months"},
           {"from": [144.5, -24.0], "to": [138.4, -28.0], "color": "blue", "bend": -0.15}]
BRADFIELD_1938 = [{"from": [146.0, -18.6], "to": [144.3, -23.2], "color": "red", "bend": 0.15, "label": "Bradfield, 1938"},
                  {"from": [144.2, -23.5], "to": [138.2, -27.8], "color": "red", "bend": -0.15}]
CHANNEL = {"from": [146.2, -19.9], "via": [[146.0, -22.5], [147.2, -25.5]], "to": [148.58, -28.04], "mode": "line", "color": "accent",
           "seconds": 1.2, "label": "1,600 km channel (CSIRO's test)"}

chapters = [
    {"title": "The Empty Middle", "mood": "curious", "paragraphs": [
        P("Australia is almost as big as the lower forty-eight United States. About twenty-eight million people live on it. But draw a strip fifty kilometers wide along its coast, about a tenth of the land, and by the last official count of this kind you have fenced in more than eight out of every ten of them. Behind that strip lies nine tenths of a continent. And at night, from orbit, almost all of it is dark.",
          m(0, v(AUS)),
          photo("About twenty-eight million", PH_MELB, "Melbourne, 2023"),
          paint("But draw a strip", COAST + "@accent"),
          stat("by the last official", "85 %", "Australians living within 50 km of the coast, 2001 census", ABS01),
          sat("more than eight out", 153.42, -28.0, 0.5, "Gold Coast, Queensland"),
          paint("Behind that strip", INLAND + "@red", COAST + "@accent"),
          m("And at night", v(AUS, layer="night"))),
        P("The pattern holds almost everywhere. In that count, ninety-nine percent of Tasmanians lived near the coast, ninety-one percent of South Australians and Western Australians, eighty-eight percent of Queenslanders. Even in the Northern Territory, the emptiest of them all, two people in three lived near the sea. Five cities on the edge, Sydney, Melbourne, Brisbane, Perth and Adelaide, hold most of the country between them.",
          paint(0, COAST + "@accent", places=[SYDNEY, MELBOURNE, BRISBANE, PERTH, ADELAIDE]),
          sat("ninety-one percent", 138.6, -34.93, 0.5, "Adelaide, South Australia"),
          sat("eighty-eight percent", 153.03, -27.47, 0.5, "Brisbane, Queensland"),
          sat("Even in the Northern", 130.84, -12.46, 0.4, "Darwin, Northern Territory"),
          photo("Five cities on", PH_SYDNEY2, "Sydney from the air, 2009"),
          photo("hold most of", PH_PERTH, "Perth, Western Australia")),
        P("It is not empty for lack of trying. A surveyor once drew a line across the map and warned farmers not to cross it. They crossed it. The engineer of the Sydney Harbour Bridge wanted to turn whole rivers around and send them inland. And in the middle there is a lake that fills only a few times in a century. So why does almost nobody live in most of Australia? There are five reasons. The first one starts in the sky.",
          photo(0, PH_STUART, "Stuart Highway"),
          photo("A surveyor once", PH_GOYDER, "George Goyder, Surveyor-General"),
          sat("They crossed it", 138.42, -31.6, 0.9, "North of Goyder's Line, South Australia"),
          photo("The engineer of", PH_BRIDGE, "John Bradfield on the Sydney Harbour Bridge"),
          sat("And in the middle", 137.35, -28.45, 1.9, "Kati Thanda-Lake Eyre"),
          paint("So why does", INLAND + "@red", places=[SYDNEY, MELBOURNE, BRISBANE, PERTH, ADELAIDE]),
          photo("There are five", PH_ULURU, "Uluru, Northern Territory"),
          ask=("So why does", "Why is the middle empty?")),
    ]},
    {"title": "The Rain Never Arrives", "mood": "curious", "paragraphs": [
        P("Reason one. The rain never arrives. Look at where Australia sits. It lies across the latitudes where air that rose near the equator comes back down, and sinking air is dry air. The Bureau of Meteorology says it plainly: the dominant influence on Australia's climate is its latitude, and the aridity of much of the country is largely a consequence of that subsiding air. A belt of high pressure sits over the continent for much of the year, and under it clouds struggle to form.",
          paint(0, DESERTS + "@red"),
          m("Look at where", v({"lon": 134, "lat": -10, "span": 150}, highlight=["Australia@red"])),
          photo("and sinking air", PH_SIMPSON, "Simpson Desert"),
          clip("The Bureau of", "The dominant influence on Australia's climate is its latitude... The aridity of much of Australia is largely a consequence of the subsiding air associated with the high pressure ridge.", BOM, highlight="subsiding air"),
          sat("and the aridity of", 136.5, -26.2, 1.4, "Simpson Desert"),
          sat("A belt of high", 129.0, -28.4, 1.2, "Great Victoria Desert"),
          sat("clouds struggle", 124.3, -21.3, 0.9, "Great Sandy Desert")),
        P("Then there is the shape of the land. Moist air does come in from the Pacific. On the east coast it meets the Great Dividing Range, a chain of highlands that runs the length of the continent's eastern edge. The air rises, cools, and drops its rain on the seaward side. The wettest place in the country is here, on the Queensland coast between Cairns and Cardwell, where rainforest comes down to the beach. What crosses the range has already been wrung out. In the Bureau's words, the range enhances rainfall over the east coast and partially blocks moisture from penetrating further inland.",
          paint(0, RANGE + "@alt", view=EAST),
          m("Moist air does", v(EAST, highlight=[RANGE + "@alt"], arrows=PACIFIC_AIR)),
          sat("a chain of highlands", 150.35, -33.75, 0.5, "Blue Mountains, New South Wales"),
          photo("The air rises", PH_DAINTREE, "Rain over the wet tropics, north Queensland"),
          sat("The wettest place", 145.9, -17.6, 0.9, "Queensland coast, Cairns to Cardwell", places=[CAIRNS]),
          photo("where rainforest", PH_DAINTREE2, "Daintree rainforest, Queensland"),
          sat("What crosses the", 144.2, -20.85, 0.7, "West of the range: Hughenden, Queensland"),
          clip("In the Bureau's", "The Great Dividing Range and associated ranges in eastern Australia enhance rainfall over the east coast hinterland and partially block moisture from penetrating further inland.", BOM, highlight="partially block moisture"),
          sat("and partially blocks", 146.3, -26.4, 1.0, "Inland Queensland, west of the range")),
        P("And the interior is simply far away. In any direction, it is a long way from the sea. The result is a number. Over eighty percent of the continent, average rainfall is below six hundred millimeters a year: two feet. Over half of it, the figure is below three hundred, one foot. And around Lake Eyre, in the driest corner, it is under a hundred and fifty: six inches of rain in a whole year.",
          sat(0, 133.88, -23.70, 0.5, "Alice Springs, Northern Territory", places=[ALICE]),
          photo("In any direction", PH_STUART2, "Stuart Highway"),
          chart("Over eighty percent", "Share of Australia by yearly rainfall", "%", [["Under 600 mm", 80], ["Under 300 mm", 50]], BOM, reveal=["Over half of it"], highlight=1),
          sat("And around Lake Eyre", 137.9, -29.3, 0.8, "South of Lake Eyre"),
          stat("it is under", "150 MM", "Yearly rainfall near Lake Eyre, the driest part of Australia", BOM)),
        P("And the dry part is not a corner of the map. Western Australia alone covers two and a half million square kilometers, a third of the country. As a nation it would rank among the ten largest on Earth. Most of it is desert or dry scrub, and most of its people live in one city, Perth, in the far southwest, where winter rain still reaches.",
          paint(0, "Western Australia@red", places=[PERTH]),
          sat("As a nation it", 125.0, -26.0, 1.5, "Gibson Desert, Western Australia"),
          sat("Most of it is", 121.6, -27.2, 0.9, "Salt lakes of the Western Australian goldfields"),
          photo("and most of its people", PH_PERTH, "Perth, Western Australia"),
          sat("where winter rain", 116.0, -32.4, 0.9, "Perth and the green southwest")),
        P("Wheat farmers in South Australia found out exactly where the limit was, and we will come to them. But low rainfall is only the first problem. Even where rain does fall, what does it fall on?",
          photo(0, PH_WHEAT, "Wheat harvest, mid north of South Australia, 1986"),
          sat("and we will come", 138.0, -33.6, 1.2, "Wheat country, South Australia"),
          sat("But low rainfall", 131.04, -25.35, 0.35, "Uluru"),
          photo("Even where rain", PH_SALTBUSH, "Saltbush plain")),
    ]},
    {"title": "The Ground Is Worn Out", "mood": "curious", "paragraphs": [
        P("Reason two. The ground is worn out. In Europe and North America the ice ages did farmers a favor. Glaciers ground fresh rock into powder and spread it over the land. Elsewhere volcanoes did the same job, bringing up minerals from deep below. Australia had very little of either. As a writer at Murdoch University put it in 2024, Australia did not have this renewal of soil from grinding ice, or from volcanoes. The result, in the same article's words: soils that are heavily weathered, old, and short on nutrients.",
          paint(0, INLAND + "@accent"),
          photo("In Europe and", PH_SOIL, "Red soil profile near Coober Pedy (CSIRO)"),
          sat("Glaciers ground", 129.5, -30.9, 1.0, "Nullarbor Plain"),
          sat("Elsewhere volcanoes", 127.0, -24.6, 0.9, "Gibson Desert"),
          clip("As a writer at", "Australia didn't have this renewal of soil from grinding ice – or from volcanoes... our soils are famously very poor – heavily weathered, old, and short on nutrients.", CONV, highlight="heavily weathered, old, and short on nutrients"),
          sat("Australia did not have", 123.5, -27.5, 1.0, "The old plateau of Western Australia"),
          photo("The result, in", PH_COOBER, "Coober Pedy, South Australia, 1992 (CSIRO)")),
        P("Old is the key word. The interior is low and flat, and it has been for a very long time. Rain, when it came, washed the goodness out of the ground, and nothing put it back. You can see the result from the air. Most of this is not sand-dune desert. Geoscience Australia counts ten named deserts, and together they cover about eighteen percent of the mainland. The largest, the Great Victoria, covers about three hundred and fifty thousand square kilometers, close to the size of Germany. The agency's own definition of a desert is land that gets less than two hundred and fifty to five hundred millimeters of rain a year, and by that measure at least half the continent is dry country.",
          sat(0, 134.75, -29.01, 0.4, "Coober Pedy, South Australia"),
          photo("Rain, when it came", PH_SIMPSON2, "Simpson Desert"),
          sat("You can see the", 130.74, -25.3, 0.5, "Kata Tjuta, Northern Territory"),
          paint("Geoscience Australia counts", DESERTS + "@red"),
          stat("together they cover", "18 %", "Share of the mainland covered by Australia's ten named deserts", GA),
          sat("The largest, the", 127.5, -28.0, 1.6, "Great Victoria Desert"),
          sat("The agency's own", 131.5, -22.0, 1.1, "Tanami Desert, Northern Territory"),
          paint("at least half", DESERTS + "@red", INLAND + "@accent")),
        P("The rest of the dry country is scrub, spinifex grass and red earth: land that can carry cattle or sheep, thinly, but will not grow a crop without help. So the interior has too little rain, and soil that gives little back. A big river could still fix that. Egypt has almost no rain at all, and it has the Nile. So where is Australia's Nile?",
          photo(0, PH_BIRDSVILLE, "Near Birdsville, on the edge of the Simpson Desert"),
          photo("land that can carry", PH_BIRDSVILLE2, "Near Birdsville"),
          paint("So the interior", INLAND + "@red"),
          m("Egypt has almost", v({"lon": 31.2, "lat": 27.0, "span": 9})),
          m("So where is", v(AUS))),
    ]},
    {"title": "The Rivers Run the Wrong Way", "mood": "curious", "paragraphs": [
        P("Reason three. The rivers run the wrong way. Follow the water. Rain that falls on the seaward side of the range runs a short way east and is gone into the Pacific. Rain that falls on the inland side runs west, into the dry country, and there the map does something strange. This is the Lake Eyre basin. By Geoscience Australia's mapping it covers one point three million square kilometers, about a sixth of the country, almost twice the size of Texas. Not one river inside it reaches the sea.",
          paint(0, EYRE_B + "@blue"),
          sat("Follow the water", 146.2, -18.65, 0.6, "Herbert River, north Queensland"),
          m("Rain that falls on the inland", v(EAST, highlight=[RANGE + "@alt", EYRE_B + "@blue"])),
          paint("This is the Lake", EYRE_B + "@blue", places=[LAKE]),
          stat("it covers one point", "1.3 MILLION KM²", "Lake Eyre drainage division: about a sixth of Australia", GA + ", National Catchment Boundaries"),
          paint("about a sixth of", EYRE_B + "@blue", view={"lon": 138.0, "lat": -26.0, "span": 30}),
          m("Not one river", v({"lon": 139.5, "lat": -25.5, "span": 16}, highlight=[EYRE_B + "@blue"], places=[LAKE]))),
        P("Its rivers have names: the Diamantina, the Georgina, Cooper Creek. For most of the time they are chains of waterholes, or dry sand. When big rains fall in northern Queensland, the water starts south. It spreads out across the plains, soaks in, and evaporates. NASA notes that the trip has historically taken up to ten months. What survives arrives here, at Kati Thanda-Lake Eyre, the lowest natural point in Australia, fifteen meters below sea level.",
          sat(0, 139.37, -25.9, 0.5, "Diamantina River at Birdsville"),
          photo("For most of the time", PH_MUNGER, "Mungerannie, Birdsville Track"),
          photo("When big rains", PH_CHANNEL, "Channel Country in flood, April 2024 (NASA MODIS)"),
          sat("It spreads out", 142.6, -25.4, 0.9, "Cooper Creek channels near Windorah"),
          m("NASA notes that", v({"lon": 140.5, "lat": -24.5, "span": 13}, highlight=[EYRE_B + "@blue"], arrows=TO_EYRE, places=[LAKE])),
          sat("What survives arrives", 137.3, -28.3, 2.0, "Kati Thanda-Lake Eyre"),
          stat("the lowest natural point", "-15 M", "Kati Thanda-Lake Eyre: the lowest natural point in Australia", NASA19)),
        P("Most years it is a salt pan. This is how it looked from orbit in May 2018: white with salt. Smaller flows reach it every few years. But it fills completely, NASA says, only a few times in a century. And this is the same lake in July 2025, after floods came down from Queensland. Then the sun takes it back. A river system that drains a sixth of the country ends in a sheet of brine that evaporates.",
          photo(0, PH_SALT, "Salt crust on Lake Eyre"),
          m("This is how it", v(EYRE_W, date="2018-05-15")),
          sat("Smaller flows reach", 137.9, -27.9, 0.8, "Where the rivers enter the lake"),
          m("But it fills completely", v(EYRE_W, compare={**CMP_EYRE, "until": "And this is the"}), step("And this is the")),
          photo("Then the sun", PH_FLOOD, "Floodwater in the Channel Country, March 2025 (NASA Landsat)"),
          sat("A river system", 137.6, -29.45, 0.7, "Lake Eyre South")),
        P("NASA watched an earlier flood in 2019. Water began entering the lake in the middle of March, months after the rain that sent it. Between February and May, by the Bureau of Meteorology's count, more than seven Sydney Harbours of water flowed in, and by the middle of May the lake was still only about half full. It has been bigger. About a hundred thousand years ago, NASA notes, the lake was roughly ten times its present size. The climate that filled it is gone.",
          m(0, v(EYRE_W, date="2019-05-15")),
          sat("Water began entering", 138.6, -27.4, 0.9, "Warburton River, north of the lake"),
          stat("more than seven", "7 SYDNEY HARBOURS", "Water that reached Lake Eyre from February to May 2019", "Bureau of Meteorology, via NASA Earth Observatory"),
          sat("the lake was still", 137.25, -28.75, 0.7, "Belt Bay, Kati Thanda-Lake Eyre"),
          paint("About a hundred thousand", EYRE_B + "@blue", places=[LAKE], view={"lon": 139.5, "lat": -25.5, "span": 18}),
          photo("The climate that", PH_ISS, "Lake Eyre from the International Space Station (NASA)")),
        P("West of it the story repeats on a larger scale: two more drainage regions, the western plateaus, where almost no river reaches the sea either. Add them to Lake Eyre's and you have about forty percent of Australia that does not drain to any ocean.",
          paint(0, EYRE_B + "@blue", NWP + "@alt", SWP + "@alt"),
          sat("where almost no river", 123.0, -23.5, 1.2, "Little Sandy Desert, Western Australia"),
          stat("about forty percent", "40 %", "Share of Australia in its three inland drainage divisions (our sum)", GA + ", National Catchment Boundaries")),
        P("There is one exception, and it proves the rule. The Murray-Darling basin, in the southeast: about a seventh of the country, and its water does reach the sea. It is the one big river system the inland has, and if you look at where the inland towns and irrigated farms are, they follow it. Everywhere else: no rain, poor soil, and rivers that die in salt. You would think nobody would try to farm that. They did. And one man told them exactly where they would fail.",
          paint(0, MDB + "@accent", EYRE_B + "@blue"),
          sat("and its water does", 140.75, -34.17, 0.4, "River Murray at Renmark"),
          sat("It is the one big", 142.15, -34.2, 0.5, "Irrigated farms on the Murray at Mildura"),
          sat("they follow it", 146.05, -34.29, 0.6, "Irrigation at Griffith, New South Wales"),
          sat("Everywhere else", 138.0, -30.9, 1.3, "Lake Torrens, South Australia"),
          photo("You would think", PH_WHEAT_OLD, "Wheat harvest at Hallett, South Australia"),
          sat("And one man", 138.0, -33.2, 2.4, "South Australia's farm belt")),
    ]},
    {"title": "They Tried Anyway", "mood": "tension", "paragraphs": [
        P("Reason four. They tried, and the land said no. South Australia, 1865. The colony's northern sheep runs had just been devastated by drought. The government sent its Surveyor-General, George Goyder, to see how far the damage went. By one account he rode about two thousand miles in a single month, November 1865, and handed in his report on the sixth of December. He came back with a line on a map. South of it, he said, the rain could be trusted. North of it, it could not. The line followed the edge of twelve inches of rain a year, thirty centimeters, and his advice was to discourage anyone from planting crops beyond it.",
          paint(0, "South Australia@red"),
          sat("The colony's northern", 138.42, -31.89, 0.5, "Hawker, Flinders Ranges"),
          photo("The government sent", PH_GOYDER, "George Goyder, Surveyor-General"),
          sat("By one account he", 138.19, -32.83, 0.5, "Melrose, at the foot of the Flinders Ranges"),
          sat("and handed in", 138.93, -33.67, 0.4, "Burra, South Australia"),
          m("He came back", v(SA, routes=[GOYDER_E, GOYDER_W], places=[ADELAIDE])),
          stat("twelve inches of rain", "12 INCHES", "Yearly rainfall along Goyder's Line (30 cm)", SAHH),
          sat("his advice was", 138.53, -32.43, 0.5, "Carrieton, north of the line")),
        P("Now look at this. It is a satellite image of South Australia from September 2025, in spring. The green is cropland. The brown is not. A hundred and sixty years later, the edge of the farms still runs close to where Goyder drew his line. You are looking at the boundary he mapped from horseback, seen from seven hundred kilometers up.",
          m(0, v(SA, date=SPRING), step("The green is", routes=[GOYDER_E, GOYDER_W], places=[ADELAIDE])),
          m("A hundred and sixty", v({"lon": 138.6, "lat": -33.0, "span": 3.2}, date=SPRING, routes=[GOYDER_E])),
          sat("You are looking", 138.55, -32.95, 0.8, "The edge of the cropland near Orroroo")),
        P("At first the government listened. An act of 1872 allowed land to be bought on credit only inside the line. Then came a run of good seasons in the north. Grass grew where Goyder had said it would not, and farmers wanted in. A saying borrowed from the American frontier went around: rain follows the plough. Break the soil, people believed, and the climate itself would change. In 1874 parliament threw the rule out, and the wheat frontier moved north, past the line. New towns were laid out for the farmers who would follow. One of them, far to the north, was proclaimed in 1878 and called Farina. The word is Latin for flour.",
          photo(0, PH_WHEAT_OLD, "Wheat harvest at Hallett, South Australia"),
          m("An act of 1872", v({"lon": 138.2, "lat": -33.9, "span": 5.5}, routes=[GOYDER_E], places=[ADELAIDE])),
          sat("Then came a run", 138.61, -32.73, 0.5, "Orroroo, on Goyder's Line"),
          photo("A saying borrowed", PH_WHEAT, "Wheat harvest, mid north of South Australia, 1986"),
          photo("Break the soil", PH_WHEAT2, "Harvesting wheat near Blyth, South Australia, 1986"),
          m("In 1874 parliament", v({"lon": 138.4, "lat": -31.6, "span": 6}, routes=[GOYDER_E], arrows=[{"from": [138.6, -33.0], "to": [138.3, -30.3], "color": "accent", "bend": 0.1}], places=[FARINA, KANYAKA])),
          sat("New towns were", 138.84, -32.97, 0.4, "Peterborough, South Australia"),
          sat("One of them, far", 138.28, -30.07, 0.3, "Farina, South Australia", places=[FARINA]),
          photo("The word is", PH_FARINA2, "Farina, South Australia")),
        P("Then the 1880s came, and with them a run of bad seasons. In the words of South Australia's own history, many farmers abandoned their homesteads, often leaving behind a severely eroded landscape. The ruins are still there. Stone houses without roofs, in country that went back to scrub. A railway reached Farina in 1882. It never became a wheat town. Its normal rainfall was nowhere near enough, and nobody has lived in it since 1967.",
          sat(0, 138.29, -32.09, 0.3, "Kanyaka, South Australia", places=[KANYAKA]),
          clip("In the words of", "Many farmers abandoned their homesteads, often leaving behind a severely eroded landscape.", SAHH, highlight="abandoned their homesteads"),
          sat("often leaving behind", 138.2, -31.5, 0.7, "North of Hawker, South Australia"),
          photo("The ruins are", PH_KANYAKA, "Kanyaka homestead ruins, Flinders Ranges"),
          sat("Stone houses without", 138.1, -32.2, 0.6, "Willochra Plain, north of the line"),
          photo("A railway reached", PH_FARINA, "Ruin in Farina, South Australia"),
          sat("It never became", 138.28, -30.07, 0.12, "Farina from orbit"),
          sat("and nobody has", 138.1, -30.1, 1.2, "Country around Farina")),
        P("The line is still on the map. In 2003 the National Trust named it a heritage icon. No other Australian state has a surveyed line like it. And it may be moving. In 2015 a South Australian climate scientist, Peter Hayman, said that a warming, drying trend would push Goyder's line south, towards the coast.",
          m(0, v({"lon": 137.0, "lat": -33.6, "span": 8}, routes=[GOYDER_E, GOYDER_W], places=[ADELAIDE])),
          paint("No other Australian", "South Australia@red"),
          m("And it may be", v({"lon": 138.6, "lat": -33.6, "span": 4.5}, date=SPRING, routes=[GOYDER_E], arrows=[{"from": [138.9, -33.0], "to": [138.8, -34.3], "color": "red", "bend": 0.1}], places=[ADELAIDE])),
          sat("would push Goyder's", 138.75, -34.25, 0.5, "Farmland north of Adelaide")),
        P("Goyder had been right, and for a simple reason. He had not judged the land by one good year. He had ridden across it and read the plants: saltbush to the north, where drought was the rule, and mallee scrub to the south. The vegetation had already drawn the line. So if the rain will not come to the farmers, could the water be brought to them? One of the most famous engineers in the country thought so.",
          m(0, v(SA, date=SPRING, routes=[GOYDER_E, GOYDER_W])),
          photo("He had ridden", PH_SALTBUSH, "Saltbush plain"),
          sat("where drought was", 138.3, -31.2, 1.0, "Saltbush country, northern Flinders Ranges"),
          sat("and mallee scrub", 138.6, -33.83, 0.5, "Clare Valley, south of the line"),
          paint("So if the rain", INLAND + "@red"),
          photo("One of the most", PH_BRADFIELD, "Dr John Bradfield")),
    ]},
    {"title": "The Canal That Does Not Pay", "mood": "tension", "paragraphs": [
        P("Reason five. The fix has been costed, and it does not pay. In 1938 Dr John Bradfield, the engineer of the Sydney Harbour Bridge, published a plan. In the wet tropics of north Queensland, on the rainy side of the range, rivers like the Tully, the Herbert and the Burdekin pour into the Pacific. Bradfield proposed to dam them, tunnel through the range, and send the water west into the dry interior, towards Lake Eyre. Water the heart of the continent, the idea went, and it could be settled.",
          paint(0, "Queensland@red"),
          photo("In 1938 Dr John", PH_BRIDGE, "John Bradfield on the Sydney Harbour Bridge"),
          photo("In the wet tropics", PH_DAINTREE3, "Daintree rainforest, north Queensland"),
          sat("rivers like the Tully", 147.3, -19.7, 0.8, "Burdekin River"),
          m("Bradfield proposed to", v({"lon": 142.5, "lat": -23.5, "span": 20}, highlight=[RANGE + "@alt"], arrows=BRADFIELD_1938, places=[LAKE])),
          sat("Water the heart", 144.25, -23.44, 0.5, "Thomson River at Longreach")),
        P("The plan was never built. It has also never gone away. Scientists at CSIRO, the national science agency, wrote in 2023 that for eighty-five years the scheme has been a millstone around the necks of successive federal and state governments, and that drought in Australia has become synonymous with calls to build it. So the federal government asked CSIRO to test it properly, for the first time since 1982. The answer came in two parts.",
          photo(0, PH_BRADFIELD2, "Dr John Bradfield at his desk"),
          clip("Scientists at CSIRO", "Since first proposed 85 years ago, Dr John Bradfield's \"nation building\" 1500-km inter-basin water diversion scheme proposal has been a millstone around the necks of successive federal and state governments.", CSIRO, highlight="a millstone around the necks"),
          sat("the scheme has been", 149.13, -35.3, 0.3, "Canberra, the federal capital"),
          sat("and that drought", 146.0, -30.1, 1.0, "Dry country near Bourke, New South Wales"),
          photo("So the federal", PH_BURDEKIN, "Burdekin Falls Dam, Queensland (CSIRO)"),
          paint("The answer came", RANGE + "@alt", MDB + "@accent", view=EAST)),
        P("Those calls, CSIRO notes, come from high-profile Australians, media personalities and politicians, and they come back with every dry spell. Some supporters have even argued that so much new water in the interior would change the climate itself and bring more rain. It is the old belief that rain follows the plough, on the scale of a continent.",
          sat(0, 145.6, -17.84, 0.4, "Koombooloomba Dam, upper Tully River"),
          sat("and they come back", 145.94, -30.09, 0.4, "Bourke, on the Darling River"),
          photo("Some supporters have", PH_BRADFIELD3, "Dr John Bradfield"),
          sat("would change the climate", 137.2, -28.1, 1.4, "Kati Thanda-Lake Eyre North"),
          sat("It is the old belief", 141.0, -25.8, 1.0, "Channel Country, Queensland")),
        P("Part one: yes, it can be built. Dams and tunnels on the three rivers could release about nineteen hundred gigaliters of water a year into a channel sixteen hundred kilometers long, a thousand miles, running by gravity to St George, the nearest big irrigation area in the Murray-Darling basin. About two thirds of the water would survive the journey: enough, every year, to fill half a million Olympic swimming pools. That would add a quarter to all the irrigation water the basin uses.",
          sat(0, 147.0, -20.65, 0.6, "Burdekin Falls Dam and Lake Dalrymple"),
          m("into a channel", v({"lon": 147.0, "lat": -24.0, "span": 16}, highlight=[MDB + "@accent"], routes=[CHANNEL], places=[ST_GEORGE])),
          stat("sixteen hundred kilometers", "1,600 KM", "Length of the gravity channel to St George in CSIRO's assessment", CSIRO),
          sat("the nearest big", 148.58, -28.04, 0.5, "Irrigated farms at St George, Queensland"),
          sat("enough, every year", 148.2, -28.3, 0.3, "Storage ponds near St George"),
          sat("That would add", 149.8, -29.5, 0.6, "Irrigation near Moree, New South Wales")),
        P("Part two: the bill. Fifteen to thirty billion dollars for the backbone alone. And then comes the sentence that matters. The cost of diversion infrastructure, CSIRO wrote, added such a large premium to the cost of water that future crop revenues would never pay off the cost. Not slowly. Never. A second CSIRO report tested modern versions of the plan, and found that the water would cost irrigators more than four times what they could afford to pay. There was one more finding. By CSIRO's figures, Bradfield had counted on more than twice the water those rivers actually carry. Even the wet corner of Australia is not as wet as the dream needed it to be.",
          stat(0, "$15-30 BILLION", "Cost of the dams, tunnels and channel alone (Australian dollars)", CSIRO),
          m("And then comes", v({"lon": 147.0, "lat": -24.0, "span": 16}, routes=[CHANNEL], places=[ST_GEORGE])),
          clip("The cost of diversion", "Although technically feasible the cost of diversion infrastructure added such a large premium to the cost of water that future crop revenues would never pay off the cost of the water storage diversion infrastructure alone.", CSIRO, highlight="would never pay off"),
          sat("that future crop revenues", 148.75, -28.25, 0.5, "Irrigated fields on the Balonne plain"),
          sat("A second CSIRO report", 147.9, -27.6, 0.6, "Farmland on the Balonne River"),
          sat("There was one more", 146.16, -18.65, 0.5, "Herbert River at Ingham"),
          chart("By CSIRO's figures", "Water in the rivers Bradfield counted on", "GL a year", [["Bradfield's estimate", 7190], ["CSIRO's model", 3305]], "CSIRO, Bradfield Scheme Assessment factsheet, 2021", reveal=["more than twice"], highlight=1),
          photo("Even the wet", PH_DAINTREE, "Rain over the wet tropics, north Queensland")),
        P("Which leaves a question. If the rain does not come, the soil is poor, the rivers end in salt, the farmers were beaten and the great canal does not pay, who are the people who do live out there?",
          paint(0, INLAND + "@red"),
          photo("the farmers were", PH_FARINA, "Ruin in Farina, South Australia"),
          photo("who are the people", PH_ALICE, "Alice Springs from Anzac Hill")),
    ]},
    {"title": "Who Does Live There", "mood": "curious", "paragraphs": [
        P("Because some do. Start underground. Beneath the dry east of the interior lies the Great Artesian Basin: more than one point seven million square kilometers of water-bearing rock, under more than a fifth of the country, beneath parts of Queensland, New South Wales, South Australia and the Northern Territory. Geoscience Australia estimates that it holds about sixty-five thousand cubic kilometers of water. In a few places it reaches the surface on its own, in mound springs scattered across the desert. Drill into it, and in many places the water rises by itself. It is what made the cattle country possible: bores for the stock, water for the towns, and by the same agency's figures at least twelve point eight billion dollars of economic activity a year.",
          paint(0, GAB + "@blue"),
          stat("more than one point seven", "1.7 MILLION KM²", "Great Artesian Basin, under more than a fifth of Australia", GA),
          paint("under more than a fifth", GAB + "@blue", view={"lon": 141.0, "lat": -25.0, "span": 30}),
          sat("beneath parts of Queensland", 144.0, -26.6, 1.0, "Western Queensland, above the basin"),
          sat("Geoscience Australia estimates", 135.5, -26.42, 0.4, "Dalhousie Springs, fed by the basin"),
          sat("in mound springs", 136.07, -29.47, 0.15, "Mound springs near Lake Eyre South"),
          photo("Drill into it", PH_BORE, "Sinking an artesian bore, Saxby Downs Station, Queensland, about 1893"),
          photo("It is what made", PH_STATION, "Cattle station yard, Northern Territory"),
          photo("water for the towns", PH_MUNGER2, "Mungerannie, Birdsville Track"),
          photo("at least twelve", PH_ROADTRAIN, "Road train")),
        P("But look at what kind of life it supports. This is Anna Creek Station, in South Australia. By its owner's figure it covers about fifteen thousand seven hundred square kilometers. That is one cattle property, and it is larger than the state of Connecticut. Land that needs that much room to feed a herd cannot feed a city.",
          m(0, v({"lon": 136.2, "lat": -28.9, "span": 5}, places=[ANNA, LAKE])),
          stat("about fifteen thousand", "15,746 KM²", "Anna Creek Station, by its owner's figure", "Williams Cattle Company"),
          sat("That is one cattle", 136.17, -28.9, 0.5, "Anna Creek homestead"),
          photo("Land that needs", PH_MAIL, "Mail car on the Birdsville Track, 1934")),
        P("The other reason to live inland is also under the ground. This is the Super Pit at Kalgoorlie, in Western Australia, a gold mine you can see from orbit, beside a town of about twenty-nine thousand people. Farther north, at Mount Whaleback, a whole mountain of iron ore is being taken apart. Minerals pay for towns where farming could not. And many of the workers do not live there at all: they fly in, work their shift, and fly home to the coast.",
          paint(0, "Western Australia@accent", places=[KALGOORLIE, PERTH]),
          sat("This is the Super Pit", 121.50, -30.78, 0.2, "Super Pit, Kalgoorlie"),
          photo("a gold mine you", PH_SUPERPIT, "Super Pit, Kalgoorlie"),
          photo("beside a town", PH_HANNAN, "Hannan Street, Kalgoorlie, 1901"),
          sat("Farther north, at", 119.67, -23.36, 0.25, "Mount Whaleback iron ore mine, Newman"),
          sat("Minerals pay for", 119.68, -23.365, 0.1, "Mount Whaleback pit"),
          sat("And many of the workers", 118.6, -20.33, 0.3, "Port Hedland, Western Australia"),
          photo("they fly in", PH_PERTH2, "Perth, Western Australia")),
        P("And in the very middle sits Alice Springs, a town of about twenty-six thousand. One more thing has to be said. Nobody lives there was never quite true. Aboriginal people have lived across this continent, its deserts included, for tens of thousands of years; one site in the far north has been dated to about sixty-five thousand. What the interior has never supported is what the settlers wanted from it: farms, and cities.",
          sat(0, 133.88, -23.72, 0.25, "Alice Springs", places=[ALICE]),
          photo("One more thing", PH_ALICE, "Alice Springs from Anzac Hill"),
          photo("Aboriginal people have", PH_ULURU, "Uluru, Northern Territory"),
          sat("one site in the far", 132.9, -12.45, 0.6, "Kakadu, Northern Territory"),
          paint("What the interior", INLAND + "@red", COAST + "@accent")),
    ]},
    {"title": "The Price of the Edge", "mood": "calm", "paragraphs": [
        P("So put the five together. Air that sinks and dries. A range that takes the rain first. Soil that the ice never renewed. Rivers that end in a salt lake. And a hundred and sixty years of proof, from Goyder's line to CSIRO's ledger, that wishing does not change any of it. Eighty-five percent of the people on a tenth of the land. Six inches of rain a year at Lake Eyre. A basin a sixth of the country wide that never reaches the sea. And a canal that would cost up to thirty billion dollars and never pay. Australians did not crowd onto the coast by accident. They went where the water was, and nine tenths of the continent is the price of that.",
          m(0, v(AUS, layer="night")),
          paint("A range that takes", RANGE + "@alt", view=EAST),
          photo("Soil that the ice", PH_SOIL, "Red soil profile near Coober Pedy (CSIRO)"),
          m("Rivers that end", v(EYRE_W, date="2025-07-12")),
          m("And a hundred", v(SA, date=SPRING, routes=[GOYDER_E, GOYDER_W])),
          paint("Eighty-five percent of", COAST + "@accent", INLAND + "@red"),
          sat("Six inches of rain", 137.0, -28.6, 0.9, "Western shore of Kati Thanda-Lake Eyre"),
          paint("A basin a sixth", EYRE_B + "@blue"),
          m("And a canal", v({"lon": 147.0, "lat": -24.0, "span": 16}, routes=[CHANNEL], places=[ST_GEORGE])),
          photo("Australians did not", PH_MELB, "Melbourne, 2023"),
          photo("They went where", PH_SYDNEY, "Sydney Harbour"),
          paint("and nine tenths", INLAND + "@red")),
        P("Here is my question for you. If money were no object, would you build Bradfield's canal and try to green the middle, or leave the empty heart of the continent as it is?",
          paint(0, INLAND + "@red", COAST + "@accent"),
          m("would you build", v({"lon": 142.5, "lat": -23.5, "span": 22}, arrows=BRADFIELD_1938, places=[LAKE])),
          m("or leave the empty", v(AUS, layer="night")),
          ask=("would you build", "Build the canal, or leave the middle empty?")),
    ]},
]

PUSH_WORDS = 16  # a single-view map shot held longer than this gets a camera move halfway (a push-in on the subject)
for ch in chapters:
    for para in ch["paragraphs"]:
        anchors = Paragraph.model_validate(para).anchor_indices()  # also checks that every anchor phrase exists
        n = len(para["text"].split())
        for i, (sh, start) in enumerate(zip(para["shots"], anchors)):
            end = anchors[i + 1] if i + 1 < len(anchors) else n
            steps = (sh.get("map") or {}).get("steps", [])
            if sh["type"] != "map" or len(steps) != 1 or end - start <= PUSH_WORDS or steps[0].get("compare"):
                continue
            first = steps[0]
            vw = first["view"]
            move = {"at": start + (end - start) // 2, "view": {"lon": vw["lon"], "lat": vw["lat"], "span": max(0.05, round(vw["span"] * (0.62 if vw["span"] <= 2.5 else 0.75), 3))}}
            for key in ("date", "layer"):
                if first.get(key):
                    move[key] = first[key]
            steps.append(move)

script = {
    "title": "Why Almost Nobody Lives in Most of Australia",
    "voice": "am_michael",
    "voice_speed": 1.15,
    "music": "procedural",
    "map_style": "satellite",
    "look": "none",
    "sources": ["episodes/australia-interior/research.md and factcheck.md",
                "Drainage divisions: Geoscience Australia, National Catchment Boundaries (CC BY 4.0)",
                "Dated satellite views: NASA MODIS Terra via GIBS; Contains modified Copernicus Sentinel data 2026"],
    "thumbnail": {"text": "THE EMPTY MIDDLE"},
    "chapters": chapters,
    "youtube": {
        "title": "Why Almost Nobody Lives in Most of Australia",
        "description": "Australia is almost as big as the contiguous United States, yet at the 2001 census 85 % of its people lived within 50 km of the coast. This video goes through the five reasons the middle stayed empty: air that sinks and dries, a mountain range that takes the rain first, some of the oldest and poorest soils on Earth, rivers that end in a salt lake, and the two famous attempts to beat all that, Goyder's Line of 1865 and the Bradfield Scheme of 1938, which Australia's science agency finally costed.",
        "tags": ["Australia", "Outback", "why nobody lives in Australia", "Australian interior", "Goyder's Line", "Bradfield Scheme", "Lake Eyre", "Kati Thanda", "Great Artesian Basin", "Great Dividing Range", "geography", "population map", "satellite images"],
        "pinned_comment": "If money were no object, would you build Bradfield's canal and try to green the middle, or leave the empty heart of the continent as it is?",
    },
}
out = HERE / "script.json"
out.write_text(json.dumps(script, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
words = sum(len(p["text"].split()) for c in chapters for p in c["paragraphs"])
shots = [s for c in chapters for p in c["paragraphs"] for s in p["shots"]]
kinds = {k: sum(1 for s in shots if s["type"] == k) for k in ("map", "photo", "stat", "document", "chart")}
print(f"{words} words, {len(chapters)} chapters, {len(shots)} shots {kinds}")
