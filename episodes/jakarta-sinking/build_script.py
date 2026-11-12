"""Builds script.json for jakarta-sinking (beats are easier to review here than in the JSON).  python build_script.py

Sources: research.md + verification.md (Antara, Katadata, Jatengpos, Disway, DSDA, Jakarta Post, Kompas/FIA UI, NASA Earth
Observatory, Al Jazeera, Euronews/AFP, Mongabay, Eco-Business, detikInet, Virginia Tech / Science Advances) and our own
Landsat / Sentinel-2 measurements (tools/demak_shoreline.py, tools/ikn_clearing.py). Coordinates: checked on the storyboard.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
AFTER = "2026-06-01/2026-10-31"  # dry season (Java / Borneo are cloudy the rest of the year)
# Single clear days picked from the Sentinel-2 archive (2026-11-12): the composites showed seams and no-data wedges.
JKT_DAY = "2025-08-26/2025-08-26"    # tiles 48MXU + 48MYU, both < 1 % cloud (2026-08-08 left a tint seam at the tile edge)
DEMAK_DAY = "2026-10-14/2026-10-14"  # tile 49MDN, 0 % cloud
IKN_DAY = "2026-08-29/2026-08-29"    # tiles 50MME + 50MMD, same pass, 6-10 % cloud


def day_for(view):
    lon, span = view["lon"], view["span"]
    if span > 2:
        return None
    if lon > 115:
        return IKN_DAY
    if 110.2 < lon < 110.8 and span <= 0.4:
        return DEMAK_DAY
    if 106.5 < lon < 107.1 and span <= 0.7:
        return JKT_DAY
    return AFTER
LS = "landsat"

JAVA = {"lon": 109.2, "lat": -6.7, "span": 7.5}
INDONESIA = {"lon": 112.0, "lat": -3.5, "span": 16}
JKT_BAY = {"lon": 106.80, "lat": -6.08, "span": 0.42}
JKT_BAY_W = {"lon": 106.76, "lat": -6.07, "span": 0.5}  # Landsat wipe: 30 m pixels need a wide frame
JKT_NORTH = {"lon": 106.80, "lat": -6.11, "span": 0.12}
MUARA_BARU_V = {"lon": 106.805, "lat": -6.104, "span": 0.045}
PLUIT_V = {"lon": 106.792, "lat": -6.118, "span": 0.06}
PIK2_V = {"lon": 106.70, "lat": -6.035, "span": 0.12}
DEMAK_W = {"lon": 110.495, "lat": -6.91, "span": 0.16}
DEMAK_V = {"lon": 110.50, "lat": -6.912, "span": 0.07}
BEDONO_V = {"lon": 110.485, "lat": -6.925, "span": 0.05}
TIMBUL_V = {"lon": 110.517, "lat": -6.913, "span": 0.05}
SEMARANG_V = {"lon": 110.43, "lat": -6.94, "span": 0.18}
IKN_W = {"lon": 116.696, "lat": -0.959, "span": 0.12}
IKN_V = {"lon": 116.6962, "lat": -0.9587, "span": 0.05}
SEPAKU_V = {"lon": 116.73, "lat": -0.93, "span": 0.08}
BORNEO_V = {"lon": 116.6, "lat": -1.1, "span": 2.4}  # > 2: undated wide view (dated mosaics leave gaps this wide)


def near(lon, lat, span=0.05):
    return {"lon": lon, "lat": lat, "span": span}


def place(name, lon, lat, label=None, kind="site", icon=None):
    d = {"name": name, "lon": lon, "lat": lat, "kind": kind, "label": label if label is not None else name}
    if icon:
        d["icon"] = icon
    return d


JAKARTA = place("Jakarta", 106.8272, -6.1754, "Jakarta", "capital")
MUARA_BARU = place("Muara Baru", 106.805, -6.103, "Muara Baru", "site")
PLUIT = place("Pluit", 106.795, -6.115, "Pluit", "site")
MUARA_ANGKE = place("Muara Angke", 106.772, -6.106, "Muara Angke", "site")
PIK2 = place("PIK 2", 106.70, -6.03, "Pantai Indah Kapuk 2", "site")
TIMBULSLOKO = place("Timbulsloko", 110.518, -6.914, "Timbulsloko", "city")
BEDONO = place("Bedono", 110.48467, -6.92716, "Bedono", "city")
DEMAK = place("Demak", 110.64, -6.89, "Demak", "city")
SEMARANG = place("Semarang", 110.42, -6.97, "Semarang", "city")
PEKALONGAN = place("Pekalongan", 109.68, -6.88, "Pekalongan", "city")
SERANG = place("Serang", 106.15, -6.12, "Serang", "city")
GRESIK = place("Gresik", 112.65, -7.16, "Gresik", "city")
NUSANTARA = place("Nusantara", 116.6962, -0.9587, "Nusantara: Garuda Palace", "capital")
SEPAKU = place("Sepaku", 116.73, -0.93, "Sepaku", "city")
BALIKPAPAN = place("Balikpapan", 116.83, -1.24, "Balikpapan", "city")
GSW = {"from": [106.15, -6.03], "to": [112.65, -7.10], "mode": "line", "seconds": 4, "label": "Giant Sea Wall, about 575 km",
       "via": [[106.50, -6.02], [106.80, -6.07], [107.10, -5.97], [107.60, -6.20], [108.20, -6.30], [108.57, -6.70],
               [109.10, -6.83], [109.68, -6.86], [110.20, -6.90], [110.43, -6.93], [110.60, -6.80], [111.10, -6.55],
               [111.60, -6.70], [112.05, -6.88], [112.65, -7.10]]}
MOVE = {"from": [106.8272, -6.1754], "to": [116.6962, -0.9587], "mode": "line", "seconds": 3, "label": "To Borneo"}

CMP_DEMAK = {"before": "1990-06-01/1990-10-31", "after": AFTER, "source": LS, "seconds": 2.6,
             "label_before": "1990", "label_after": "2026"}
CMP_BAY = {"before": "1990-07-09", "after": AFTER, "source": LS, "seconds": 2.6,
           "label_before": "1990", "label_after": "2026"}
CMP_IKN = {"before": "2019-08-16/2019-08-16", "after": IKN_DAY, "seconds": 2.4,  # 16 Aug 2019: ten days before the announcement;  # Landsat: one 185 km swath covers the box (S2 composites left a swath-edge patch)  # single clear days (86 % / 91 %): composites left a swath-edge patch
           "label_before": "2019", "label_after": "2026"}


def m(at, *steps, text=None, keep=False, cut=False):
    s = {"type": "map", "at": at, "map": {"steps": list(steps)}}
    if keep:
        s["map"]["keep"] = True
    if cut:
        s["map"]["cut"] = True
    if text:
        s["on_screen_text"] = text
    return s


def v(view, at=None, date=None, **kw):
    if date is None:
        date = day_for(view)
    d = {"view": view, **kw}
    if at is not None:
        d["at"] = at
    if date:
        d["date"] = date
    return d


def step(at, **kw):
    return {"at": at, **kw}


def photo(at, name, text=None):
    d = {"type": "photo", "at": at, "photo": name}
    if text:
        d["on_screen_text"] = text
    return d


def stat(at, value, label, source, note=None):
    d = {"value": value, "label": label, "source": source}
    if note:
        d["note"] = note
    return {"type": "stat", "at": at, "stat": d}


def clip(at, text, source, highlight=None):
    d = {"text": text, "source": source}
    if highlight:
        d["highlight"] = highlight
    return {"type": "document", "at": at, "document": d}


def chart(at, title, unit, data, source, reveal=None, highlight=0, kind="bar"):
    c = {"type": kind, "title": title, "unit": unit, "data": data, "source": source, "highlight": highlight}
    if reveal:
        c["reveal"] = reveal
    return {"type": "chart", "at": at, "chart": c}


def P(text, *shots, ask=None):
    d = {"text": text, "shots": list(shots)}
    if ask:
        d["ask"] = {"at": ask[0], "text": ask[1]}
    return d


OWN_DEMAK = "Our measurement, Landsat 5, 8 and 9"
OWN_IKN = "Our measurement, Sentinel-2"
JP = "The Jakarta Post"
NASA_EO = "NASA Earth Observatory"
AFP = "AFP via Euronews, Jul 25, 2023"

PH_MAKJAH = "File:Rumah Mak Jah di Desa Bedono yang Tenggelam karena abrasi.jpg"  # CC BY 4.0, Tim LindungiHutan
PH_FARMER = "File:Ihwanudin, petani mangrove di Desa Bedono, Demak yang bertahan menanam mangrove di tengah ancaman abrasi.jpg"  # CC BY 4.0
PH_PALACE = "File:President Joko Widodo inspecting the construction of the Presidential Palace in Nusantara (5 June 2024).jpg"  # PD
PH_GARUDA = "File:Istana Garuda IKN.png"  # CC0
PH_FLOOD1 = "File:VOA People walk through Jakarta's flooded streets.jpg"  # PD, 17 Jan 2013 (rain flood)
PH_FLOOD2 = "File:VOA A car tries to drive through Jakarta's flooded streets.jpg"  # PD
PH_SEAWALL = "File:Sunda Kelapa lighthouse and sea wall.jpg"  # CC BY-SA 4.0, Rochelimit
PH_MUARA = "File:Waterway muara baru - panoramio.jpg"  # CC BY-SA 3.0
PH_PIK2 = "File:Pantai Indah Kapuk 2 - Tangerang, BT (23 June 2023) 01.jpg"  # CC BY-SA 4.0, Firzafp
PH_PIK2B = "File:Pantai Indah Kapuk 2 - Tangerang, BT (22 Februari 2024) 1.jpg"  # CC BY 4.0
PH_NIGHT = "nasa:iss073e0222649"  # Jakarta at night, ISS, 26 May 2025

# Own measurements (filled from the tool outputs; see demak_shoreline.json / ikn_clearing.json)
DEMAK_HA = (2507, 445)  # land in the three boxes, 1990 -> 2026 (demak_shoreline.json)
IKN_HA = 650  # green in 2019, bare or built in 2026, 6 x 6 km box around the palace (ikn_clearing.json)

chapters = [
    {"title": "A Wall of Trees", "mood": "tension", "paragraphs": [
        P("On October 19, 2026, two officials waded into the mud of a village called Timbulsloko, on the north coast of Java, and planted mangrove seedlings. The ceremony was billed as the start of the Giant Sea Wall: a barrier about five hundred and seventy-five kilometres long, meant to protect tens of millions of people from the sea.",
          m(0, v(JAVA, places=[TIMBULSLOKO]), step("a village", view=near(110.52, -6.91, 0.35), places=[TIMBULSLOKO]), step("planted", view=TIMBUL_V, places=[TIMBULSLOKO])),
          stat("about five", "~575 km", "Planned length of Java's Giant Sea Wall", "Antara; Katadata, Oct 2026")),
        P("Three weeks later, residents told a local paper that the seedlings had died. Planting at a ceremony is not enough, a local woman, Masnuah, told the paper. Someone has to look after them.",
          m(0, v(near(110.512, -6.906, 0.04))),
          clip("Planting at", "Menanam mangrove tidak cukup hanya saat ada acara seremonial. Setelah ditanam, harus ada yang bertanggung jawab merawatnya.\n(Planting mangroves at a ceremony is not enough. Once planted, someone has to be responsible for looking after them.)",
               "Masnuah, to Disway Jateng, Nov 9, 2026", highlight="harus ada yang bertanggung jawab merawatnya"),
          m("Someone has", v(near(110.508, -6.921, 0.035)), cut=True)),
        P("This is Timbulsloko's coast from orbit in 1990. And this is the same coast this year. Nadhiri, village head since 2009, told a local paper that Timbulsloko used to be a rich village, with rice fields, dry fields and fish ponds. Today the sea comes up to the houses.",
          m(0, v(DEMAK_W, compare={**CMP_DEMAK, "until": "And this", "seconds": 1.8}), step("And this", places=[TIMBULSLOKO, BEDONO]), cut=True),
          m("village head", v(TIMBUL_V, places=[TIMBULSLOKO]), cut=True),
          m("Today the sea", v(near(110.526, -6.908, 0.04)), cut=True)),
        P("Four hundred kilometres to the west, the country's capital is sinking too. Jakarta was once called the fastest-sinking city in the world. Indonesia's answers have been a wall, a new capital in the forest of Borneo, and now a wall along half of Java. Which of them can still work?",
          m(0, v(JAVA, places=[TIMBULSLOKO, JAKARTA])),
          m("Jakarta was", v(JKT_NORTH, places=[MUARA_BARU, PLUIT]), cut=True),
          m("a new capital", v(INDONESIA, places=[JAKARTA, NUSANTARA], routes=[MOVE])),
          m("and now", v(JAVA, routes=[GSW], places=[GRESIK])),
          ask=("Which of", "A wall, a new capital, or a longer wall?")),
    ]},
    {"title": "Faster Than the Sea", "mood": "curious", "paragraphs": [
        P("About thirty-two million people live in greater Jakarta, NASA says, more than twice as many as in 1990. For decades, many of them, and many factories, drew their water from wells beneath the city.",
          photo(0, PH_NIGHT, "Jakarta at night, from the ISS, May 2025"),
          stat("more than twice", "~32 million", "People in greater Jakarta, more than double 1990", NASA_EO + ", 2021"),
          m("For decades", v(near(106.83, -6.2, 0.6), places=[JAKARTA]), cut=True)),
        P("When water is pumped out of the clay and sand under a city, the ground packs down and drops. Between 1982 and 2010, Indonesian geodesists measured Jakarta sinking one to fifteen centimetres a year, and in some spots twenty to twenty-eight.",
          m(0, v(JKT_NORTH, places=[PLUIT, MUARA_BARU])),
          stat("Between 1982", "Up to 28 cm a year", "Jakarta subsidence hot spots, 1982-2010", "Abidin et al., Natural Hazards, 2011")),
        P("In 2018 one of them, Heri Andreas of the Bandung Institute of Technology, told the BBC that about ninety-five percent of North Jakarta could be under water by 2050. It was a projection, and it made headlines around the world.",
          m(0, v(MUARA_BARU_V, places=[MUARA_BARU])),
          stat("about ninety-five", "95%", "North Jakarta under water by 2050: one researcher's 2018 projection", "Heri Andreas, ITB, to the BBC, 2018")),
        P("Floods are not new here. In 2007 a monsoon flood covered more than seventy percent of the city, NASA reports, and in 2013 the streets flooded again. By some estimates, up to forty percent of Jakarta now lies below sea level. Every centimetre the ground loses makes the next high tide a little more dangerous.",
          m(0, v(near(106.83, -6.19, 0.2), places=[JAKARTA])),
          photo("and in 2013", PH_FLOOD1, "Jakarta flood, January 2013"),
          stat("By some", "40%", "Share of Jakarta below sea level, by some estimates", NASA_EO + ", 2021"),
          m("Every centimetre", v(near(106.80, -6.12, 0.09), places=[PLUIT]), cut=True)),
        P("The sea itself rises about four millimetres a year around Indonesia, according to the national weather agency. So where it was worst, the land was dropping dozens of times faster than the sea was rising.",
          chart(0, "Sinking land vs rising sea, cm a year", " cm", [["Muara Baru, before 2019", 20], ["Muara Baru, 2019", 10], ["Sea level, Indonesia", 0.4]],
                "Heri Andreas via The Jakarta Post, 2019 (lower ends of the ranges); BMKG via Mongabay, 2025", reveal=["about four", "So where"], highlight=2),
          m("faster than", v(near(106.80, -6.10, 0.05), places=[MUARA_BARU]), cut=True)),
        P("Then something changed. By 2019, Andreas measured Muara Baru at about ten to twelve centimetres a year, down from twenty or more. A 2022 study of ninety-nine coastal cities found that Jakarta's sinking had slowed significantly, likely because less groundwater was being pumped.",
          m(0, v(PLUIT_V, places=[PLUIT])),
          m("A 2022", v(near(106.80, -6.14, 0.2)), cut=True),
          clip("slowed significantly", "Jakarta's sinking slowed significantly, likely due to reduced groundwater extraction.", "Wu, Wei & D'Hondt, Geophysical Research Letters, 2022, as summarised by SciDev", highlight="reduced groundwater extraction")),
        P("In 2021 the city declared zones where groundwater may no longer be drawn, and its water company says its pipes now reach about four in five residents, with everyone connected by 2029.",
          m(0, v(near(106.86, -6.2, 0.25), places=[JAKARTA])),
          stat("about four", "~82%", "Jakarta's piped-water coverage, Jul 2026 (target: 100% by 2029)", "PAM Jaya via Katadata, Jul 2026")),
        P("But slower is not stopped. Studies of the last few years still find several centimetres a year along the north coast, close to ten times the rise of the sea. And land that has sunk does not come back up.",
          m(0, v(near(106.77, -6.105, 0.07), places=[MUARA_ANGKE])),
          m("And land", v(JKT_NORTH), cut=True)),
    ]},
    {"title": "The Wall That Leaks", "mood": "tension", "paragraphs": [
        P("Jakarta's first answer was a wall. Since 2014 the city and the national government have been building concrete dikes along the shore and the river mouths, under a programme called NCICD.",
          m("Since 2014", v(JKT_NORTH, places=[MUARA_BARU, MUARA_ANGKE, PLUIT]), cut=True)),
        P("The plan covers about forty kilometres of the most exposed coast. By the end of 2025 a little under half of it was built, and the finish date was 2030.",
          stat(0, "~40 km", "NCICD coastal dikes: a little under half built by end-2025, target 2030", "DSDA Jakarta, Jul 2025; The Jakarta Post, Dec 2025")),
        P("On December 6, 2025, part of the wall at Muara Baru failed. Sea water ran into dozens of neighbourhoods behind it. Governor Pramono Anung said he understood the hardship of the residents, and promised repairs from 2026.",
          m(0, v(MUARA_BARU_V, places=[MUARA_BARU])),
          m("Sea water", v(near(106.80, -6.11, 0.07)), cut=True)),
        P("Nurhasan lives about eight hundred metres from that dike. He told interviewers, in a report Kompas republished, that it had started leaking three or four years earlier. This dike was built in Ahok's time, he said, meaning a governor who left office in 2017.",
          m(0, v(near(106.808, -6.11, 0.035))),
          clip("This dike", "Bocornya mulai sekitar 3-4 tahun lalu. Ini tanggul dibangun zamannya Ahok.\n(It started leaking about three or four years ago. This dike was built in Ahok's time.)", "Nurhasan, 40, Muara Baru, via Kompas / FIA UI, Dec 8, 2025", highlight="Bocornya mulai sekitar 3-4 tahun lalu"),
          m("meaning a governor", v(near(106.80, -6.098, 0.04), places=[MUARA_BARU]), cut=True)),
        P("Just outside the wall at Muara Baru stands a mosque the sea has already taken. Built in 1996, Wal Adhuna began to be swallowed by the sea in the 2000s. Today it stands in the water, on the wrong side of the dike.",
          m(0, v(near(106.8065, -6.109, 0.035), places=[place("Wal Adhuna", 106.8065, -6.11107, "Wal Adhuna mosque", "site")])),
          m("Today it", v(near(106.81, -6.112, 0.05)), cut=True)),
        P("The head of the city's water agency draws a line. These coastal dikes, she says, are not the Giant Sea Wall. That is a bigger idea, out in the bay.",
          m(0, v(near(106.812, -6.108, 0.05))),
          clip("These coastal", "Jadi pertanyaannya apakah tanggul-tanggul pengaman pantai ini Giant Sea Wall? Bukan. Beda.\n(So the question is: are these coastal dikes the Giant Sea Wall? No. They are different.)", "Ika Agustin Ningrum, head of DSDA Jakarta, Dec 11, 2025", highlight="Bukan. Beda."),
          m("That is", v(JKT_BAY), cut=True)),
        P("An earlier version, unveiled in 2014, was shaped like the Garuda, Indonesia's mythical bird, with seventeen artificial islands. It was cancelled in 2017. Four of the islands were finished anyway. Thirteen were halted.",
          m(0, v(near(106.78, -6.085, 0.14), places=[PLUIT])),
          stat("Four of", "4 of 17", "Reclamation islands finished in Jakarta Bay; 13 halted", "Mongabay, Mar 2019")),
        P("Not everyone wanted a wall in the bay. In 2014, two fishers' groups, KIARA and KNTI, estimated that at least sixteen thousand eight hundred fishermen would lose their homes or their livelihood to the offshore plan. The fishing harbours of Muara Angke and Muara Baru sit right on this shore.",
          m(0, v(near(106.772, -6.103, 0.05), places=[MUARA_ANGKE])),
          stat("at least", "16,855", "Fishers estimated to lose homes or livelihoods to the 2014 offshore plan", "KIARA and KNTI, via The Jakarta Post, Oct 2014"),
          m("The fishing", v(near(106.79, -6.10, 0.08), places=[MUARA_ANGKE, MUARA_BARU]), cut=True)),
        P("From orbit you can see what was built. This is Jakarta Bay in 1990. And this is the same bay this year, with new islands, new suburbs on reclaimed land, and Pantai Indah Kapuk 2 spreading west along the coast.",
          m(0, v(JKT_BAY_W, compare={**CMP_BAY, "until": "And this", "seconds": 2.0}), step("And this", places=[PIK2]), cut=True),
          m("reclaimed land", v(near(106.76, -6.09, 0.12), places=[PLUIT]), cut=True),
          m("Pantai Indah", v(PIK2_V, places=[PIK2]), cut=True)),
        P("NASA counted more than one thousand one hundred hectares of new land along this coast between 1990 and 2019. Land made on the sea, in a city that is sinking into it.",
          stat(0, "1,185+ ha", "New land along Jakarta's coast, 1990-2019", NASA_EO + ", May 2021"),
          m("Land made", v(near(106.76, -6.095, 0.12))),
          photo("in a city", PH_PIK2B, "Pantai Indah Kapuk 2, February 2024")),
    ]},
    {"title": "Plan B: Leave", "mood": "curious", "paragraphs": [
        P("In August 2019, President Joko Widodo announced a different answer: move the capital. On August 26 he named a site in East Kalimantan, on the island of Borneo, more than a thousand kilometres from Jakarta.",
          m(0, v(INDONESIA, places=[JAKARTA])),
          m("On August", v(INDONESIA, places=[JAKARTA, NUSANTARA], routes=[MOVE])),
          m("on the island", v(BORNEO_V, places=[NUSANTARA, BALIKPAPAN]), cut=True)),
        P("His reasons: Jakarta was crowded, polluted and sinking, and the new site was relatively free of earthquakes and volcanoes. The new city was named Nusantara. The plan at the time, news agencies reported: build from 2021 and move by 2024. Construction began in July 2022, about thirty kilometres inland from the sea near Balikpapan Bay.",
          m(0, v(near(106.83, -6.17, 0.3), places=[JAKARTA])),
          m("The new city", v(BORNEO_V, places=[NUSANTARA, BALIKPAPAN]), cut=True),
          m("Construction", v(near(116.70, -0.965, 0.22), places=[NUSANTARA]), cut=True)),
        P("This is the site in August 2019, ten days before it was announced. And this is the same forest this year. The plan promised that three quarters of the area would stay forest, for a first population of half a million people.",
          m(0, v(IKN_W, compare={**CMP_IKN, "until": "And this"}), step("And this", places=[NUSANTARA]),
            step("The plan", view=IKN_V, places=[NUSANTARA]), cut=True),
          stat("for a first", "75% forest", "Share of Nusantara meant to stay forest; first population 500,000", NASA_EO + ", Feb 2024")),
        P("The price was put at four hundred and sixty-six trillion rupiah, around thirty-two billion dollars, with the state meant to pay a fifth and private investors the rest. By 2024 the state had spent eighty-nine trillion rupiah.",
          photo(0, PH_PALACE, "The presidential palace under construction, June 2024"),
          stat("By 2024", "Rp 89 trillion", "State money spent on Nusantara, 2022-2024", JP + ", Aug 20, 2026")),
        P("NASA's own images showed the forest giving way in less than two years, from April 2022 to February 2024. Indonesian journalists at Tempo counted nearly two thousand five hundred hectares cleared or degraded in the core government zone in that time. In our own Sentinel-2 images, about six hundred and fifty hectares around the palace that were green in 2019 are bare or built over this year.",
          m(0, v(IKN_V, places=[NUSANTARA])),
          stat("nearly two", "~2,464 ha", "Forest cleared or degraded in Nusantara's core zone, Apr 2022 - Feb 2024", "Tempo analysis of NASA Landsat images, 2024"),
          m("In our own", v(near(116.71, -0.95, 0.06)), cut=True),
          stat("about six", "~650 ha", "Green in 2019, bare or built in 2026: 6 x 6 km around the palace", OWN_IKN, "Some of it was plantation that would have been cut anyway")),
        P("Not everyone wanted the city. The Balik people of Sepaku live right next to the site. We don't want to be relocated from the land of our ancestors, their chief Sibukdin told Al Jazeera in 2023. A neighbour, Sernai, sixty-eight, said: They will take my house eventually.",
          m(0, v(SEPAKU_V, places=[SEPAKU, NUSANTARA])),
          clip("We don't", "\"We don't want to be relocated from the land of our ancestors.\"", "Sibukdin, Balik chief, Sepaku, to Al Jazeera, Mar 15, 2023", highlight="the land of our ancestors"),
          m("told Al Jazeera", v(near(116.725, -0.925, 0.05), places=[SEPAKU]), cut=True),
          clip("A neighbour", "\"They will take my house eventually.\"", "Sernai, 68, Sepaku, to Al Jazeera, Mar 15, 2023")),
        P("The Indigenous peoples' alliance AMAN estimated that at least twenty thousand Indigenous people would have to move for the new capital. In March 2024, hundreds of households in Sepaku received letters from the capital's authority, according to the mining watchdog JATAM. The authority's head at the time had promised room for dialogue.",
          m(0, v(near(116.74, -0.94, 0.06), places=[SEPAKU])),
          stat("at least twenty", "20,000+", "Indigenous people who would have to move: AMAN's estimate", "AMAN, via Al Jazeera, Mar 2023"),
          clip("The authority's", "\"We will give some room for dialogue, so they can have dialogue with us.\"", "Bambang Susantono, then head of the Nusantara authority, to Al Jazeera, 2023")),
        P("In August 2024, Indonesia held its Independence Day ceremony in Nusantara for the first time. It looked like the move had begun.",
          photo(0, PH_GARUDA, "The Garuda Palace, Nusantara"),
          m("It looked", v(IKN_V, places=[NUSANTARA]), cut=True)),
    ]},
    {"title": "The Capital That Stalled", "mood": "calm", "paragraphs": [
        P("Then the president changed. Prabowo Subianto took office in October 2024. In 2025 his government made Nusantara a political capital by 2028, with between one thousand seven hundred and four thousand one hundred civil servants to move first.",
          m(0, v(near(116.70, -0.962, 0.08), places=[NUSANTARA])),
          stat("with between", "1,700-4,100", "Civil servants to move first: a 'political capital' by 2028", "Perpres 79/2025, via CNN Indonesia and Kontan")),
        P("The money has shrunk year by year: about forty-three trillion rupiah in 2024, thirteen trillion in 2025, six point three trillion in 2026. About ten thousand people have moved in, against the half a million once planned. In his State of the Nation speech in August 2026, Prabowo did not mention Nusantara at all.",
          chart(0, "Nusantara budget, trillion rupiah", " T", [["2024", 43], ["2025", 13], ["2026", 6.3]], "ABC News, Oct 19, 2026; The Jakarta Post, Aug 2026",
                reveal=["thirteen trillion", "six point"], highlight=2),
          stat("About ten", "~10,000", "People who have moved to Nusantara so far (plan: 500,000 at first)", "ABC News, Oct 19, 2026"),
          m("In his", v(near(116.69, -0.975, 0.06)))),
        P("The authority's head, Basuki Hadimuljono, asked for about fifteen point eight trillion rupiah more for 2027 alone. In the 2027 budget bill, Indonesian business media report, Nusantara is not among the government's eight priorities. Most of next year's money is meant for buildings for parliament and the courts.",
          m(0, v(near(116.705, -0.97, 0.05))),
          stat("about fifteen", "+Rp 15.8 trillion", "Extra money the Nusantara authority asked for, 2027", "Katadata, Sep 9, 2026")),
        P("An economist, Bhima Yudhistira, put it plainly. The relocation of the capital clearly does not appear to be a priority for Prabowo, as it is seen as a sunk cost.",
          m(0, v(near(116.69, -0.96, 0.07))),
          clip("The relocation", "\"The relocation of the capital clearly does not appear to be a priority for Prabowo, as it is seen as a sunk cost.\"", "Bhima Yudhistira, CELIOS, to The Jakarta Post, Aug 2026", highlight="a sunk cost"),
          photo("as it is", PH_GARUDA, "The Garuda Palace, Nusantara")),
        P("And in May 2026, Indonesia's Constitutional Court ruled that Jakarta remains the capital until the president signs a decree moving it.",
          m(0, v(near(106.8272, -6.1754, 0.08), places=[JAKARTA]))),
        P("So the city that was built partly because Jakarta is sinking is not yet the capital. Jakarta, by law, still is. And the money the government talks about now is going somewhere else: back to the sea.",
          m(0, v(IKN_W)),
          m("Jakarta, by law", v(JKT_BAY), cut=True),
          m("back to the sea", v(JAVA, routes=[GSW])))
    ]},
    {"title": "Where the Sea Already Won", "mood": "calm", "paragraphs": [
        P("Back to Demak, the coast where this story began. Here the sea is not a forecast.",
          m(0, v(JAVA, places=[DEMAK])), m("Here the sea", v(near(110.52, -6.91, 0.3), places=[TIMBULSLOKO, BEDONO]), cut=True)),
        P("In the 1990s, mangroves along this shore were cut down to make fish ponds. Without their roots, the coast lost its defence. And the ground here sinks too: satellite radar measured about eight to nine centimetres a year at Timbulsloko between 2017 and 2019.",
          photo("Without their", PH_FARMER, "A mangrove farmer in Bedono, 2025"),
          stat("satellite radar", "~8.7 cm a year", "Subsidence at Timbulsloko, Sentinel-1 radar, 2017-2019", "Universitas Diponegoro, Jurnal Geodesi")),
        P("We measured this coast ourselves, in Landsat images from 1990 to 2026. This is 1990. And this is this year. In three boxes around Bedono, Timbulsloko and Surodadi, about two thousand five hundred hectares were land in 1990. This year, about four hundred and fifty are left. Around Timbulsloko, nine tenths of the land has turned to water. Some of it was fish ponds that flooded for good. The rest is open sea.",
          m(0, v(near(110.55, -6.87, 0.35), places=[TIMBULSLOKO])),
          m("This is 1990.", v(DEMAK_W, compare={**CMP_DEMAK, "until": "And this", "hold": 0.4}), step("And this", places=[TIMBULSLOKO, BEDONO]), cut=True),
          stat("about two thousand", "~2,500 ha -> ~450 ha", "Land in three boxes at Bedono, Timbulsloko and Surodadi, 1990 -> 2026", OWN_DEMAK),
          m("Around Timbulsloko", v(TIMBUL_V, places=[TIMBULSLOKO]), cut=True),
          m("The rest", v(near(110.50, -6.89, 0.06)), cut=True)),
        P("In Bedono, the next village, about two hundred and fifty families were moved away, Kompas reported. One family stayed. Pasijah, known as Mak Jah, raised her house and planted mangroves around it. For years she lived almost alone in her hamlet.",
          m(0, v(BEDONO_V, places=[BEDONO])),
          photo("One family", PH_MAKJAH, "Mak Jah's house, Bedono")),
        P("In Timbulsloko, the fisherman Sularso raised his floor three times after 2018, a metre and a half in all, for about twenty-two million rupiah. For me, there is no future, he told reporters in 2023.",
          m(0, v(TIMBUL_V, places=[TIMBULSLOKO])),
          clip("For me", "\"For me, there is no future.\"", "Sularso, 54, fisherman, Timbulsloko, to AFP, Jul 2023")),
        P("His neighbour Sulkan said: As long as there are still neighbours, there are still houses, I'm staying here. The village head says people stay for one reason. Warga bertahan di sini karena masalah ekonomi. People stay here for economic reasons.",
          m(0, v(near(110.512, -6.918, 0.04), places=[TIMBULSLOKO])),
          clip("As long", "\"As long as there are still neighbours, there are still houses, I'm staying here.\"", "Sulkan, 49, Timbulsloko, to AFP, Jul 2023"),
          m("The village", v(near(110.522, -6.905, 0.035), places=[TIMBULSLOKO]), cut=True),
          clip("Warga", "Warga bertahan di sini karena masalah ekonomi.\n(People stay here for economic reasons.)", "Nadhiri, village head of Timbulsloko, to Jatengpos, Oct 19, 2026", highlight="masalah ekonomi")),
        P("This April, a study in Science Advances measured northern Java from 2017 to 2023. At the most exposed coastal hot spots it found, the ground dropped up to ten centimetres a year in Pekalongan, eight in Semarang and about three and a half in Jakarta. Sinking land, not the rising sea, it found, is the main driver of flood risk along most of this coast.",
          m(0, v(JAVA, places=[SERANG, PEKALONGAN, SEMARANG, DEMAK])),
          m("At the most", v(near(109.6, -6.95, 2.8), places=[PEKALONGAN, SEMARANG]), cut=True),
          chart("up to ten", "Coastal hot spots, max sinking, northern Java, 2017-23", " cm a year", [["Pekalongan", 10], ["Semarang", 8], ["Jakarta", 3.6]],
                "Ohenhen, Shirzaei et al., Science Advances, Apr 2026", reveal=["eight in", "about three"], highlight=0),
          m("in Jakarta", v(near(106.80, -6.12, 0.1), places=[JAKARTA]), cut=True),
          m("Sinking land", v(near(110.0, -6.85, 2.4), places=[PEKALONGAN, SEMARANG, DEMAK]), cut=True)),
        P("In Demak and Pekalongan, more than thirty percent of the city area sinks faster than five centimetres a year. By 2050, the study says, sinking land could make up as much as eighty-five percent of the rise in water levels along much of the coast. More than a hundred and fifty million people live on Java.",
          m(0, v(near(109.68, -6.87, 0.12), places=[PEKALONGAN])),
          stat("as much as", "Up to 85%", "Sinking land's share of water-level rise on much of Java's coast, 2050", "Science Advances, Apr 2026"),
          m("More than a", v(JAVA, places=[JAKARTA, PEKALONGAN, SEMARANG, DEMAK]), cut=True)),
        P("What we see in Java, one of the authors said, is likely a preview of what could unfold elsewhere.",
          m(0, v(near(110.9, -6.75, 2.4))),
          clip("is likely", "\"What we see in Java is likely a preview of what could unfold elsewhere.\"", "Leonard Ohenhen, Virginia Tech, Apr 8, 2026", highlight="a preview")),
    ]},
    {"title": "The 575 Kilometre Bet", "mood": "tension", "paragraphs": [
        P("On August 14, 2026, Prabowo told parliament that the country must build the Giant Sea Wall, a great dike to secure the north coast of Java. This absolutely must be done, he said.",
          m(0, v(JAVA, routes=[GSW])),
          m("a great dike", v(near(108.6, -6.75, 2.4)), cut=True),
          clip("This absolutely", "Ini mutlak harus kita lakukan.\n(This absolutely must be done.)", "President Prabowo Subianto, Aug 14, 2026", highlight="Ini mutlak harus kita lakukan")),
        P("The plan is about five hundred and seventy-five kilometres of wall in fifteen segments, from Serang in the west to Gresik in East Java. Earlier versions said seven hundred. The authority in charge puts the cost at eighty to a hundred billion dollars, over fifteen to twenty years.",
          m(0, v(JAVA, routes=[GSW], places=[SERANG, GRESIK])),
          stat("eighty to a", "US$80-100 bn", "Estimated cost of the Giant Sea Wall, 15-20 years", "North Java Coast Authority via detik, Feb 24, 2026")),
        P("The president says the north coast is home to tens of millions of people. A new authority was created in August 2025 to run the project, led by a retired vice admiral, Didit Herdiawan Ashaf. Jakarta's own section alone is put at about eight billion dollars, The Jakarta Post reported, and the president asked the city to pay half.",
          m(0, v(near(108.6, -6.75, 2.4), places=[PEKALONGAN])),
          m("Jakarta's own", v(JKT_BAY, places=[JAKARTA]), cut=True)),
        P("Jakarta's part has grown from twelve to nineteen kilometres. Governor Pramono says the city must find at least five trillion rupiah a year for it, and that he wants a hybrid wall: concrete where it must be, mangroves where they can grow.",
          m(0, v(JKT_BAY_W)),
          stat("at least five", "Rp 5 trillion a year", "What Jakarta must find for its section of the wall", JP + ", Jun 2025"),
          m("a hybrid wall", v(near(106.74, -6.06, 0.1)), cut=True)),
        P("Concrete work is planned to begin in 2027. As one official put it in October: we will proceed with it next year. Until then, the first segment of the Giant Sea Wall is a row of mangroves in Timbulsloko.",
          clip("we will", "\"...we will proceed with it next year, God willing.\"", "Nazib Faizal, Coordinating Ministry for Infrastructure, to Antara, Oct 7, 2026", highlight="next year"),
          m("Until then", v(TIMBUL_V, places=[TIMBULSLOKO]), cut=True)),
        P("Critics are not convinced. Susan Herawati of the fishers' rights group KIARA warned against fake, quick-fix solutions that act like a fire extinguisher. WALHI's Jakarta office called the wall a false climate solution.",
          clip("Susan", "\"...fake, quick-fix solutions that act like a fire extinguisher.\"", "Susan Herawati, KIARA, via Mongabay, Sep 11, 2025", highlight="a fire extinguisher"),
          m("that act like", v(near(106.77, -6.10, 0.045), places=[MUARA_ANGKE]), cut=True),
          clip("WALHI's", "\"...a false climate solution.\"", "Suci Fitria Tanjung, WALHI Jakarta, via Eco-Business, Feb 28, 2025")),
        P("Lawyers in Semarang point to the toll road built across the ponds between Semarang and Demak as a sea dike, and say the entire coastal region is interconnected.",
          m(0, v(SEMARANG_V, places=[SEMARANG, BEDONO])),
          m("the toll road", v(near(110.46, -6.945, 0.08)), cut=True),
          m("as a sea dike", v(near(110.475, -6.935, 0.05)), cut=True),
          ),
        P("Scientists add one more point. A wall can hold back the sea, but it cannot stop the ground behind it from sinking. Subsidence is one of the most actionable components of coastal risk, says Manoochehr Shirzaei of Virginia Tech.",
          m(0, v(JKT_NORTH, places=[MUARA_BARU])),
          m("but it cannot", v(near(106.82, -6.14, 0.1)), cut=True),
          clip("Subsidence is", "\"Subsidence is one of the most actionable components of coastal risk.\"", "Manoochehr Shirzaei, Virginia Tech, Apr 8, 2026", highlight="most actionable"),
          m("says Manoochehr", v(near(106.79, -6.12, 0.08)), cut=True)),
    ]},
    {"title": "The Choice", "mood": "calm", "paragraphs": [
        P("Jakarta has a wall that leaks, a new capital that is not yet the capital, and a plan for a wall along half of Java. The wall would take fifteen to twenty years to build. The ground under Jakarta and Demak keeps sinking in every one of them. In Timbulsloko, the sea is already at the door.",
          m(0, v(MUARA_BARU_V)), m("a new capital", v(IKN_V), cut=True), m("and a plan", v(JAVA, routes=[GSW])),
          m("The wall would", v(near(108.0, -6.5, 3.0), routes=[GSW])), m("The ground", v(near(106.80, -6.115, 0.06)), cut=True),
          m("In Timbulsloko", v(DEMAK_W, compare={**CMP_DEMAK, "hold": 0.4}), cut=True)),
        P("If you had Indonesia's eighty billion dollars, what would you do first: build the wall, pipe clean water to every house so the pumping stops, or help the villages move inland?",
          m(0, v(JAVA, places=[JAKARTA, TIMBULSLOKO])),
          ask=("If you", "The wall, the water, or moving inland?")),
    ]},
]
# ---- beats: a new real picture at least every ~6 s. Gaps are filled from views of the place the sentence is about.
sys.path.insert(0, str(HERE.parent.parent / "pipeline"))
from schema import Paragraph  # noqa: E402

MAX_WORDS = 10


def sat(view, label=None, date=None):
    return m(0, v(view, date=date), text=label)


def pic(name, label=None):
    return photo(0, name, label)


# Filler pictures. Every map view is generated once (a point along that shore x a frame width), so no crop comes back;
# a photo is used at most PHOTO_MAX times and never within PHOTO_GAP seconds of its last use (ep 11 v1 cycled five
# photos 8-12 times each). A village's photos only go under sentences about that village.
SEC_WORD = 0.43
PHOTO_MAX, PHOTO_GAP = 3, 110.0  # gap in estimated seconds; real speech runs faster than SEC_WORD (v2 repeats came back 35-54 s apart)
SHORES = {
    "jakarta": [(106.840, -6.122), (106.813, -6.135), (106.827, -6.175), (106.93, -6.10), (106.738, -6.096), (106.958, -6.095),
                (106.85, -6.16), (106.772, -6.106), (106.73, -6.13), (106.88, -6.11), (106.80, -6.19), (106.795, -6.118)],
    "bay": [(106.76, -6.085), (106.79, -6.093), (106.70, -6.03), (106.67, -6.02), (106.73, -6.05), (106.82, -6.07)],
    "ikn": [(116.75, -1.10), (116.73, -0.93), (116.80, -1.05), (116.66, -1.00), (116.79, -0.92), (116.72, -1.08), (116.63, -0.93),
            (116.78, -0.99)],
    "demak": [(110.64, -6.89), (110.42, -6.95), (110.58, -6.82), (110.472, -6.918), (110.60, -6.77), (110.47, -6.94),
              (110.55, -6.86), (110.38, -6.96), (110.66, -6.84)],
    "pantura": [(110.20, -6.92), (109.10, -6.83), (111.10, -6.55), (112.65, -7.10), (108.57, -6.70), (109.68, -6.86), (107.60, -6.20),
                (111.60, -6.70), (110.85, -6.60), (108.20, -6.30), (112.05, -6.88), (106.15, -6.03)],
}
SPANS = {"pantura": [0.12, 0.18, 0.25, 0.15], None: [0.05, 0.07, 0.09, 0.06, 0.08, 0.1]}
LABELS = {"jakarta": "North Jakarta", "bay": "Jakarta Bay", "ikn": "Nusantara", "demak": "Sayung, Demak", "pantura": "Java's north coast"}
PHOTOS = {
    "jakarta": [],
    "bay": [],
    "ikn": [(PH_PALACE, "The presidential palace under construction, June 2024"), (PH_GARUDA, "The Garuda Palace, Nusantara")],
    "demak": [],
}
VIEW_PLACE = {}
used_views: set = set()
view_next = dict.fromkeys(SHORES, 0)
photo_uses: dict = {}


def next_view(place):
    pts, spans = SHORES[place], SPANS.get(place, SPANS[None])
    for _ in range(len(pts) * len(spans)):
        k = view_next[place]
        view_next[place] += 1
        lon, lat = pts[k % len(pts)]
        span = spans[(k // len(pts)) % len(spans)]
        key = (round(lon, 2), round(lat, 2), round(span, 2))
        if key not in used_views:
            used_views.add(key)
            return sat(near(lon, lat, span), LABELS[place])
    raise SystemExit(f"out of fresh views for {place}")


view_last: dict = {}
view_count: dict = {}
SHIFTS = [(0, 0, 1.0), (0.18, 0, 1.0), (-0.18, 0, 1.0), (0, 0.15, 1.0), (0, -0.15, 1.0), (0, 0, 1.3), (0, 0, 0.8),
          (0.2, 0.12, 1.15), (-0.2, -0.12, 1.15), (0.12, -0.15, 0.85), (-0.12, 0.15, 0.85)]


def fresh_view(vw, t):
    """A hand-placed view seen too recently or too often becomes a shifted / reframed one of the same spot, so the
    picture changes but the place stays (ep 11 v1 showed one Buxton crop 17 times)."""
    for dx, dy, z in SHIFTS:
        span = round(vw["span"] * z, 3)
        lon, lat = round(vw["lon"] + dx * vw["span"], 4), round(vw["lat"] + dy * vw["span"] * 9 / 16, 4)
        key = (round(lon, 2), round(lat, 2), round(span, 2))
        if view_count.get(key, 0) < 3 and t - view_last.get(key, -1e9) >= 75:
            view_count[key] = view_count.get(key, 0) + 1
            view_last[key] = t
            used_views.add(key)
            return {**vw, "lon": lon, "lat": lat, "span": span}
    raise SystemExit(f"no fresh framing left for {vw}")


# Burst shots of one scene (the 24131 Ocean Dr truck-loading set) read as the same picture: they share one count.
FAMILY = {PH_FLOOD1: "flood", PH_FLOOD2: "flood", PH_PIK2: "pik", PH_PIK2B: "pik"}


def filler(group, t):
    for name, label in PHOTOS.get(group, []):
        fam = FAMILY.get(name, name)
        uses = photo_uses.get(fam, [])
        if len(uses) < PHOTO_MAX and all(t - u >= PHOTO_GAP for u in uses):
            photo_uses.setdefault(fam, []).append(t)
            return pic(name, label)
    return next_view(VIEW_PLACE.get(group, group))


def topic_of(text, chapter):
    if re.search(r"Nusantara|Borneo|Kalimantan|Balik|Sepaku|Sibukdin|Sernai|[Pp]alace|new capital|decree|Widodo|relocat|forest|cleared|Tempo|core government|new site|earthquakes", text):
        return "ikn"
    if re.search(r"Demak|Timbulsloko|Bedono|Mak Jah|Pasijah|Sularso|Sulkan|mangrove|fish ponds|village head", text):
        return "demak"
    if re.search(r"islands|reclaim|Pantai Indah|bay|new land", text):
        return "bay"
    if re.search(r"Java|Semarang|Pekalongan|Serang|Gresik|segments|north coast|seventy-five kilometres", text):
        return "pantura"
    if re.search(r"Jakarta|Muara|Pluit|dike|wall|groundwater|wells|pumped|sink|NCICD|Nurhasan|governor", text):
        return "jakarta"
    return None


CHAPTER_DEFAULT = {"A Wall of Trees": "demak", "Faster Than the Sea": "jakarta", "The Wall That Leaks": "jakarta",
                   "Plan B: Leave": "ikn", "The Capital That Stalled": "ikn", "Where the Sea Already Won": "demak",
                   "The 575 Kilometre Bet": "pantura", "The Choice": "pantura"}


def topic(para_text, at, chapter):
    """The sentence under the new picture decides; failing that the paragraph, then the chapter."""
    seen, sentence = 0, para_text
    for part in re.split(r"(?<=[.?!])\s+", para_text):
        k = len(part.split())
        if seen <= at < seen + k:
            sentence = part
            break
        seen += k
    t = topic_of(sentence, chapter)
    return t or topic_of(para_text, chapter) or CHAPTER_DEFAULT[chapter]


def _phrase_index(words, phrase):
    want = phrase.split()
    bare = [w.strip('.,;:!?"') for w in words]
    hits = [i for i in range(len(bare)) if bare[i:i + len(want)] == [w.strip('.,;:!?"') for w in want]]
    return hits[0] if hits else None


# Hand-placed photos and views count against the limits before any filler is chosen.
word_base = 0
for ch in chapters:
    for para in ch["paragraphs"]:
        pm = Paragraph.model_validate(para)
        for sh, at in zip(para["shots"], pm.anchor_indices()):
            if sh["type"] == "photo":
                photo_uses.setdefault(sh["photo"], []).append((word_base + at) * SEC_WORD)
            t = (word_base + at) * SEC_WORD
            for st in (sh.get("map") or {}).get("steps", []):
                if st.get("view") and not st.get("compare"):
                    st["view"] = fresh_view(st["view"], t)
                elif st.get("view"):
                    vw = st["view"]
                    used_views.add((round(vw["lon"], 2), round(vw["lat"], 2), round(vw["span"], 2)))
        word_base += len(para["text"].split()) + 8

word_base = 0
for ch in chapters:
    for para in ch["paragraphs"]:
        for sh in para["shots"]:  # drop until=None placeholders (the wipe then starts at the next step / runs alone)
            for st in (sh.get("map") or {}).get("steps", []):
                if (st.get("compare") or {}).get("until", 1) is None:
                    del st["compare"]["until"]
        pm = Paragraph.model_validate(para)
        marks = set(pm.anchor_indices())
        for idx in pm.step_indices():
            marks |= set(idx)
        if pm.ask_index() is not None:
            marks.add(pm.ask_index())
        n = len(para["text"].split())
        STAT_WORDS = 9  # a stat card stays whole for ~4 s (count, label), then pictures may follow
        anchors0 = pm.anchor_indices()
        stat_ends = set()
        for sh, start in zip(para["shots"], anchors0):
            later = [x for x in anchors0 if x > start]
            if sh["type"] == "stat" and (min(later) if later else n) - start > STAT_WORDS + 4:
                marks.add(start + STAT_WORDS)
                stat_ends.add(start + STAT_WORDS)
        stops = sorted(marks | {0}) + [n]
        words = para["text"].split()
        blocks = [(min(idx), max(idx)) for idx in pm.step_indices() if len(idx) > 1]
        anchors = pm.anchor_indices()
        for sh, start in zip(para["shots"], anchors):
            later = [x for x in anchors if x > start]
            nxt = min(later) if later else n
            if sh["type"] in ("document", "chart"):  # a document or a chart holds until the next hand-placed shot
                blocks.append((start, nxt))
            elif sh["type"] == "stat":
                blocks.append((start, nxt if nxt - start <= STAT_WORDS + 4 else start + STAT_WORDS))
            for st in (sh.get("map") or {}).get("steps", []):  # a wipe keeps the screen until it has finished
                if st.get("compare"):
                    until = st["compare"].get("until")
                    k = _phrase_index(words, until) if until else start
                    blocks.append((k if k is not None else start, nxt))
        new = []
        for a, b in zip(stops, stops[1:]):
            inside = any(lo <= a and b <= hi for lo, hi in blocks)
            parts = 0 if inside else (b - a - 1) // MAX_WORDS
            opens = a == 0 and min(anchors) > 4  # a paragraph without its own first picture: give it one
            spots = ([a] if a in stat_ends or opens else []) + [a + (b - a) * j // (parts + 1) for j in range(1, parts + 1)]
            for at in spots:
                group = topic(para["text"], at, ch["title"])
                shot = json.loads(json.dumps(filler(group, (word_base + at) * SEC_WORD)))
                shot["at"] = at
                new.append(shot)
        if new:
            pos = dict(zip(map(id, para["shots"]), anchors))
            para["shots"] = sorted(para["shots"] + new, key=lambda sh: pos.get(id(sh), sh["at"] if isinstance(sh["at"], int) else 0))
        word_base += len(para["text"].split()) + 8

BASEMAP_NAMED = {"Jakarta", "Semarang", "Pekalongan", "Serang", "Gresik", "Demak", "Balikpapan"}
for ch in chapters:
    for para in ch["paragraphs"]:
        for sh in para["shots"]:
            span = None
            for st in (sh.get("map") or {}).get("steps", []):
                span = st["view"]["span"] if st.get("view") else span
                if st.get("places"):
                    st["places"] = [pl for pl in st["places"] if pl["name"] not in BASEMAP_NAMED]
                    if not st["places"]:
                        del st["places"]

for ch in chapters:
    for para in ch["paragraphs"]:
        for sh in para["shots"]:
            seen = set()
            for st in (sh.get("map") or {}).get("steps", []):
                if st.get("places"):
                    st["places"] = [pl for pl in st["places"] if pl["name"] not in seen]
                    seen |= {pl["name"] for pl in st["places"]}
                    if not st["places"]:
                        del st["places"]

# Between close views a flight passes through coarse imagery for a second: cut instead. Wide-to-wide moves still fly.
prev_span = None
for ch in chapters:
    for para in ch["paragraphs"]:
        for sh in para["shots"]:
            if sh["type"] != "map":
                prev_span = None
                continue
            views = [st["view"]["span"] for st in sh["map"]["steps"] if st.get("view")]
            if views and prev_span is not None and (views[0] <= 2 or prev_span <= 2) and not sh["map"].get("keep"):
                sh["map"]["cut"] = True
            prev_span = views[-1] if views else prev_span

script = {
    "title": "Sinking Jakarta",
    "voice": "am_michael",
    "music": "procedural",
    "map_style": "satellite",
    "look": "none",
    "sources": ["episodes/jakarta-sinking/research.md, verification.md and factcheck.md", "Landsat data courtesy of the U.S. Geological Survey", "Contains modified Copernicus Sentinel data 2019-2026"],
    "thumbnail": {"text": "THE WALL"},
    "chapters": chapters,
    "youtube": {
        "title": "Indonesia Is Building a 575 km Wall Against the Sea",
        "description": "Jakarta has sunk faster than almost any city on Earth. Indonesia's answers: a coastal wall that leaked in December 2025, a new capital cut out of the forest of Borneo that is still not the capital, and now a Giant Sea Wall of about 575 kilometres along Java's north coast, which began in October 2026 with a row of mangroves in Timbulsloko. We follow it from orbit with Landsat and Sentinel-2 images and measure the coast at Demak, where the sea has already taken the fields.",
        "tags": ["Jakarta", "sinking city", "Giant Sea Wall", "Indonesia", "Nusantara", "new capital", "land subsidence", "Demak", "Timbulsloko", "sea level", "satellite images", "Landsat", "Sentinel-2", "Java"],
        "pinned_comment": "With US$80 billion: build the 575 km wall, pipe clean water to every house so the pumping stops, or help the villages move inland?",
    },
}
out = HERE / "script.json"
out.write_text(json.dumps(script, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
words = sum(len(p["text"].split()) for c in chapters for p in c["paragraphs"])
print(f"{words} words, {len(chapters)} chapters, {sum(len(p['shots']) for c in chapters for p in c['paragraphs'])} shots")
