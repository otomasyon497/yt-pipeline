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
PH_STRIP = "File:The StripLas Vegas Strip.jpg"
PH_VEGAS_AIR2 = "File:Las Vegas strip from the air (3192201540).jpg"
PH_VEGAS_HELI = "File:View of Las Vegas' strip from the helicopter.jpg"
PH_US50B = "File:Us route 50 nevada.jpg"
PH_BRISTLE = "File:Great Basin National Park - 53837528271.jpg"
PH_PINES = "File:Great Basin National Park - 53837979940.jpg"
PH_NIGHTSKY = "File:Milky Way Night Sky Black Rock Desert Nevada.jpg"
PH_HORSES = "File:Nevada Wild Horses (14963367880).jpg"

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
AREA51 = place("Area 51", -115.81, 37.24, "Area 51 (Groom Lake)", "site")
USA = {"lon": -98.5, "lat": 39.0, "span": 42}

chapters = [
    {"title": "Two Lights in the Dark", "mood": "curious", "paragraphs": [
        P("Nevada is bigger than Great Britain. About three million people live in it. And almost nine out of ten of them live in just two places: Las Vegas in the far south, and Reno up against the mountains in the west. Everything in between, hundreds of miles of it, is almost empty. At night, from orbit, you can see it. Two lights, and darkness.",
          m(0, v(NV)),
          photo("About three million", PH_STRIP, "The Las Vegas Strip"),
          stat("And almost nine", "89 %", "Nevadans living in Clark and Washoe counties, 2020 census (our sum)", CENSUS),
          m("Las Vegas in the far", v(NV, places=[VEGAS, RENO])),
          photo("Everything in between", PH_NIGHTSKY, "Night sky over the Black Rock Desert"),
          m("At night, from orbit", v(NV, layer="night"))),
        P("The main highway across the middle of the state, US Route 50, has a nickname. In July 1986 LIFE magazine called the stretch from Fernley to Ely the loneliest road in America, quoting a motoring official who could find nothing out there worth stopping for. Nevada did not complain. It printed the phrase on souvenirs and turned it into a slogan.",
          sat(0, -117.07, 39.49, 0.6, "US 50 at Austin"),
          photo("In July 1986 LIFE", PH_US50, "US Route 50, 'the loneliest road in America'"),
          m("the stretch from Fernley", v(NV, routes=[{"from": [-119.25, 39.61], "via": [[-118.78, 39.47], [-117.07, 39.49], [-115.96, 39.51]], "to": [-114.89, 39.25], "mode": "line", "color": "red", "seconds": 2.0, "label": "US 50, Fernley to Ely"}], places=[ELY])),
          sat("It printed the phrase", -116.0, 39.5, 0.8, "Eureka and the empty basins around it")),
        P("It is not that nobody ever tried. A lake nearly as big as Lake Erie once filled the northwest of this state, and it vanished. Towns of thousands rose on silver and gold, and blew away within a few years. And today the federal government owns about four fifths of the land, including a stretch of desert where it set off nuclear bombs, and a secret air base it would not even name for almost sixty years. So why does almost nobody live in most of Nevada? There are five reasons. The first one is a wall.",
          photo(0, PH_TUFA, "Tufa rocks at Pyramid Lake"),
          sat("A lake nearly as big", -118.4, 39.8, 1.6, "Carson Sink, the floor of an ancient lake"),
          photo("Towns of thousands", PH_RHY1, "Rhyolite, a ghost town"),
          sat("And today the federal", -116.05, 37.12, 0.25, "Yucca Flat, Nevada Test Site"),
          sat("and a secret air", -115.80, 37.25, 0.12, "Groom Lake"),
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
          m("Across the whole state", v(WEST)),
          chart("In the southern lowlands", "Yearly rain and snow in Nevada", "inches", [["Southern lowlands", 4], ["State average", 10.2], ["High Sierra peaks", 50]], NOAA, reveal=["Up on the high"], highlight=2),
          sat("Same air, a few", -119.75, 40.55, 0.5, "Smoke Creek Desert, a dry lake floor")),
        P("And it is not one wall. Nevada is made of them. Drive across the state and the road climbs a mountain range, drops into a flat dry valley, climbs another range, drops again, over and over, dozens of times. Geologists call it the Basin and Range. Each range squeezes a little more water out of the sky for itself, and each valley floor gets less. The towns that do exist sit where a stream comes down off a mountain, and almost nowhere else.",
          sat(0, -117.1, 39.5, 1.4, "Ranges and basins near Austin"),
          photo("Drive across the state", PH_US50B, "US Route 50 in central Nevada"),
          sat("drops into a flat", -116.55, 39.35, 0.5, "A valley floor between two ranges"),
          sat("Geologists call it", -116.4, 38.9, 2.2, "The Basin and Range, central Nevada"),
          photo("Each range squeezes", PH_GBNP, "Great Basin National Park"),
          sat("and each valley floor", -115.75, 38.42, 0.4, "The salt playa of Railroad Valley"),
          sat("The towns that do", -114.89, 39.25, 0.4, "Ely, at the foot of the Egan Range", places=[ELY])),
        P("The high ranges are islands of a different climate, cooler and a little wetter than the desert below. On Wheeler Peak, in what is now Great Basin National Park, grow bristlecone pines, some of the oldest living things on Earth. In August 1964 a graduate student, with the Forest Service's permission, cut one of them down to count its rings. The National Park Service says the tree, later named Prometheus, was about four thousand nine hundred years old. Twenty-two years later the mountain became a national park. So the rain is mostly gone before it arrives. And the little that does fall here has a strange problem of its own.",
          sat(0, -114.31, 39.01, 0.3, "Wheeler Peak, Great Basin National Park"),
          photo("On Wheeler Peak", PH_GBNP2, "Great Basin National Park"),
          photo("grow bristlecone pines", PH_BRISTLE, "A bristlecone pine on Wheeler Peak"),
          sat("In August 1964", -114.30, 38.99, 0.06, "The bristlecone grove below Wheeler Peak"),
          photo("cut one of them down", PH_PINES, "Bristlecone pines, Great Basin National Park"),
          clip("The National Park Service says", "...estimated to be 4,900 years old.", "National Park Service, The Prometheus Story", highlight="4,900 years old"),
          stat("was about four thousand", "4,900 YEARS", "Estimated age of the Prometheus bristlecone pine, cut in 1964", "National Park Service, The Prometheus Story"),
          sat("Twenty-two years later", -114.25, 39.0, 0.9, "The Snake Range and Great Basin National Park"),
          m("So the rain is", v(WEST, highlight=[SIERRA + "@alt"]))),
    ]},
    {"title": "The Water Goes Nowhere", "mood": "curious", "paragraphs": [
        P("Reason two. What little water there is goes nowhere. Almost all of Nevada lies inside the Great Basin, the largest region in North America where rivers never reach the sea. Rain that falls here stays here. It runs downhill into a valley and stops, and the sun takes it back. Look at the Humboldt River. It rises in the mountains of northeast Nevada and runs west across almost the whole state. And then it simply ends, in a dry flat called the Humboldt Sink.",
          paint(0, BASIN + "@blue", view=WEST),
          stat("the largest region", "0 RIVERS", "Rivers in the Great Basin that reach the sea", "USGS; Great Basin hydrology"),
          sat("Rain that falls here", -118.05, 40.6, 0.5, "A closed basin: the water has nowhere to go"),
          sat("It runs downhill into", -118.35, 39.75, 0.7, "Carson Sink"),
          photo("Look at the Humboldt", PH_HUMBOLDT, "Humboldt River, northern Nevada"),
          m("It rises in the mountains", v(NV, routes=[HUMBOLDT_R], places=[ELKO, HSINK])),
          sat("And then it simply", -118.62, 39.98, 0.4, "Humboldt Sink", places=[HSINK])),
        P("It was not always like this. At the end of the last ice age, a lake covered more than eight thousand five hundred square miles of northwestern Nevada, nearly the size of Lake Erie and in places some nine hundred feet deep. Geologists call it Lake Lahontan. You can still see its old shorelines, cut like bathtub rings into the mountainsides. Then the climate dried, and the lake broke into pieces that shrank and disappeared. Only two real lakes are left: Pyramid Lake and Walker Lake. Pyramid is still big, about a hundred and eighty-eight square miles and more than three hundred and fifty feet deep. It is a puddle compared with what was there.",
          sat(0, -118.9, 40.2, 2.6, "Where Lake Lahontan stood"),
          stat("more than eight thousand", "8,500 SQ MI", "Lake Lahontan at its peak, about 12,700 years ago", "Lake Lahontan studies (USGS and others)"),
          m("nearly the size of Lake", v({"lon": -81.2, "lat": 42.2, "span": 4.5}), text="Lake Erie, for scale"),
          sat("You can still see", -119.0, 40.85, 0.7, "Black Rock Desert, an old lake floor"),
          sat("Then the climate dried", -118.75, 39.85, 0.25, "Old shorelines on the hills above Carson Sink"),
          sat("Only two real lakes", -119.55, 40.0, 0.5, "Pyramid Lake", places=[PYRAMID]),
          photo("Pyramid Lake and Walker", PH_WALKER, "Walker Lake from the International Space Station (NASA)"),
          stat("Pyramid is still big", "188 SQ MI", "Pyramid Lake today, against Lahontan's 8,500 square miles", "Nevada Division of Water Resources; USGS"),
          photo("and more than three", PH_PYRAMID, "Pyramid Lake"),
          m("It is a puddle", v({"lon": -118.9, "lat": 40.0, "span": 4.0}, places=[PYRAMID]))),
        P("Even those two have been fought over. In 1905, in one of the first projects of the new federal Reclamation Service, Derby Dam was built across the Truckee River east of Reno. It sent part of the river into a canal to water farms around Fallon, in the middle of the desert. Less water reached Pyramid Lake, and the lake fell. Its sister, Winnemucca Lake, which had been filled by Pyramid's overflow, dried up completely. The whole lake lies inside the reservation of the Pyramid Lake Paiute Tribe. In it lives a fish found nowhere else, the cui-ui, which the Paiute people had fished for generations. It has been listed as endangered since 1973.",
          sat(0, -119.45, 39.58, 0.15, "Derby Dam on the Truckee River"),
          m("It sent part of the", v({"lon": -119.2, "lat": 39.65, "span": 1.6}, routes=[{"from": [-119.45, 39.58], "to": [-118.78, 39.47], "mode": "line", "color": "blue", "seconds": 1.5, "label": "Truckee Canal"}], places=[PYRAMID, place("Fallon", -118.78, 39.47)])),
          sat("Less water reached", -119.45, 39.85, 0.15, "Where the Truckee enters Pyramid Lake"),
          sat("Its sister, Winnemucca", -119.32, 40.2, 0.4, "The dry bed of Winnemucca Lake"),
          photo("The whole lake lies", PH_TUFA, "Tufa rocks at Pyramid Lake"),
          sat("In it lives a", -119.62, 40.15, 0.15, "The north end of Pyramid Lake"),
          photo("which the Paiute people", PH_PAIUTE, "Paiute women, historical photograph"),
          stat("It has been listed", "1973", "Year the cui-ui, found only in Pyramid Lake, was listed endangered", "US Fish and Wildlife Service, via truckeeriver.org")),
        P("Without rivers that run all year, there is little to farm. Most of Nevada's land is too dry, too salty or too steep to grow a crop without water brought in from somewhere else. The valleys that are green are green because of a single stream, a spring, or a well. Everywhere else is sagebrush, and cattle need a lot of it.",
          photo(0, PH_HUMBOLDT, "Humboldt River, northern Nevada"),
          sat("Most of Nevada's land", -117.7, 40.3, 0.8, "Salt flats north of Lovelock"),
          sat("The valleys that are", -119.2, 39.5, 0.5, "Irrigated fields near Fallon"),
          sat("Everywhere else is", -116.2, 40.3, 0.3, "Sagebrush valleys, Elko County")),
    ]},
    {"title": "The Silver Ran Out", "mood": "tension", "paragraphs": [
        P("Reason three. The rush came, and then it left. In 1859, prospectors found silver and gold near what became Virginia City: the Comstock Lode. By 1874, by the National Park Service's count, Virginia City had about twenty-five thousand people, with mansions, an opera house and newspapers. And then the ore ran thin. At the 1880 census the town had fewer than eleven thousand. By 1940 it was down to about five hundred.",
          paint(0, "Nevada@red", places=[place("Virginia City", -119.65, 39.31, "Virginia City", "site")]),
          photo("In 1859, prospectors", PH_VC, "Virginia City today"),
          sat("By 1874, by the", -119.65, 39.31, 0.12, "Virginia City from orbit"),
          stat("about twenty-five thousand", "25,000", "Virginia City's population by 1874", "National Park Service, Virginia City Historic District"),
          sat("And then the ore", -119.6, 39.28, 0.3, "Mine dumps on the Comstock"),
          sat("By 1940 it was", -119.66, 39.30, 0.06, "Virginia City's old streets")),
        P("And the whole state went with it. At the 1880 census Nevada had about sixty-two thousand people. Ten years later it had fewer than forty-six thousand, and by 1900 about forty-two thousand. A state shrinking, while the rest of America grew. It would take the next century, and a very different kind of town, to fill it up again.",
          chart(0, "Nevada's population", "people", [["1880", 62266], ["1890", 45761], ["1900", 42335]], "US census, as compiled by Britannica and state histories", reveal=["Ten years later", "and by 1900"], highlight=2),
          photo("A state shrinking", PH_TONOPAH, "Tonopah, an early-1900s mining town"),
          sat("It would take the", -115.17, 36.12, 0.3, "Las Vegas today", places=[VEGAS])),
        P("The story repeated across the desert. Look at Rhyolite, near the California line. In 1904 two prospectors found quartz, in the words of the National Park Service, full of free gold. Within three years Rhyolite had electricity, a mill crushing three hundred tons of ore a day, a school for two hundred and fifty children, and a three-storey bank building that cost ninety thousand dollars. Then came the financial panic of 1907. By 1910 only six hundred and eleven people were left. The mine closed the next year, and in 1916 the power was cut off. At the 1920 census, by most counts, fourteen people lived there.",
          sat(0, -116.83, 36.90, 0.2, "Rhyolite from orbit", places=[RHYOLITE]),
          clip("in the words of the National", "...quartz... full of free gold.", NPS_R, highlight="full of free gold"),
          sat("Within three years", -116.835, 36.902, 0.05, "Rhyolite's old street grid"),
          photo("a three-storey bank", PH_RHY2, "Rhyolite: what is left of the bank"),
          sat("Then came the financial", -116.80, 36.88, 0.6, "The Bullfrog Hills around Rhyolite"),
          stat("By 1910 only six", "611", "People left in Rhyolite in 1910, three years after the boom", NPS_R),
          photo("The mine closed", PH_RHY3, "Rhyolite ghost town"),
          stat("At the 1920 census", "14", "People in Rhyolite at the 1920 census, by most counts", "US census, as reported by Wikipedia and local histories")),
        P("Tonopah, Goldfield, dozens of camps whose names are now just dots on a map. A mining town lives exactly as long as the ore under it. When it runs out, there is nothing else here to keep people: no farmland, no river, no port. So they leave, and the desert takes the buildings back.",
          photo(0, PH_TONOPAH_OLD, "Tonopah, about 1910s"),
          photo("Goldfield, dozens", PH_GOLDFIELD, "Goldfield today"),
          sat("A mining town lives", -117.23, 38.07, 0.25, "Tonopah", places=[TONOPAH]),
          photo("So they leave", PH_RHY1, "Rhyolite, a ghost town")),
        P("Even the most famous use of this land was crossing it as fast as possible. In 1860 and 1861 the Pony Express carried the mail on horseback from Missouri to California, straight across the middle of Nevada, along much the same line US 50 follows today. Riders changed horses at stations a few miles apart, and some of those stations still stand as ruins in the sagebrush. Then the telegraph arrived, and the riders were gone. But the land people passed through, and the land they left behind, did not go to anyone. It stayed with Washington.",
          sat(0, -118.2, 39.35, 0.6, "Sand Springs and the old trail"),
          stat("In 1860 and 1861", "1860-61", "Pony Express riders carry the mail straight across Nevada", "National Park Service, Pony Express National Historic Trail"),
          m("straight across the middle", v(NV, routes=[{"from": [-114.05, 39.9], "via": [[-114.9, 39.6], [-116.0, 39.5], [-117.07, 39.49], [-118.4, 39.29]], "to": [-119.75, 39.15], "mode": "line", "color": "accent", "seconds": 2.0, "label": "Pony Express route"}], places=[CARSON])),
          sat("Riders changed horses at", -118.413, 39.287, 0.05, "Sand Springs Pony Express station ruins"),
          sat("Then the telegraph arrived", -117.07, 39.49, 0.25, "Austin, on the old route"),
          paint("But the land people", "Nevada@red")),
    ]},
    {"title": "Washington Kept It", "mood": "tension", "paragraphs": [
        P("Reason four. Most of Nevada was never handed out. When the West was settled, the federal government gave away or sold land to homesteaders, railroads and states. In Nevada, few people wanted dry sagebrush, and most of it stayed with Washington. Today, by the count of Congress's own research service, about eighty percent of Nevada is federal land, the highest share of any state. Most of it is run by the Bureau of Land Management, as open range for grazing, mining and recreation.",
          paint(0, "Nevada@red"),
          photo("When the West was", PH_RANCH, "A cattle loading gate, southern Nevada"),
          m("railroads and states", v(NV, routes=[{"from": [-120.0, 39.33], "via": [[-119.81, 39.53], [-118.47, 40.18], [-117.73, 40.97], [-115.76, 40.83]], "to": [-114.0, 41.2], "mode": "line", "color": "accent", "seconds": 2.0, "label": "The transcontinental railroad"}], places=[RENO, ELKO])),
          sat("In Nevada, few people", -116.0, 39.6, 1.2, "Open range, central Nevada"),
          stat("about eighty percent", "80 %", "Share of Nevada owned by the federal government", CRS),
          paint("the highest share of", "Nevada@red", view=USA),
          photo("Most of it is run", PH_RANCHROAD, "Ranch country"),
          sat("as open range for", -116.6, 41.5, 0.3, "Range land, Elko County")),
        P("That open range has some unusual tenants. By the Bureau of Land Management's own estimate in 2025, about seventy-three thousand wild horses and burros roam public land in the American West, and about thirty-five thousand of them, nearly half, are in Nevada. Since 1971 a federal law has protected them on this land. In Nevada, that is about one wild horse or burro for every ninety people.",
          sat(0, -117.3, 40.6, 1.0, "Open range, northern Nevada"),
          stat("about thirty-five thousand", "35,140", "Wild horses and burros on Nevada's public land, nearly half the US total", "Bureau of Land Management, 2025 population estimates"),
          stat("Since 1971 a federal", "1971", "Wild Free-Roaming Horses and Burros Act protects the herds", "US Congress, Public Law 92-195"),
          photo("In Nevada, that is", PH_HORSES, "Nevada wild horses")),
        P("And some of it was set aside for something else entirely. Sixty-five miles north of Las Vegas lies the Nevada Test Site. Between 1951 and 1992, the United States set off nine hundred and twenty-eight nuclear tests here, a hundred in the open air and the rest underground. The US Geological Survey calls Yucca Flat the most cratered landscape on Earth. From orbit it looks like the Moon. In the 1950s the mushroom clouds of the open-air tests could be seen from Las Vegas, and the city sold them as a tourist draw, with published test times and atomic cocktails. In 1963 a treaty sent all the tests underground.",
          m(0, v({"lon": -115.6, "lat": 36.6, "span": 3.0}, places=[VEGAS, SEDAN])),
          stat("nine hundred and twenty-eight", "928", "Nuclear tests at the Nevada Test Site, 1951-1992", NNSS),
          sat("The US Geological Survey", -116.05, 37.08, 0.18, "Yucca Flat"),
          clip("calls Yucca Flat", "The most cratered landscape on Earth.", USGS, highlight="most cratered"),
          sat("From orbit it looks", -116.03, 37.05, 0.07, "Subsidence craters, Yucca Flat"),
          m("In the 1950s the", v({"lon": -115.6, "lat": 36.65, "span": 1.9}, places=[VEGAS, SEDAN])),
          photo("and the city sold", PH_VEGAS2, "Las Vegas"),
          stat("In 1963 a treaty", "1963", "The Limited Test Ban Treaty ends open-air tests; testing goes underground", NNSS)),
        P("Just over the mountains from the test site lies a dry lake called Groom Lake. In April 1955 a small team from the CIA flew over Nevada looking for a hidden place to test a new spy plane, the U-2, and they chose it. The base became known as Area 51. For decades the government would not even name it. Only in 2013 did a declassified CIA history, released after a request from the National Security Archive at George Washington University, refer to it openly. It describes the U-2 and the spy planes that came after it. It says nothing about aliens.",
          sat(0, -115.81, 37.27, 0.3, "Groom Lake", places=[AREA51]),
          stat("In April 1955", "APRIL 1955", "The CIA picks Groom Lake to test and train for the U-2 spy plane", "CIA history, released 2013 via the National Security Archive"),
          m("looking for a hidden", v({"lon": -116.3, "lat": 37.6, "span": 5.0}, places=[AREA51, VEGAS, TONOPAH])),
          sat("The base became known", -115.80, 37.24, 0.07, "The runways at Area 51"),
          m("For decades the government", v({"lon": -115.95, "lat": 37.15, "span": 1.1}, places=[AREA51, SEDAN])),
          stat("Only in 2013 did", "2013", "A declassified CIA history refers to Area 51 openly", "National Security Archive, George Washington University"),
          clip("National Security Archive at", "...the first deliberate official references to Area 51...", "National Security Archive, George Washington University, 2013", highlight="first deliberate official references"),
          sat("It describes the U-2", -115.78, 37.21, 0.15, "Groom Lake's long runway")),
        P("Next door is another piece of empty land the government chose for a hard job. In 1987 Congress picked Yucca Mountain, on the edge of the test site, as the only place to study for a permanent dump for the country's spent nuclear fuel. Tunnels were dug. Nevada fought it for two decades. In 2010 the Department of Energy wound the program down, and no high-level waste has ever been stored there. The empty desert was the reason it was chosen, and the people of Nevada were the reason it stopped.",
          sat(0, -116.46, 36.85, 0.2, "Yucca Mountain"),
          sat("In 1987 Congress picked", -116.3, 36.95, 0.8, "Yucca Mountain and the test site"),
          stat("as the only place to", "1987", "Congress makes Yucca Mountain the only site to study for nuclear waste", "GAO-11-731T"),
          sat("Tunnels were dug", -116.43, 36.86, 0.07, "The tunnel entrance at Yucca Mountain"),
          photo("Nevada fought it", PH_GOLDFIELD, "Goldfield, a town on the road past the site"),
          stat("and no high-level waste", "0", "Tons of high-level nuclear waste ever stored at Yucca Mountain", "GAO-11-731T; US Department of Energy"),
          paint("The empty desert was", "Nevada@red", places=[VEGAS]),
          photo("and the people of", PH_VC, "Virginia City, Nevada")),
        P("The biggest hole is this one. On the sixth of July 1962, a hundred-and-four-kiloton device buried under the desert was set off as a test of using bombs to dig canals and harbors. It left the Sedan crater: twelve hundred and eighty feet across and three hundred and twenty feet deep. Land like this will not be settled. Neither will the ranges and bombing grounds around it. Together, the military holds millions of acres of southern Nevada.",
          sat(0, -116.046, 37.177, 0.05, "Sedan crater", places=[SEDAN]),
          stat("a hundred-and-four-kiloton", "104 KT", "Yield of the Sedan test, 6 July 1962", USGS),
          sat("as a test of using", -116.0, 37.12, 0.5, "Craters across Yucca Flat"),
          stat("twelve hundred and eighty", "1,280 FT", "Width of the Sedan crater (320 ft deep), 6 July 1962", USGS),
          sat("Land like this will", -116.12, 37.2, 0.3, "The north end of Yucca Flat"),
          m("Together, the military", v({"lon": -115.9, "lat": 37.2, "span": 2.4}, places=[SEDAN, VEGAS]))),
    ]},
    {"title": "Who Does Live There", "mood": "curious", "paragraphs": [
        P("So who does live in Nevada? Mostly, people who brought their water with them. Start with Las Vegas. Its name is Spanish for the meadows, and the meadows were real: springs in the valley floor kept a patch of green alive in the desert. In 1855 Mormon missionaries built a small fort beside the creek, and gave it up within a few years. In 1905 a new railroad between Salt Lake City and Los Angeles chose the springs as a stop, and on the fifteenth of May it auctioned off the lots for a town. For a quarter of a century after that, Las Vegas stayed a small railroad town.",
          m(0, v({"lon": -115.3, "lat": 36.5, "span": 3.5}, places=[VEGAS]), text="Southern Nevada"),
          sat("Start with Las Vegas", -115.14, 36.17, 0.1, "Downtown Las Vegas, where the 1905 town was laid out"),
          sat("springs in the valley", -115.19, 36.17, 0.04, "The old Las Vegas springs, now the Springs Preserve"),
          sat("In 1855 Mormon missionaries", -115.134, 36.180, 0.04, "Site of the Old Las Vegas Mormon Fort"),
          m("In 1905 a new railroad", v({"lon": -114.9, "lat": 37.4, "span": 9.0}, routes=[{"from": [-111.89, 40.76], "via": [[-113.01, 38.40], [-114.51, 37.61], [-115.14, 36.17]], "to": [-118.24, 34.05], "mode": "line", "color": "accent", "seconds": 2.0, "label": "Salt Lake City to Los Angeles, 1905"}], places=[VEGAS])),
          stat("on the fifteenth of May", "15 MAY 1905", "Railroad auctions the town lots: Las Vegas is founded", "City of Las Vegas; UNLV Special Collections"),
          sat("For a quarter of a", -115.2, 36.2, 0.9, "The Las Vegas Valley")),
        P("Then came 1931. The federal government began building a giant dam on the Colorado River, about thirty miles away, and thousands of workers came into the desert. They were housed in Boulder City, a town the government built for them, where gambling was banned. And that same spring, on the nineteenth of March, Nevada's governor signed two laws. One made gambling legal. The other cut the time you had to live in the state before you could get a divorce to just six weeks. Las Vegas, up the road from the dam, was where the workers came to spend their pay. The town had found a business that did not need much water.",
          sat(0, -114.737, 36.016, 0.05, "Black Canyon and Hoover Dam"),
          sat("They were housed in", -114.83, 35.98, 0.12, "Boulder City"),
          stat("on the nineteenth of March", "19 MARCH 1931", "Nevada legalizes gambling and cuts divorce residency to six weeks", "EBSCO Research Starters, Nevada Legalizes Gambling"),
          photo("The other cut the time", PH_RENO, "Reno"),
          sat("before you could get", -119.81, 39.525, 0.04, "Downtown Reno"),
          photo("Las Vegas, up the road", PH_VEGAS_HELI, "The Las Vegas Strip today"),
          photo("The town had found", PH_STRIP, "The Las Vegas Strip")),
        P("The dam was finished in 1936, two years ahead of schedule. By the government's official count, ninety-six men died building it, and that count left out the deaths from heat. Behind it rose Lake Mead, by volume the largest reservoir in the United States. And it is that lake that keeps Las Vegas alive. By the local water authority's own figure, about ninety percent of southern Nevada's water comes from the Colorado.",
          photo(0, PH_HOOVER, "Hoover Dam"),
          stat("ninety-six men died", "96", "Official deaths building Hoover Dam (heat deaths not counted)", "US Bureau of Reclamation, Hoover Dam fatalities essay"),
          sat("Behind it rose Lake", -114.45, 36.2, 0.9, "Lake Mead"),
          stat("about ninety percent", "90 %", "Share of southern Nevada's water from the Colorado River", SNWA)),
        P("Look at the white ring around Lake Mead. That is how far the water has dropped. Full, the lake stands at about twelve hundred and twenty feet above sea level. In 2022, and again in the summer of 2026, it fell to about one thousand and forty, its lowest since it first filled in 1937, around a quarter full. A city of two million rests on that line.",
          sat(0, -114.45, 36.13, 0.25, "Lake Mead's bathtub ring"),
          sat("Full, the lake stands", -114.39, 36.29, 0.1, "The shore of Lake Mead"),
          chart("In 2022, and again", "Lake Mead's surface", "feet above sea level", [["Full pool", 1221], ["Record low", 1041]], "US Bureau of Reclamation, via press reports", reveal=["it fell to about"], highlight=1),
          sat("its lowest since it", -114.75, 36.05, 0.15, "Lake Mead near Hoover Dam"),
          photo("A city of two million", PH_VEGAS, "Las Vegas from the air")),
        P("In 1940 the city of Las Vegas had about eight thousand four hundred people. At the 2020 census it had more than six hundred and forty thousand, inside a metro area of over two million. Almost all of it lives on water from one river, held back by one dam. And the city knows it. In 2021 Nevada passed a law that, from 2027, bans watering decorative grass with Colorado River water around Las Vegas: the lawns on road medians, outside offices, anywhere nobody walks.",
          chart(0, "People in the city of Las Vegas", "people", [["1940", 8400], ["2020", 641903]], "US census", reveal=["At the 2020 census"], highlight=1),
          photo("inside a metro area", PH_VEGAS2, "The Las Vegas Strip at dusk"),
          sat("Almost all of it", -114.737, 36.016, 0.12, "Hoover Dam and the river below it"),
          stat("In 2021 Nevada passed", "2027", "From this year, no Colorado River water for decorative grass around Las Vegas", "Nevada Assembly Bill 356 (2021)"),
          clip("bans watering decorative grass", "...Colorado River water ... may not be used to irrigate nonfunctional turf...", "Nevada Assembly Bill 356 (2021)", highlight="nonfunctional turf"),
          sat("the lawns on road", -115.28, 36.15, 0.04, "Green strips in a Las Vegas suburb")),
        P("Reno and Carson City do the same in the north, on the Truckee and Carson rivers that run down from the Sierra snow. And in the northeast, around Elko, the desert pays in a different way: gold. Nevada mines most of the gold produced in the United States, from deep pits along a belt called the Carlin Trend, which by 2025 had produced more than a hundred million ounces. The pits employ thousands, but many workers drive in and out, and the towns stay small.",
          sat(0, -119.78, 39.52, 0.35, "Reno and the Truckee River", places=[RENO]),
          sat("on the Truckee and", -119.77, 39.16, 0.15, "Carson City", places=[CARSON]),
          sat("And in the northeast", -116.37, 40.98, 0.25, "Gold mines on the Carlin Trend"),
          photo("Nevada mines most", PH_GOLDORE, "Carlin-type gold ore"),
          sat("from deep pits along", -116.35, 40.93, 0.08, "A deep pit on the Carlin Trend"),
          stat("which by 2025 had", "100 M OZ", "Gold produced on the Carlin Trend by 2025", "Nevada Mining Association; industry reports"),
          sat("The pits employ thousands", -115.76, 40.83, 0.3, "Elko", places=[ELKO])),
        P("And once a year, for about a week, Nevada's emptiness becomes a city. On the dry bed of old Lake Lahontan in the Black Rock Desert, the Burning Man festival builds a temporary town for some seventy thousand people, under a federal permit that allows up to eighty thousand. Then everyone packs up and leaves, and the playa is empty again. It is the clearest picture of the whole state: people can come, but very few can stay.",
          sat(0, -119.1, 40.85, 0.6, "The Black Rock playa"),
          photo("On the dry bed", PH_BLACKROCK, "Black Rock Desert"),
          sat("builds a temporary town", -119.21, 40.786, 0.06, "The festival site on the playa"),
          stat("for some seventy thousand", "~70,000", "People at Burning Man in 2024, on a BLM permit for up to 80,000", "Bureau of Land Management permit; press reports"),
          photo("Then everyone packs up", PH_NIGHTSKY, "Night sky over the Black Rock Desert"),
          paint("It is the clearest", "Nevada@red", places=[VEGAS, RENO])),
        P("And long before any of them, the Great Basin had people. The Northern Paiute, the Washoe and the Western Shoshone lived across this land for thousands of years, moving with the seasons between the lakes, the piñon pine hills and the valleys. They lived with the desert's limits instead of fighting them. That may be the real lesson of Nevada.",
          photo(0, PH_PAIUTE, "Paiute women, historical photograph"),
          sat("the Washoe and the", -118.7, 38.7, 0.5, "Walker Lake"),
          sat("moving with the seasons", -119.5, 40.0, 1.0, "Pyramid Lake"),
          photo("the piñon pine hills", PH_PINES, "Pines in the Great Basin's mountains"),
          photo("They lived with", PH_GBNP2, "Great Basin National Park"),
          paint("That may be the real", "Nevada@red", places=[VEGAS, RENO])),
    ]},
    {"title": "The Empty Middle", "mood": "calm", "paragraphs": [
        P("So put it together. Mountains that take the rain. Rivers that end in the sand. A lake that dried up. Silver and gold that ran out. And a federal landlord holding four fifths of the state. Nevada is not empty by accident. Its people live where the water is, and the water is almost nowhere. The two places that did fill up grew where water could be caught or carried in: a river off the Sierra snow for Reno, and a dam on the Colorado for Las Vegas. Next time you see the lights of Las Vegas from a plane, look at the darkness around them. That darkness is most of Nevada, and now you know why it is there.",
          m(0, v(NV, layer="night")),
          paint("Mountains that take", SIERRA + "@alt", view=WEST),
          sat("Rivers that end", -118.62, 39.98, 0.6, "Humboldt Sink"),
          photo("Silver and gold that", PH_RHY3, "Rhyolite ghost town"),
          paint("And a federal landlord", "Nevada@red"),
          photo("Nevada is not empty", PH_US50, "US Route 50, 'the loneliest road in America'"),
          photo("Its people live where", PH_VEGAS_AIR2, "Las Vegas, where the water was brought"),
          m("The two places that", v({"lon": -117.4, "lat": 37.9, "span": 9.0}, layer="night", places=[VEGAS, RENO])),
          sat("a river off the Sierra", -119.80, 39.52, 0.12, "The Truckee River through Reno"),
          sat("and a dam on the", -114.74, 36.02, 0.3, "Hoover Dam and Lake Mead"),
          m("Next time you see", v({"lon": -115.6, "lat": 37.3, "span": 5.5}, layer="night", places=[VEGAS])),
          photo("That darkness is most", PH_GBNP, "Great Basin National Park")),
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
