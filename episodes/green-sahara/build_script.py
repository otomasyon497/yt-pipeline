"""Builds script.json for green-sahara.  python build_script.py

Same production logic as episodes/mediterranean-dried (hand-placed shots, painted regions, a photo or map frame at most
twice). Sources: research.md. Regions: geo/make_regions.py.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent.parent / "pipeline"))
from schema import Paragraph  # noqa: E402


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


def sat(at, lon, lat, span, label=None, **kw):
    """One close satellite view (Sentinel-2, the clearest recent day) of a named spot."""
    return m(at, v(near(lon, lat, span), **kw), text=label)


def paint(at, *names, view=None, **kw):
    view = view or SAH
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




WIN = "2024-01-10/2024-03-01"
SPR = "2024-03-10/2024-04-30"  # Sicily is green in spring; summer views read as flat beige

SAH = {"lon": 12.0, "lat": 21.0, "span": 56}
AFR = {"lon": 15.0, "lat": 10.0, "span": 85}
CHADV = {"lon": 16.5, "lat": 15.0, "span": 14}
EASTS = {"lon": 27.0, "lat": 22.0, "span": 20}
SUM = "2024-07-01/2024-08-31"
AUT = "2023-10-01/2023-11-15"
WIN = "2024-01-10/2024-03-01"
LAKE = "file:megachad.geojson@blue"
DESERT = "file:sahara.geojson@accent"

AHP = "deMenocal et al. 2000; Shanahan et al. 2015"
ARM = "Armstrong et al., Nature Communications 2023"
KK = "Kuper & Kröpelin, Science 2006"
YU = "Yu et al., Geophysical Research Letters 2015"
MEGA = "Bouchette et al., Quaternary Research 2010; and others"
GOB = "Sereno et al., PLoS ONE 2008"

PH_BODELE = "File:Dust storms from Bodélé Depression, Chad (MODIS 2017-12-29).jpg"
PH_ENNEDI = "File:The Ennedi Massif in Northern Chad (iss072e404551).jpg"
PH_ARCHEI = "File:Tchad Grottes d'Archéi.jpg"
PH_CHEBBI = "File:Erg chebbi sunrise.jpg"
PH_BOSUM = "File:Lake Bosumtwi, Ghana.jpg"
PH_BOSUM2 = "File:Lake Bosumtwi Panorama.jpg"
PH_CHAD_STS = "File:Lake Chad by STS-66.jpg"
PH_DUNE = "File:Sand dune in the desert, Sahara Desert, Egypt.jpg"
PH_WDESERT = "File:Western Desert, Sahara Desert, Egypt.jpg"
PH_DAKHLA = "File:Sand dunes in the desert, Sahara Desert, Dakhla Oasis, Egypt.jpg"
PH_ISS_ALG2 = "File:ISS-66 Sahara Desert, Algeria (2).jpg"
PH_ISS_MALI = "File:ISS-56 Sahara, Mali.jpg"
PH_OUNIANGA = "File:ISS-64 Sahara Desert, Ounianga, Chad.jpg"
PH_ISS_ALG = "File:ISS-64 Sahara Desert, Algeria.jpg"
PH_DUST_ATL = "File:Saharan Dust over the Atlantic (MODIS).jpg"
PH_DUST_CAR = "File:Saharan Dust over the Caribbean and South America (MODIS 2022-06-09).jpg"
PH_CENTRAL = "File:Central sahara lrg.jpg"
PH_TASSILI_ART = "File:Cave painting from the Tassili n'Ajjer mountains.jpg"
PH_TASSILI = "File:Tassili Desert Algeria.jpg"
PH_TASSILI_ISS = "File:ISS-64 Tassili N'Ajjer National Park, Illizi, Algeria.jpg"
PH_TIBESTI = "File:The Tibesti Mountains in the Sahara (iss073e0906087).jpg"
PH_NILE_NIGHT = "File:Egypt’s Nile River stretches from Luxor to Cairo (iss073e0422271).jpg"
PH_LIBYA = "File:Human Fingerprints on an Ancient Landscape (153611 - libya plateau oli2 20241117 lrg).jpg"

CHAD = place("Lake Chad", 14.2, 13.2, "Lake Chad", "site")
BODELE = place("Bodélé Depression", 17.6, 16.9, "Bodélé Depression", "site")
GOBERO = place("Gobero", 9.4, 16.8, "Gobero", "site")
GILF = place("Gilf Kebir", 25.8, 23.4, "Gilf Kebir", "site")
TASSILI = place("Tassili n'Ajjer", 8.5, 25.0, "Tassili n'Ajjer", "site")
CAIRO, ASWAN = place("Cairo", 31.24, 30.04), place("Aswan", 32.9, 24.09)
BOSUM = place("Lake Bosumtwi", -1.41, 6.5, "Lake Bosumtwi", "site")
CORE = place("Mauritania core", -18.6, 20.75, "Sea-floor core off Mauritania", "site")
OWEINAT = place("East Oweinat", 28.6, 22.6, "East Oweinat farms", "site")
HOWAR = {"from": [22.8, 15.8], "via": [[25.0, 16.6], [27.5, 17.2], [29.5, 17.8]], "to": [31.8, 18.4], "mode": "line", "color": "blue", "seconds": 2.0, "label": "Wadi Howar, the 'Yellow Nile' (approximate)"}
MONSOON = [{"from": [-2.0, 4.0], "to": [2.0, 19.0], "mode": "line", "color": "accent", "seconds": 1.6, "label": "Monsoon rains push north"},
           {"from": [10.0, 4.0], "to": [14.0, 20.0], "mode": "line", "color": "accent", "seconds": 1.6}]
MONSOON_NOW = [{"from": [-2.0, 4.0], "to": [-0.5, 12.0], "mode": "line", "color": "accent", "seconds": 1.4, "label": "Today the rains stop near the Sahel"},
               {"from": [10.0, 4.0], "to": [11.0, 12.0], "mode": "line", "color": "accent", "seconds": 1.4}]
TO_NILE = [{"from": [26.0, 23.0], "to": [31.0, 25.5], "mode": "line", "color": "red", "seconds": 1.5, "label": "People move to the Nile"},
           {"from": [27.0, 18.0], "to": [32.5, 22.0], "mode": "line", "color": "red", "seconds": 1.5}]
DUST = {"from": [17.6, 16.9], "via": [[0.0, 17.0], [-30.0, 12.0]], "to": [-58.0, -2.0], "mode": "air", "color": "accent", "seconds": 2.2, "label": "Dust to the Amazon"}

ARCHEI = place("Guelta d'Archei", 21.85, 16.9, "Guelta d'Archei", "site")
OUNIANGA = place("Ounianga", 20.5, 19.05, "Ounianga lakes", "site")
TIBESTI = place("Emi Koussi", 18.55, 19.79, "Emi Koussi, 3,415 m", "site")

chapters = [
    {"title": "A Desert That Was Not", "mood": "curious", "paragraphs": [
        P("The Sahara is the largest hot desert on Earth. It covers about nine million square kilometers, almost the size of the United States, and in many places it gets less rain in a year than London gets in a week. From orbit it looks like a single orange sea of sand and rock.",
          m(0, v(AFR, highlight=[DESERT])),
          stat("It covers about nine", "~9.2 M KM²", "Area of the Sahara, the largest hot desert", "Wikipedia, Sahara"),
          m("almost the size of", v(SAH, highlight=[DESERT, "United States of America@neutral"])),
          photo("in many places it", PH_DUNE, "Dunes in Egypt's Western Desert"),
          photo("From orbit it looks", PH_ISS_ALG2, "The Sahara in Algeria, from the space station")),
        P("In fact only about a quarter of it is sand. The rest is gravel plains, bare rock plateaus and mountains. In the Tibesti, in northern Chad, the volcano Emi Koussi rises to three thousand four hundred and fifteen meters, the highest point in the Sahara.",
          sat(0, 12.5, 21.0, 1.6, "Sand seas of the central Sahara"),
          sat("The rest is gravel", 25.8, 21.2, 0.8, "Gravel plains of the eastern Sahara"),
          m("In the Tibesti, in", v({"lon": 18.0, "lat": 20.5, "span": 9}, places=[TIBESTI])),
          sat("the volcano Emi Koussi", 18.55, 19.79, 0.35, "Emi Koussi, Tibesti, Chad")),
        P("But about ten thousand years ago, this was not a desert. There were lakes here, some of them enormous. There were rivers, grassland and trees. Hippos and crocodiles lived in the middle of what is now sand. People fished with bone harpoons, herded cattle and painted the animals they saw on the rocks. One of those lakes was about the size of the Caspian Sea.",
          sat(0, 18.5, 19.05, 0.4, "The Ounianga lakes, northern Chad"),
          m("There were lakes here", v(SAH, highlight=[LAKE], places=[CHAD])),
          photo("There were rivers, grassland", PH_LIBYA, "Dry river channels on a Libyan plateau"),
          photo("Hippos and crocodiles lived", PH_ARCHEI, "Rock art at Archei, Ennedi, Chad"),
          photo("People fished with bone", PH_TASSILI_ART, "Cattle painting, Tassili n'Ajjer, Algeria"),
          m("One of those lakes", v(CHADV, highlight=[LAKE], places=[CHAD]))),
        P("So what happened? How does a land of lakes turn into the biggest hot desert on the planet, and why did it happen so fast? The answer has to do with a slow wobble of the whole Earth. And what the green Sahara left behind is still feeding a rainforest on the other side of the Atlantic today.",
          photo(0, PH_CHEBBI, "Erg Chebbi dunes at sunrise, Morocco"),
          m("How does a land", v(AFR, highlight=[DESERT, LAKE])),
          sat("and why did it", 11.0, 24.5, 1.2, "The Tassili and the Erg of central Algeria"),
          m("The answer has to", v({"lon": 0.0, "lat": 15.0, "span": 120})),
          m("And what the green", v({"lon": -25.0, "lat": 5.0, "span": 90}, routes=[DUST])),
          ask=("So what happened?", "Why did the Sahara turn to desert?")),
    ]},
    {"title": "Clues in the Rocks", "mood": "curious", "paragraphs": [
        P("The first clues were painted on the rocks. In October 1933 a Hungarian explorer, László Almásy, found a rock shelter at the Gilf Kebir, a remote plateau in southwestern Egypt. On its walls were small human figures with their arms and legs spread, as if swimming. He called it the Cave of Swimmers. Decades later, Almásy and his cave inspired the novel and the film The English Patient.",
          m(0, v(EASTS, places=[GILF])),
          stat("In October 1933 a", "1933", "László Almásy finds the Cave of Swimmers, Gilf Kebir", "Wikipedia, Cave of Swimmers"),
          sat("found a rock shelter", 25.9, 23.4, 0.9, "The Gilf Kebir plateau"),
          sat("a remote plateau in", 25.6, 23.0, 0.25, "Cliffs and wadis of the Gilf Kebir"),
          photo("On its walls were", PH_WDESERT, "Egypt's Western Desert today"),
          sat("He called it the", 25.4, 23.1, 0.08, "A wadi in the Gilf Kebir"),
          stat("Decades later, Almásy and", "1992 · 1996", "The English Patient: novel by Michael Ondaatje, then the film", "General")),
        P("Almásy believed the swimmers were real: that people had once swum in water here, in one of the driest places on Earth. Not everyone agrees on what the figures mean. But the paintings, thousands of years old, are only one site among many. In 2002 a small expedition found a second shelter a few kilometers away, now called the Cave of Beasts. Its walls hold thousands of painted figures: people, cattle, giraffes, ostriches, and strange headless creatures that gave the cave its name.",
          sat(0, 26.1, 23.6, 0.4, "The Gilf Kebir, now among the driest places on Earth"),
          stat("in one of the", "6,000-9,000 YEARS", "Estimated age of the Cave of Swimmers paintings (estimates vary)", "Wikipedia, Cave of Swimmers"),
          photo("Not everyone agrees on", PH_DAKHLA, "Dunes near Dakhla Oasis, Egypt"),
          m("are only one site", v(SAH, places=[GILF, TASSILI, GOBERO])),
          stat("In 2002 a small", "2002", "An Egyptian-Italian party finds the Cave of Beasts, Wadi Sura", "Wikipedia, Cave of Beasts; University of Cologne"),
          sat("now called the Cave", 25.3, 23.05, 0.15, "Wadi Sura, Gilf Kebir"),
          stat("Its walls hold thousands", "5,000-8,000", "Painted figures in the Cave of Beasts (counts vary)", "Wikipedia; University of Cologne"),
          sat("and strange headless creatures", 25.5, 23.2, 0.5, "The southwestern Gilf Kebir")),
        P("Far to the west, on the Tassili n'Ajjer plateau in Algeria, there are more than fifteen thousand rock paintings and engravings, spread over about seventy-two thousand square kilometers. They were made over thousands of years. The oldest show wild animals: elephants, giraffes, rhinos and hippos. Later ones show herds of cattle, with people milking and driving them. Last come horses, and finally camels. You can read the drying of the Sahara on these walls, animal by animal.",
          m(0, v({"lon": 8.5, "lat": 25.5, "span": 10}, places=[TASSILI])),
          stat("there are more than", "15,000+", "Rock paintings and engravings at Tassili n'Ajjer (UNESCO)", "UNESCO World Heritage"),
          photo("spread over about seventy-two", PH_TASSILI_ISS, "Tassili n'Ajjer from the space station"),
          photo("They were made over", PH_TASSILI, "Sandstone towers of the Tassili"),
          stat("The oldest show wild", "WILD ANIMALS", "The oldest Saharan rock art: elephants, giraffes, rhinos, hippos", "UNESCO; Penn State Earth 105"),
          photo("Later ones show herds", PH_TASSILI_ART, "Herders and cattle, Tassili n'Ajjer"),
          sat("Last come horses, and", 8.7, 24.6, 0.2, "Tassili n'Ajjer from orbit", date=WIN),
          stat("You can read the", "WILD → CATTLE → CAMEL", "The order of animals on the Tassili walls", "UNESCO World Heritage")),
        P("Some of those animals never quite left. In the Ennedi mountains of Chad, at a gorge called the Guelta d'Archei, there is a pool that holds water all year. Camels come to drink there. And in that pool live a handful of crocodiles, perhaps fewer than ten. They have been cut off from every other crocodile for thousands of years, ever since the rivers that once linked the Ennedi to the rest of Africa dried up.",
          photo(0, PH_ENNEDI, "The Ennedi massif, Chad, from the space station"),
          m("In the Ennedi mountains", v({"lon": 21.5, "lat": 17.0, "span": 6}, places=[ARCHEI])),
          sat("there is a pool", 21.85, 16.9, 0.05, "The Guelta d'Archei gorge"),
          photo("Camels come to drink", PH_ARCHEI, "Cattle painted on the rock at Archei"),
          stat("And in that pool", "~7-10", "Crocodiles left at the Guelta d'Archei", "IUCN World Heritage Outlook; George 1999"),
          sat("They have been cut", 21.7, 16.95, 0.3, "Canyons of the Ennedi around Archei")),
        P("Then there are the bones. In the year 2000 a team led by the paleontologist Paul Sereno was looking for dinosaurs in the Ténéré desert of Niger. Instead they found a graveyard. At a place called Gobero, on the shore of a lake that has long since vanished, they excavated about two hundred human burials. Around the graves lay the bones of animals the people had eaten: hippos, crocodiles, turtles and big fish.",
          m(0, v({"lon": 9.0, "lat": 17.5, "span": 12}, places=[GOBERO])),
          stat("In the year 2000", "2000", "Paul Sereno's team finds the Gobero graveyard, Niger", "University of Chicago"),
          sat("was looking for dinosaurs", 9.5, 17.2, 0.7, "The Ténéré desert, Niger"),
          sat("Instead they found a", 9.4, 16.8, 0.15, "The Ténéré near Gobero"),
          stat("they excavated about two", "~200", "Burials excavated at Gobero, 2005-2006", GOB),
          sat("Around the graves lay", 9.2, 17.0, 0.2, "Dunes over the old Gobero shore"),
          stat("hippos, crocodiles, turtles and", "HIPPO · CROCODILE", "Animal bones found at Gobero", GOB)),

        P("The first people buried there were hunters and fishers. They were tall and strongly built, and they were buried with harpoons and fishhooks made of bone. Next to them lay the bones of Nile perch, fish up to almost two meters long. Later came a different people, who also fished but kept cattle. One grave held a woman lying with two small children, their arms reaching toward each other.",
          sat(0, 9.3, 16.9, 0.35, "Dry ground of the former Gobero lake"),
          stat("They were tall and", "~9,700 YEARS AGO", "The first fishers settle at Gobero", "University of Chicago, Gobero"),
          stat("Next to them lay", "NILE PERCH", "Fish up to almost two meters long, found with the Gobero burials", GOB),
          sat("Later came a different", 9.0, 17.6, 0.5, "The Ténéré today", date=AUT),
          sat("One grave held a", 9.6, 16.6, 0.25, "Dunes of the southern Ténéré"),
          stat("their arms reaching toward", "3", "A woman buried with two children, Gobero", GOB)),
        P("And there are the rivers. Across the eastern Sahara, satellite radar and images show old river channels under the sand. One of them, the Wadi Howar, runs from the border of Chad toward the Nile. Geologists call it the Yellow Nile. For thousands of years it carried water, and herders and their cattle lived along it. Along its banks, archaeologists have found pottery, grinding stones and the bones of cattle. Today it gets at most a few centimeters of rain in a year.",
          m(0, v(EASTS, routes=[HOWAR])),
          photo("satellite radar and images", PH_LIBYA, "Fossil drainage on a Libyan plateau, Landsat 2024"),
          m("One of them, the", v({"lon": 27.0, "lat": 17.5, "span": 13}, routes=[HOWAR])),
          sat("Geologists call it the", 26.5, 17.3, 0.6, "Wadi Howar, Sudan"),
          sat("For thousands of years", 27.8, 17.4, 0.3, "Along the dry Wadi Howar"),
          sat("Along its banks, archaeologists", 25.6, 16.9, 0.25, "Banks of the Wadi Howar"),
          stat("Today it gets at", "≤25 MM", "Rain a year in the Wadi Howar today", "Wikipedia, Wadi Howar")),
    ]},
    {"title": "A Sea in the Desert", "mood": "calm", "paragraphs": [
        P("The biggest of all the lakes was in the middle of the Sahara, in what is now Chad. Geologists call it Lake Mega-Chad. Its old shorelines, beach ridges and sand spits can still be traced across the desert. At its largest, around ten thousand years ago, it covered something like three hundred and forty thousand square kilometers, and in places it was more than a hundred and fifty meters deep.",
          m(0, v(CHADV, places=[CHAD])),
          m("Geologists call it Lake", v(CHADV, highlight=[LAKE], places=[CHAD])),
          sat("Its old shorelines, beach", 18.2, 17.5, 0.8, "Old shores of Mega-Chad, northern Chad"),
          sat("At its largest, around", 16.0, 14.5, 1.2, "Central Chad, inside the old lake"),
          stat("it covered something like", "~340,000 KM²", "Lake Mega-Chad at its highstand (estimates 340,000-400,000)", MEGA),
          sat("and in places it", 17.0, 15.6, 0.6, "The floor of Mega-Chad, central Chad"),
          stat("more than a hundred", "~160 M", "Greatest depth of Lake Mega-Chad (estimates 160-173 m)", MEGA)),
        P("In 2006 two geologists, Nick Drake and Charlie Bristow, used satellite images and radar height data from the Space Shuttle to follow those shorelines around the basin. They found beach terraces standing at almost exactly the same height, about three hundred and twenty-nine meters above sea level, hundreds of kilometers apart. A lake leaves a level line. These were its marks.",
          stat(0, "2006", "Drake and Bristow map Mega-Chad's shorelines with Landsat and Shuttle radar", "The Holocene, 2006"),
          m("used satellite images and", v({"lon": 17.5, "lat": 16.5, "span": 8}, highlight=[LAKE])),
          sat("to follow those shorelines", 18.4, 17.3, 0.25, "A beach ridge of Mega-Chad"),
          stat("about three hundred and", "~329 M", "Height of a Mega-Chad beach terrace above sea level", "Drake & Bristow, The Holocene 2006"),
          sat("hundreds of kilometers apart", 18.7, 17.9, 0.4, "Shoreline ridges at the northern edge of the old lake"),
          sat("A lake leaves a", 18.9, 17.6, 0.12, "Ridges on the old lake floor")),
        P("That is about the size of the Caspian Sea, the largest lake on Earth today. Our map shows its shape, drawn from the height of the land: every low point that connects to today's Lake Chad, up to about three hundred and twenty meters above sea level. The lake filled a basin bigger than Germany.",
          chart(0, "Lake Mega-Chad against today's lakes", "km²", [["Lake Mega-Chad", 340000], ["Caspian Sea", 371000], ["Lake Superior", 82100]], MEGA + "; Wikipedia", highlight=0),
          m("Our map shows its", v({"lon": 16.0, "lat": 14.5, "span": 11}, highlight=[LAKE])),
          stat("every low point that", "~320 M", "Our Mega-Chad outline: land below 320 m joined to Lake Chad (NOAA ETOPO)", "Our calculation, NOAA ETOPO 2022"),
          m("up to about three", v({"lon": 18.5, "lat": 17.0, "span": 6}, highlight=[LAKE], places=[BODELE])),
          m("The lake filled a", v(CHADV, highlight=[LAKE, "Germany@neutral"]))),
        P("From around eleven and a half thousand years ago until about five thousand years ago, Mega-Chad stood high. Then it shrank. Today's Lake Chad is what is left, a shallow lake on the southern edge of the Sahara. On average it is only about a meter and a half deep, full of reeds and islands. Tens of millions of people in Chad, Niger, Nigeria and Cameroon depend on its water and its fish. And even that is in trouble. Since the 1960s it has lost about ninety percent of its open water, to drought and to farming that takes water from its rivers.",
          stat(0, "11,500-5,000", "Years ago: Mega-Chad's long highstand", "Quaternary Research"),
          sat("Mega-Chad stood high. Then", 18.0, 17.0, 1.0, "The northern basin of Mega-Chad"),
          m("Then it shrank.", v(CHADV, highlight=[LAKE], places=[CHAD])),
          m("Today's Lake Chad is", v({"lon": 15.0, "lat": 13.5, "span": 6}, places=[CHAD])),
          sat("a shallow lake on", 14.2, 13.3, 1.4, "Lake Chad today"),
          stat("On average it is", "~1.5 M", "Average depth of Lake Chad", "Wikipedia, Lake Chad"),
          sat("full of reeds and", 14.35, 13.05, 0.12, "Reed islands of Lake Chad"),
          m("Tens of millions of", v({"lon": 14.0, "lat": 12.5, "span": 9}, highlight=["Chad@accent", "Niger@accent", "Nigeria@accent", "Cameroon@accent"], places=[CHAD])),
          stat("depend on its water", "4 COUNTRIES", "Chad, Niger, Nigeria and Cameroon share Lake Chad", "UNEP"),
          photo("And even that is", PH_CHAD_STS, "Lake Chad from the Space Shuttle, 1994"),
          stat("Since the 1960s it", "−90 %", "Lake Chad's open water lost since the 1960s", "UNEP; World Bank"),
          sat("to drought and to", 14.6, 13.0, 0.3, "Farms and wetlands on Lake Chad's shore")),
        P("A few lakes survive far inside the desert. At Ounianga in northern Chad, about eighteen lakes sit among the dunes, fed not by rain but by water rising from under the ground, water that fell during wetter times. Some are fresh, some are saltier than the sea, and some are tinted red and green by algae. In 2012 UNESCO listed them as a World Heritage site.",
          m(0, v(CHADV, highlight=[LAKE], places=[OUNIANGA])),
          sat("At Ounianga in northern", 20.5, 19.05, 0.5, "The Ounianga lakes among the dunes"),
          sat("sit among the dunes", 20.62, 19.0, 0.12, "Dunes between the Ounianga lakes"),
          photo("fed not by rain", PH_OUNIANGA, "Ounianga from the space station"),
          sat("water that fell during", 20.75, 19.06, 0.06, "A lake shore at Ounianga Serir"),
          sat("Some are fresh, some", 20.85, 19.08, 0.08, "Lakes of Ounianga Serir"),
          stat("In 2012 UNESCO listed", "2012", "The Lakes of Ounianga become a World Heritage site", "UNESCO World Heritage")),
        P("North of the lake lies the floor of the old sea. The Bodélé Depression, in the low heart of the basin, was once under deep water. Today it is the dustiest place on Earth. It is covered in pale dust made partly of the shells of diatoms, tiny algae that lived in Mega-Chad, and of the bones of its fish. When the winds blow between the Tibesti and Ennedi mountains, they lift that old lake bed into the sky. From space, it is one of the easiest dust sources on Earth to spot: in winter, long pale plumes stream out of it toward the southwest.",
          m(0, v(CHADV, highlight=[LAKE], places=[BODELE])),
          sat("The Bodélé Depression, in", 17.6, 16.9, 1.2, "The Bodélé Depression, the old lake floor"),
          stat("Today it is the", "DUSTIEST", "The Bodélé: the largest single source of dust on Earth", "NASA Earth Observatory"),
          sat("It is covered in", 17.3, 16.8, 0.15, "Pale diatomite of the Bodélé"),
          photo("When the winds blow", PH_TIBESTI, "The Tibesti mountains from the space station"),
          photo("they lift that old", PH_BODELE, "Dust storms from the Bodélé, December 2017"),
          sat("From space, it is", 17.2, 17.2, 1.8, "The Bodélé and its dust streaks from orbit"),
          m("in winter, long pale", v({"lon": 15.0, "lat": 15.0, "span": 22}, places=[BODELE], routes=[{"from": [17.6, 16.9], "to": [10.0, 12.0], "mode": "air", "color": "accent", "seconds": 1.5, "label": "Dust plumes"}]))),
    ]},
    {"title": "The Wobble", "mood": "curious", "paragraphs": [
        P("So why was the Sahara green? The answer is in the sky. Earth's axis is tilted, and it slowly wobbles, like a spinning top, tracing a circle about once every twenty-six thousand years. Together with the slow change in the shape of Earth's orbit, this wobble decides whether the north gets its summer when Earth is closest to the Sun or when it is farthest away. Today it is the second case: Earth is farthest from the Sun in early July, in the middle of the northern summer. That cycle comes back roughly every twenty-one thousand years. In the early twentieth century a Serbian engineer, Milutin Milanković, worked out these cycles by hand and argued that they drive the ice ages. He was right, and they drive the monsoons too.",
          m(0, v(AFR, highlight=[DESERT])),
          stat("Earth's axis is tilted", "PRECESSION", "The slow wobble of Earth's axis, like a spinning top", "General astronomy"),
          stat("tracing a circle about", "~26,000 YEARS", "One full turn of Earth's axis", "General astronomy"),
          photo("Together with the slow", PH_ISS_MALI, "The Sahel and Sahara from the space station"),
          m("this wobble decides whether", v({"lon": 15.0, "lat": 20.0, "span": 110})),
          stat("Today it is the", "EARLY JULY", "When Earth is farthest from the Sun today", "General astronomy"),
          m("in the middle of", v({"lon": 15.0, "lat": 30.0, "span": 90}, highlight=[DESERT])),
          stat("That cycle comes back", "~21,000 YEARS", "How often the northern summer sun peaks", ARM),
          stat("In the early twentieth", "MILANKOVIĆ", "Milutin Milanković calculated Earth's orbital cycles by hand", "General history of science"),
          m("and argued that they", v({"lon": 10.0, "lat": 55.0, "span": 110})),
          m("they drive the monsoons", v(AFR, routes=MONSOON))),
        P("About ten thousand years ago, northern summers came when Earth was near the Sun. The summer sun over North Africa was several percent stronger than today. The land heated up more, and hot air rising over the Sahara drew in moist air from the Atlantic, like a sea breeze the size of a continent. The West African monsoon, which today brings summer rain only to the Sahel, pushed its rains hundreds of kilometers further north.",
          m(0, v({"lon": 15.0, "lat": 15.0, "span": 70})),
          stat("The summer sun over", "+4 %", "Northern summer sunshine at the green/dry switch, compared with today (about)", AHP),
          sat("The land heated up", 5.0, 20.0, 1.5, "The Hoggar and Aïr region in summer", date=SUM),
          m("drew in moist air", v(AFR, routes=MONSOON_NOW)),
          sat("like a sea breeze", -4.0, 6.0, 0.6, "The Gulf of Guinea coast, Côte d'Ivoire"),
          m("The West African monsoon", v(AFR, routes=MONSOON)),
          sat("which today brings summer", 2.0, 13.5, 0.6, "The Sahel in Niger, end of the rainy season", date=AUT),
          m("pushed its rains hundreds", v(SAH, routes=MONSOON, highlight=[LAKE]))),
        P("And once the rains came, the land helped them. Grass and trees are darker than sand, so they soak up more sunlight. Plants breathe out water. Lakes add moisture to the air. All of that pulls in more rain, which grows more plants. The green Sahara kept itself green, until the push from the sky grew too weak. Scientists read this history in mud: pollen in old lake beds, and the dust and plant wax that washed into the sea off West Africa.",
          sat(0, 1.5, 13.0, 0.3, "Fields and bush in the Sahel, wet season", date=SUM),
          sat("Grass and trees are", 2.2, 12.6, 0.1, "Green and bare ground, Sahel"),
          photo("Plants breathe out water", PH_BOSUM2, "Rainforest around Lake Bosumtwi, Ghana"),
          sat("Lakes add moisture to", 14.3, 13.1, 0.4, "Lake Chad's wetlands"),
          photo("The green Sahara kept", PH_CENTRAL, "The central Sahara from orbit"),
          sat("Scientists read this history", 14.1, 13.4, 0.12, "Mud flats at the edge of Lake Chad"),
          sat("and the dust and", -17.2, 21.5, 0.6, "The Mauritanian coast, where Saharan dust meets the sea")),
        P("This was not a one-time event. In 2023 a team of climate scientists modeled North Africa over the last eight hundred thousand years and found green periods roughly every twenty-one thousand years, each driven by the wobble. They were weaker or missing during the big ice ages, when ice sheets in the north held the rains back. At the height of the last ice age the Sahara was even bigger than it is today. Sediments under the Mediterranean and the Atlantic record the same rhythm, back for millions of years. The Sahara has been greening and drying again and again, like a slow heartbeat.",
          sat(0, 2.5, 28.5, 1.5, "The Tademaït plateau, Algeria"),
          stat("modeled North Africa over", "800,000 YEARS", "North African humid periods modeled over the last 800,000 years", ARM),
          stat("found green periods roughly", "EVERY ~21,000", "Years between green Saharas, driven by precession", ARM),
          m("They were weaker or", v({"lon": 10.0, "lat": 45.0, "span": 120})),
          m("At the height of", v(AFR, highlight=[DESERT])),
          photo("Sediments under the Mediterranean", PH_DUST_ATL, "Saharan dust settling on the Atlantic"),
          m("The Sahara has been", v({"lon": 14.0, "lat": 18.0, "span": 60}, highlight=[DESERT])),
          m("like a slow heartbeat", v({"lon": 14.0, "lat": 18.0, "span": 60}, highlight=[LAKE], routes=[HOWAR]))),
        P("Those green windows may have mattered for our own species. Some researchers think that when the Sahara turned green, it opened corridors of water and grass across North Africa, and that groups of early humans used them to move north, toward the Mediterranean and beyond. When the desert came back, the doors closed again.",
          m(0, v(AFR, highlight=[LAKE], routes=[HOWAR])),
          stat("Some researchers think that", "CORRIDORS", "Green periods may have opened routes north for early humans", "Hypothesis, various studies"),
          m("it opened corridors of", v({"lon": 15.0, "lat": 22.0, "span": 50}, routes=[{"from": [20.0, 5.0], "via": [[18.0, 15.0]], "to": [15.0, 31.0], "mode": "line", "color": "accent", "seconds": 1.8, "label": "Green corridors (one idea)"}])),
          photo("toward the Mediterranean and", PH_TASSILI_ISS, "Tassili n'Ajjer, on the route north"),
          sat("When the desert came", 14.0, 26.0, 1.5, "The Murzuq sand sea, Libya")),
    ]},
    {"title": "The Drying", "mood": "tension", "paragraphs": [
        P("Lake Mega-Chad went first in the north. As the rains failed, its level dropped, its northern arm toward the Bodélé dried out, and the great lake broke up into smaller ones. By about five thousand years ago, the floor of the northern basin was open to the wind.",
          m(0, v(CHADV, highlight=[LAKE], places=[BODELE])),
          sat("As the rains failed", 18.0, 17.6, 0.6, "The dry northern arm of Mega-Chad"),
          m("and the great lake", v({"lon": 15.0, "lat": 13.5, "span": 6}, places=[CHAD])),
          sat("By about five thousand", 17.6, 16.9, 0.5, "The Bodélé, open to the wind")),
        P("After about ten thousand years ago the wobble moved on, and the summer sun over North Africa slowly weakened. The monsoon began to retreat south. But how fast did the green disappear? In 2000 a team studying mud from the sea floor off Mauritania found a surprise. The dust in their core jumped suddenly, around five and a half thousand years ago. By their reading, the end of the green Sahara came within decades to centuries, not slowly over thousands of years.",
          m(0, v(AFR, routes=MONSOON)),
          m("The monsoon began to", v(AFR, routes=MONSOON_NOW)),
          m("In 2000 a team", v({"lon": -16.0, "lat": 20.0, "span": 14}, places=[CORE])),
          sat("found a surprise. The", -16.4, 20.9, 0.6, "Cap Blanc, Mauritania, on the dusty Atlantic coast"),
          stat("The dust in their", "~5,500 YEARS AGO", "Sudden rise of Saharan dust in a core off Mauritania", "deMenocal et al., QSR 2000"),
          stat("By their reading, the", "DECADES", "How fast the end came, by the 2000 study", "deMenocal et al., QSR 2000"),
          m("not slowly over thousands", v({"lon": 5.0, "lat": 20.0, "span": 45}, highlight=[DESERT]))),
        P("How can a slow wobble cause a fast collapse? Because the feedbacks run in reverse. As the rain weakened, plants died back, the land grew paler and reflected more sunlight, and the air over it stopped rising as strongly. Less rain meant fewer plants, and fewer plants meant less rain. Past a tipping point, the green could not hold itself up.",
          sat(0, 3.0, 17.5, 0.4, "The southern Sahara in Mali, where the green ended"),
          sat("As the rain weakened", 1.2, 15.5, 0.3, "Thin vegetation at the Sahara's edge, Niger"),
          photo("Less rain meant fewer", PH_DUNE, "Desert sand, Egypt"),
          stat("Past a tipping point", "TIPPING POINT", "Plants and rain feed each other, so a slow push can end in a fast fall", AHP)),
        P("Later studies made the picture more complicated. A 2015 study that brought together records from all over Africa found that the end came at different times in different places. At about twenty degrees north it came around five thousand years ago. Much further south, at Lake Bosumtwi in Ghana, the wet period lasted until about three thousand years ago. The rains did not switch off. They retreated south, and each place dried in its turn. They are still fragile today. In the 1970s and 1980s a long run of droughts brought famine to the Sahel, and Lake Chad shrank to a fraction of its size.",
          m(0, v({"lon": 5.0, "lat": 12.0, "span": 40})),
          stat("A 2015 study that", "2015", "Shanahan et al.: the end came later the further south", "Nature Geoscience 2015"),
          m("found that the end", v(AFR, places=[CORE, BOSUM])),
          stat("At about twenty degrees", "~5,000 YEARS AGO", "End of the wet period near 20° N", "Shanahan et al. 2015"),
          sat("Much further south, at", -1.41, 6.5, 0.12, "Lake Bosumtwi, a crater lake in Ghana"),
          photo("the wet period lasted", PH_BOSUM, "Lake Bosumtwi, Ghana"),
          m("The rains did not", v(AFR, routes=MONSOON_NOW, highlight=[DESERT])),
          sat("and each place dried", -1.0, 10.0, 0.6, "Savanna in northern Ghana"),
          stat("In the 1970s and", "1970s-1980s", "Long droughts and famine in the Sahel", "General history"),
          sat("and Lake Chad shrank", 14.0, 13.6, 0.6, "The dry northern basin of Lake Chad")),
        P("The animals went the same way. Hippos, elephants and giraffes followed the water south, or died out. The herders' cattle needed grass, and the grass was going. Much later, in roughly the time of the Roman Empire, a new animal spread across the desert, one that could go for days without water: the camel. It is the last animal painted on the Tassili walls.",
          sat(0, 13.0, 12.0, 0.5, "Savanna on the Niger-Nigeria border, where the herds went"),
          sat("The herders' cattle needed", 15.5, 14.0, 0.4, "Grazing land in the Sahel, Chad", date=SUM),
          stat("Much later, in roughly", "~2,000 YEARS AGO", "Camels become common in the Sahara, Roman era", "Britannica; Zerboni & Nicoll 2019"),
          sat("one that could go", 8.9, 24.9, 0.15, "The Tassili plateau today", date=AUT)),
        P("For the people of the Sahara, that was enough. In 2006 two German archaeologists, Rudolph Kuper and Stefan Kröpelin, brought together radiocarbon dates from a hundred and fifty excavations across the eastern Sahara. They found people living across the region during the wet period, and then a sharp break in the Egyptian Sahara around 5300 BC. The herders left. One of the places they left behind is Nabta Playa, a dry lake bed in southern Egypt, where people set up a circle of standing stones about seven thousand years ago. Some researchers think it marked the summer solstice and the coming of the rains, though that reading is debated.",
          m(0, v(EASTS, places=[GILF])),
          stat("In 2006 two German", "150", "Excavations behind the eastern Sahara timeline", KK),
          sat("brought together radiocarbon dates", 29.0, 24.0, 1.0, "The desert west of the Nile"),
          sat("They found people living", 28.0, 22.5, 1.5, "The eastern Sahara on the Egypt-Sudan border"),
          stat("and then a sharp", "~5300 BC", "Settlement in the Egyptian Sahara breaks off", KK),
          photo("The herders left.", PH_DAKHLA, "Dunes of the Western Desert"),
          m("One of the places", v(EASTS, places=[place("Nabta Playa", 30.73, 22.51, "Nabta Playa", "site")])),
          sat("a dry lake bed", 30.73, 22.51, 0.3, "Nabta Playa, southern Egypt"),
          stat("where people set up", "~7,000 YEARS", "Age of the Nabta Playa stone circle", "Live Science; Wikipedia, Nabta Playa"),
          sat("about seven thousand years", 30.725, 22.507, 0.05, "Around the Nabta Playa stone circle"),
          stat("Some researchers think it", "SOLSTICE?", "A proposed calendar for the summer rains (debated)", "Live Science; ICOMOS 2010"),
          sat("though that reading is", 30.68, 22.45, 0.6, "The Nabta basin today")),
        P("Some moved south with the rains, into the Sahel. Many went east, to the one place in that region that still had water all year: the valley of the Nile. As the desert emptied, the Nile valley filled with farmers and herders. Kuper and Kröpelin argued that this crowding into a narrow river valley helped set the stage for the rise of pharaonic Egypt. The pyramids of Giza were built about two and a half thousand years later.",
          m(0, v(AFR, routes=MONSOON_NOW)),
          m("Many went east, to", v(EASTS, routes=TO_NILE, places=[CAIRO, ASWAN])),
          photo("As the desert emptied", PH_NILE_NIGHT, "The Nile valley from Luxor to Cairo at night"),
          sat("Kuper and Kröpelin argued", 32.65, 25.7, 0.3, "Farmland in the Nile valley at Luxor"),
          sat("The pyramids of Giza", 31.13, 29.98, 0.04, "The pyramids of Giza"),
          stat("built about two and", "~2500 BC", "The Great Pyramid of Giza is built", "Wikipedia, Great Pyramid of Giza")),
    ]},
    {"title": "What the Green Left", "mood": "calm", "paragraphs": [
        P("The green Sahara left more than paintings. Every year the winds lift dust off the Sahara and carry it across the Atlantic. A 2015 NASA study used a satellite laser to measure it. About twenty-seven million tons of that dust fall on the Amazon rainforest every year. Much of it comes from the Bodélé, the floor of Lake Mega-Chad. Some of the dust blows north instead, and every few years it turns the skies over Spain and the Alps orange.",
          photo(0, PH_DUST_CAR, "Saharan dust reaching the Caribbean and South America"),
          m("Every year the winds", v({"lon": -20.0, "lat": 8.0, "span": 110}, routes=[DUST], places=[BODELE])),
          stat("A 2015 NASA study", "CALIPSO", "NASA's lidar satellite measured the dust, 2007-2013", YU),
          stat("About twenty-seven million tons", "27.7 M TONS", "Saharan dust settling on the Amazon each year", YU),
          photo("Much of it comes", PH_BODELE, "Dust blowing off the Bodélé"),
          m("Some of the dust", v({"lon": 5.0, "lat": 38.0, "span": 40}, routes=[{"from": [5.0, 25.0], "to": [5.0, 45.0], "mode": "air", "color": "accent", "seconds": 1.5, "label": "Dust to Europe"}]))),
        P("That dust carries phosphorus, from the old lake's fish and algae. Amazon soils are poor in phosphorus, and rain keeps washing it away. The study estimated that about twenty-two thousand tons of phosphorus arrive from Africa each year, close to what the rainforest loses. A dead lake in the Sahara helps feed the largest rainforest on Earth.",
          stat(0, "PHOSPHORUS", "A nutrient the Amazon is short of", YU),
          sat("Amazon soils are poor", -60.0, -3.0, 0.5, "The Amazon rainforest near Manaus"),
          sat("and rain keeps washing", -59.5, -3.2, 0.15, "Rainforest and river near Manaus"),
          stat("The study estimated that", "~22,000 TONS", "Phosphorus reaching the Amazon from Saharan dust each year", YU),
          sat("close to what the", -60.5, -2.8, 0.25, "The Rio Negro near Manaus"),
          sat("A dead lake in", -61.0, -2.5, 0.12, "Rainforest canopy, central Amazon")),
        P("The green Sahara also left water under the sand. Beneath Egypt, Libya, Sudan and Chad lies one of the largest groundwater systems in the world, the Nubian Sandstone Aquifer. Much of its water fell as rain during wet periods thousands to hundreds of thousands of years ago, and very little is being added today. In the Egyptian desert, farms pump that ancient water into green circles in the sand.",
          m(0, v(EASTS, places=[OWEINAT])),
          stat("Beneath Egypt, Libya, Sudan", "~2 M KM²", "Area of the Nubian Sandstone Aquifer", "Wikipedia, Fossil water"),
          m("the Nubian Sandstone Aquifer", v(EASTS, highlight=["Egypt@accent", "Libya@accent", "Sudan@accent", "Chad@accent"])),
          stat("Much of its water", "FOSSIL WATER", "Much of it thousands to hundreds of thousands of years old", "Wikipedia, Fossil water; J. Hydrology 2020"),
          sat("thousands to hundreds of", 24.0, 24.0, 1.0, "Sand sheet over the aquifer, western Egypt"),
          sat("and very little is", 30.55, 25.45, 0.3, "Kharga Oasis, Egypt, fed by the aquifer"),
          sat("In the Egyptian desert", 28.6, 22.6, 0.4, "Irrigated circles at East Oweinat, Egypt"),
          sat("farms pump that ancient", 28.55, 22.55, 0.1, "Center-pivot fields in the Sahara")),
        P("At the southern edge of the desert, people are trying to hold the line. In 2007 the African Union launched the Great Green Wall, a plan to restore a belt of trees, grass and farmland about eight thousand kilometers long, from Senegal to Djibouti. Progress has been slow and patchy. But in places, farmers who protect the trees that sprout on their fields have turned bare ground green again.",
          m(0, v(AFR, highlight=["Senegal@accent", "Mauritania@accent", "Mali@accent", "Niger@accent", "Chad@accent", "Sudan@accent", "Ethiopia@accent"])),
          stat("In 2007 the African", "2007", "The African Union launches the Great Green Wall", "African Union; UNCCD"),
          sat("a plan to restore", -15.5, 15.0, 0.4, "The Sahel in Senegal"),
          stat("about eight thousand kilometers", "~8,000 KM", "Length of the planned Great Green Wall", "UNCCD"),
          sat("Progress has been slow", 7.5, 13.6, 0.3, "Farmland with trees, southern Niger"),
          sat("farmers who protect the", 7.9, 13.5, 0.06, "Trees kept in the fields of Niger's Zinder region")),
        P("Will the Sahara turn green again by itself? If the wobble keeps its rhythm, the next peak of northern summer sun comes in about ten thousand years. How green the next green Sahara becomes may depend on how much greenhouse gas is in the air by then. And in 2018 one study suggested a shortcut: in a computer model, covering the Sahara with huge wind and solar farms more than doubled its rainfall, because the panels and turbines change how the land heats and the wind blows. Nobody has tried it at that scale.",
          m(0, v(AFR, highlight=[DESERT])),
          stat("the next peak of", "~10,000 YEARS", "Until the next peak of northern summer sun", "Live Science; Duque-Villegas et al. 2022"),
          photo("How green the next", PH_ISS_ALG, "Dunes of the Algerian Sahara from orbit"),
          stat("how much greenhouse gas", "GREENHOUSE GAS", "In models, future green periods depend on the CO₂ in the air", "Duque-Villegas et al., Climate of the Past 2022"),
          stat("And in 2018 one", "×2 RAIN", "Sahara rainfall in a model with vast wind and solar farms", "Li et al., Science 2018"),
          sat("covering the Sahara with", -6.86, 31.0, 0.08, "The Noor Ouarzazate solar complex, Morocco"),
          sat("because the panels and", -6.87, 31.01, 0.04, "Mirrors of Noor Ouarzazate"),
          photo("Nobody has tried it", PH_CHEBBI, "Erg Chebbi, Morocco")),
    ]},
    {"title": "The Green Under the Sand", "mood": "calm", "paragraphs": [
        P("So the next time you see the Sahara on a map, remember that it has not always been this way. Ten thousand years ago it held a lake the size of the Caspian, rivers that ran toward the Nile, hippos and fishers and herds of cattle. A slow wobble of the Earth brought the rain, and a slow wobble took it away. The paintings, the bones, the crocodiles of Archei and the dust over the Atlantic are what is left. And the next time a dust storm turns a European sky orange, some of that dust may once have been the bottom of a lake. Five thousand years is a blink for a planet. The people who painted cattle on the rocks of the Sahara lived not long before the first pharaohs.",
          m(0, v(AFR, highlight=[DESERT])),
          photo("remember that it has", PH_ISS_ALG2, "The Sahara from the space station"),
          m("Ten thousand years ago", v(SAH, highlight=[LAKE], routes=[HOWAR])),
          sat("rivers that ran toward", 26.5, 17.3, 0.6, "Wadi Howar, the Yellow Nile"),
          photo("hippos and fishers and", PH_TASSILI, "The Tassili n'Ajjer, where the herds were painted"),
          m("A slow wobble of", v(AFR, routes=MONSOON)),
          m("and a slow wobble", v(AFR, routes=MONSOON_NOW)),
          photo("The paintings, the bones", PH_OUNIANGA, "The Ounianga region from the space station"),
          photo("and the dust over", PH_DUST_ATL, "Saharan dust over the Atlantic"),
          m("And the next time", v({"lon": 5.0, "lat": 38.0, "span": 42}, routes=[{"from": [8.0, 24.0], "to": [3.0, 44.0], "mode": "air", "color": "accent", "seconds": 1.5}])),
          stat("Five thousand years is", "~5,000 YEARS", "Since the green Sahara ended in the north", AHP),
          photo("The people who painted", PH_CENTRAL, "The central Sahara from orbit"),
          sat("not long before the", 31.13, 29.98, 0.06, "Giza")),
        P("Here is my question for you. If you could visit the green Sahara for one day, ten thousand years ago, where would you go: fishing on Lake Mega-Chad, along the Yellow Nile with the herders, or to the painters at Tassili?",
          photo(0, PH_ENNEDI, "The Ennedi massif, Chad, from the space station"),
          sat("ten thousand years ago,", 18.2, 17.5, 0.8, "The old shore of Mega-Chad"),
          m("where would you go", v(SAH, highlight=[LAKE], routes=[HOWAR], places=[TASSILI])),
          m("along the Yellow Nile", v(EASTS, routes=[HOWAR])),
          sat("or to the painters", 8.6, 24.8, 0.4, "Tassili n'Ajjer"),
          ask=("where would you go", "Mega-Chad, the Yellow Nile, or Tassili?")),
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
            if sh["type"] != "map" or len(steps) != 1 or end - start <= PUSH_WORDS or steps[0].get("compare") or steps[0].get("highlight"):
                continue
            first = steps[0]
            vw = first["view"]
            move = {"at": start + (end - start) // 2, "view": {"lon": vw["lon"], "lat": vw["lat"], "span": max(0.05, round(vw["span"] * (0.62 if vw["span"] <= 2.5 else 0.75), 3))}}
            for key in ("date", "layer"):
                if first.get(key):
                    move[key] = first[key]
            steps.append(move)

script = {
    "title": "When the Sahara Was Green",
    "voice": "am_michael",
    "voice_speed": 1.15,
    "music": "procedural",
    "map_style": "satellite",
    "look": "none",
    "sources": ["episodes/green-sahara/research.md and factcheck.md", "Contains modified Copernicus Sentinel data 2026"],
    "thumbnail": {"text": "SEA IN THE SAHARA?"},
    "chapters": chapters,
    "youtube": {
        "title": "When the Sahara Was Green",
        "description": "About ten thousand years ago the Sahara was not a desert. It had lakes, one of them the size of the Caspian Sea, rivers flowing toward the Nile, hippos, crocodiles, fishers and cattle herders. This video follows the clues in the rock art, the graves and the dry riverbeds, explains how a slow wobble of the Earth brought the monsoon rains north and then took them away, and shows what the green Sahara left behind: dust that feeds the Amazon and ancient water under the sand.",
        "tags": ["Sahara", "green Sahara", "African Humid Period", "Lake Mega-Chad", "Lake Chad", "Bodélé Depression", "Cave of Swimmers", "Tassili n'Ajjer", "Gobero", "Saharan dust Amazon", "precession", "geography", "satellite images"],
        "pinned_comment": "If you could visit the green Sahara for one day, ten thousand years ago, where would you go: fishing on Lake Mega-Chad, along the Yellow Nile with the herders, or to the painters at Tassili?",
    },
}
out = HERE / "script.json"
out.write_text(json.dumps(script, ensure_ascii=False, indent=1) + chr(10), encoding="utf-8")
words = sum(len(p["text"].split()) for c in chapters for p in c["paragraphs"])
shots = [s for c in chapters for p in c["paragraphs"] for s in p["shots"]]
kinds = {k: sum(1 for s in shots if s["type"] == k) for k in ("map", "photo", "stat", "document", "chart")}
print(f"{words} words, {len(chapters)} chapters, {len(shots)} shots {kinds}")
