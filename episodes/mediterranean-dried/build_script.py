"""Builds script.json for mediterranean-dried.  python build_script.py

Same production logic as episodes/mongolia-empty (hand-placed shots, seafloor drawdown highlights from pipeline/bathy.py,
a photo or map frame at most twice). Sources: research.md.
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
    view = view or MED
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
MED = {"lon": 17.0, "lat": 38.0, "span": 46}
WMED = {"lon": 3.5, "lat": 38.5, "span": 18}
GIBV = {"lon": -5.5, "lat": 36.0, "span": 3.2}
NILEV = {"lon": 31.5, "lat": 27.5, "span": 13}
EUAF = {"lon": 8.0, "lat": 38.0, "span": 62}
SICV = {"lon": 14.3, "lat": 36.6, "span": 7}


def dry(m_):
    return f"seafloor:mediterranean:{m_}@red"


GC = "Garcia-Castellanos et al., Nature 2009"
RYAN = "Ryan, Sedimentology 2009 review"
HSU = "Hsü, The Mediterranean Was a Desert (1983)"
NILE22 = "Communications Earth & Environment, 2022"
WMS = "Wikipedia, Messinian salinity crisis"
WMED_SRC = "Wikipedia, Mediterranean Sea"

PH_CABO_ROCK = "File:Detail of rocks, Cabo de Gata, Andalusia, Spain.jpg"
PH_CABO_PAN = "File:Panoramica del Cabo de Gata, Almeria (Almeria).jpg"
PH_MONSUL = "File:Playa Monsul - Cabo de Gata.jpg"
PH_LOMA = "File:Loma Pelada, Parque Natural Cabo de Gata - Nijar (26739960137).jpg"
PH_DS3 = "File:Dead Sea Salt-3 (10494735593).jpg"
PH_DS2 = "File:Dead Sea Salt-2 (10494737573).jpg"
PH_TERR1 = "File:Dead Sea Halite Terraces and Salt Crust Formations 01.jpg"
PH_TERR2 = "File:Dead Sea Halite Terraces and Salt Crust Formations 02.jpg"
PH_GIB_STS = "File:STS059-238-074 Strait of Gibraltar.jpg"
PH_GIB23 = "File:The Strait of Gibraltar, April 2023.jpg"
PH_GIB11 = "File:Straits-of-Gibraltar-2011.jpg"
PH_DRILL = "File:Bohrkrone Glomar Challenger Basel 27102013.jpg"
PH_GYP_C = "File:Gypsum cones.jpg"
PH_YESARES = "File:Yesares gypsum.jpg"
PH_SHUTTLE = "File:Atlantis seen over the Mediterranean Sea, near the Algerian coast.jpeg"
PH_EGYPT = "File:Egypt and the Mediterranean Sea (iss071e207494).jpg"
PH_ISS_MED = "File:The International Space Station above the Mediterranean Sea (iss073e0767188).jpg"
PH_MODIS = "File:Mediterranean Sea (MODIS 2019-04-04).jpg"
PH_NILE_ISS = "File:The Nile River flows into the Mediterranean Sea (iss071e405499).jpg"
PH_NILE_WIDE = "File:ISS035-E-007148 Nile - Sinai - Dead Sea - Wide Angle View.jpg"
PH_NILE_MODIS = "File:Nile Delta (MODIS 2026-01-04).jpg"
PH_NILE_FOG = "File:Nile delta fog tmo 20240107 lrg.jpg"
PH_ROCK = "File:Rock-of-Gibraltar-2011.jpg"
PH_ROCK_CL = "File:Rock of Gibraltar in the clouds.jpg"

GIB = place("Gibraltar", -5.35, 36.14)
CAIRO, ASWAN = place("Cairo", 31.24, 30.04), place("Aswan", 32.9, 24.09)
MESSINA = place("Messina", 15.55, 38.19)
MALTA = place("Malta", 14.45, 35.9, "Malta", "site")
BALEARIC = place("Balearic Islands", 2.9, 39.6, "Balearic Islands", "site")
SORBAS = place("Sorbas", -2.12, 37.1, "Sorbas gypsum", "site")
REALMONTE = place("Realmonte", 13.47, 37.31, "Realmonte salt mine", "site")
LYON, ARLES = place("Lyon", 4.83, 45.76), place("Arles", 4.63, 43.68)
COAST = ["Spain", "France", "Italy", "Greece", "Turkey", "Egypt", "Libya", "Tunisia", "Algeria", "Morocco", "Croatia", "Albania", "Syria", "Lebanon", "Israel", "Cyprus"]
INFLOW = {"from": [-9.0, 36.0], "to": [-3.0, 36.1], "mode": "sea", "color": "accent", "seconds": 1.5, "label": "Atlantic water flows in"}
BETIC = {"from": [-6.6, 37.1], "via": [[-4.6, 37.4], [-3.6, 37.2], [-2.0, 37.6]], "to": [-1.0, 37.8], "mode": "line", "color": "accent", "seconds": 1.5, "label": "Betic seaway (southern Spain)"}
RIFIAN = {"from": [-6.4, 34.4], "via": [[-5.0, 34.2], [-4.0, 34.2]], "to": [-3.0, 35.1], "mode": "line", "color": "accent", "seconds": 1.5, "label": "Rifian seaway (northern Morocco)"}
NORTH = {"from": [5.0, 30.0], "to": [5.0, 36.5], "mode": "line", "color": "red", "seconds": 1.5, "label": "Africa moves north"}
FLOOD = {"from": [-9.0, 36.0], "via": [[-5.6, 35.95]], "to": [-1.0, 36.6], "mode": "sea", "color": "red", "seconds": 1.8, "label": "The Atlantic breaks in"}
CHANNEL = {"from": [-6.6, 35.95], "via": [[-5.6, 35.95]], "to": [-4.4, 36.05], "mode": "line", "color": "red", "seconds": 1.5, "label": "Flood channel, about 200 km (approximate path)"}
SPILL = {"from": [11.6, 37.6], "via": [[13.0, 36.8]], "to": [15.6, 36.0], "mode": "sea", "color": "red", "seconds": 1.5, "label": "West spills into east"}

chapters = [
    {"title": "A Sea of Salt", "mood": "curious", "paragraphs": [
        P("The Mediterranean is one of the most familiar seas on Earth. It covers about two and a half million square kilometers, and more than twenty countries have a coast on it. On average it is about one and a half kilometers deep, and in one trench off Greece it goes down more than five kilometers. Its only natural link to the open ocean is a gap about fourteen kilometers wide between Spain and Morocco, and only about three hundred meters deep at its shallowest point: the Strait of Gibraltar.",
          m(0, v(MED)),
          photo("It covers about two", PH_MODIS, "The Mediterranean from orbit, April 2019"),
          stat("two and a half million", "2.5 M KM²", "Area of the Mediterranean Sea", WMED_SRC),
          m("more than twenty countries", v(MED, highlight=[c + "@accent" for c in COAST])),
          stat("On average it is", "~1,500 M", "Average depth of the Mediterranean", WMED_SRC),
          stat("and in one trench", "5,267 M", "Calypso Deep, off Greece: the Mediterranean's deepest point", WMED_SRC),
          m("Its only natural link", v(GIBV, places=[GIB])),
          photo("between Spain and Morocco", PH_GIB_STS, "The Strait of Gibraltar from the Space Shuttle"),
          stat("and only about three", "~300 M", "Depth of the Strait of Gibraltar at its shallowest point", "Wikipedia, Strait of Gibraltar")),
        P("Six million years ago, almost none of that water was there. The link to the Atlantic closed, the sea evaporated, and the floor of the Mediterranean became a vast basin of salt, in places perhaps more than a kilometer below the level of the ocean next door. Then the Atlantic broke back in and refilled it, perhaps in less than two years. We know this because of salt under the sea floor, canyons buried under the Nile, and a drill ship that pulled up something nobody expected.",
          m(0, v(MED, highlight=[dry(200)])),
          m("the sea evaporated", v(MED, highlight=[dry(600)]), v(MED, at="became a vast basin", highlight=[dry(1500)])),
          photo("in places perhaps more", PH_TERR1, "Salt crust at the Dead Sea today"),
          m("Then the Atlantic broke", v(GIBV, routes=[FLOOD])),
          stat("and refilled it, perhaps", "< 2 YEARS", "How fast the Atlantic may have refilled the basin, in one model", GC),
          photo("We know this because", PH_YESARES, "Gypsum from the crisis, Sorbas, Spain"),
          photo("canyons buried under the", PH_NILE_ISS, "The Nile meets the Mediterranean"),
          stat("and a drill ship", "1970", "A drill ship pulls salt from under the Mediterranean floor", "Deep Sea Drilling Project, Leg 13")),
        P("So how does a whole sea dry up, and how do you fill it again? And could it happen again? There is a twist, too: some scientists now think the sea fell much less far than the classic story says. To answer all of that, start where the scientists did: with salt, in a place where salt should not be.",
          m(0, v(WMED, highlight=[dry(1500)])),
          photo("and how do you", PH_ROCK, "The Rock of Gibraltar"),
          m("And could it happen", v(MED, places=[GIB])),
          m("some scientists now think", v(MED, highlight=[dry(2500)])),
          m("much less far than", v(MED, highlight=[dry(600)])),
          sat("To answer all of", 13.47, 37.31, 0.04, "A salt mine at Realmonte, Sicily", date=SPR),
          photo("with salt, in a", PH_DS3, "Rock salt forming in the Dead Sea"),
          ask=("And could it happen", "Could the Mediterranean dry up again?")),
    ]},
    {"title": "Salt Under the Sea", "mood": "curious", "paragraphs": [
        P("In the 1960s, ships surveying the Mediterranean with sound found something strange under the mud of the sea floor: a hard layer that bounced the sound straight back. Geologists called it the M reflector. Nobody knew what it was. In the summer of 1970 an American drill ship, the Glomar Challenger, set out to find out. It was part of the Deep Sea Drilling Project, which drilled holes in the ocean floor from a ship floating in water several kilometers deep. The ship held itself in place over the hole with thrusters, while a string of drill pipe kilometers long hung beneath it. The two chief scientists on that cruise, known as Leg 13, were William Ryan, an American, and Kenneth Hsü, a Swiss geologist born in China.",
          m(0, v(WMED, places=[BALEARIC])),
          photo("a hard layer that", PH_SHUTTLE, "The Space Shuttle Atlantis over the Mediterranean"),
          stat("Geologists called it the", "M REFLECTOR", "A hard layer under the Mediterranean mud that echoed sound back", HSU),
          photo("In the summer of", PH_ISS_MED, "The Mediterranean from the International Space Station"),
          stat("the Glomar Challenger, set", "GLOMAR CHALLENGER", "Drill ship of the Deep Sea Drilling Project, at sea 1968-1983", "Wikipedia, Deep Sea Drilling Project"),
          m("which drilled holes in", v({"lon": 10.0, "lat": 38.5, "span": 28}, places=[BALEARIC])),
          photo("The ship held itself", PH_DRILL, "A drill bit from the Glomar Challenger, in Basel"),
          m("while a string of", v({"lon": 4.0, "lat": 39.0, "span": 8}, places=[BALEARIC])),
          stat("The two chief scientists", "LEG 13", "The 1970 Mediterranean cruise of the Glomar Challenger", RYAN),
          stat("and Kenneth Hsü, a", "RYAN & HSÜ", "William Ryan and Kenneth Hsü, co-chief scientists of Leg 13", RYAN)),
        P("The drill came up with things nobody expected so deep under the sea. Under the normal sea-floor mud were layers of gypsum and rock salt. There were thin, wavy layers that looked like mats left by microbes in shallow, sun-warmed water. And some of the salt had a chicken-wire texture that geologists knew from the salt flats on the shore of the Persian Gulf, near Abu Dhabi, where it forms on dry land under a blazing sun.",
          m(0, v(MED, places=[BALEARIC])),
          photo("Under the normal sea-floor", PH_GYP_C, "Gypsum"),
          photo("There were thin, wavy", PH_TERR2, "Layered salt crust, Dead Sea"),
          stat("And some of the", "CHICKEN-WIRE", "A salt texture known from desert salt flats, found in the cores", HSU),
          sat("that geologists knew from", 52.6, 24.0, 0.4, "Salt flats on the Persian Gulf coast"),
          sat("near Abu Dhabi", 53.9, 24.1, 0.3, "Salt flats (sabkha) on the Abu Dhabi coast"),
          sat("where it forms on", 53.55, 24.05, 0.08, "A sabkha drying in the sun, Abu Dhabi")),
        P("Why does that matter? Because salt like this does not form on the floor of a deep sea. It forms where seawater evaporates. Let a pool of seawater dry in the sun, and gypsum crystallizes first, once most of the water has gone. Rock salt only appears when roughly nine tenths of the water is gone. To lay down thick salt, a sea has to lose most of its water, again and again.",
          sat(0, 35.45, 31.1, 0.3, "Evaporation ponds at the south end of the Dead Sea"),
          photo("It forms where seawater", PH_DS2, "Salt crystallizing in the Dead Sea"),
          sat("Let a pool of", 35.4, 31.03, 0.08, "Salt pans by the Dead Sea"),
          stat("Rock salt only appears", "~90 %", "Share of seawater that must evaporate before rock salt crystallizes", "Evaporite chemistry, general"),
          m("To lay down thick", v(MED, highlight=[dry(1000)]))),
        P("The Dead Sea, between Israel and Jordan, shows what that looks like today. Its shore is the lowest dry land on Earth, more than four hundred meters below sea level, and its water is so salty that swimmers float on it without trying, and salt crystals grow on the bottom and along the shore. It is also shrinking, by around a meter a year, because more water evaporates than flows in.",
          m(0, v({"lon": 35.5, "lat": 31.5, "span": 2.0})),
          sat("Its shore is the", 35.5, 31.55, 0.4, "The Dead Sea from orbit"),
          stat("more than four hundred", "−430 M", "The Dead Sea shore: the lowest dry land on Earth", "Wikipedia, Dead Sea"),
          sat("swimmers float on it", 35.58, 31.75, 0.1, "Beaches on the Dead Sea's northern shore"),
          sat("salt crystals grow on", 35.48, 31.2, 0.1, "Salt flats on the Dead Sea's southern shore"),
          stat("It is also shrinking", "~1 M / YEAR", "How fast the Dead Sea's level has been falling", "Wikipedia, Dead Sea")),
        P("And there was a lot of it. Later surveys found that salt lies under almost the whole deep Mediterranean, in places more than a kilometer thick. Altogether, more than a million cubic kilometers of it. That is about five percent of all the salt dissolved in all the world's oceans today, taken out and laid down in one sea.",
          photo(0, PH_NILE_WIDE, "The eastern Mediterranean from the space station"),
          m("Later surveys found that", v({"lon": 18.0, "lat": 37.0, "span": 40}, highlight=[dry(2000)])),
          stat("in places more than", "1 KM+", "Thickness of the salt layer in places", WMS),
          stat("Altogether, more than a", "1 M+ KM³", "Salt from the crisis under the Mediterranean", RYAN),
          stat("That is about five", "~5 %", "Share of the ocean's dissolved salt now locked under the Mediterranean", RYAN),
          photo("taken out and laid", PH_CABO_ROCK, "Rocks of Cabo de Gata, Spain")),
        P("In 1973 Hsü, Ryan and the Italian geologist Maria Bianca Cita published their explanation in Nature. The Mediterranean, they argued, had dried out, and not once, but over and over: a deep, hot, empty basin far below sea level, with salt lakes on its floor. Many scientists thought it was absurd. Some argued that the salt could have settled out at the bottom of a deep sea that never dried, filled with heavy brine. The argument went on for decades. Hsü later wrote a book about the expedition with a title that said it plainly: The Mediterranean Was a Desert.",
          stat(0, "1973", "Hsü, Ryan and Cita: the Mediterranean dried out", "Nature, 1973"),
          m("The Mediterranean, they argued", v(MED, highlight=[dry(1500)])),
          sat("a deep, hot, empty", 42.42, 11.63, 0.15, "Lake Assal, Djibouti: a salt lake below sea level today"),
          sat("with salt lakes on", 42.4, 11.66, 0.05, "Salt shores of Lake Assal"),
          photo("Many scientists thought it", PH_DS3, "Salt in the Dead Sea"),
          stat("Some argued that the", "DEEP BRINE?", "The rival idea: salt settling in a deep sea that never dried", WMS),
          m("a deep sea that never", v(WMED)),
          photo("The argument went on", PH_MONSUL, "Playa de Mónsul, Cabo de Gata, Spain"),
          stat("Hsü later wrote a", "1983", "Hsü's book The Mediterranean Was a Desert", "Princeton University Press"),
          photo("with a title that", PH_SHUTTLE, "The Mediterranean from orbit")),
        P("There was one more clue in the cores. Right on top of the salt, with no gap between them, lay ordinary deep-sea ooze, full of the tiny shells of creatures that live in the open ocean. Whatever had happened, it had ended suddenly. One moment the basin was making salt; the next, it was a deep sea again. That sudden switch would turn out to be the most dramatic part of the story.",
          stat(0, "SALT → OOZE", "In the cores, open-ocean ooze lies right on top of the salt", HSU),
          m("Right on top of", v(MED, places=[BALEARIC])),
          stat("full of the tiny", "FORAMINIFERA", "Single-celled creatures with shells, typical of the open ocean", "General"),
          m("Whatever had happened, it", v(MED, highlight=[dry(1500)])),
          m("the next, it was", v({"lon": 15.0, "lat": 37.0, "span": 30})),
          sat("That sudden switch would", -5.35, 36.13, 0.06, "The Rock of Gibraltar from orbit")),
    ]},
    {"title": "Cut Off", "mood": "tension", "paragraphs": [
        P("So how do you cut off a sea? Today the Mediterranean loses more water to evaporation than all its rivers and rain put back. The hot, dry summers around it see to that. What keeps it full is the Atlantic. Through the Strait of Gibraltar, ocean water pours in at the surface, while heavier, saltier Mediterranean water slides out underneath. Close that door, and the sea starts to shrink. Scientists estimate that, cut off today, it would lose most of its water in roughly a thousand years.",
          m(0, v(MED)),
          photo("Today the Mediterranean loses", PH_EGYPT, "Egypt's coast from the space station"),
          sat("The hot, dry summers", 20.1, 32.1, 0.4, "The coast of Libya at Benghazi"),
          m("What keeps it full", v(GIBV, routes=[INFLOW])),
          photo("ocean water pours in", PH_GIB23, "The Strait of Gibraltar, April 2023"),
          stat("while heavier, saltier Mediterranean", "~38 G/KG", "Salinity of the Mediterranean; the Atlantic outside is about 36", WMED_SRC),
          m("Close that door, and", v(MED, highlight=[dry(200)])),
          m("the sea starts to", v(MED, highlight=[dry(500)])),
          m("Scientists estimate that, cut", v(MED, highlight=[dry(1000)])),
          stat("it would lose most", "~1,000 YEARS", "Time for most of the sea to evaporate if it were cut off today (estimate)", WMS)),
        P("That inflow is not small. On average, about eight hundred thousand cubic meters of Atlantic water pour through the strait every second. That is roughly four times the flow of the Amazon, just to keep the Mediterranean topped up and stop it from getting saltier.",
          m(0, v({"lon": -5.5, "lat": 36.0, "span": 1.6}, routes=[INFLOW])),
          stat("about eight hundred thousand", "~810,000 M³/S", "Average Atlantic inflow through the Strait of Gibraltar", "Soto-Navarro et al., JGR 2010"),
          chart("That is roughly four", "Atlantic inflow at Gibraltar against the Amazon", "m³/s", [["Gibraltar inflow", 810000], ["Amazon (average)", 209000]], "Soto-Navarro et al. 2010; Amazon average flow", highlight=0),
          sat("just to keep the", -5.4, 36.0, 0.15, "Ships in the Strait of Gibraltar")),
        P("Six million years ago there was no Strait of Gibraltar. The Mediterranean was joined to the Atlantic through narrow seaways across what are now southern Spain and northern Morocco. And Africa was, as it still is, pushing slowly north into Europe. As the plates squeezed together, the land around those seaways rose. At the same time, ice was growing at the poles, and sea level around the world was falling. Today the old Betic seaway is dry land: the city of Granada stands on rocks that were once the floor of that channel.",
          m(0, v({"lon": -4.0, "lat": 36.0, "span": 9}, routes=[BETIC, RIFIAN])),
          sat("across what are now", -3.7, 37.15, 0.4, "The Granada basin, on the old Betic seaway"),
          sat("and northern Morocco", -4.6, 34.3, 0.4, "Northern Morocco, on the old Rifian seaway"),
          m("And Africa was, as", v(EUAF, routes=[NORTH])),
          sat("As the plates squeezed", -3.3, 37.05, 0.4, "The Sierra Nevada, southern Spain", date=WIN),
          sat("the land around those", -4.4, 35.1, 0.4, "The Rif mountains, Morocco"),
          stat("At the same time", "ICE", "Growing ice sheets lowered sea level around the world", WMS),
          photo("and sea level around", PH_NILE_WIDE, "The eastern Mediterranean from the space station"),
          sat("Today the old Betic", -3.6, 37.18, 0.08, "Granada, built on the floor of the old seaway")),
        P("About five point nine six million years ago, the change began. A study published in Nature in 1999 dated it from layers of rock around the Mediterranean, and found that it started at the same moment everywhere. The gypsum in those rocks comes in repeated bands, and the bands follow slow wobbles in Earth's orbit. Count the bands, and you have a clock.",
          stat(0, "5.96 M YEARS", "Start of the salinity crisis, the same age across the basin", "Krijgsman et al., Nature 1999"),
          sat("A study published in", -2.1, 37.09, 0.12, "Gypsum hills at Sorbas, Almería"),
          photo("The gypsum in those", PH_YESARES, "Gypsum bands of the Yesares member, Sorbas, Spain"),
          stat("and the bands follow", "~21,000 YEARS", "One wobble of Earth's axis (precession): one gypsum band", "Krijgsman et al., Nature 1999"),
          sat("Count the bands, and", -2.07, 37.1, 0.04, "Gypsum layers, Sorbas")),
        P("At first the sea did not vanish. For a few hundred thousand years, water still came in from the Atlantic, but not enough. The sea grew saltier, and gypsum settled out in the shallow basins along its edges. Then, around five point six million years ago, the link to the ocean was cut almost completely. Now the sea fell. Rivers kept flowing in, but the sun took more than they brought, and the level dropped and dropped. Salt piled up on the deep floor, layer after layer, as the brine shrank, refilled and shrank again.",
          m(0, v(WMED, highlight=[dry(200)])),
          stat("For a few hundred", "5.96-5.6 M YEARS", "First stage: gypsum in shallow basins around the edges", WMS),
          sat("The sea grew saltier", 13.9, 37.45, 0.3, "Gypsum country in central Sicily", date=SPR),
          stat("Then, around five point", "5.59 M YEARS", "The Mediterranean loses its link to the Atlantic, until 5.33", WMS),
          m("Now the sea fell", v(MED, highlight=[dry(500)]), v(MED, at="and the level dropped", highlight=[dry(1500)])),
          photo("Salt piled up on", PH_DS2, "Salt forming in a shrinking sea: the Dead Sea"),
          photo("as the brine shrank", PH_TERR1, "Salt terraces, Dead Sea")),
        P("What would the dry basin have been like? Air that sinks warms up as it is squeezed, by about one degree Celsius for every hundred meters it goes down. A basin floor a kilometer below sea level would be about ten degrees hotter than the coast above it. Death Valley in California, less than a hundred meters below sea level, already holds the official record for the hottest air temperature ever measured.",
          m(0, v(MED, highlight=[dry(1500)])),
          m("Air that sinks warms", v(WMED, highlight=[dry(2500)])),
          stat("by about one degree", "~1 °C / 100 M", "How much sinking dry air warms as it is compressed", "Atmospheric physics, general"),
          stat("A basin floor a", "+10 °C", "Extra warmth on a floor 1 km below sea level (our calculation)", "Atmospheric physics, general"),
          sat("hotter than the coast", -2.2, 36.85, 0.3, "The coast of Almería, Spain"),
          sat("Death Valley in California", -116.83, 36.25, 0.15, "Badwater Basin, Death Valley, 86 m below sea level"),
          stat("already holds the official", "56.7 °C", "Highest air temperature on record, Death Valley, 1913", "World Meteorological Organization")),
        P("Near the very end, the water changed again. The last layers of the crisis hold the fossils of creatures from brackish lakes, the kind that lived in a great body of fresh and salty water that then stretched across Eastern Europe, ancestor of today's Black and Caspian Seas. Geologists call this phase the Lago Mare, the lake-sea. For a while, the Mediterranean was not a sea at all, but a chain of brackish lakes.",
          m(0, v(MED, highlight=[dry(600)])),
          stat("The last layers of", "LAGO MARE", "The crisis's last stage: brackish lakes with eastern fauna", WMS),
          m("the kind that lived", v({"lon": 38.0, "lat": 44.0, "span": 30}), text="Eastern Europe"),
          m("ancestor of today's Black", v({"lon": 42.0, "lat": 43.5, "span": 24}, places=[place("Black Sea", 34.0, 43.3, kind="site"), place("Caspian Sea", 50.5, 42.0, kind="site")])),
          photo("Geologists call this phase", PH_CABO_ROCK, "Rocks of Cabo de Gata, Spain"),
          m("For a while, the", v(MED, highlight=[dry(1500)]))),
        P("How far did it fall? On this map, the red is the sea floor that would lie bare if the Mediterranean dropped two hundred meters. At one and a half kilometers, the sea splits into separate salty lakes, and the Adriatic is gone entirely. Some geologists think parts of the basin fell even further. Others think the drop was smaller. We will come back to that, because the best evidence is buried under a river.",
          m(0, v(MED)),
          m("On this map, the", v(MED, highlight=[dry(200)])),
          m("would lie bare if", v({"lon": 5.0, "lat": 42.0, "span": 14}, highlight=[dry(200)])),
          m("At one and a half", v(MED, highlight=[dry(1500)])),
          m("and the Adriatic is", v({"lon": 16.0, "lat": 42.5, "span": 10}, highlight=[dry(1500)])),
          m("Some geologists think parts", v(MED, highlight=[dry(2500)])),
          m("Others think the drop", v(MED, highlight=[dry(600)])),
          photo("because the best evidence", PH_NILE_FOG, "The Nile valley and delta")),
    ]},
    {"title": "The Lost Canyons", "mood": "curious", "paragraphs": [
        P("In the 1960s, Egypt began building the Aswan High Dam on the Nile. Engineers drilled into the riverbed to see what the dam would stand on. A Soviet geologist working there, I. S. Chumakov, found something odd. Under the Nile's sand and gravel lay a deep, narrow gorge cut into the rock, and the bottom of it held marine sediments, laid down by the sea, far from any coast. At the time it made little sense. It took the salt from the Glomar Challenger to explain it.",
          sat(0, 32.88, 23.97, 0.15, "The Aswan High Dam"),
          m("on the Nile", v(NILEV, places=[ASWAN, CAIRO])),
          stat("A Soviet geologist working", "1960s", "Drilling for the Aswan High Dam finds a buried gorge under the Nile", WMS),
          sat("Under the Nile's sand", 32.89, 24.08, 0.08, "The Nile at Aswan"),
          stat("and the bottom of", "MARINE", "Sea sediments found deep under the Nile at Aswan", WMS),
          sat("far from any coast", 32.9, 24.2, 0.3, "The Nile valley north of Aswan"),
          m("At the time it", v(NILEV, highlight=[dry(1500)], places=[ASWAN])),
          m("It took the salt", v({"lon": 4.0, "lat": 39.0, "span": 8}, places=[BALEARIC]))),
        P("A river can only cut down as far as the water it flows into. If the Mediterranean had fallen far below the ocean, every river around it would have started cutting down too, chasing the falling shoreline. That is exactly what the Nile did. Its old canyon is still there, buried under the delta and the fields of Egypt. Near Cairo its floor lies about one and a half kilometers below the surface. Under the coast, it is about three kilometers down. That is deeper than the Grand Canyon, hidden under farmland and cities. Tens of millions of people now live on top of it, and most of them have no idea it is there.",
          photo(0, PH_NILE_ISS, "The Nile flowing into the Mediterranean"),
          m("If the Mediterranean had", v(NILEV, highlight=[dry(1500)], places=[CAIRO])),
          sat("every river around it", 12.45, 44.95, 0.4, "The Po delta, Italy"),
          sat("That is exactly what", 31.0, 30.6, 1.6, "The Nile delta"),
          photo("Its old canyon is", PH_NILE_MODIS, "The Nile delta, January 2026"),
          sat("Near Cairo its floor", 31.24, 30.05, 0.15, "Cairo"),
          chart("Under the coast, it", "How deep the buried Nile canyon goes", "m", [["Near Cairo", 1500], ["Under the coast", 3000], ["Grand Canyon", 1800]], NILE22 + "; US National Park Service", highlight=1),
          sat("hidden under farmland and", 31.4, 31.1, 0.2, "Farmland of the Nile delta"),
          sat("Tens of millions of", 31.0, 30.97, 0.1, "Tanta, in the middle of the delta")),
        P("When the Atlantic came back, the sea flooded into these canyons. The Nile's gorge became a long, narrow arm of the sea, reaching far up into Egypt, all the way to around Aswan. That is why the drillers there found marine sediments. Over the next few million years, the river filled its old canyon with mud and sand, and built the flat delta on top.",
          m(0, v(NILEV, places=[CAIRO, ASWAN])),
          sat("The Nile's gorge became", 30.85, 27.6, 0.4, "The Nile valley in Middle Egypt"),
          sat("all the way to", 32.65, 25.7, 0.3, "The Nile valley near Luxor"),
          sat("Over the next few", 31.3, 30.8, 0.3, "Delta fields north of Cairo"),
          photo("and built the flat", PH_NILE_FOG, "The Nile delta from orbit")),
        P("The Nile is not alone. Under the Rhône valley in France lies another buried canyon, hundreds of meters deep, found by drilling. Rivers elsewhere around the sea have them too. Each one is a record of how far down the sea went. Out under the sea itself, seismic surveys show the same story: a wide erosion surface, cut by rivers and waves into the slopes that lay bare before the water came back. And the rivers had time. The isolated phase lasted roughly two hundred and sixty thousand years.",
          sat(0, 4.6, 43.5, 0.5, "The Rhône delta, France"),
          m("Under the Rhône valley", v({"lon": 4.8, "lat": 44.7, "span": 5}, places=[LYON, ARLES])),
          sat("Rivers elsewhere around the", 0.85, 40.7, 0.4, "The Ebro delta, Spain"),
          m("Each one is a", v(MED, highlight=[dry(1000)])),
          m("Out under the sea", v({"lon": 5.0, "lat": 41.5, "span": 12}, highlight=[dry(1000)])),
          stat("a wide erosion surface", "EROSION SURFACE", "Seismic surveys trace a surface cut into the bare slopes", WMS),
          sat("into the slopes that", 3.2, 41.9, 0.3, "The Costa Brava, Spain"),
          sat("And the rivers had", 32.89, 24.08, 0.08, "The Nile at Aswan"),
          stat("The isolated phase lasted", "~260,000 YEARS", "From 5.59 to 5.33 million years ago (our calculation)", WMS)),
        P("So how far? For decades the usual answer was: very far, maybe one and a half to two kilometers or more in parts of the basin. In 2022 a team studying the Nile canyon came to a smaller number. From the depth and slope of the buried canyon, they estimated that during that phase the sea fell by about six hundred meters. It is still a lot. Six hundred meters is enough to empty much of the shallow sea floor around the coasts. And it shows the debate is not settled.",
          m(0, v(MED, highlight=[dry(2000)])),
          stat("maybe one and a", "1.5-2 KM+", "The classic estimate of the fall in parts of the basin", HSU),
          stat("In 2022 a team", "~600 M", "Sea-level fall in one phase of the crisis, from the Nile canyon", NILE22),
          sat("From the depth and", 30.9, 30.3, 0.4, "Where the Nile valley opens into the delta"),
          m("Six hundred meters is", v(MED, highlight=[dry(600)])),
          m("And it shows the", v({"lon": 12.0, "lat": 39.0, "span": 20}, highlight=[dry(600)]))),
    ]},
    {"title": "The Flood", "mood": "tension", "paragraphs": [
        P("Then, five point three three million years ago, it ended. The Atlantic came back. Africa and Spain were still close together, but somewhere at the western end, a weak point gave way. We do not know exactly why. Perhaps the land sank, or perhaps a stream cutting back from the Atlantic side broke through. Seawater began to spill over a ridge of rock into the empty basin far below.",
          stat(0, "5.33 M YEARS", "The Atlantic returns: the Zanclean flood", GC),
          sat("The Atlantic came back", -5.6, 35.95, 0.6, "The Strait of Gibraltar today"),
          m("We do not know", v(GIBV, highlight=[dry(500)])),
          sat("or perhaps a stream", -5.95, 35.75, 0.3, "Morocco's coast on the Atlantic side of the strait"),
          photo("Seawater began to spill", PH_GIB_STS, "The strait between Spain and Morocco")),
        P("At first it may have been a trickle. But water flowing over rock cuts into it, and the deeper the cut, the more water flows through. In 2009, a team led by Daniel Garcia-Castellanos published a model in Nature. In it, the flow grew until it tore a channel about two hundred kilometers long through the sea floor between Spain and Morocco. It was less a single waterfall than a long, steep rapid, cutting its own bed ever deeper. Seismic surveys and boreholes had already found that channel, buried under later sediment.",
          m(0, v(GIBV, places=[GIB])),
          photo("But water flowing over", PH_GIB11, "The strait from the shore"),
          sat("and the deeper the", -5.6, 36.01, 0.1, "Tarifa, at the strait's narrowest point"),
          stat("In 2009, a team", "2009", "Garcia-Castellanos and colleagues model the refill", GC),
          m("the flow grew until", v({"lon": -5.4, "lat": 36.0, "span": 4.5}, routes=[CHANNEL])),
          photo("It was less a", PH_ROCK_CL, "The Rock of Gibraltar in the clouds"),
          sat("Seismic surveys and boreholes", -5.45, 35.95, 0.25, "The narrowest part of the strait")),
        P("And then it went very fast. In their model, about ninety percent of the water arrived in a period of a few months to two years. At its peak, the flow through the strait reached around a hundred million cubic meters every second. That is about five hundred times the flow of the Amazon, the biggest river on Earth. And the sea level inside the basin may have risen by more than ten meters a day.",
          m(0, v(MED, routes=[FLOOD], highlight=[dry(1500)])),
          stat("about ninety percent of", "90 %", "Share of the water refilled in a few months to two years, in the model", GC),
          stat("At its peak, the", "10⁸ M³/S", "Peak flow through the strait in the model", GC),
          chart("That is about five", "Peak flood flow against the Amazon", "m³/s", [["Zanclean flood (model)", 100000000], ["Amazon (average)", 209000]], GC + "; Amazon average flow", highlight=0),
          m("And the sea level", v(MED, highlight=[dry(1500)]), v(MED, at="more than ten meters", highlight=[dry(200)]))),
        P("Ten meters a day is about the height of a three-story building, every single day, across a sea the size of the Mediterranean. If the model is right, the floor of the Strait of Gibraltar is a scar of that flood: a channel cut in a few years, then drowned and left under the sea.",
          m(0, v(WMED, highlight=[dry(1000)]), v(WMED, at="every single day", highlight=[dry(500)])),
          photo("across a sea the", PH_MODIS, "The Mediterranean from orbit"),
          m("If the model is", v({"lon": -5.4, "lat": 36.0, "span": 4.5}, routes=[CHANNEL])),
          photo("then drowned and left", PH_GIB23, "The Strait of Gibraltar today")),
        P("Picture the shore of a salty lake, far down in the dry basin. Week after week, the water climbs up the old slopes, ten meters a day, drowning salt flats, river valleys and canyons. The coastline you know today was being drawn in a matter of months.",
          photo(0, PH_LOMA, "Dry hills of Cabo de Gata, Spain"),
          photo("Week after week, the", PH_CABO_PAN, "Cabo de Gata, southeast Spain"),
          m("drowning salt flats, river", v(WMED, highlight=[dry(600)]), v(WMED, at="The coastline you know", highlight=[dry(200)]))),
        P("Once the western basin was full, the water had to get over another barrier: the shallow sill between Sicily and Africa. Researchers have described what may be the marks of that second spill: a huge heap of flood debris at the foot of the Malta Escarpment, reported in 2018, and more than three hundred streamlined ridges across the Sicily sill, reported in 2024. If the flood happened this way, it poured from the western Mediterranean into the eastern half.",
          m(0, v(SICV, places=[MALTA], highlight=[dry(500)])),
          sat("the shallow sill between", 10.98, 37.0, 0.4, "Cape Bon, Tunisia, facing Sicily"),
          stat("a huge heap of", "2018 · 2024", "Studies of possible flood marks off Malta and across the Sicily sill", "Micallef et al., Scientific Reports 2018; Communications Earth & Environment 2024"),
          sat("the Malta Escarpment, reported", 14.4, 35.9, 0.35, "Malta"),
          sat("streamlined ridges across the", 14.95, 36.85, 0.3, "Southeastern Sicily, at the edge of the sill", date=SPR),
          m("If the flood happened", v(SICV, routes=[SPILL], highlight=[dry(500)]))),
        P("Not everyone agrees. A 2020 review pointed out that other explanations are possible, and some researchers think the refill was slower or came in stages. But the core of the story is not in doubt. The Atlantic came back, and the age of salt was over. Geologists mark that moment as the start of a new chapter of Earth's history, the Pliocene, and its first stage is named the Zanclean, after Zancle, the ancient Greek name for Messina in Sicily.",
          stat(0, "DEBATED", "How fast the refill happened is still argued over", "Earth-Science Reviews, 2020"),
          m("and some researchers think", v(GIBV, routes=[FLOOD])),
          m("The Atlantic came back,", v(MED)),
          stat("Geologists mark that moment", "5.33 M YEARS", "Start of the Pliocene and its first stage, the Zanclean", "International Commission on Stratigraphy"),
          m("and its first stage", v({"lon": 15.0, "lat": 38.5, "span": 4}, places=[MESSINA])),
          sat("after Zancle, the ancient", 15.56, 38.19, 0.1, "Messina, ancient Zancle")),
    ]},
    {"title": "What It Left", "mood": "calm", "paragraphs": [
        P("The salt is still there. Under the floor of the Mediterranean it lies buried beneath younger mud, and its age is named after Messina too: the Messinian. In Sicily, where the land has been pushed up since, the same salt is mined. At Realmonte, near Agrigento, miners dig rock salt that was laid down when the sea dried out. Sicily is one of the few places where you can touch the crisis on dry land, because the movement of the plates lifted its salt and gypsum above the sea.",
          m(0, v(MED, places=[MESSINA])),
          stat("and its age is", "MESSINIAN", "The age of the salt, named after Messina, Sicily", "International Commission on Stratigraphy"),
          sat("In Sicily, where the", 14.0, 37.5, 1.4, "Sicily", date=SPR),
          m("At Realmonte, near Agrigento", v({"lon": 13.6, "lat": 37.35, "span": 1.2}, places=[REALMONTE])),
          sat("miners dig rock salt", 13.47, 37.31, 0.04, "The Realmonte salt mine", date=SPR),
          sat("Sicily is one of", 13.75, 37.45, 0.3, "Gypsum hills of the Platani valley, Sicily", date=SPR)),
        P("The same rocks gave Sicily another treasure. Sulfur formed in the gypsum of the crisis, and in the nineteenth century the island's sulfur mines supplied most of the world's sulfur, dug out by hand, often by children.",
          sat(0, 14.05, 37.5, 0.3, "Old mining country near Caltanissetta, Sicily", date=SPR),
          stat("and in the nineteenth", "1800s", "Sicily's sulfur mines lead world production", "Wikipedia, Sulfur mining in Sicily"),
          sat("dug out by hand", 13.95, 37.42, 0.08, "The hills of the Sicilian sulfur basin", date=SPR)),
        P("In Spain, near Sorbas in Almería, you can walk through hills of gypsum from the crisis. Under the sea, the deep salt is so heavy and soft that it slowly flows, bending the layers above it. Off Israel, gas companies drilling for fields such as Leviathan, discovered in 2010, have had to drill through the salt to reach the gas below it.",
          m(0, v({"lon": -2.2, "lat": 37.0, "span": 1.5}, places=[SORBAS])),
          photo("you can walk through", PH_GYP_C, "Gypsum layers"),
          m("Under the sea, the", v({"lon": 18.0, "lat": 37.0, "span": 40}, highlight=[dry(2500)])),
          stat("that it slowly flows", "SALT FLOWS", "Buried salt creeps slowly, folding the rock above it", "General geology"),
          stat("Off Israel, gas companies", "LEVIATHAN", "Gas field off Israel, below the Messinian salt", "Industry and press reports"),
          sat("have had to drill", 34.95, 32.8, 0.3, "The coast at Haifa, Israel")),
        P("Could it happen again? The Mediterranean still needs the Atlantic to stay full. And Africa is still moving toward Europe, a few millimeters a year. Over millions of years, that could close the strait again. If it does, the sea will start to shrink, and in about a thousand years its deep basins will be lakes of brine once more. Nobody alive will see it. But the salt under the sea says it has happened before.",
          m(0, v(GIBV, routes=[INFLOW])),
          m("And Africa is still", v(EUAF, routes=[NORTH])),
          photo("Over millions of years", PH_ROCK, "The Rock of Gibraltar"),
          sat("that could close the", -5.45, 35.95, 0.25, "The Strait of Gibraltar"),
          m("If it does, the", v(MED, highlight=[dry(200)])),
          m("in about a thousand", v(MED, highlight=[dry(1500)])),
          photo("Nobody alive will see", PH_ISS_MED, "The Mediterranean from orbit")),
    ]},
    {"title": "The Desert Under the Sea", "mood": "calm", "paragraphs": [
        P("Put it together. Africa pushed north, the seaways closed, and the sun took the water faster than the rivers could bring it. More than a million cubic kilometers of salt were left on the floor. The rivers cut canyons down toward the falling shore. And then, five point three three million years ago, the Atlantic came back through Gibraltar, perhaps in less than two years. Every part of that story was pieced together from drill cores, buried canyons and salt.",
          m(0, v(EUAF, routes=[NORTH])),
          m("the seaways closed, and", v({"lon": -4.0, "lat": 36.0, "span": 9}, routes=[BETIC, RIFIAN])),
          m("More than a million", v(MED, highlight=[dry(1500)])),
          photo("The rivers cut canyons", PH_NILE_MODIS, "The Nile and its delta"),
          m("And then, five point", v(GIBV, routes=[FLOOD], places=[GIB])),
          stat("came back through Gibraltar", "< 2 YEARS", "The refill in the Garcia-Castellanos model", GC),
          photo("Every part of that", PH_DRILL, "A drill bit from the Glomar Challenger")),
        P("So the next time you stand on a Mediterranean beach, think about what lies under the water. Below the blue, below the mud, is a layer of salt left by a sea that once nearly disappeared. Under the deltas are canyons cut by rivers that chased a falling sea. And at the western end is a channel torn open by one of the biggest floods we know of.",
          photo(0, PH_MONSUL, "Playa de Mónsul, Cabo de Gata"),
          m("Below the blue, below", v(MED, highlight=[dry(1500)])),
          photo("left by a sea", PH_TERR2, "Salt crust, Dead Sea"),
          sat("Under the deltas are", 31.2, 31.3, 0.6, "The edge of the Nile delta"),
          sat("rivers that chased a", 4.6, 43.5, 0.5, "The Rhône delta, France"),
          photo("And at the western", PH_GIB11, "The Strait of Gibraltar"),
          m("one of the biggest", v(MED, routes=[FLOOD]))),
        P("Here is my question for you. If you could stand on the floor of the dry Mediterranean six million years ago, where would you go first: down into the Nile canyon, out to the salt lakes of the deep basin, or to the edge at Gibraltar to watch the Atlantic come in?",
          photo(0, PH_EGYPT, "Egypt and the Mediterranean from orbit"),
          m("on the floor of", v(MED, highlight=[dry(1500)], places=[GIB, CAIRO])),
          m("down into the Nile", v(NILEV, highlight=[dry(1500)], places=[CAIRO])),
          m("out to the salt", v(WMED, highlight=[dry(1500)])),
          photo("or to the edge", PH_ROCK_CL, "The Rock of Gibraltar"),
          ask=("where would you go", "Nile canyon, salt lakes, or Gibraltar?")),
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
    "title": "How the Mediterranean Sea Dried Up",
    "voice": "am_michael",
    "voice_speed": 1.15,
    "music": "procedural",
    "map_style": "satellite",
    "look": "none",
    "sources": ["episodes/mediterranean-dried/research.md and factcheck.md", "Contains modified Copernicus Sentinel data 2026"],
    "thumbnail": {"text": "DRIED UP?"},
    "chapters": chapters,
    "youtube": {
        "title": "How the Mediterranean Sea Dried Up",
        "description": "About six million years ago the Mediterranean was cut off from the Atlantic and almost completely dried out, leaving a deep basin floored with salt. This video follows the clues: the salt a drill ship pulled from under the sea floor in 1970, the canyon buried beneath the Nile, how far the sea fell, and the flood through Gibraltar that may have refilled it in less than two years. And could it happen again?",
        "tags": ["Mediterranean", "Mediterranean Sea dried up", "Messinian salinity crisis", "Zanclean flood", "Strait of Gibraltar", "Glomar Challenger", "Kenneth Hsü", "Nile canyon", "geology", "megaflood", "geography", "satellite images"],
        "pinned_comment": "If you could stand on the floor of the dry Mediterranean six million years ago, where would you go first: the Nile canyon, the salt lakes of the deep basin, or Gibraltar to watch the Atlantic come in?",
    },
}
out = HERE / "script.json"
out.write_text(json.dumps(script, ensure_ascii=False, indent=1) + chr(10), encoding="utf-8")
words = sum(len(p["text"].split()) for c in chapters for p in c["paragraphs"])
shots = [s for c in chapters for p in c["paragraphs"] for s in p["shots"]]
kinds = {k: sum(1 for s in shots if s["type"] == k) for k in ("map", "photo", "stat", "document", "chart")}
print(f"{words} words, {len(chapters)} chapters, {len(shots)} shots {kinds}")
