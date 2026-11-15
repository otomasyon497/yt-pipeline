"""Builds script.json for mongolia-empty.  python build_script.py

Same production logic as episodes/northern-maine-empty (hook template, numbered reasons, painted regions without
push-in, hand-placed shots with varied seasons, a photo or map frame at most twice). Sources: research.md.
Regions: geo/make_regions.py.
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
    view = view or ME
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



MN = {"lon": 103.0, "lat": 46.8, "span": 30}
ASIA = {"lon": 100.0, "lat": 47.0, "span": 75}
GOBI = "file:gobi.geojson"
SUM = "2024-07-01/2024-08-31"
WIN = "2024-01-10/2024-03-01"
AUT = "2023-09-20/2023-10-15"

NSO = "National Statistics Office of Mongolia, livestock census"
UN = "United Nations; FAO GIEWS; UNDP"
WB = "World Bank"

PH_ALTAI = "File:Altai Tavan Bogd - panoramio.jpg"
PH_GLACIER = "File:Altai Tavan Bogd - Potanin glacier - panoramio.jpg"
PH_CAMELS = "File:Camels in Gobi Desert 02.jpg"
PH_DUNES = "File:Camels at Khongoryn Els 01.jpg"
PH_ZUD_GOATS = "File:Zud 2.JPG"
PH_ZUD_CAMEL = "File:Zud 1.JPG"
PH_BAYANZAG = "File:Bayanzag 10.jpg"
PH_BAYANZAG2 = "File:Bayanzag 07.jpg"
PH_GENGHIS = "File:Genghis Khan Equestrian Statue.jpg"
PH_POLO = "File:The book of Ser Marco Polo - the Venetian concerning the kingdoms and marvels of the East (1903) (14766426971).jpg"
PH_GERDIST = "File:Ger district of Ulaanbaatar.jpg"
PH_NALAIKH = "File:Ger district of Nalaikh.jpg"
PH_YURT = "File:Yurt in Gobi Desert.jpg"
PH_OVOO = "File:Ovoo in Gobi Desert.jpg"
PH_SHEEP = "File:Sheep herd (2540223383).jpg"
PH_GOATS = "File:Goat herd in mongolia.jpg"
PH_STEPPE = "File:Mongolian nature steppe and mountain.jpg"
PH_NAADAM = "File:Naadam 2023 - Horse racing 06.jpg"
PH_HOVSGOL = "File:On Lake Hovsgol (3756943119).jpg"
PH_ORKHON = "File:Orkhon River Valley (25156751117).jpg"
PH_HORSE = "File:Orkhon River Valley (25156845687).jpg"
PH_STORM = "File:Orkhon River Valley (40027403011).jpg"
PH_BUCKET = "File:Socialist Mongolia Herder Award Bucket (35703718785).jpg"
PH_TRAIN = "File:Trans-Mongolian Railway (49309525323).jpg"
PH_UB = "File:Ulaanbaatar 377 (26274377965).jpg"
PH_UB2 = "File:Ulaanbaatar city Mongolia 20230926 102617.jpg"
PH_OT_CAMP = "File:Oyu Tolgoi 16.JPG"

UB = place("Ulaanbaatar", 106.92, 47.92)
DARKHAN, ERDENET = place("Darkhan", 105.95, 49.47), place("Erdenet", 104.05, 49.03)
OLGII, DALAN = place("Ölgii", 89.97, 48.97), place("Dalanzadgad", 104.42, 43.57)
BAYANZAG = place("Bayanzag", 103.73, 44.14, "Flaming Cliffs (Bayanzag)", "site")
OYU = place("Oyu Tolgoi", 106.86, 43.0, "Oyu Tolgoi copper mine", "site")
TAVAN = place("Tavan Tolgoi", 105.55, 43.6, "Tavan Tolgoi coal", "site")
KARAKORUM = place("Karakorum", 102.83, 47.2, "Karakorum", "site")
BEIJING, MOSCOW = place("Beijing", 116.4, 39.9), place("Moscow", 37.6, 55.75)
RAIL = {"from": [106.4, 51.9], "via": [[106.2, 50.2], [106.92, 47.92], [108.3, 46.4], [110.1, 44.9]], "to": [111.9, 43.72],
        "mode": "line", "color": "accent", "seconds": 2.0, "label": "Trans-Mongolian railway"}
COAL = {"from": [105.55, 43.6], "via": [[106.6, 43.3]], "to": [107.35, 42.7], "mode": "line", "color": "red", "seconds": 1.5, "label": "Coal to China"}

chapters = [
    {"title": "One Dot of Light", "mood": "curious", "paragraphs": [
        P("Mongolia sits between Russia and China, and it is huge: more than one and a half million square kilometers, almost three times the size of France. About three and a half million people live there. That makes it the most thinly populated independent country on Earth. And roughly half of those people live in a single city. At night, from orbit, the whole country is one bright dot and a few sparks.",
          m(0, v(ASIA, highlight=["Mongolia@red", "Russia@accent", "China@accent"])),
          m("and it is huge", v(MN, highlight=["Mongolia@red"])),
          stat("almost three times the", "1,564,116 KM²", "Mongolia's area: about 2.8 times metropolitan France (our calculation)", "Wikipedia, Mongolia; INSEE"),
          photo("About three and a", PH_STEPPE, "The Mongolian steppe"),
          stat("That makes it the", "~2 / KM²", "People per square kilometer: the lowest of any sovereign state", "Wikipedia, Mongolia"),
          photo("And roughly half of", PH_UB, "Ulaanbaatar"),
          m("At night, from orbit", v(MN, layer="night", places=[UB])),
          m("the whole country is", v({"lon": 104.5, "lat": 47.5, "span": 14}, layer="night", places=[UB, DARKHAN, ERDENET]))),
        P("Mongolia touches only two countries, Russia to the north and China to the south, and it has no coast at all. The nearest sea is hundreds of kilometers away, across China. Its population has grown: from about eight hundred and forty-five thousand at the 1956 census, to about two million in 1989, to about three point three million in 2020. But most of that growth went into towns. Today around seven in ten Mongolians live in cities.",
          m(0, v(ASIA, highlight=["Russia@accent", "China@accent", "Mongolia@red"])),
          m("and China to the", v({"lon": 110.0, "lat": 42.0, "span": 22}, highlight=["China@accent", "Mongolia@red"])),
          m("The nearest sea is", v({"lon": 112.0, "lat": 43.0, "span": 30}, highlight=["Mongolia@red"], places=[BEIJING])),
          chart("Its population has grown", "People in Mongolia", "census", [["1956", 845481], ["1989", 1987274], ["2020", 3296866]], "Mongolian census, via Wikipedia", reveal=["to about two million", "to about three point"], highlight=2),
          sat("But most of that", 106.95, 47.92, 0.15, "Ulaanbaatar spreading up its valley"),
          stat("Today around seven in", "69 %", "Share of Mongolians living in towns and cities, 2023", "CIA World Factbook")),
        P("Out there is the coldest capital city in the world, and a lake that holds most of the country's fresh water. There are more horses, sheep, goats, cattle and camels than people, many times over. And in the south, in 1923, explorers dug up the first dinosaur eggs anyone recognized as dinosaur eggs. So why is Mongolia so empty? There are five reasons, and the first is the ground itself: it is too high, too dry and too cold.",
          sat(0, 106.92, 47.92, 0.25, "Ulaanbaatar in winter", date=WIN),
          photo("There are more horses", PH_SHEEP, "Sheep and goats on the steppe"),
          photo("camels than people, many", PH_CAMELS, "Bactrian camels in the Gobi"),
          photo("And in the south", PH_BAYANZAG, "The Flaming Cliffs, Bayanzag"),
          stat("the first dinosaur eggs", "1923", "First recognized dinosaur eggs found at the Flaming Cliffs, Gobi", "American Museum of Natural History"),
          m("So why is Mongolia", v(ASIA, highlight=["Mongolia@red"], places=[UB])),
          sat("There are five reasons", 99.5, 47.5, 0.5, "The Khangai mountains"),
          photo("it is too high", PH_ALTAI, "The Altai mountains, western Mongolia"),
          ask=("So why is Mongolia", "Why is Mongolia so empty?")),
    ]},
    {"title": "Too High, Too Dry, Too Cold", "mood": "curious", "paragraphs": [
        P("Reason one. The land is too high, too dry and too cold. The average point in Mongolia stands about one thousand five hundred and eighty meters above the sea. It is about as far from any ocean as you can get. Mountains ring it on the west and north, and the moist air from the seas never makes it this far.",
          m(0, v(MN, highlight=["Mongolia@red"], places=[UB])),
          stat("The average point in", "1,580 M", "Mongolia's average height above sea level", "Geography of Mongolia"),
          m("It is about as", v({"lon": 95.0, "lat": 40.0, "span": 60}, highlight=["Mongolia@red"])),
          photo("Mountains ring it on", PH_GLACIER, "The Potanin glacier, Altai Tavan Bogd"),
          sat("and the moist air", 90.0, 48.9, 0.6, "The Altai, Mongolia's western wall")),
        P("So the winters are brutal. In January the average temperature in parts of the country falls to around minus thirty degrees. Ulaanbaatar, at about thirteen hundred meters, is the coldest national capital in the world; across a whole year, its average hovers around freezing. And the sky is clear more than two hundred and fifty days a year.",
          sat(0, 100.0, 49.5, 0.5, "Northern Mongolia in winter", date=WIN),
          stat("In January the average", "−30 °C", "January averages in the coldest parts of Mongolia", "Wikipedia, Mongolia"),
          sat("Ulaanbaatar, at about thirteen", 106.9, 47.9, 0.12, "Ulaanbaatar from orbit"),
          photo("across a whole year", PH_STORM, "Storm over the Orkhon valley"),
          stat("And the sky is", "250+ DAYS", "Sunny days a year in Mongolia", "Wikipedia, Mongolia")),
        P("The south is drier still. The Gobi covers much of it, about two fifths of the country by Mongolia's own count. In the Gobi only fifty to a hundred millimeters of rain fall in a year, and some places get none at all for years. Even in the wetter north it is around three hundred. That is less than half of what falls on Paris.",
          paint(0, GOBI + "@red", view=MN, places=[UB]),
          stat("about two fifths of", "41 %", "Share of Mongolia that is Gobi desert and desert steppe", "Mongolian studies, Springer 2021"),
          sat("In the Gobi only", 102.2, 43.78, 0.4, "Khongoryn Els, the singing dunes"),
          chart("Even in the wetter", "Rain and snow in a year", "mm", [["Gobi", 75], ["Northern Mongolia", 310], ["Paris", 640]], "Geography of Mongolia; Météo-France", highlight=0),
          photo("That is less than", PH_DUNES, "Camels below the Khongoryn Els dunes")),
        P("Put cold and dry together and you get a land where very little can be farmed. Less than one percent of Mongolia is arable. Around Ulaanbaatar the ground is free of frost only from about mid-May to late August. And three quarters of the land has already been degraded by drought, overgrazing and wind. In 2026 Mongolia hosted the United Nations conference on desertification.",
          sat(0, 105.9, 49.4, 0.3, "Land near Darkhan, in the north"),
          stat("Less than one percent", "0.7 %", "Share of Mongolia's land that is arable", "CIA World Factbook, 2023"),
          sat("Around Ulaanbaatar the ground", 107.1, 47.85, 0.3, "Hills east of Ulaanbaatar in October", date=AUT),
          stat("And three quarters of", "76.9 %", "Mongolia's land degraded, 2020 national assessment", "Mongolian Mining Journal; MJGG"),
          sat("by drought, overgrazing and", 104.5, 45.5, 0.4, "Dry steppe, central Mongolia"),
          photo("In 2026 Mongolia hosted", PH_OVOO, "An ovoo, a sacred cairn, in the Gobi")),
        P("There is water in the far north. Lake Khövsgöl, up against the Russian border, is about two hundred and sixty-seven meters deep and holds around seventy percent of Mongolia's fresh water. But it sits in larch forest and mountains where the lake freezes over for months. In the far west, the Altai mountains rise to four thousand three hundred and seventy-four meters at Khüiten Peak, and glaciers fill the valleys.",
          sat(0, 100.5, 51.1, 0.9, "Lake Khövsgöl from orbit"),
          stat("is about two hundred", "~70 %", "Share of Mongolia's fresh water held in Lake Khövsgöl", "Wikipedia, Lake Khövsgöl"),
          photo("But it sits in", PH_HOVSGOL, "Lake Khövsgöl"),
          sat("where the lake freezes", 100.5, 51.0, 0.6, "Khövsgöl frozen in winter", date=WIN),
          stat("In the far west", "4,374 M", "Khüiten Peak, Mongolia's highest point, in the Altai", "Wikipedia, Mongolia"),
          photo("at Khüiten Peak", PH_ALTAI, "The Altai Tavan Bogd range"),
          sat("and glaciers fill the", 87.85, 49.15, 0.25, "Glaciers of Altai Tavan Bogd")),
        P("Even there, people live by animals. In Bayan-Ölgii, the westernmost province, most people are Kazakhs, and some still hunt foxes in winter with trained golden eagles. Since 1999 they have held a Golden Eagle Festival there every autumn. Across the whole country, Kazakhs are about four percent of the population. Everywhere else, the herders are Mongols.",
          m(0, v({"lon": 91.0, "lat": 48.5, "span": 6}, places=[OLGII])),
          sat("and some still hunt", 89.97, 48.97, 0.12, "Ölgii, capital of Bayan-Ölgii"),
          stat("Since 1999 they have", "1999", "The first Golden Eagle Festival, Ölgii", "Wikipedia, Golden Eagle Festival"),
          stat("Across the whole country", "3.8 %", "Kazakhs in Mongolia's population, 2020 census", "Wikipedia, Demographics of Mongolia"),
          sat("Everywhere else, the herders", 96.5, 46.0, 0.4, "Pasture in the Gobi-Altai")),
        P("And yet the ground was never empty of life. In 1923 an American expedition led by Roy Chapman Andrews reached red cliffs in the Gobi and found nests of fossil eggs, the first that scientists recognized as dinosaur eggs. Andrews called the place the Flaming Cliffs, for the way they glow in the evening sun. One skeleton lay right on top of a nest, and Andrews named the animal Oviraptor, the egg thief, assuming it had died stealing eggs. In 1993 an expedition from the same museum found one sitting on its own nest. It had been brooding its eggs, not robbing them. Those cliffs are sandstone, laid down as dunes in a desert some seventy-five million years ago. The Gobi was not always a desert. But it has been one for a very long time.",
          sat(0, 103.73, 44.14, 0.08, "Bayanzag, the Flaming Cliffs"),
          m("In 1923 an American", v({"lon": 104.0, "lat": 44.5, "span": 6}, places=[BAYANZAG, DALAN])),
          photo("found nests of fossil", PH_BAYANZAG2, "The Flaming Cliffs"),
          photo("Andrews called the place", PH_BAYANZAG, "Bayanzag in the evening light"),
          stat("One skeleton lay right", "OVIRAPTOR", "The egg thief, named in 1924; in 1993 found brooding its own nest", "American Museum of Natural History"),
          m("assuming it had died", v({"lon": 103.7, "lat": 44.1, "span": 1.4}, places=[BAYANZAG])),
          stat("In 1993 an expedition", "1993", "An AMNH team finds an oviraptorid sitting on its own nest", "American Museum of Natural History"),
          sat("Those cliffs are sandstone", 103.4, 44.3, 0.15, "Red sandstone badlands of the Gobi"),
          sat("The Gobi was not", 103.5, 43.5, 0.5, "The Gobi")),
    ]},
    {"title": "A Land for Herds", "mood": "calm", "paragraphs": [
        P("Reason two. This land feeds animals, not crops. Where wheat will not grow, grass still does, thin and short, but it covers hundreds of thousands of square kilometers. For thousands of years the people of Mongolia lived the only way that grass allowed: as herders, moving with their animals to fresh pasture with the seasons, carrying their homes with them.",
          sat(0, 103.0, 47.0, 0.4, "Steppe in the Khangai foothills"),
          photo("Where wheat will not", PH_ORKHON, "Herds in the Orkhon valley"),
          sat("but it covers hundreds", 110.0, 47.5, 0.6, "The eastern steppe"),
          photo("For thousands of years", PH_GOATS, "A herd on the dry steppe"),
          sat("as herders, moving with", 101.5, 47.2, 0.3, "Khangai valleys"),
          photo("carrying their homes with", PH_YURT, "A ger in the Gobi")),
        P("That home is the ger, a round tent of felt over a wooden frame that a family can take down in an hour or two and load onto a camel or a truck. Its door traditionally faces south. In summer, families camp near water; in winter, they move to sheltered valleys with pens for the animals. A herd needs room. In a dry year, a family may move many times to find grass, and the pasture is shared, not fenced. A place that feeds people this way can only feed a few of them per square kilometer.",
          photo(0, PH_POLO, "Gers on carts, from a 1903 edition of Marco Polo"),
          stat("a round tent of", "~2 HOURS", "Time a family needs to take down a ger and pack it", "Wikipedia, Yurt"),
          sat("take down in an", 102.9, 46.3, 0.05, "Övörkhangai steppe"),
          photo("load onto a camel", PH_CAMELS, "Bactrian camels, the Gobi's pack animals"),
          sat("In summer, families camp", 101.2, 47.7, 0.12, "River valleys in Arkhangai"),
          sat("in winter, they move", 101.0, 47.4, 0.12, "Sheltered valleys in Arkhangai"),
          sat("A herd needs room", 101.0, 46.4, 0.3, "Pasture in the Khangai"),
          sat("In a dry year", 106.5, 45.0, 0.3, "Dry pasture in the Middle Gobi", date=AUT),
          sat("A place that feeds", 112.0, 47.0, 0.4, "The open steppe near the Chinese border")),
        P("And the animals far outnumber the people. At the end of 2023 Mongolia counted about sixty-four point seven million head of livestock. Mongolians call them the five snouts: sheep, goats, cattle, horses and camels. Almost nine in ten were sheep and goats. Even the horses alone outnumber the people. Goats matter most to the herders' cash, because their soft under-hair is sold as cashmere. Mongolia is the world's second-largest producer of raw cashmere, after China. That is roughly twenty animals for every person in the country.",
          sat(0, 100.8, 48.6, 0.3, "Herds on the Khangai slopes"),
          stat("At the end of", "64.7 M", "Livestock in Mongolia at the end of 2023", NSO),
          photo("Mongolians call them the", PH_DUNES, "Camels below the Khongoryn Els dunes"),
          chart("Almost nine in ten", "Mongolia's herd by kind (2018)", "%", [["Sheep", 46.0], ["Goats", 40.8], ["Cattle", 6.6], ["Horses", 5.9], ["Camels", 0.7]], "National Statistics Office, via AKIpress"),
          stat("Even the horses alone", "3.9 M", "Horses in Mongolia, 2018 (5.9 % of 66.5 M); people: 3.3 M (our calculation)", NSO),
          sat("Goats matter most to", 105.2, 45.0, 0.25, "Goat pasture in the Middle Gobi"),
          stat("That is roughly twenty", "~20", "Animals per person in Mongolia, end of 2023 (our calculation)", NSO)),
        P("And the herds have been growing. In 2018 the count reached sixty-six and a half million, the most since Mongolia began counting its animals in 1918. More goats mean more cashmere, but goats pull grass up by the roots and cut the soil with their hooves. Overgrazing is one of the main reasons so much of the land is wearing out. In 2018 there were about two hundred and thirty thousand herding households. The steppe can only carry so many animals, and so it can only carry so many herders.",
          stat(0, "66.5 M", "Livestock counted in 2018, a record since counting began in 1918", "National Statistics Office, via AKIpress"),
          sat("the most since Mongolia", 108.5, 48.5, 0.4, "Steppe in Khentii in October", date=AUT),
          sat("More goats mean more", 104.8, 45.8, 0.3, "Grazed steppe, central Mongolia", date=AUT),
          photo("but goats pull grass", PH_GOATS, "Goats on bare ground"),
          sat("Overgrazing is one of", 107.5, 45.3, 0.3, "Worn pasture near the Gobi"),
          stat("In 2018 there were", "230,800", "Herding households with livestock, 2018", "National Statistics Office, via AKIpress"),
          sat("The steppe can only", 113.0, 47.8, 0.5, "The eastern steppe")),
        P("Horses still matter here more than almost anywhere. Every summer at Naadam, the national festival, listed by UNESCO since 2010, Mongolians hold wrestling, archery and horse racing, and children ride horses in races across the open steppe, some of them many kilometers long. It is a country built around animals. But that also means a country that depends, every winter, on the weather.",
          photo(0, PH_HORSE, "A horse in the Orkhon valley"),
          photo("Every summer at Naadam", PH_NAADAM, "Naadam horse race, 2023"),
          stat("wrestling, archery and horse", "3 GAMES", "Naadam's three contests: wrestling, archery, horse racing", "UNESCO, Naadam"),
          sat("some of them many", 106.55, 47.85, 0.15, "Open steppe west of Ulaanbaatar"),
          sat("It is a country", 102.7, 47.6, 0.3, "Orkhon valley grassland"),
          sat("But that also means", 102.7, 47.6, 0.6, "The same grassland in October", date=AUT)),
    ]},
    {"title": "The White Death", "mood": "tension", "paragraphs": [
        P("Reason three. The winters kill. Mongolians have a word for it: dzud. A dzud comes when a dry summer leaves the animals thin, and then deep snow, ice or extreme cold covers the grass so they cannot reach it. Animals that cannot graze for weeks starve and freeze, by the million. They do not die in one night. They weaken over weeks, and the herders can only watch.",
          sat(0, 110.0, 46.5, 0.5, "The eastern steppe, where the 2024 losses were heavy", date=AUT),
          stat("Mongolians have a word", "DZUD", "A summer drought, then a winter of snow, ice or cold that starves the herds", "UN OCHA"),
          sat("A dzud comes when", 103.5, 46.8, 0.3, "Pasture after a dry summer", date=AUT),
          sat("and then deep snow", 105.0, 46.0, 0.4, "Pasture in central Mongolia"),
          photo("Animals that cannot graze", PH_ZUD_GOATS, "Animals lost in a dzud"),
          sat("They do not die", 105.5, 46.8, 0.3, "Central Mongolian pasture", date=AUT),
          sat("They weaken over weeks", 111.0, 45.6, 0.3, "Pasture in Dornogovi")),
        P("In the winter of 2009 and 2010 more than ten million animals died, about a quarter of all the livestock in the country, according to the United Nations. In 2023 and 2024 it happened again. By late April about seven million animals were dead; a later United Nations assessment put the losses at eight point one million. The national herd fell from sixty-four point seven million to fifty-seven point six million in a single year.",
          stat(0, "10 M+", "Animals killed in the 2009-2010 dzud: about a quarter of all livestock", UN),
          sat("about a quarter of", 101.0, 47.8, 0.4, "The Khangai in winter", date=WIN),
          photo("In 2023 and 2024", PH_ZUD_CAMEL, "A camel lost in a dzud"),
          stat("a later United Nations", "8.1 M", "Animals lost in the 2023-2024 dzud (UNDP assessment)", UN),
          chart("The national herd fell", "Livestock in Mongolia", "million head", [["End of 2023", 64.7], ["End of 2024", 57.6]], NSO, reveal=["to fifty-seven point six"], highlight=1)),
        P("Early forecasts warned that sixteen million animals could die, and the Red Cross launched an emergency appeal. Roads were buried. Families in remote camps ran out of hay and fuel, and aid groups reported children missing school because they were needed to keep the surviving animals alive. In some provinces in the south and east, the losses were worst of all. Dzuds are not new. A run of them from 1999 to 2002 killed millions of animals, and the 2010 dzud was worse. But now they come close together: the winters of 2022 to 2023 and 2023 to 2024 were both dzuds, and Mongolia's government says the country has warmed by more than two degrees since 1940, faster than most of the world.",
          stat(0, "16 M", "Animals an early-March 2024 forecast said could die (the final toll was lower)", "bne IntelliNews"),
          sat("Roads were buried. Families", 112.0, 46.0, 0.5, "Steppe in Sükhbaatar province", date=AUT),
          sat("and aid groups reported", 110.5, 44.5, 0.4, "Dornogovi, among the worst-hit provinces"),
          stat("In some provinces in", "4", "Worst-hit provinces in spring 2024: Sükhbaatar, Dornogovi, Govisümber, Khentii", "FAO GIEWS, May 2024"),
          sat("Dzuds are not new", 109.0, 47.5, 0.4, "Khentii in winter", date=WIN),
          sat("But now they come", 98.5, 48.5, 0.5, "Western Mongolia in winter", date=WIN),
          stat("and Mongolia's government says", "+2 °C", "Warming in Mongolia since 1940, government figures", "Mongolia's national communications to the UNFCCC"),
          m("faster than most of", v({"lon": 100.0, "lat": 47.0, "span": 40}, highlight=["Mongolia@red"]))),
        P("For a herding family, a dzud can wipe out everything they own in a few weeks. A family with no animals has nothing to live on in the countryside. So many of them do what poor rural families everywhere do. They pack up and go to the city. And in Mongolia there is really only one city to go to.",
          sat(0, 108.5, 47.3, 0.3, "Winter camps on the steppe", date=WIN),
          sat("A family with no", 104.0, 47.5, 0.4, "Herding country, central Mongolia"),
          m("They pack up and", v(MN, places=[UB], routes=[{"from": [100.0, 46.0], "to": [106.92, 47.92], "mode": "line", "color": "red", "seconds": 1.5}, {"from": [112.5, 46.5], "to": [106.92, 47.92], "mode": "line", "color": "red", "seconds": 1.5}, {"from": [104.0, 44.0], "to": [106.92, 47.92], "mode": "line", "color": "red", "seconds": 1.5}])),
          photo("And in Mongolia there", PH_UB2, "Ulaanbaatar")),
    ]},
    {"title": "Empire, Then Empty", "mood": "calm", "paragraphs": [
        P("Reason four is history. Eight hundred years ago this was the center of the world. In 1206 a chief named Temüjin took the title Genghis Khan, and his armies built the largest connected land empire there has ever been. At its height it stretched from Korea to Hungary. Its capital, Karakorum, stood in the Orkhon valley. But an empire run from horseback never needed big cities at home, and when it broke up, the herders were still herders.",
          photo(0, PH_GENGHIS, "Genghis Khan statue, Tsonjin Boldog"),
          m("In 1206 a chief", v({"lon": 75.0, "lat": 45.0, "span": 100}, highlight=["Mongolia@red"])),
          stat("and his armies built", "1206", "Temüjin takes the title Genghis Khan and founds the Mongol Empire", "Wikipedia, Mongolia"),
          m("At its height it", v({"lon": 75.0, "lat": 45.0, "span": 105}, highlight=["Mongolia@red", "South Korea@accent", "Hungary@accent"])),
          sat("Its capital, Karakorum, stood", 102.84, 47.2, 0.06, "Karakorum and the Erdene Zuu monastery"),
          photo("But an empire run", PH_POLO, "Mongol camp, from a 1903 edition of Marco Polo"),
          sat("and when it broke", 102.7, 47.5, 0.4, "The Orkhon valley today")),
        P("His grandson Kublai Khan founded the Yuan dynasty in 1271 and went on to rule all of China. When that dynasty fell in 1368, the Mongols went back to the steppe. Later the Qing dynasty of China ruled the country for more than two centuries. When the Qing collapsed in 1911, Mongolia declared independence under a Buddhist ruler, the Bogd Khan. In 1921 a revolution backed by Soviet Russia broke away, and in 1924 Mongolia became a people's republic, the first Soviet satellite state. In the late 1930s, under the leader Khorloogiin Choibalsan, a wave of purges killed more than twenty thousand people, among them an estimated seventeen thousand Buddhist monks. In the 1950s the herds were put into state collectives; by 1958 there were seven hundred and twenty-seven of them. Soviet troops stayed in the country until the early 1990s.",
          m(0, v(ASIA, highlight=["Mongolia@red", "China@accent"], places=[BEIJING])),
          stat("founded the Yuan dynasty", "1271", "Kublai Khan founds the Yuan dynasty and goes on to rule China", "Wikipedia, Yuan dynasty"),
          sat("When that dynasty fell", 116.39, 39.92, 0.08, "Beijing, the Yuan capital Khanbaliq"),
          m("Later the Qing dynasty", v({"lon": 105.0, "lat": 42.0, "span": 40}, highlight=["China@red", "Mongolia@accent"])),
          stat("When the Qing collapsed", "1911", "Mongolia declares independence under the Bogd Khan", "Wikipedia, Mongolia"),
          photo("In 1921 a revolution", PH_STORM, "Storm over the steppe"),
          stat("and in 1924 Mongolia", "1924", "The Mongolian People's Republic, the first Soviet satellite state", "Wikipedia, Mongolian People's Republic"),
          m("the first Soviet satellite", v(ASIA, highlight=["Mongolia@red", "Russia@accent"], places=[MOSCOW, UB])),
          stat("In the late 1930s", "20,000+", "People killed in the purges of 1937-1939, including about 17,000 monks", "Wikipedia, Mongolian People's Republic"),
          photo("a wave of purges", PH_STEPPE, "The steppe"),
          sat("among them an estimated", 102.84, 47.2, 0.035, "Erdene Zuu monastery, Karakorum"),
          photo("In the 1950s the", PH_BUCKET, "A socialist-era award for a model herder"),
          stat("by 1958 there were", "727", "Herding collectives in 1958, the peak", "Wikipedia, Mongolian People's Republic"),
          m("Soviet troops stayed in", v(ASIA, highlight=["Russia@red", "Mongolia@accent"], places=[MOSCOW, UB]))),
        P("In the winter of 1989 and 1990 young Mongolians began protesting in the capital. In March 1990 a small group went on hunger strike on the central square. Two days later the ruling party's leadership resigned. Nobody was killed.",
          photo(0, PH_UB, "Central Ulaanbaatar"),
          stat("In March 1990 a", "7 MARCH 1990", "Democratic Union members begin a hunger strike on the main square", "Wikipedia, Mongolian Revolution of 1990"),
          stat("Two days later the", "9 MARCH 1990", "The Politburo resigns", "Wikipedia, Mongolian Revolution of 1990"),
          sat("Nobody was killed.", 106.917, 47.919, 0.04, "Sükhbaatar Square")),
        P("The Soviets had built towns, mines and a railway, from the Russian border through Ulaanbaatar to China. It reached Ulaanbaatar in 1949 and linked up with Beijing in 1955. Darkhan, an industrial town north of the capital, was founded in 1961, and Erdenet grew up around a huge copper mine. For the first time, many Mongolians lived in apartments and worked in factories. Then in 1990 a peaceful revolution ended one-party rule. In 1991 the collectives were broken up and their animals handed out. With factories closing and jobs disappearing, people went back to the herds: herding households rose from about seventy thousand in 1990 to about two hundred thousand by the end of the decade.",
          m(0, v(MN, routes=[RAIL], places=[UB])),
          photo("It reached Ulaanbaatar in", PH_TRAIN, "The Trans-Mongolian railway"),
          sat("Darkhan, an industrial town", 105.95, 49.47, 0.1, "Darkhan"),
          sat("and Erdenet grew up", 104.12, 49.03, 0.1, "The Erdenet copper mine"),
          stat("Then in 1990 a", "1990", "A peaceful revolution; the first multiparty elections follow that summer", "Wikipedia, Mongolian People's Republic"),
          sat("In 1991 the collectives", 104.0, 46.3, 0.4, "Herding country, central Mongolia", date=AUT),
          chart("herding households rose from", "Herding households in Mongolia", "households", [["1990", 70000], ["late 1990s", 200000]], "Yamamura et al., Research Institute for Humanity and Nature", reveal=["to about two hundred"], highlight=1)),
        P("Many of those new herders had small flocks and little experience. When the dzuds came, starting in 2000, they were hit hardest. And so the country that had briefly gone back to the steppe started moving to town.",
          sat(0, 106.0, 45.5, 0.4, "The Middle Gobi"),
          photo("When the dzuds came", PH_ZUD_GOATS, "Animals lost in a dzud"),
          sat("And so the country", 106.85, 47.95, 0.08, "Ger districts on Ulaanbaatar's edge")),
    ]},
    {"title": "One City", "mood": "tension", "paragraphs": [
        P("Reason five. Everyone who leaves the land goes to the same place. In its center today, Soviet-era apartment blocks stand next to new glass towers. Ulaanbaatar began in 1639 as a monastery of tents called Örgöö, which moved across the steppe for more than a century and settled in its present valley in 1778. In 1950 about seventy thousand people lived there. By 1989 it was five hundred and forty thousand. By the end of 2022 it was just over one point six million, almost half of the whole country.",
          photo(0, PH_UB2, "Ulaanbaatar today"),
          sat("In its center today", 106.905, 47.915, 0.08, "Central Ulaanbaatar"),
          sat("Ulaanbaatar began in 1639", 106.92, 47.92, 0.06, "Central Ulaanbaatar"),
          chart("In 1950 about seventy", "People in Ulaanbaatar", "people", [["1950", 69951], ["1989", 540300], ["2022", 1600000]], "Census figures via Wikipedia, Ulaanbaatar", reveal=["By 1989 it was", "By the end of"], highlight=2),
          m("almost half of the", v(MN, places=[UB], highlight=["Mongolia@red"]))),
        P("The city was planned for about six hundred thousand people, a number it reached in 1990. The newcomers could not afford apartments, so they set up their gers on the hills around it. These ger districts now hold more than half of the city's people, often without running water or sewers. About a third of ger-district households live below the poverty line. To get through winters of minus thirty, they burn raw coal in their stoves.",
          sat(0, 106.85, 47.96, 0.1, "Ger districts on the northern hills"),
          photo("The newcomers could not", PH_GERDIST, "Ger districts above central Ulaanbaatar"),
          stat("These ger districts now", "50 %+", "Share of Ulaanbaatar's people living in ger districts", WB),
          sat("often without running water", 106.83, 47.97, 0.06, "Fenced ger plots, northern hills"),
          sat("To get through winters", 106.9, 47.93, 0.2, "Ulaanbaatar in winter", date=WIN)),
        P("Ulaanbaatar sits in a valley, and in winter cold air gets trapped there under a lid of warmer air. The smoke cannot escape. In the ger districts, the World Bank found that winter levels of fine particles can be more than a hundred times the World Health Organization's daily guideline. Doctors in the city have reported a sharp rise in breathing illnesses, especially among children. One of the coldest capitals on Earth has also become one of the most polluted.",
          sat(0, 106.95, 47.9, 0.4, "The Tuul valley and Ulaanbaatar"),
          stat("In the ger districts", "100×", "Winter fine-particle levels in ger districts against the WHO daily guideline", WB),
          sat("can be more than", 106.88, 47.98, 0.06, "Ger district rooftops in winter", date=WIN),
          sat("World Health Organization's daily", 106.75, 47.95, 0.08, "Western ger districts in winter", date=WIN),
          stat("Doctors in the city", "2.7×", "Rise in respiratory illness per 10,000 people in Ulaanbaatar over a decade", "NPR, 2019"),
          sat("One of the coldest", 106.95, 47.93, 0.3, "Ulaanbaatar under winter smoke", date=WIN)),
        P("The government has tried. In May 2019 it banned burning raw coal in the capital and handed out processed coal briquettes instead. Some winters the air got better. Then the smog came back. In the fifteen years to 2018 the World Bank counted a fifty-five percent rise in the city's population from migration alone, and the newcomers keep coming.",
          stat(0, "MAY 2019", "Ulaanbaatar bans burning raw coal in homes", "Mongolian government; ADB"),
          sat("and handed out processed", 106.8, 47.97, 0.08, "Ger district stovepipes, northern Ulaanbaatar"),
          photo("Then the smog came", PH_NALAIKH, "A ger district street"),
          stat("In the fifteen years", "+55 %", "Growth in Ulaanbaatar's population from migration over fifteen years", WB),
          sat("rise in the city's", 107.15, 47.9, 0.1, "Ulaanbaatar's eastern edge in October", date=AUT),
          sat("and the newcomers keep", 107.05, 47.97, 0.1, "New ger plots on the eastern edge")),
        P("Mongolia does have wealth. It is under the ground. In the south Gobi, about eighty kilometers from the Chinese border, the Oyu Tolgoi mine produces copper and gold, and Tavan Tolgoi is one of the largest coal deposits in the world. Mining makes up around four fifths of the country's exports, and almost all the coal goes to China, by truck and, since 2022, by a new railway to the border that was expected to cut the cost of moving a ton of coal from forty-seven dollars to twelve. Oyu Tolgoi is owned about two thirds by the mining company Rio Tinto and one third by the Mongolian state. In 2025 the economy grew by almost seven percent, largely on its copper. But a mine needs few people, and it does not need them to stay.",
          sat(0, 106.86, 43.02, 0.1, "Oyu Tolgoi from orbit"),
          m("In the south Gobi", v({"lon": 106.0, "lat": 43.5, "span": 5}, places=[OYU, TAVAN, DALAN], routes=[COAL])),
          sat("and Tavan Tolgoi is", 105.55, 43.6, 0.1, "Tavan Tolgoi coal pits"),
          stat("Mining makes up around", "~80 %", "Share of Mongolia's exports from mining", "USGS Minerals Yearbook; press reports"),
          stat("and almost all the", "94 %", "Share of Mongolia's coal exports that went to China, 2022", "Mining in Mongolia, via press reports"),
          m("by a new railway", v({"lon": 106.5, "lat": 43.2, "span": 3}, routes=[COAL], places=[TAVAN])),
          chart("from forty-seven dollars", "Cost of moving a ton of coal to the border", "US$", [["By truck", 47], ["By the new railway", 12]], "Mining in Mongolia, via press reports", highlight=1),
          sat("Oyu Tolgoi is owned", 106.85, 43.0, 0.25, "The Oyu Tolgoi mine and its plant"),
          stat("In 2025 the economy", "6.8 %", "Mongolia's economic growth in 2025, driven by Oyu Tolgoi copper", "Focus Economics, via press reports"),
          photo("But a mine needs", PH_OT_CAMP, "The Oyu Tolgoi mine camp")),
    ]},
    {"title": "The Emptiest Country", "mood": "calm", "paragraphs": [
        P("So put it together. The land is high, dry and cold, and less than one percent of it can be farmed. What it can do is feed animals, and animals need a lot of room. The winters kill the herds and push the herders out. History built an empire but not cities, and then the collapse of the Soviet system sent people back to the steppe and then into one city. And the wealth that is left is dug out of the ground by a small workforce.",
          m(0, v(MN, highlight=["Mongolia@red"], places=[UB])),
          sat("and less than one", 102.0, 44.5, 0.5, "The Gobi", date=AUT),
          photo("What it can do", PH_ORKHON, "The Orkhon valley"),
          sat("The winters kill the", 108.0, 46.0, 0.4, "The steppe in October", date=AUT),
          photo("History built an empire", PH_GENGHIS, "Genghis Khan statue"),
          photo("and then the collapse", PH_TRAIN, "The Trans-Mongolian railway"),
          photo("and then into one", PH_GERDIST, "Ulaanbaatar's ger districts"),
          sat("And the wealth that", 106.86, 42.99, 0.05, "The Oyu Tolgoi open pit")),
        P("Mongolia is not empty because nobody wants to live there. It is empty because, for most of its history, this land could only support people who kept moving. Next time you see a map of Asia at night, look between Russia and China. That dark square, with one bright dot, is Mongolia. Out on the steppe, a ger may now have a solar panel by the door and a motorbike next to the horses. The herders who remain have not stopped moving. There are just fewer of them every year, and more of their children in the city. Mongolia's emptiness is not a mystery. It is the shape of a hard land, a herding way of life, and a century of history, all pushing people toward one valley.",
          photo(0, PH_HOVSGOL, "Lake Khövsgöl, northern Mongolia"),
          sat("It is empty because", 99.0, 47.0, 0.5, "The Khangai mountains in autumn", date=AUT),
          m("Next time you see", v(ASIA, layer="night")),
          m("That dark square, with", v(MN, layer="night", places=[UB])),
          photo("Out on the steppe", PH_YURT, "A ger with a solar panel, the Gobi"),
          photo("and a motorbike next", PH_HORSE, "A horse in the Orkhon valley"),
          sat("The herders who remain", 104.6, 46.2, 0.3, "Herding camps, central Mongolia", date=AUT),
          sat("There are just fewer", 106.98, 47.98, 0.08, "Ger districts on Ulaanbaatar's northern hills", date=WIN),
          m("Mongolia's emptiness is not", v(MN, highlight=["Mongolia@red"], places=[UB])),
          photo("It is the shape", PH_OVOO, "An ovoo on a Gobi track"),
          photo("and a century of", PH_BUCKET, "A socialist-era herder's award"),
          sat("all pushing people toward", 106.92, 47.92, 0.5, "The Tuul valley and Ulaanbaatar", date=AUT)),
        P("Here is my question for you. If you could spend one year in Mongolia, would you live in a ger on the steppe and move with the herds, or in an apartment in Ulaanbaatar?",
          photo(0, PH_SHEEP, "Sheep and goats on the steppe"),
          photo("would you live in", PH_NAADAM, "Naadam"),
          sat("or in an apartment", 106.91, 47.915, 0.05, "Apartment blocks, central Ulaanbaatar"),
          ask=("would you live in", "A ger on the steppe, or the city?")),
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
    "title": "Why Mongolia Is the Emptiest Country on Earth",
    "voice": "am_michael",
    "voice_speed": 1.15,
    "music": "procedural",
    "map_style": "satellite",
    "look": "none",
    "sources": ["episodes/mongolia-empty/research.md and factcheck.md", "Contains modified Copernicus Sentinel data 2026"],
    "thumbnail": {"text": "SO EMPTY"},
    "chapters": chapters,
    "youtube": {
        "title": "Why Mongolia Is the Emptiest Country on Earth",
        "description": "Mongolia is almost three times the size of France, yet about three and a half million people live there, and roughly half of them in one city. This video goes through the five reasons it is the most thinly populated country on Earth: a high, dry, cold land where less than one percent can be farmed, grass that feeds herds rather than crops, the killer winters called dzud, a history that built an empire but no cities and then a Soviet collapse, and the pull of Ulaanbaatar and the mines.",
        "tags": ["Mongolia", "why Mongolia is empty", "emptiest country", "Ulaanbaatar", "Gobi Desert", "dzud", "nomads", "ger", "Genghis Khan", "Mongolian steppe", "Oyu Tolgoi", "geography", "satellite images"],
        "pinned_comment": "If you could spend one year in Mongolia, would you live in a ger on the steppe and move with the herds, or in an apartment in Ulaanbaatar?",
    },
}
out = HERE / "script.json"
out.write_text(json.dumps(script, ensure_ascii=False, indent=1) + chr(10), encoding="utf-8")
words = sum(len(p["text"].split()) for c in chapters for p in c["paragraphs"])
shots = [s for c in chapters for p in c["paragraphs"] for s in p["shots"]]
kinds = {k: sum(1 for s in shots if s["type"] == k) for k in ("map", "photo", "stat", "document", "chart")}
print(f"{words} words, {len(chapters)} chapters, {len(shots)} shots {kinds}")
