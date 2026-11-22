"""Builds script.json for russia-far-east.  python build_script.py

Same production logic as episodes/chesapeake-bay-bridge-tunnel (hand-placed shots, a photo or map frame at most twice,
60 s apart). The narration lives in drafts/narration.md; every sentence comes from research.md. Photos and satellite
tests: visuals.md. Painted regions (Natural Earth admin-1): geo/make_regions.py.
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
SUMMER = "2025-06-15/2025-08-31"   # scratch rfe_sat.py 2026-11-22 (per-view windows in visuals.md)
SUMMER24 = "2024-06-15/2024-08-31"
ICE_DAY = "2024-01-20"             # Sentinel-2 scene 2024-01-19: Amur Bay frozen beside Vladivostok
MODIS_ICE = "2024-03-08"           # MODIS: Sea of Okhotsk almost all ice
MODIS_OPEN = "2024-09-15"          # MODIS: open water, clearest summer test
MODIS_PRIM = "2025-01-25"          # MODIS: Amur Bay frozen, Ussuri Bay open


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
LATLINE = {"lon": 70.0, "lat": 45.0, "span": 150.0}   # Nice to Vladivostok
EURASIA = {"lon": 95.0, "lat": 55.0, "span": 130.0}
RUSSIA = {"lon": 105.0, "lat": 62.0, "span": 140.0}
FAR_EAST = {"lon": 140.0, "lat": 58.0, "span": 72.0}
ASIA_E = {"lon": 120.0, "lat": 50.0, "span": 60.0}    # Siberia, Mongolia and the coast
OKHOTSK = {"lon": 147.0, "lat": 53.0, "span": 30.0}
PRIMORYE = {"lon": 132.0, "lat": 44.0, "span": 8.0}
VLAD_W = {"lon": 131.9, "lat": 43.2, "span": 3.0}
YAKUTIA = {"lon": 134.0, "lat": 64.0, "span": 32.0}
KOLYMA = {"lon": 146.0, "lat": 62.0, "span": 22.0}
CHUKOTKA = {"lon": 170.0, "lat": 66.0, "span": 24.0}
KAMCHATKA = {"lon": 159.0, "lat": 54.0, "span": 14.0}
AMUR_V = {"lon": 131.0, "lat": 50.0, "span": 24.0}
BAM_V = {"lon": 120.0, "lat": 53.0, "span": 48.0}
TRANSSIB_V = {"lon": 88.0, "lat": 52.0, "span": 110.0}
CHINA_V = {"lon": 128.0, "lat": 46.0, "span": 26.0}
HOKKAIDO = {"lon": 144.0, "lat": 45.0, "span": 7.0}
MEDIT = {"lon": 8.0, "lat": 42.0, "span": 30.0}

FEFD = "file:fefd.geojson@red"
FEFD_A = "file:fefd.geojson@accent"
CHINA_NE = "file:china_ne.geojson@alt"
AIGUN = "file:aigun.geojson@red"
PRIM = "file:primorye.geojson@red"

# ------------------------------------------------------------------ sources (research.md)
ROSSTAT = "Rosstat, 2021 census"
CENSUS89 = "1989 USSR census (Demoscope); Rosstat 2021"
OWNCEN = "Own calculation: 1989 USSR census, Rosstat 2021"
CLIM = "1991-2020 normals: Pogoda i Klimat / NOAA; Meteo-France"
NASA = "NASA Earth Observatory"
WMO = "World Meteorological Organization"
WIKI_COLD = "Station records (Stepanova; Burt)"
USGS = "U.S. Geological Survey"
NBS = "National Bureau of Statistics of China, 2020 census"
ERDC = "Far East and Arctic Development Corporation"
MSU = "Seventeen Moments in Soviet History (MSU)"
HIST = "Treaty texts as summarised by historians"
DAL = "Archival count cited by historians of Dalstroy"

# ------------------------------------------------------------------ photos (Commons, licence checked: visuals.md)
PH_NICE_AIR = "File:Baie des Anges - Vue aérienne (2024).jpg"
PH_NICE_BEACH = "File:Nice-plage-baie-des-Anges.jpg"
PH_NICE_MARCH = "File:Plage à Nice (promenade des anglais) en mars 2022 (4).JPG"
PH_NICE_PALM = "File:Palmae in Nice (FR-06000).jpg"
PH_NICE_BAY = "File:La baie des Anges (Nice) (3293122147).jpg"
PH_VLA_HORN = "File:Golden Horn bay and Egersheld peninsula.jpg"
PH_VLA_NIGHT = "File:Vladivostok Golden Horn bay 2022-08.jpg"
PH_VLA_1899 = "File:View of Vladivostok, Russia, from the Bay of the Golden Horn.tif"
PH_VLA_1992 = "File:Overview of Zolotoy Rog.JPEG"
PH_RUSSKY = "File:Russky bridge in the morning (21466395884).jpg"
PH_ZOLOTOY = "File:Zolotoy Bridge from downtown Vladivostok Russia (14782664096).jpg"
PH_VLA_SKY = "File:Vladivostok skyline 2022-08.jpg"
PH_AMURSKY = "File:Amursky bay 2022.jpg"
PH_ICEFISH = "File:Тумнин 03.jpg"
PH_VERKH_AIR = "File:Flughafen Werchojansk I.JPG"
PH_VERKH_VAL = "File:Talkessel von Werchojansk.JPG"
PH_VERKH_POLE = "File:Werchojansk, Kältepoldenkmal.JPG"
PH_VERKH_1917 = "File:Г. Верхоянск.jpg"
PH_FROST = "File:Frost indicator in Yakutia.jpg"
PH_YAK_PILES = "File:Jakutsk Pfahlbau.jpg"
PH_YAK_PILES2 = "File:Новые сваи в Якутске3.JPG"
PH_PIPES = "File:Raised pipes in permafrost.jpg"
PH_YAK_STREET = "File:Улица Пояркова Якутск-(SmallSonMarex).jpg"
PH_LENA1 = "File:Lena River (near Yakutsk, Siberia, Russia) 1 (21473479995).jpg"
PH_LENA4 = "File:Lena River (near Yakutsk, Siberia, Russia) 4 (21447252376).jpg"
PH_MAG_VIEW = "File:Вид Магадана.jpg"
PH_MAG_LIGHTS = "File:Огни Магадана.jpg"
PH_MAG_GERTNER = "File:Magadan, Gertner Bay.jpg"
PH_MAG_UNSPLASH = "File:Magadan, Russia (Unsplash fk3XUcfTAvk).jpg"
PH_NAGAEVO = "File:Nagaevo bay - panoramio.jpg"
PH_KOLYMA_2001 = "File:Kolyma Highway (Road of Bones).jpg"
PH_R504_2024 = "File:R-504 highway 08.2024.jpg"
PH_R504_AUTUMN = "File:R504 Kolyma in autumn.jpg"
PH_R504_RIVER = "File:R504 kolyma.jpg"
PH_MINE_BRIG = "File:Бригада Андрея Ивановича Подосенова за работой в шахте.jpg"
PH_YOUTH_BRIG = "File:Молодежная бригада Сердюка лагподразделения «Артык». Индигирлаг, Дальстрой.jpg"
PH_BUTUG_MILL = "File:Butugichag-mill.JPG"
PH_BUTUG_ADMIN = "File:Butugichag-admin.JPG"
PH_GULAG_LAZO = "File:Gulag Lazo (2914364802).jpg"
PH_UST_NERA = "File:Усть-Нера, 1960-е.jpg"
PH_MOD_OKH_2020 = "File:Sea Ice in the Sea of Okhotsk (MODIS 2020-02-02).jpg"
PH_MOD_SWIRL = "File:Sea ice swirls in the Sea of Okhotsk (MODIS 2019-03-21).jpg"
PH_MOD_HOKK = "File:Swirls of Sea Ice approaching Hokkaido, Japan (MODIS 2021-03-24).jpg"
PH_MOD_ICYHEART = "File:The Icy Heart of the North Pacific (MODIS 2021-03-09).jpg"
PH_MOD_STREETS = "File:Cloud Streets and Sea Ice in Sea of Okhotsk (MODIS 2024-01-02).jpg"
PH_MOD_SAKH = "File:Sea Ice in the Gulf of Sakhalin and the Tartar Strait (MODIS 2020-02-19).jpg"
PH_MOD_RUSSIA = "File:Sea Ice off Russia (MODIS 2022-04-07).jpg"
PH_MOD_SNOW = "File:Snow in eastern Russia (MODIS 2015-01-02).jpg"
PH_MOD_AMUR = "File:Amur River between China and Russia (MODIS 2021-06-09).jpg"
PH_ABASHIRI = "File:Abashiri Drift ice01.JPG"
PH_AURORA = "File:Hokkaido-Abashiri Drift Icebreaker Ship Aurora-xl.jpg"
PH_DRIFT_TRAIN = "File:JRH Senmo-main-line Kiha40 Drift-ice.jpg"
PH_PIA_FLOES = "File:Ice floes of Hokkaido PIA12056.jpg"
PH_KLYUCH = "File:Klyuchevskaya Sopka (Klyuchevskoi), Kamchatka, Russia - January 12th, 2021 (50828886532).jpg"
PH_KORYAK = "File:Koryaksky volcano rising above Petropavlovsk-Kamchatsky (53160200107).jpg"
PH_PETRO = "File:Petropavlovsk-Kamchatsky (51605162749).jpg"
PH_AVACHA = "File:Kamchatka Volcano Avachinsky (Kamchatka) (16084696896).jpg"
PH_TOLBACHIK = "File:Kamchatka Volcano Tolbachik (23200636942).jpg"
PH_SHAKEMAP = "File:2025-07-29 Petropavlovsk-Kamchatsky, Russia M8.7 earthquake shakemap (USGS).jpg"
PH_TSU_MAP = "File:Tsunami warnings (2025 Kamchatka Peninsula earthquake).jpg"
PH_SWOT = "File:SWOT Spots Tsunami Wave After Kamchatka Quake (154666).jpg"
PH_TS_1897 = "File:JEFFERSON(1897) p021 A TRAIN ON THE TRANS SIBERIAN RAILWAY.jpg"
PH_TS_1904 = "File:DEMIDOV(1904) p054 TYPE OF ENGINE OF THE TRANS-SIBERIAN RAILWAY (14782106042).jpg"
PH_TS_1913 = "File:The Trans-Siberian Railway, c. 1913.jpg"
PH_KHAB_BRIDGE = "File:2019-07-16-khv-Amur-bridge.jpg"
PH_AMUR_1916 = "File:East end, Amur Bridge 1 7-8 miles LCCN2014709643.jpg"
PH_BLAG_HEIHE = "File:Blagoveshchensk, Russia, and Heihe, China (12757409723).jpg"
PH_BLAG_HEIHE2 = "File:Blagoveshchensk, Russia --- Heihe, China (8789415981).jpg"
PH_TYNDA = "File:Tynda-26-april-2007.jpg"
PH_TYNDA_RAIL = "File:Tynda rail.jpg"
PH_ANADYR = "File:Anadyr harbour2.jpg"
PH_PEVEK = "File:Pevek 2008.jpg"
PH_PEVEK_S = "File:View of Pevek from the south.jpg"
PH_YUZHNO = "File:Yuzhno-sakhalinsk-in-sakhalin-oblast-russia-september-2015-001.jpg"
PH_MURAVYOV = "File:Nikolay-Muravyov-Amursky.png"
PH_IGNATIEV = "File:Ignatiev NP by Timm.jpg"
PH_MAP_1880 = "File:The Islands of Japan with Corea, Manchooria, and the New Russian Acquisitions.jpg"
PH_MAP_1851 = "File:John-Tallis-1851-Tibet-Mongolia-and-Manchuria-33621.jpg"
PH_CIA_BORDER = "File:MANCHURIA-U.S.S.R BOUNDARY Ct002999.jpg"
PH_HARBIN = "File:Harbin kitaisukaya 1940's.jpg"
PH_USSURI_BR = "File:Мост через Уссури пос Горные Ключи.JPG"

# ------------------------------------------------------------------ places
NICE = place("Nice", 7.26, 43.70, "Nice, 43.7° N", "city")
VLAD = place("Vladivostok", 131.89, 43.12, "Vladivostok, 43.1° N", "city")
VLAD_C = place("Vladivostok", 131.89, 43.12, "Vladivostok", "city")
MOSCOW = place("Moscow", 37.62, 55.75, "Moscow", "capital")
KHAB = place("Khabarovsk", 135.07, 48.48, "Khabarovsk", "city")
YAKUTSK = place("Yakutsk", 129.73, 62.03, "Yakutsk", "city")
VERKH = place("Verkhoyansk", 133.39, 67.55, "Verkhoyansk", icon="warning")
OYM = place("Oymyakon", 142.78, 63.46, "Oymyakon", icon="warning")
MAGADAN = place("Magadan", 150.80, 59.56, "Magadan", "port")
ABASHIRI = place("Abashiri", 144.27, 44.02, "Abashiri, Japan", "port")
AMUR_M = place("Amur mouth", 140.70, 53.10, "Mouth of the Amur", icon="water")
AIGUN_P = place("Aigun", 127.46, 49.97, "Aigun (Aihui)", "site")
BEIJING = place("Beijing", 116.40, 39.90, "Beijing", "capital")
PETRO = place("Petropavlovsk-Kamchatsky", 158.65, 53.02, "Petropavlovsk-Kamchatsky", "city")
QUAKE = place("Epicentre", 160.24, 52.49, "M8.8, 29 July 2025", icon="warning")
ANADYR = place("Anadyr", 177.50, 64.73, "Anadyr", "city")
BLAG = place("Blagoveshchensk", 127.53, 50.27, "Blagoveshchensk", "city")
HEIHE = place("Heihe", 127.49, 50.24, "", "city")
HARBIN = place("Harbin", 126.63, 45.75, "Harbin", "city")
SHENYANG = place("Shenyang", 123.43, 41.80, "Shenyang", "city")
CHANGCHUN = place("Changchun", 125.32, 43.88, "Changchun", "city")
YUZHNO = place("Yuzhno-Sakhalinsk", 142.73, 46.96, "Yuzhno-Sakhalinsk", "city")
SUSUMAN = place("Susuman", 148.16, 62.78, "Susuman", icon="mine")
TYNDA = place("Tynda", 124.72, 55.15, "Tynda", icon="train")
TAYSHET = place("Tayshet", 98.00, 55.94, "Tayshet", "city")
SOVGAVAN = place("Sovetskaya Gavan", 140.30, 48.97, "Sovetskaya Gavan", "port")
VENICE = place("Venice", 12.33, 45.44, "Venice, 45.4° N", "city")
SIB_HIGH = place("Siberian High", 102.0, 51.0, "SIBERIAN HIGH (winter)", "label")
OKH_SEA = place("Sea of Okhotsk", 149.0, 54.5, "SEA OF OKHOTSK", "sea")
SAKHALIN = place("Sakhalin", 142.8, 50.5, "Sakhalin", "label")
KAMCH_L = place("Kamchatka", 159.5, 56.5, "Kamchatka", "label")
ALASKA = place("Alaska", -165.0, 64.8, "Alaska", "label")
KOLYMA_GOLD = place("Kolyma gold fields", 149.5, 62.5, "Kolyma gold fields", icon="mine")
LONDON = place("London", -0.13, 51.51, "London", "capital")

# ------------------------------------------------------------------ lines (approximate routes through the main towns)
LAT43 = {"from": [7.26, 43.5], "to": [131.89, 43.5], "mode": "line", "label": "Same latitude", "color": "accent", "seconds": 4.0}
TRANSSIB = {"from": [37.62, 55.75], "via": [[60.6, 56.84], [73.37, 54.99], [82.92, 55.03], [92.87, 56.01], [104.28, 52.29],
            [107.58, 51.83], [113.50, 52.03], [123.93, 54.00], [128.47, 50.92], [135.07, 48.48]], "to": [131.89, 43.12],
            "mode": "line", "label": "Trans-Siberian Railway", "color": "accent", "seconds": 5.0}
TRANSSIB_E = {"from": [113.50, 52.03], "via": [[123.93, 54.00], [128.47, 50.92], [135.07, 48.48]], "to": [131.89, 43.12],
              "mode": "line", "label": "Trans-Siberian", "color": "accent", "seconds": 3.0}
BAM = {"from": [98.00, 55.94], "via": [[105.76, 56.79], [109.31, 55.64], [114.0, 56.9], [124.72, 55.15], [132.60, 51.07],
       [137.02, 50.55]], "to": [140.30, 48.97], "mode": "line", "label": "Baikal-Amur Mainline (BAM)", "color": "red", "seconds": 5.0}
KOLYMA_RD = {"from": [150.80, 59.56], "via": [[150.9, 60.1], [151.4, 61.3], [148.16, 62.78], [145.0, 63.9], [143.23, 64.57],
             [135.60, 62.65]], "to": [129.73, 62.03], "mode": "line", "label": "Kolyma Highway", "color": "red", "seconds": 5.0}
AMUR_BORDER = {"from": [121.5, 53.3], "via": [[127.5, 50.25], [130.6, 48.0], [135.07, 48.48]], "to": [133.1, 45.0],
               "mode": "line", "label": "Border on the Amur and Ussuri", "color": "alt", "seconds": 4.0}

WINTER_WIND = [{"from": [104.0, 52.0], "to": [131.0, 44.0], "color": "blue", "bend": -0.12},
               {"from": [112.0, 58.0], "to": [140.0, 52.0], "color": "blue", "bend": -0.1},
               {"from": [118.0, 64.0], "to": [150.0, 59.0], "color": "blue", "bend": -0.08}]
AMUR_FLOW = [{"from": [137.5, 51.5], "to": [142.5, 53.8], "color": "blue", "label": "Fresh water from the Amur", "bend": 0.2}]
ICE_DRIFT = [{"from": [146.0, 51.0], "to": [144.5, 44.6], "color": "blue", "label": "Drift ice", "bend": -0.1}]
PLATE = [{"from": [167.0, 49.5], "to": [161.0, 52.0], "color": "red", "label": "Pacific plate, ~80 mm a year", "bend": 0.0}]
CMP_OKH = {"before": MODIS_OPEN, "after": MODIS_ICE, "source": "modis", "seconds": 2.6,
           "label_before": "SEPTEMBER", "label_after": "MARCH"}

chapters = []
heads = iter(HEADS)


def chapter(*paras):
    title, mood = next(heads)
    chapters.append({"title": title, "mood": mood, "paragraphs": list(paras)})


# ================================================================== Hook
chapter(
    P("P0",
      photo(0, PH_NICE_BEACH, "Nice, on the French Riviera"),
      photo("under palm trees.", PH_NICE_PALM, "Palms in Nice"),
      stat("The average temperature that", "+9.5 °C", "Average January temperature in Nice, 1991-2020", CLIM),
      m("Now go east along", v(LATLINE, places=[NICE]), step("across Europe and Asia,", routes=[LAT43]),
        step("You arrive in Vladivostok,", places=[NICE, VLAD])),
      photo("the biggest city on", PH_VLA_HORN, "Vladivostok, 2022"),
      stat("Its average January temperature", "-11.9 °C", "Average January temperature in Vladivostok, 1991-2020", CLIM)),
    P("P1",
      sat(0, 131.90, 43.11, 0.2, "Ice beside Vladivostok, January 2024", date=ICE_DAY),
      photo("that people walk out", PH_ICEFISH, "Ice fishing in the Russian Far East (Tumnin River)"),
      sat("fish through holes in", 131.80, 43.15, 0.5, "Amur Bay, frozen, 19 January 2024", date=ICE_DAY),
      stat("Same latitude as the", "21 °C", "Colder in January than Nice, at the same latitude", CLIM),
      m("And north of Vladivostok", v(FAR_EAST, highlight=[FEFD], places=[VLAD_C]))),
    P("P2",
      m(0, v(RUSSIA, highlight=[FEFD]), text="The Far Eastern Federal District"),
      stat("covers almost seven million", "6.95 MILLION KM²", "Area of the Far Eastern Federal District", ROSSTAT, note="About 40 % of Russia"),
      m("an area bigger than", v(FAR_EAST, highlight=[FEFD])),
      stat("At the last census,", "7.98 MILLION", "People in the whole district, 2021 census", ROSSTAT),
      m("More people than that", v(near(-0.13, 51.51, 4.0), places=[LONDON]), text="London: about 8.8 million people (2021)")),
    P("P3",
      photo(0, PH_VLA_NIGHT, "Vladivostok, Golden Horn Bay"),
      m("Part of the answer", v(ASIA_E, arrows=WINTER_WIND, places=[SIB_HIGH])),
      photo("and part is in", PH_YAK_PILES, "Yakutsk: a building on piles"),
      photo("Part of it is", PH_CIA_BORDER, "The China-USSR border along the Amur, 1960 map"),
      photo("a railway built twice,", PH_TYNDA_RAIL, "The BAM at Tynda"),
      photo("and a system of", PH_BUTUG_MILL, "Ruins of a Kolyma camp mill, Butugychag"),
      photo("Since the Soviet Union", PH_PEVEK_S, "Pevek, Chukotka"),
      stat("some regions here have", "-70 %", "Chukotka's population, 1989 to 2021", OWNCEN),
      m("To see why, we", v(ASIA_E, arrows=WINTER_WIND))),
)

# ================================================================== 1. The wind
chapter(
    P("P4",
      m(0, v(LATLINE, places=[NICE, VLAD])),
      m("Nice has the Mediterranean", v(MEDIT, places=[NICE])),
      photo("in winter the wind", PH_NICE_MARCH, "Nice in March"),
      m("Vladivostok has the Pacific", v(PRIMORYE, places=[VLAD_C], date=MODIS_PRIM)),
      m("It comes from behind", v(ASIA_E, arrows=WINTER_WIND, places=[VLAD_C]))),
    P("P5",
      photo(0, PH_MOD_SNOW, "Siberia under snow (NASA MODIS, January 2015)"),
      photo("the ground is covered", PH_FROST, "Frost in Yakutia"),
      m("The air over it", v(ASIA_E, places=[SIB_HIGH])),
      m("Meteorologists call it the", v(EURASIA, places=[SIB_HIGH])),
      photo("It is one of", PH_VERKH_VAL, "Verkhoyansk valley in March"),
      photo("and it sits there", PH_VERKH_AIR, "Verkhoyansk airport in March")),
    P("P6",
      m(0, v(ASIA_E, arrows=WINTER_WIND, places=[SIB_HIGH])),
      m("So for months on", v(PRIMORYE, arrows=[{"from": [127.0, 47.5], "to": [132.5, 43.3], "color": "blue", "bend": -0.1}], places=[VLAD_C])),
      m("This is the winter", v(CHINA_V, arrows=WINTER_WIND)),
      photo("brings bitter, dry continental", PH_MOD_STREETS, "Winter wind over the Sea of Okhotsk (NASA MODIS)")),
    P("P7",
      m(0, v(YAKUTIA, places=[YAKUTSK])),
      m("there are two small", v(YAKUTIA, places=[VERKH, OYM])),
      stat("In eighteen ninety-two, Verkhoyansk", "-67.8 °C", "Verkhoyansk, February 1892", WIKI_COLD),
      stat("In nineteen thirty-three, the", "-67.7 °C", "Oymyakon, 6 February 1933", WIKI_COLD)),
    P("P8",
      sat(0, 133.39, 67.55, 0.2, "Verkhoyansk in summer"),
      stat("On the twentieth of", "+38 °C", "Verkhoyansk, 20 June 2020: the Arctic's highest recorded temperature", WMO),
      photo("The World Meteorological Organization", PH_VERKH_POLE, "Verkhoyansk: monument to the Pole of Cold"),
      sat("accepted it as the", 133.42, 67.54, 0.5, "The Yana valley at Verkhoyansk"),
      stat("One town, a range", "~106 °C", "Between Verkhoyansk's coldest and hottest readings", "Own calculation from the records above")),
    P("P9",
      photo(0, PH_NICE_AIR, "Nice: the Baie des Anges"),
      m("Vladivostok gets its winter", v(ASIA_E, arrows=WINTER_WIND, places=[VERKH, VLAD_C])),
      m("A few hundred kilometres", v(OKHOTSK, date=MODIS_ICE))),
)

# ================================================================== 2. The sea
chapter(
    P("P10",
      m(0, v(OKHOTSK, places=[OKH_SEA, SAKHALIN, KAMCH_L])),
      stat("It covers more than", "1.5 MILLION KM²", "Area of the Sea of Okhotsk", NASA, note="Almost three times the size of mainland France"),
      m("almost three times the", v({"lon": 147.5, "lat": 53.3, "span": 29.0}, compare=CMP_OKH))),
    P("P11",
      photo(0, PH_MOD_OKH_2020, "The Sea of Okhotsk, 2 February 2020 (NASA MODIS)"),
      stat("ice can cover between", "50-90 %", "Of the sea under ice at the yearly peak", NASA),
      stat("On average it stays", "180 DAYS", "Average time the ice stays", NASA),
      photo("NASA calls it the", PH_MOD_ICYHEART, "The icy heart of the North Pacific, March 2021 (NASA MODIS)"),
      m("The sea reaches south", v({"lon": 80.0, "lat": 48.0, "span": 150.0}, places=[VENICE, place("Ice edge", 143.5, 45.0, "Sea ice, ~45° N", icon="water")]))),
    P("P12",
      photo(0, PH_MOD_SWIRL, "Ice swirls in the Sea of Okhotsk, March 2019 (NASA MODIS)"),
      m("The winds from East", v(OKHOTSK, arrows=WINTER_WIND[1:])),
      m("And a large amount", v(AMUR_V, places=[AMUR_M])),
      m("Fresh water floats on", v({"lon": 141.0, "lat": 53.5, "span": 9.0}, arrows=AMUR_FLOW, places=[AMUR_M], date=MODIS_ICE)),
      photo("so the great river", PH_MOD_SAKH, "Ice in the Gulf of Sakhalin, February 2020 (NASA MODIS)")),
    P("P13",
      m(0, v(OKHOTSK, arrows=ICE_DRIFT, places=[ABASHIRI])),
      photo("Between mid-January and early", PH_MOD_HOKK, "Sea ice approaching Hokkaido, March 2021 (NASA MODIS)"),
      photo("a port on the", PH_ABASHIRI, "Drift ice at Abashiri, Hokkaido")),
    P("P14",
      photo(0, PH_AURORA, "An icebreaker sightseeing boat off Abashiri"),
      photo("A frozen sea is", PH_MOD_RUSSIA, "Ice off the Russian coast, April 2022 (NASA MODIS)"),
      photo("and the cold water", PH_PIA_FLOES, "Ice floes off Hokkaido (NASA)"),
      m("Along the northern shores", v({"lon": 147.0, "lat": 59.0, "span": 18.0}, places=[MAGADAN])),
      photo("The biggest is Magadan.", PH_MAG_VIEW, "Magadan"),
      sat("We will come back", 150.80, 59.56, 0.25, "Magadan on the Sea of Okhotsk"),
      photo("But first, look at", PH_LENA1, "The Lena near Yakutsk")),
)

# ================================================================== 3. Permafrost
chapter(
    P("P15",
      m(0, v(YAKUTIA, highlight=["Sakha Republic@accent"])),
      photo("This is permafrost: soil,", PH_FROST, "Frozen ground, Yakutia"),
      sat("that have stayed below", 143.23, 64.57, 0.2, "Ust-Nera, on the Indigirka"),
      sat("and in much of", 129.85, 62.10, 1.0, "The Lena valley at Yakutsk", date=SUMMER24),
      photo("In summer only the", PH_LENA4, "Summer on the Lena")),
    P("P16",
      sat(0, 129.72, 62.035, 0.08, "Yakutsk: a city on frozen ground"),
      photo("The ice in the", PH_PIPES, "Pipes raised above the permafrost"),
      photo("A road, a pipe", PH_R504_RIVER, "A road across Yakutia"),
      photo("So in the far", PH_YAK_PILES, "Yakutsk: a building on piles"),
      photo("with a gap underneath", PH_YAK_STREET, "A street in Yakutsk")),
    P("P17",
      sat(0, 129.73, 62.03, 0.25, "Yakutsk"),
      stat("had about three hundred", "355,443", "People in Yakutsk, 2021 census", ROSSTAT),
      sat("It is described as", 129.70, 62.06, 0.12, "Yakutsk"),
      sat("The river Lena flows", 129.95, 62.00, 0.45, "The Lena at Yakutsk: no bridge", date=SUMMER24),
      photo("Cars cross on the", PH_LENA1, "The Lena near Yakutsk")),
    P("P18",
      m(0, v(FAR_EAST, places=[YAKUTSK, MAGADAN, VLAD_C])),
      m("the sea is frozen", v(OKHOTSK, date=MODIS_ICE, places=[OKH_SEA])),
      photo("And yet Russia came", PH_VLA_1992, "Vladivostok, 1992"),
      photo("Which raises a different", PH_RUSSKY, "Vladivostok today"),
      photo("If the land was", PH_VLA_SKY, "Vladivostok")),
)

# ================================================================== 4. Treaties and the railway
chapter(
    P("P19",
      m(0, v(RUSSIA, places=[MOSCOW, place("Okhotsk", 143.30, 59.36, "Okhotsk (1647)", "port")])),
      photo("But the southern part", PH_MAP_1851, "Manchuria on an 1851 map"),
      sat("the part with the", 131.90, 43.11, 0.15, "Vladivostok's sheltered harbour", date=SUMMER24),
      m("It belonged, at least", v(AMUR_V, highlight=[AIGUN, PRIM], places=[VLAD_C])),
      m("The border ran far", v(AMUR_V, places=[place("Stanovoy Range", 128.0, 56.0, "Stanovoy Range", icon="mountain")]))),
    P("P20",
      sat(0, 127.48, 49.98, 0.2, "Aigun (Aihui) on the Amur, today in China"),
      m("In eighteen fifty-eight, China's", v(CHINA_V, places=[BEIJING])),
      photo("The Russian governor of", PH_MURAVYOV, "Nikolay Muravyov(-Amursky)"),
      m("At the town of", v(AMUR_V, places=[AIGUN_P])),
      stat("on the twenty-eighth of", "28 MAY 1858", "Treaty of Aigun", HIST),
      m("Russia received the land", v(AMUR_V, highlight=[AIGUN], places=[AIGUN_P]))),
    P("P21",
      m(0, v(CHINA_V, places=[BEIJING])),
      photo("A Russian envoy, Nikolay", PH_IGNATIEV, "Nikolay Ignatyev"),
      stat("and in November eighteen", "14 NOV 1860", "Convention of Peking: the coast east of the Ussuri", HIST),
      m("gave Russia the coast", v(AMUR_V, highlight=[AIGUN, PRIM])),
      m("That is today's Primorsky", v(PRIMORYE, highlight=[PRIM], places=[VLAD_C])),
      m("China calls these the", v(CHINA_V, highlight=[AIGUN, PRIM], places=[BEIJING]), text="Outer Manchuria")),
    P("P22",
      photo(0, PH_VLA_HORN, "Vladivostok, Golden Horn Bay"),
      sat("a Russian military ship", 131.90, 43.115, 0.08, "The Golden Horn Bay", date=SUMMER24),
      stat("They set up a", "2 JULY 1860", "Vladivostok founded as a military post", "Vladivostok city history"),
      photo("Roughly translated, the name", PH_ZOLOTOY, "Vladivostok: 'Ruler of the East'"),
      m("Russia now had a", v(FAR_EAST, places=[VLAD_C, place("Okhotsk", 143.30, 59.36, "Okhotsk", "port")])),
      m("But it was still", v(TRANSSIB_V, places=[MOSCOW, VLAD_C]))),
    P("P23",
      m(0, v(TRANSSIB_V, routes=[TRANSSIB], places=[MOSCOW, VLAD_C])),
      photo("Work on the Trans-Siberian", PH_AMUR_1916, "The Amur bridge at Khabarovsk, 1916"),
      sat("and it linked Moscow", 135.07, 48.48, 0.3, "Khabarovsk on the Amur"),
      m("Look at the Far", v(FAR_EAST, layer="night")),
      m("A thin chain of", v(AMUR_V, layer="night", routes=[TRANSSIB_E])),
      stat("Khabarovsk, about six hundred", "603,519", "People in Vladivostok, 2021 census", ROSSTAT, note="Khabarovsk: 617,441"),
      m("A few cities along", v({"lon": 134.0, "lat": 52.0, "span": 30.0}, layer="night", places=[KHAB, VLAD_C, BLAG])),
      m("Most people in the", v(FAR_EAST, layer="night", routes=[TRANSSIB_E]))),
    P("P24",
      m(0, v(FAR_EAST, places=[KOLYMA_GOLD, MAGADAN])),
      photo("in the dark part", PH_R504_AUTUMN, "The Kolyma region in autumn"),
      photo("So in the twentieth", PH_KHAB_BRIDGE, "The Amur at Khabarovsk, 2019"),
      m("The first was force.", v(KOLYMA, places=[MAGADAN, KOLYMA_GOLD]))),
)

# ================================================================== 5. Force
chapter(
    P("P25",
      stat(0, "13 NOV 1931", "Dalstroy, the Far North Construction Trust, is created", DAL),
      m("Its job was to", v(KOLYMA, places=[KOLYMA_GOLD])),
      sat("There were no roads", 148.5, 62.0, 1.5, "The upper Kolyma basin", date=SUMMER24),
      sat("Dalstroy turned the small", 150.75, 59.53, 0.12, "Nagaev Bay, Magadan's harbour"),
      m("and from there it", v(KOLYMA, routes=[KOLYMA_RD], places=[MAGADAN]))),
    P("P26",
      photo(0, PH_KOLYMA_2001, "The Kolyma Highway, 2001"),
      stat("about two thousand kilometres", "~2,000 KM", "Kolyma Highway, built 1932 to the early 1950s", DAL),
      photo("Most of the people", PH_R504_RIVER, "On the Kolyma Highway"),
      m("and who worked the", v(KOLYMA, places=[KOLYMA_GOLD, SUSUMAN])),
      photo("the Soviet system of", PH_BUTUG_ADMIN, "Butugychag camp ruins"),
      photo("By one archival count,", PH_GULAG_LAZO, "Remains of a Gulag camp in Kolyma"),
      stat("in nineteen fifty-two the", "~200,000", "Prisoners in camps under Dalstroy, 1952", DAL)),
    P("P27",
      m(0, v(KOLYMA, routes=[KOLYMA_RD], places=[MAGADAN])),
      stat("Estimates by historians range", "130,000 TO 1 MILLION+", "Estimates of deaths in Kolyma: no agreed number", "Historians' estimates differ"),
      photo("We do not know", PH_BUTUG_MILL, "Butugychag"),
      photo("What is not in", PH_R504_2024, "The R504 Kolyma Highway, 2024"),
      m("They called it the", v(KOLYMA, routes=[KOLYMA_RD], places=[MAGADAN, SUSUMAN]))),
    P("P28",
      sat(0, 150.78, 59.575, 0.15, "Magadan"),
      stat("and in nineteen fifty-seven", "1957", "Dalstroy dissolved", DAL),
      photo("Some former prisoners stayed,", PH_NAGAEVO, "Magadan, Nagaev Bay"),
      photo("So the state turned", PH_MAG_UNSPLASH, "Magadan")),
)

# ================================================================== 6. Money and the BAM
chapter(
    P("P29",
      photo(0, PH_MAG_LIGHTS, "Magadan at night"),
      m("Workers in the Far", v(FAR_EAST, highlight=[FEFD_A])),
      photo("and they were guaranteed", PH_PEVEK, "Pevek, Chukotka, 2008"),
      photo("For many people, that", PH_ANADYR, "Anadyr harbour, Chukotka"),
      sat("work hard, save, and", 177.50, 64.73, 0.3, "Anadyr, June 2024", date=SUMMER24)),
    P("P30",
      m(0, v(BAM_V, routes=[TRANSSIB_E])),
      m("the Baikal-Amur Mainline, or", v(BAM_V, routes=[TRANSSIB_E, BAM], places=[TAYSHET, SOVGAVAN])),
      sat("across seven mountain ranges,", 117.0, 56.8, 1.2, "Along the BAM: the Kodar Range"),
      stat("About forty percent of", "~40 %", "Of BAM track laid on permafrost", MSU),
      stat("The full line runs", "4,324 KM", "Tayshet to Sovetskaya Gavan", "Russian Railways (via Wikipedia)")),
    P("P31",
      photo(0, PH_TYNDA, "Tynda, the 'capital of the BAM'"),
      sat("Young volunteers from across", 137.02, 50.55, 0.3, "Komsomolsk-on-Amur, the BAM's eastern junction"),
      sat("and new towns grew", 124.72, 55.15, 0.2, "Tynda", date=SUMMER24),
      stat("In nineteen eighty-four, a", "1984", "Golden spike: less than a third of the line working", MSU),
      m("But at that point,", v(BAM_V, routes=[BAM])),
      photo("The line was cut", PH_TYNDA_RAIL, "Single track at Tynda"),
      stat("and it was only", "1991", "The BAM is declared complete", MSU)),
    P("P32",
      m(0, v(RUSSIA, highlight=[FEFD_A])),
      sat("Mining towns on the", 148.16, 62.78, 0.3, "Susuman, a Kolyma mining town", date=SUMMER24),
      sat("railway towns in the", 109.31, 55.64, 0.3, "Severobaikalsk, a BAM town"),
      photo("all built by a", PH_PEVEK_S, "Pevek, Chukotka"),
      m("and shipped in their", v(FAR_EAST, highlight=[FEFD_A], places=[MAGADAN, ANADYR, YAKUTSK])),
      m("And then, at the", v(RUSSIA, highlight=[FEFD_A], places=[MOSCOW]))),
)

# ================================================================== 7. The emptying
chapter(
    P("P33",
      m(0, v(KOLYMA, highlight=["Magadan@red"], places=[MAGADAN])),
      stat("the last Soviet census", "385,340", "Magadan Oblast, 1989 (without Chukotka)", CENSUS89),
      photo("in Magadan Oblast, the", PH_MAG_GERTNER, "Magadan, Gertner Bay"),
      stat("At Russia's census of", "136,085", "Magadan Oblast, 2021", ROSSTAT),
      stat("That is a loss", "-65 %", "Magadan Oblast, 1989 to 2021", OWNCEN),
      photo("Almost two out of", PH_MAG_UNSPLASH, "Magadan")),
    P("P34",
      m(0, v(CHUKOTKA, highlight=["Chukotka Autonomous Okrug@red"], places=[ANADYR, ALASKA])),
      stat("had about a hundred", "157,528 → 47,490", "Chukotka, 1989 to 2021", CENSUS89),
      chart("That is seventy percent", "Population change, 1989 to 2021", "%",
            [["Chukotka", -70], ["Magadan", -65], ["Kamchatka", -37], ["Sakhalin", -34], ["Primorsky", -18]], OWNCEN,
            reveal=["Kamchatka lost more", "So did Sakhalin.", "Even the southern Primorsky", "with Vladivostok in it,"])),
    P("P35",
      sat(0, 170.30, 69.70, 0.3, "Pevek, Chukotka"),
      photo("life in a place", PH_ANADYR, "Anadyr"),
      photo("The mines and factories", PH_BUTUG_ADMIN, "Abandoned camp buildings, Butugychag"),
      sat("People who could leave,", 150.82, 59.55, 0.4, "Magadan, 2025"),
      photo("Some mining settlements were", PH_MAG_LIGHTS, "Magadan today")),
    P("P36",
      m(0, v(FAR_EAST, highlight=[FEFD])),
      photo("But it was emptier", PH_MAG_VIEW, "Magadan"),
      photo("Most of those people", PH_R504_AUTUMN, "Kolyma"),
      photo("They left because the", PH_NAGAEVO, "Magadan")),
    P("P37",
      m(0, v(FAR_EAST, highlight=[FEFD_A])),
      stat("In twenty sixteen, it", "2016", "The Far Eastern Hectare: free land for Russian citizens", ERDC),
      sat("Russian citizens can apply", 142.73, 46.96, 0.25, "Yuzhno-Sakhalinsk"),
      photo("to build a house,", PH_YUZHNO, "Yuzhno-Sakhalinsk"),
      m("According to the state", v(FAR_EAST, highlight=[FEFD_A], places=[YAKUTSK, KHAB, PETRO])),
      stat("by August twenty twenty-five,", "151,103", "People given a plot in the Far East, by 27 Aug 2025", ERDC),
      sat("people had received a", 158.65, 53.02, 0.4, "Petropavlovsk-Kamchatsky"),
      stat("Just over half of", "53 %", "Of the land used for housing", ERDC, note="Farming: 28 %")),
    P("P38",
      m(0, v(FAR_EAST, highlight=["Magadan@red", "Chukotka Autonomous Okrug@red"])),
      stat("lost more than three", "~359,000", "People lost by Magadan Oblast and Chukotka, 1989-2021", OWNCEN, note="vs 151,103 hectare plots"),
      m("If you were offered", v(FAR_EAST, highlight=[FEFD_A], places=[VLAD_C, KHAB, YAKUTSK, MAGADAN, PETRO])),
      photo("Because before you answer,", PH_KORYAK, "Koryaksky volcano above Petropavlovsk-Kamchatsky"),
      ask=("If you were offered", "Would you take a free hectare in Russia's Far East? Where?")),
)

# ================================================================== 8. Kamchatka and China
chapter(
    P("P39",
      m(0, v(KAMCHATKA, places=[PETRO, QUAKE])),
      photo("the seafloor off the", PH_SHAKEMAP, "USGS ShakeMap, 29 July 2025"),
      stat("The U.S. Geological Survey", "M 8.8", "Kamchatka, 29 July 2025, 23:24 UTC", USGS),
      stat("It is among the", "TOP 10", "Among the largest earthquakes recorded since 1900", USGS, note="The largest since Tohoku, 2011"),
      m("and the largest on", v({"lon": 150.0, "lat": 46.0, "span": 32.0}, places=[QUAKE, place("Tohoku", 142.37, 38.30, "Tohoku, 2011", icon="warning")])),
      photo("Tsunami warnings went out", PH_SWOT, "The tsunami seen by the SWOT satellite (NASA)")),
    P("P40",
      m(0, v(KAMCHATKA, arrows=PLATE, places=[QUAKE])),
      photo("That same push lifts", PH_KLYUCH, "Klyuchevskaya Sopka, January 2021"),
      photo("In nineteen fifty-two, the", PH_PETRO, "Petropavlovsk-Kamchatsky"),
      photo("Russia's Pacific edge is", PH_AVACHA, "Avachinsky volcano"),
      photo("It is some of", PH_TOLBACHIK, "Tolbachik volcano, Kamchatka")),
    P("P41",
      m(0, v(AMUR_V, routes=[AMUR_BORDER], places=[KHAB])),
      sat("form a long stretch", 127.52, 50.26, 0.2, "Blagoveshchensk (Russia) and Heihe (China), across the Amur"),
      m("On the Russian side,", v(FAR_EAST, highlight=[FEFD])),
      m("On the Chinese side,", v(CHINA_V, highlight=[CHINA_NE], places=[HARBIN, CHANGCHUN, SHENYANG])),
      stat("had about ninety-eight and", "98.5 MILLION", "Heilongjiang, Jilin and Liaoning, 2020 census", NBS, note="Russian Far East: 7.98 million (2021)"),
      sat("Heilongjiang alone, the province", 126.63, 45.75, 0.4, "Harbin, capital of Heilongjiang"),
      stat("has about four times", "~4×", "Heilongjiang (31.9 M) vs the whole Russian Far East", "Own calculation: NBS 2020, Rosstat 2021")),
    P("P42",
      m(0, v(CHINA_V, highlight=[CHINA_NE], places=[HARBIN])),
      stat("At their census, all", "6.98 %", "Northeast's share of China's people, 2020", NBS, note="2010: 8.18 %"),
      photo("Analyses of that census", PH_BLAG_HEIHE2, "Heihe and Blagoveshchensk"),
      m("On both sides of", v(CHINA_V, highlight=[CHINA_NE, FEFD], routes=[AMUR_BORDER]))),
)

# ================================================================== Ending
chapter(
    P("P43",
      photo(0, PH_VLA_SKY, "Vladivostok"),
      m("Every winter, some of", v(ASIA_E, arrows=WINTER_WIND, places=[SIB_HIGH, VLAD_C])),
      photo("That air freezes the", PH_MOD_STREETS, "The Sea of Okhotsk in winter"),
      photo("than sea ice forms", PH_MOD_ICYHEART, "The Sea of Okhotsk, March 2021 (NASA MODIS)"),
      photo("and it keeps the", PH_YAK_STREET, "Yakutsk in winter")),
    P("P44",
      photo(0, PH_MAP_1851, "Manchuria on an 1851 map"),
      m("Russia took the southern", v(AMUR_V, highlight=[AIGUN, PRIM])),
      photo("It filled the north", PH_KOLYMA_2001, "The Kolyma Highway"),
      photo("and when the wages", PH_PEVEK, "Pevek, Chukotka, 2008"),
      m("What is left is", v(FAR_EAST, layer="night", routes=[TRANSSIB_E])),
      m("and behind it, an", v(RUSSIA, highlight=[FEFD]))),
    P("P45",
      m(0, v(LATLINE, routes=[LAT43], places=[NICE, VLAD])),
      photo("One faces a warm", PH_NICE_BAY, "Nice"),
      sat("The other faces the", 131.75, 43.25, 1.2, "Amur Bay in January", date=ICE_DAY),
      photo("A free hectare of", PH_AMURSKY, "Amur Bay in summer"),
      photo("The open question is", PH_VLA_1992, "Vladivostok"),
      sat("will make people choose", 131.92, 43.12, 0.15, "Vladivostok", date=SUMMER24),
      ask=("The open question is", "Would anything make you move to Russia's Far East?")),
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


TITLE = "Why Russia's Pacific Coast Is Almost Empty"
script = {
    "title": TITLE,
    "voice": "am_michael",
    "voice_speed": 1.15,
    "music": "procedural",
    "map_style": "satellite",
    "look": "none",
    "photo_upscale": True,
    "sources": ["episodes/russia-far-east/research.md and factcheck.md", "Contains modified Copernicus Sentinel data 2026",
                "NASA MODIS imagery (NASA EOSDIS GIBS)", "Regions: Natural Earth (public domain); 1858 area approximate",
                "Railway and highway lines drawn through their main towns (approximate)"],
    "thumbnail": {"text": "WHY SO EMPTY?"},
    "chapters": chapters,
    "youtube": {
        "title": TITLE,
        "description": "Vladivostok sits at the same latitude as Nice on the French Riviera, yet its January average is about minus twelve, and the bay beside it freezes. North of it lies Russia's Far East: about 40 % of Russia, with fewer than eight million people. We follow the answer from orbit: the Siberian High and the winter monsoon, the Sea of Okhotsk freezing closer to the equator than any other sea ice, permafrost under Yakutsk, the treaties of 1858 and 1860, the Trans-Siberian, the camps of Dalstroy and the Kolyma Highway, the BAM railway, the emptying after 1991 (Magadan -65 %, Chukotka -70 %), the Far Eastern Hectare, the 2025 Kamchatka earthquake, and the hundred million people across the Amur in China.",
        "tags": ["Russian Far East", "Vladivostok", "Siberia", "Sea of Okhotsk", "Siberian High", "permafrost", "Yakutsk", "Magadan",
                 "Kolyma", "Chukotka", "Kamchatka", "Trans-Siberian", "BAM railway", "Far Eastern Hectare", "geography", "satellite images"],
        "pinned_comment": "Would you take a free hectare in Russia's Far East? Where would you put it?",
    },
}
out = HERE / "script.json"
out.write_text(json.dumps(script, ensure_ascii=False, indent=1) + chr(10), encoding="utf-8")
words = sum(len(p["text"].split()) for c in chapters for p in c["paragraphs"])
shots = [s for c in chapters for p in c["paragraphs"] for s in p["shots"]]
kinds = {k: sum(1 for s in shots if s["type"] == k) for k in ("map", "photo", "stat", "document", "chart")}
print(f"{words} words, {len(chapters)} chapters, {len(shots)} shots {kinds}")
