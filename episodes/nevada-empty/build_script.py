"""Builds script.json for nevada-empty.  python build_script.py

Same production logic as episodes/australia-interior (hook template, numbered reasons, painted regions, hand-placed
shots, no fillers, a photo or map frame at most twice). Sources: research.md. Regions: geo/make_regions.py.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent.parent / "pipeline"))
from schema import Paragraph  # noqa: E402

NV = {"lon": -116.9, "lat": 38.6, "span": 10.5}
WEST = {"lon": -119.0, "lat": 38.4, "span": 15}
SIERRA, BASIN = "file:sierra.geojson", "file:great_basin.geojson"


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


def paint(at, *names, view=None, **kw):
    view = view or NV
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


NOAA = "NOAA NCICS, State Climate Summary: Nevada"
NPS_R = "National Park Service, Rhyolite Ghost Town"
USGS = "USGS EROS, Cold War Craters"
NNSS = "Nevada National Security Site (DOE/NV-1243)"
CRS = "Congressional Research Service, R42346"
CENSUS = "US Census 2020 (Nevada Legislative Counsel Bureau; Census QuickFacts)"
SNWA = "Southern Nevada Water Authority"

PH_RHY1 = "File:Rhyolite NV Ghost Town - 52133328814.jpg"
PH_RHY2 = "File:Rhyolite NV Ghost Town - 52133328559.jpg"
PH_RHY3 = "File:Rhyolite NV Ghost Town - 52133584170.jpg"
PH_BLACKROCK = "File:Black Rock Desert 1.300.dpi (24995335682).jpg"
PH_TUFA = "File:Tufa Rocks, Pyramid Lake, Nevada MET DP242995.jpg"
PH_PYRAMID = "File:Pyramid Lake in Bloom (153466).jpg"
PH_HUMBOLDT = "File:Humboldt River Papa 2.jpg"
PH_WALKER = "File:ISS-32 Walker Lake, Nevada.jpg"
PH_US50 = "File:Us Route 50 The Loneliest Road In America (225539129).jpeg"
PH_TAHOE = "File:North Lake Tahoe Aerial photo Don Ramey Logan.jpg"
PH_SIERRA = "File:Snow-capped peaks of the Sierra Nevada Mountain Range.jpg"
PH_VEGAS = "File:Las Vegas strip from the air (3191356789).jpg"
PH_VEGAS2 = "File:Aerial view showing the Las Vegas Strip at dusk, Las Vegas, Nevada LCCN2011634444.tif"
PH_RENO = "File:Reno skyline.JPG"
PH_VC = "File:Virginia City, Nevada - 2025.jpg"
PH_TONOPAH = "File:Tonopah, Nevada LCCN2007662611.tif"
PH_TONOPAH_OLD = "File:Photographs of crowds watching a parade in Tonopah, Nevada circa 1910s.tif"
PH_GOLDFIELD = "File:Myers Mountain and the eastern skyline of Goldfield in Esmeralda County, Nevada in October 2026.jpg"
PH_GBNP = "File:Great Basin National Park - 53837533696.jpg"
PH_GBNP2 = "File:Great Basin National Park - 53837789943.jpg"
PH_PAIUTE = "File:Paiute women.jpg"
PH_RANCH = "File:Walking Box Ranch, Cattle Loading Gate - panoramio.jpg"
PH_RANCHROAD = "File:Rural dirt road in cattle ranch area.jpg"
PH_GOLDORE = "File:Twin Creeks mine Nevada Carlin-type gold ore.jpg"
PH_HOOVER = "File:Hoover Dam Ohio.JPG"

VEGAS, RENO = place("Las Vegas", -115.14, 36.17), place("Reno", -119.81, 39.53)
CARSON, ELKO = place("Carson City", -119.77, 39.16), place("Elko", -115.76, 40.83)
TONOPAH, ELY = place("Tonopah", -117.23, 38.07), place("Ely", -114.89, 39.25)
RHYOLITE = place("Rhyolite", -116.83, 36.90, "Rhyolite", "site")
SEDAN = place("Sedan crater", -116.046, 37.177, "Sedan crater, 1962", "site")
PYRAMID = place("Pyramid Lake", -119.55, 40.0, "Pyramid Lake", "site")
HSINK = place("Humboldt Sink", -118.62, 39.98, "Humboldt Sink", "site")
TO_SIERRA = [{"from": [-124.5, 40.2], "to": [-120.6, 39.6], "color": "blue", "bend": 0.1},
             {"from": [-124.0, 37.4], "to": [-119.6, 37.6], "color": "blue", "bend": -0.1}]
HUMBOLDT_R = {"from": [-115.0, 41.05], "via": [[-115.76, 40.83], [-116.9, 40.7], [-117.73, 40.97], [-118.17, 40.55]], "to": [-118.62, 39.98],
              "mode": "line", "color": "blue", "seconds": 2.5, "label": "Humboldt River"}
CLARK, WASHOE = "Clark@accent", "Washoe@accent"

chapters = [
    {"title": "Two Lights in the Dark", "mood": "curious", "paragraphs": [
        P("Nevada is bigger than Great Britain. About three million people live in it. And almost nine out of ten of them live in just two places: Las Vegas in the far south, and Reno up against the mountains in the west. Everything in between, hundreds of miles of it, is almost empty. At night, from orbit, you can see it. Two lights, and darkness.",
          m(0, v(NV)),
          photo("About three million", PH_VEGAS, "Las Vegas from the air"),
          paint("And almost nine", "Nevada@red", places=[VEGAS, RENO]),
          stat("almost nine out of ten", "89 %", "Nevadans living in Clark and Washoe counties, 2020 census (our sum)", CENSUS),
          photo("Everything in between", PH_US50, "US Route 50, 'the loneliest road in America'"),
          m("At night, from orbit", v(NV, layer="night"))),
        P("It is not that nobody ever tried. A lake nearly as big as Lake Erie once filled the northwest of this state, and it vanished. Towns of thousands rose on silver and gold, and blew away within a few years. And today the federal government owns about four fifths of the land, including a stretch of desert it used to set off nuclear bombs. So why does almost nobody live in most of Nevada? There are five reasons. The first one is a wall.",
          photo(0, PH_TUFA, "Tufa rocks at Pyramid Lake"),
          sat("A lake nearly as big", -118.4, 39.8, 1.6, "Carson Sink, the floor of an ancient lake"),
          photo("Towns of thousands", PH_RHY1, "Rhyolite, a ghost town"),
          sat("And today the federal", -116.05, 37.12, 0.25, "Yucca Flat, Nevada Test Site"),
          paint("So why does almost", "Nevada@red", places=[VEGAS, RENO]),
          photo("The first one is", PH_SIERRA, "The Sierra Nevada"),
          ask=("So why does almost", "Why is most of Nevada empty?")),
    ]},
    {"title": "The Wall That Takes the Rain", "mood": "curious", "paragraphs": [
        P("Reason one. The mountains take the rain. Weather in this part of America comes from the Pacific. Wet air rolls in off the ocean and hits a wall: the Sierra Nevada, a range of granite peaks more than fourteen thousand feet high, right along the California border. The air rises, cools, and drops its water on the western slopes. Snow piles up there by the meter. By the time that air comes down the other side, into Nevada, there is very little left.",
          paint(0, SIERRA + "@alt", view=WEST),
          m("Weather in this part", v(WEST, highlight=[SIERRA + "@alt"], arrows=TO_SIERRA)),
          sat("the Sierra Nevada, a range", -119.3, 37.7, 0.6, "High Sierra, Yosemite"),
          photo("The air rises", PH_TAHOE, "Lake Tahoe, on the crest of the Sierra"),
          sat("Snow piles up there", -120.15, 39.1, 0.5, "The west side of Lake Tahoe"),
          sat("By the time that air", -119.2, 39.4, 0.6, "East of the Sierra, near Carson City", places=[CARSON])),
        P("This is called a rain shadow, and Nevada lives in it. The government's climate scientists put it bluntly: Nevada is the nation's driest state. Across the whole state, the average is about ten inches of rain and snow a year. In the southern lowlands it is closer to four. Up on the high peaks of the Sierra it is more than fifty. Same air, a few dozen miles apart.",
          sat(0, -118.6, 38.9, 1.2, "The dry side of the Sierra"),
          clip("The government's climate", "Nevada is the Nation's driest state. Statewide annual average (1895–2024) precipitation is only 10.2 inches.", NOAA, highlight="driest state"),
          chart("In the southern lowlands", "Yearly rain and snow in Nevada", "inches", [["Southern lowlands", 4], ["State average", 10.2], ["High Sierra peaks", 50]], NOAA, reveal=["Up on the high"], highlight=2),
          photo("Same air, a few", PH_BLACKROCK, "Black Rock Desert")),
        P("And it is not one wall. Nevada is made of them. Drive across the state and the road climbs a mountain range, drops into a flat dry valley, climbs another range, drops again, over and over, dozens of times. Geologists call it the Basin and Range. Each range squeezes a little more water out of the sky for itself, and each valley floor gets less. The towns that do exist sit where a stream comes down off a mountain, and almost nowhere else.",
          sat(0, -117.1, 39.5, 1.4, "Ranges and basins near Austin"),
          photo("Drive across the state", PH_US50, "US Route 50, 'the loneliest road in America'"),
          sat("Geologists call it", -116.4, 38.9, 2.2, "The Basin and Range, central Nevada"),
          photo("Each range squeezes", PH_GBNP, "Great Basin National Park"),
          sat("The towns that do", -114.89, 39.25, 0.4, "Ely, at the foot of the Egan Range", places=[ELY])),
    ]},
    {"title": "The Water Goes Nowhere", "mood": "curious", "paragraphs": [
        P("Reason two. What little water there is goes nowhere. Almost all of Nevada lies inside the Great Basin, the largest region in North America where rivers never reach the sea. Rain that falls here stays here. It runs downhill into a valley and stops, and the sun takes it back. Look at the Humboldt River. It rises in the mountains of northeast Nevada and crosses almost the whole state, about three hundred miles. And then it simply ends, in a dry flat called the Humboldt Sink.",
          paint(0, BASIN + "@blue", view=WEST),
          stat("the largest region", "0 RIVERS", "Rivers in the Great Basin that reach the sea", "USGS; Great Basin hydrology"),
          sat("It runs downhill into", -118.35, 39.75, 0.7, "Carson Sink"),
          photo("Look at the Humboldt", PH_HUMBOLDT, "Humboldt River, northern Nevada"),
          m("It rises in the mountains", v(NV, routes=[HUMBOLDT_R], places=[ELKO, HSINK])),
          sat("And then it simply", -118.62, 39.98, 0.4, "Humboldt Sink", places=[HSINK])),
        P("It was not always like this. At the end of the last ice age, a lake covered more than eight thousand five hundred square miles of northwestern Nevada, nearly the size of Lake Erie and in places some nine hundred feet deep. Geologists call it Lake Lahontan. You can still see its old shorelines, cut like bathtub rings into the mountainsides. Then the climate dried, and the lake broke into pieces that shrank and disappeared. Only two real lakes are left: Pyramid Lake and Walker Lake.",
          sat(0, -118.9, 40.2, 2.6, "Where Lake Lahontan stood"),
          stat("more than eight thousand", "8,500 SQ MI", "Lake Lahontan at its peak, about 12,700 years ago", "Lake Lahontan studies (USGS and others)"),
          sat("You can still see", -119.0, 40.85, 0.7, "Black Rock Desert, an old lake floor"),
          photo("Then the climate dried", PH_BLACKROCK, "Black Rock Desert"),
          sat("Only two real lakes", -119.55, 40.0, 0.5, "Pyramid Lake", places=[PYRAMID]),
          photo("Pyramid Lake and Walker", PH_WALKER, "Walker Lake from the International Space Station (NASA)")),
        P("Without rivers that run all year, there is little to farm. Most of Nevada's land is too dry, too salty or too steep to grow a crop without water brought in from somewhere else. The valleys that are green are green because of a single stream, a spring, or a well. Everywhere else is sagebrush, and cattle need a lot of it.",
          photo(0, PH_PYRAMID, "Pyramid Lake"),
          sat("Most of Nevada's land", -117.7, 40.3, 0.8, "Salt flats north of Lovelock"),
          sat("The valleys that are", -119.2, 39.5, 0.5, "Irrigated fields near Fallon"),
          photo("Everywhere else is", PH_RANCHROAD, "Ranch country")),
    ]},
    {"title": "The Silver Ran Out", "mood": "tension", "paragraphs": [
        P("Reason three. The rush came, and then it left. In 1859, prospectors found silver and gold near what became Virginia City: the Comstock Lode. Within fifteen years Virginia City had about twenty-five thousand people, more than any city between Denver and San Francisco. Nevada became a state in 1864, in large part because of that silver. And then the ore ran thin. By 1879 the town had fewer than eleven thousand, and it kept falling.",
          paint(0, "Nevada@red", places=[place("Virginia City", -119.65, 39.31, "Virginia City", "site")]),
          photo("In 1859, prospectors", PH_VC, "Virginia City today"),
          sat("Within fifteen years", -119.65, 39.31, 0.12, "Virginia City from orbit"),
          stat("about twenty-five thousand", "25,000", "Virginia City's population by 1874", "National Park Service, Virginia City Historic District"),
          sat("And then the ore", -119.6, 39.28, 0.3, "Mine dumps on the Comstock")),
        P("The story repeated across the desert. Look at Rhyolite, near the California line. In 1904 two prospectors found quartz, in the words of the National Park Service, full of free gold. Within three years Rhyolite had electricity, a mill crushing three hundred tons of ore a day, a school for two hundred and fifty children, and a three-storey bank building that cost ninety thousand dollars. Then came the financial panic of 1907. By 1910 only six hundred and eleven people were left. The mine closed the next year.",
          sat(0, -116.83, 36.90, 0.2, "Rhyolite from orbit", places=[RHYOLITE]),
          clip("in the words of the National", "...quartz... full of free gold.", NPS_R, highlight="full of free gold"),
          photo("Within three years", PH_RHY2, "Rhyolite: what is left of the bank"),
          stat("By 1910 only six", "611", "People left in Rhyolite in 1910, three years after the boom", NPS_R),
          photo("The mine closed", PH_RHY3, "Rhyolite ghost town")),
        P("Tonopah, Goldfield, dozens of camps whose names are now just dots on a map. A mining town lives exactly as long as the ore under it. When it runs out, there is nothing else here to keep people: no farmland, no river, no port. So they leave, and the desert takes the buildings back.",
          photo(0, PH_TONOPAH_OLD, "Tonopah, about 1910s"),
          photo("Goldfield, dozens", PH_GOLDFIELD, "Goldfield today"),
          sat("A mining town lives", -117.23, 38.07, 0.25, "Tonopah", places=[TONOPAH]),
          photo("So they leave", PH_RHY1, "Rhyolite, a ghost town")),
    ]},
    {"title": "Washington Kept It", "mood": "tension", "paragraphs": [
        P("Reason four. Most of Nevada was never handed out. When the West was settled, the federal government gave away or sold land to homesteaders, railroads and states. In Nevada, few people wanted dry sagebrush, and most of it stayed with Washington. Today, by the count of Congress's own research service, about eighty percent of Nevada is federal land, the highest share of any state. Most of it is run by the Bureau of Land Management, as open range for grazing, mining and recreation.",
          paint(0, "Nevada@red"),
          photo("When the West was", PH_RANCH, "A cattle loading gate, southern Nevada"),
          sat("In Nevada, few people", -116.0, 39.6, 1.2, "Open range, central Nevada"),
          stat("about eighty percent", "80 %", "Share of Nevada owned by the federal government", CRS),
          photo("Most of it is run", PH_RANCHROAD, "Ranch country")),
        P("And some of it was set aside for something else entirely. Sixty-five miles north of Las Vegas lies the Nevada Test Site. Between 1951 and 1992, the United States set off nine hundred and twenty-eight nuclear tests here, a hundred in the open air and the rest underground. The US Geological Survey calls Yucca Flat the most cratered landscape on Earth. From orbit it looks like the Moon.",
          m(0, v({"lon": -115.6, "lat": 36.6, "span": 3.0}, places=[VEGAS, SEDAN])),
          stat("nine hundred and twenty-eight", "928", "Nuclear tests at the Nevada Test Site, 1951-1992", NNSS),
          sat("The US Geological Survey", -116.05, 37.08, 0.18, "Yucca Flat"),
          clip("calls Yucca Flat", "The most cratered landscape on Earth.", USGS, highlight="most cratered"),
          sat("From orbit it looks", -116.03, 37.05, 0.07, "Subsidence craters, Yucca Flat")),
        P("The biggest hole is this one. On the sixth of July 1962, a hundred-and-four-kiloton device buried under the desert was set off as a test of using bombs to dig canals and harbors. It left the Sedan crater: twelve hundred and eighty feet across and three hundred and twenty feet deep. Land like this will not be settled. Neither will the ranges and bombing grounds around it. Together, the military holds millions of acres of southern Nevada.",
          sat(0, -116.046, 37.177, 0.05, "Sedan crater", places=[SEDAN]),
          stat("twelve hundred and eighty", "1,280 FT", "Width of the Sedan crater (320 ft deep), 6 July 1962", USGS),
          sat("Land like this will", -116.12, 37.2, 0.3, "The north end of Yucca Flat"),
          m("Together, the military", v({"lon": -115.9, "lat": 37.2, "span": 2.4}, places=[SEDAN, VEGAS]))),
    ]},
    {"title": "Who Does Live There", "mood": "curious", "paragraphs": [
        P("So who does live in Nevada? Mostly, people who brought their water with them. Las Vegas sits in one of the driest valleys in the country. It exists because of Hoover Dam and Lake Mead, the reservoir behind it on the Colorado River. By the local water authority's own figure, about ninety percent of southern Nevada's water comes from the Colorado. Look at the white ring around Lake Mead. That is how far the water has dropped.",
          paint(0, CLARK, view=NV, places=[VEGAS]),
          photo("Mostly, people who", PH_VEGAS2, "The Las Vegas Strip at dusk"),
          photo("It exists because", PH_HOOVER, "Hoover Dam"),
          stat("about ninety percent", "90 %", "Share of southern Nevada's water from the Colorado River", SNWA),
          sat("Look at the white", -114.45, 36.13, 0.25, "Lake Mead's bathtub ring")),
        P("Reno and Carson City do the same in the north, on the Truckee and Carson rivers that run down from the Sierra snow. And in the northeast, around Elko, the desert pays in a different way: gold. Nevada mines most of the gold produced in the United States, from deep pits along a belt called the Carlin Trend. The pits employ thousands, but many workers drive in and out, and the towns stay small.",
          photo(0, PH_RENO, "Reno"),
          sat("on the Truckee and", -119.78, 39.52, 0.35, "Reno and the Truckee River", places=[RENO]),
          sat("And in the northeast", -116.37, 40.98, 0.25, "Gold mines on the Carlin Trend"),
          photo("Nevada mines most", PH_GOLDORE, "Carlin-type gold ore"),
          sat("The pits employ thousands", -115.76, 40.83, 0.3, "Elko", places=[ELKO])),
        P("And long before any of them, the Great Basin had people. The Northern Paiute, the Washoe and the Western Shoshone lived across this land for thousands of years, moving with the seasons between the lakes, the piñon pine hills and the valleys. They lived with the desert's limits instead of fighting them. That may be the real lesson of Nevada.",
          photo(0, PH_PAIUTE, "Paiute women, historical photograph"),
          sat("moving with the seasons", -119.55, 40.05, 0.9, "Pyramid Lake, Paiute land"),
          photo("They lived with", PH_GBNP2, "Great Basin National Park"),
          paint("That may be the real", "Nevada@red", places=[VEGAS, RENO])),
    ]},
    {"title": "The Empty Middle", "mood": "calm", "paragraphs": [
        P("So put it together. Mountains that take the rain. Rivers that end in the sand. A lake that dried up. Silver and gold that ran out. And a federal landlord holding four fifths of the state. Nevada is not empty by accident. Its people live where the water is, and the water is almost nowhere.",
          m(0, v(NV, layer="night")),
          paint("Mountains that take", SIERRA + "@alt", view=WEST),
          sat("Rivers that end", -118.62, 39.98, 0.6, "Humboldt Sink"),
          photo("Silver and gold that", PH_RHY3, "Rhyolite ghost town"),
          paint("And a federal landlord", "Nevada@red"),
          photo("Nevada is not empty", PH_US50, "US Route 50, 'the loneliest road in America'")),
        P("Here is my question for you. If you could live anywhere in Nevada, would you pick the lights of Las Vegas, or a ranch at the end of a hundred-mile dirt road?",
          paint(0, "Nevada@red", places=[VEGAS, RENO]),
          photo("would you pick", PH_VEGAS, "Las Vegas from the air"),
          photo("or a ranch at", PH_RANCHROAD, "Ranch country"),
          ask=("would you pick", "Las Vegas, or the empty middle?")),
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
    "title": "Why Almost Nobody Lives in Most of Nevada",
    "voice": "am_michael",
    "voice_speed": 1.15,
    "music": "procedural",
    "map_style": "satellite",
    "look": "none",
    "sources": ["episodes/nevada-empty/research.md and factcheck.md", "Contains modified Copernicus Sentinel data 2026"],
    "thumbnail": {"text": "WHY SO EMPTY"},
    "chapters": chapters,
    "youtube": {
        "title": "Why Almost Nobody Lives in Most of Nevada",
        "description": "Nevada is bigger than Great Britain, yet almost nine in ten Nevadans live in just two counties, around Las Vegas and Reno. This video goes through the five reasons the rest stayed empty: the Sierra Nevada rain shadow that makes Nevada the driest state, a Great Basin whose rivers never reach the sea, the silver and gold rushes that came and went, a federal government that still owns about 80 % of the land, including the Nevada Test Site, and the few places where people found water.",
        "tags": ["Nevada", "why nobody lives in Nevada", "Great Basin", "Sierra Nevada", "rain shadow", "Rhyolite ghost town", "Comstock Lode", "Nevada Test Site", "Sedan crater", "Lake Lahontan", "Las Vegas", "geography", "satellite images"],
        "pinned_comment": "If you could live anywhere in Nevada, would you pick the lights of Las Vegas, or a ranch at the end of a hundred-mile dirt road?",
    },
}
out = HERE / "script.json"
out.write_text(json.dumps(script, ensure_ascii=False, indent=1) + chr(10), encoding="utf-8")
words = sum(len(p["text"].split()) for c in chapters for p in c["paragraphs"])
shots = [s for c in chapters for p in c["paragraphs"] for s in p["shots"]]
kinds = {k: sum(1 for s in shots if s["type"] == k) for k in ("map", "photo", "stat", "document", "chart")}
print(f"{words} words, {len(chapters)} chapters, {len(shots)} shots {kinds}")
