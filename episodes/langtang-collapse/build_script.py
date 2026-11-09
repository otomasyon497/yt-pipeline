"""Builds script.json for langtang-collapse (beats are easier to review here than in the JSON).  python build_script.py

Sources: research.md (R1-R10). Coordinates: OpenStreetMap place nodes (checked 2026-11-09); the collapse source from
antarcticglaciers.org (Bethan Davies, 27 Aug 2026); the flood's path traced on our Sentinel-2 scene of 2026-10-21.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
BEFORE = "2025-10-15/2025-11-10"  # clear autumn scenes a year before (2025-10-21)
AFTER = "2026-10-18/2026-10-27"  # the same season after (2026-10-21)
NDRRMA16 = "https://ndrrma.gov.np/mediafiles/rasuwa/Rasuwa_Flood_Situation_Report_ENG_16_17092026_AsGEcO1.pdf"

VALLEY = {"lon": 85.45, "lat": 28.30, "span": 0.40}
SOURCE = {"lon": 85.515, "lat": 28.30, "span": 0.09}
RASUWA_V = {"lon": 85.38, "lat": 28.28, "span": 0.07}
TIMURE_V = {"lon": 85.365, "lat": 28.245, "span": 0.07}
SYABRU_V = {"lon": 85.345, "lat": 28.165, "span": 0.07}
BETRA_V = {"lon": 85.18, "lat": 27.965, "span": 0.08}
TRISHULI_V = {"lon": 85.145, "lat": 27.915, "span": 0.08}
LANGTANG_V = {"lon": 85.51, "lat": 28.215, "span": 0.14}
PATH_V = {"lon": 85.32, "lat": 28.10, "span": 0.75}
NEPAL_V = {"lon": 84.6, "lat": 28.3, "span": 8.5}
HIMALAYA_V = {"lon": 84.0, "lat": 29.2, "span": 15}


def near(lon, lat, span=0.06):
    return {"lon": lon, "lat": lat, "span": span}


def place(name, lon, lat, label=None, kind="site", icon=None):
    d = {"name": name, "lon": lon, "lat": lat, "kind": kind, "label": label if label is not None else name}
    if icon:
        d["icon"] = icon
    return d


LIRUNG = place("Langtang Lirung", 85.5197, 28.2558, "Langtang Lirung, 7,227 m", "site")
SRC = place("Collapse", 85.5252, 28.2853, "Where the ice broke", "event")
RASUWAGADHI = place("Rasuwagadhi", 85.3778, 28.2778, "Rasuwagadhi", "site")
GYIRONG_PORT = place("Gyirong Port", 85.383, 28.284, "Gyirong Port (China)", "port")
TIMURE = place("Timure", 85.3667, 28.2528, "Timure", "site")
SYABRUBESI = place("Syafrubesi", 85.343, 28.160, "Syafrubesi", "site")
DHUNCHE = place("Dhunche", 85.2961, 28.1128, "Dhunche", "site")
MAILUNG = place("Mailung", 85.207, 28.0718, "Mailung", "site")
BETRAWATI = place("Betrawati", 85.186, 27.9731, "Betrawati", "site")
TRISHULI = place("Trishuli", 85.148, 27.9232, "Trishuli", "city")
DEVIGHAT = place("Devighat", 85.1101, 27.86, "Devighat", "site")
LANGTANG = place("Langtang", 85.509, 28.2158, "Langtang village", "site")
KATHMANDU = place("Kathmandu", 85.324, 27.7172, "Kathmandu", "capital")
GYIRONG = place("Gyirong", 85.3276, 28.3961, "Gyirong town", "city")
CHILIME = place("Chilime", 85.3319, 28.1573, "Chilime power station", "site", "factory")
CHAMOLI = place("Chamoli", 79.73, 30.38, "Chamoli, India, 2021", "event")
LHONAK = place("South Lhonak", 88.19, 27.91, "Sikkim, India, 2023", "event")
THAME = place("Thame", 86.65, 27.83, "Thame, Nepal, 2024", "event")
EPICENTRE = place("Epicentre", 84.73, 28.23, "Epicentre, 25 April 2015", "event")

# the flood's path, traced on our Sentinel-2 scene of 2026-10-21 (scoured bed), then down the Trishuli
PATH = {"from": [85.5252, 28.2853], "to": [85.1101, 27.86], "mode": "line", "seconds": 6, "label": "The flood's path",
        "via": [[85.505, 28.315], [85.481, 28.338], [85.43, 28.335], [85.395, 28.322], [85.3778, 28.2778], [85.3667, 28.2528],
                [85.345, 28.20], [85.343, 28.160], [85.30, 28.10], [85.207, 28.0718], [85.219, 28.0326], [85.186, 27.9731],
                [85.148, 27.9232]]}


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
    if date is None and view["span"] <= 2:  # undated close views use multi-day mosaics with seams
        date = AFTER
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


USGS = "USGS; EarthSky, Aug 27, 2026"
POLICE = "Nepal Police, Oct 14, 2026"
KPOST = "Kathmandu Post, Sep 2, 2026"
CAS = "Institute of Tibetan Plateau Research (CAS), preliminary, via OnlineKhabar, Sep 3, 2026"
DAHAL = "Ranjan Kumar Dahal, Tribhuvan University, via OnlineKhabar, Sep 2, 2026"
HIMAL = "Himal Southasian, 2025"
KP25 = "Kathmandu Post, Jul 11, 2025"
ICIMOD = "ICIMOD, HI-WISE report, 2023"
GOV = "Government of Nepal, Rapid Damage and Needs Assessment, 2026"
CMP = {"before": BEFORE, "after": AFTER, "seconds": 2.0}

chapters = [
    {"title": "Not an Earthquake", "mood": "tension", "paragraphs": [
        P("At 8:37 on the morning of August 26, seismographs recorded a magnitude 5.2 shock in the mountains of Nepal, near the border with Tibet. The US Geological Survey first listed it as an earthquake. It was not one.",
          m(0, v(NEPAL_V, highlight=["Nepal"], places=[KATHMANDU])),
          stat("a magnitude", "M 5.2", "The shock recorded at 08:37, 26 August 2026", USGS),
          m("near the border", v({"lon": 85.35, "lat": 28.1, "span": 2.2}, places=[LIRUNG, KATHMANDU]), cut=True),
          stat("The US", "\"Earthquake\"", "How the US Geological Survey first listed it", USGS, "M 4.4 in its first report")),
        P("This is the valley below it last October. And this is the same valley this October. That grey line running down the mountain was not there a year ago.",
          m(0, v(VALLEY, compare={**CMP, "until": "And this"}), step("And this"), step("That grey", places=[SRC]), text="Real satellite images · Sentinel-2", cut=True)),
        P("What the instruments heard was a piece of mountain falling. A block of ice and rock broke off the north side of Langtang Lirung, a peak of 7,227 metres, and dropped more than a kilometre.",
          photo("What the", "File:Le Langtang Lirung (Himalaya, Népal) (8448200379).jpg", "Langtang Lirung"),
          m("A block", v(SOURCE, places=[SRC, LIRUNG]), cut=True)),
        P("It became a flood that ran about a hundred kilometres into Nepal. By mid-October, police counted 1,456 dead and 5,285 still missing.",
          m(0, v(PATH_V, routes=[PATH]), cut=True),
          stat("By mid-October", "1,456 dead", "And 5,285 still missing in Nepal", POLICE)),
        P("A preliminary study says the ice had been moving unusually fast for two years, and satellites recorded it. So why did the warning reach phones thirty-eight minutes after the collapse? And why was this the third time in eleven years that this valley was destroyed?",
          m(0, v(SOURCE)),
          stat("thirty-eight", "38 minutes", "From the collapse to the text alerts", KPOST),
          ask=("And why", "Could anyone have seen it coming?")),
    ]},
    {"title": "Within Minutes", "mood": "tension", "paragraphs": [
        P("The ice and rock fell about eight kilometres down a side valley into the Lhende river, on the Tibetan side of the border. On the way it picked up loose rock, mud and water.",
          m(0, v(VALLEY), step("down a side", places=[SRC]), step("the Tibetan", highlight=["China"]), cut=True)),
        P("Then the flood turned west, toward the border crossing at Rasuwagadhi, about thirteen kilometres downstream. On the Chinese side stands Gyirong Port, which handled close to a third of Nepal's trade with China, by Chinese figures.",
          m(0, v(RASUWA_V), step("toward the border", places=[RASUWAGADHI]), step("On the Chinese", places=[GYIRONG_PORT]), cut=True)),
        P("Cameras there filmed the water arriving within minutes. Chinese state television showed it hitting the customs and immigration building. Some experts put its speed at more than a hundred kilometres an hour.",
          m(0, v(RASUWA_V, compare={**CMP, "hold": 0.6}), step("Chinese state", places=[GYIRONG_PORT])),
          stat("Some experts", "100+ km/h", "The flood's speed, by some experts' estimates", "OnlineKhabar, Sep 2, 2026")),
        P("After a flood here the year before, the Chinese side had built a new flood wall and dikes and held an evacuation drill. The water went through them in minutes.",
          m(0, v(RASUWA_V))),
        P("China's premier, Li Qiang, was in Gyirong the same day. A makeshift road to the port was finished a week later, and trade moved to the Korala crossing, far to the west.",
          m(0, v(near(85.33, 28.39, 0.08), places=[GYIRONG]), cut=True)),
        P("On the Nepali side it took the customs office and the dry port, with its containers and trucks. More than three hundred vehicles were swept away.",
          stat("More than", "300+", "Vehicles swept away at Rasuwagadhi", "Government of Nepal, via Wikipedia summary")),
        P("From here the river is called the Bhotekoshi. It runs south through a narrow gorge, past Timure, to Syafrubesi, where trekkers start the walk into Langtang.",
          m(0, v(TIMURE_V, compare={**CMP, "until": "through a narrow"}), step("through a narrow"), step("past Timure", places=[TIMURE]), cut=True),
          m("where trekkers", v(SYABRU_V, places=[SYABRUBESI]), cut=True)),
        P("In places the water rose about eighty metres above the normal river, high enough to reach houses built on terraces well above it.",
          m(0, v(SYABRU_V, compare={**CMP, "until": "high enough"}), step("high enough"))),
        P("Then the Trishuli: below the hill town of Dhunche, past Mailung and Betrawati, down to Trishuli and Devighat, about a hundred kilometres from where the ice fell.",
          m(0, v(PATH_V, routes=[PATH], places=[DHUNCHE, MAILUNG, BETRAWATI, TRISHULI, DEVIGHAT]), cut=True)),
        P("And the danger did not end that morning. The debris dammed the river in Tibet, and two lakes formed behind it. Two days later, Chinese authorities warned that one of them, holding about two million cubic metres, could burst. Rescue work in Nepal stopped while it overflowed. It drained over the next two days without a second disaster.",
          m(0, v(near(85.46, 28.335, 0.1), places=[SRC]), cut=True, text="The Lhende valley, Tibet"),
          stat("Two days later", "2 million m³", "Water held by one barrier lake in Tibet, 28 August", "Chinese authorities, via Wikipedia summary")),
        P("Bodies were later recovered about two hundred and fifty kilometres away, across the border in India. So who was warned, and when?",
          m(0, v({"lon": 84.4, "lat": 27.3, "span": 3.2}, highlight=["Nepal", "India"], places=[TRISHULI])),
          ask=("So who", "Who should have sounded the alarm?")),
    ]},
    {"title": "Thirty-Eight Minutes", "mood": "tension", "paragraphs": [
        P("Nepal does have a flood warning system on this river. It was built for the monsoon: rain that swells a river over hours, watched by gauges upstream.",
          m(0, v(SYABRU_V))),
        P("This flood started above all of them. The stations nearest the border were swept away before they could warn anyone.",
          m(0, v(RASUWA_V, places=[RASUWAGADHI]))),
        P("A fellow at the Stimson Center, a research institute in Washington, called this stretch of the border a monitoring blind spot. Nothing on either side was watching the ice in real time.",
          m(0, v(VALLEY, places=[RASUWAGADHI, SRC]))),
        P("Officials in Rasuwa called the Department of Hydrology and Meteorology at about nine. Text alerts went out at about 9:15, more than six hundred thousand of them. That was thirty-eight minutes after the collapse.",
          chart(0, "Morning of 26 August 2026, Nepal time", " min", [["08:37 collapse", 0], ["09:00 call", 23], ["09:15 alerts", 38]], KPOST, highlight=2, reveal=["about nine.", "Text alerts"]),
          stat("more than six", "600,000+", "Text alerts sent around 9:15", KPOST)),
        P("Once it started, the system was fast: almost 680,000 messages went out within a minute. A former environment minister still called the delay a failure of communication.",
          stat(0, "679,295", "Text alerts sent within one minute", "Government of Nepal, via Wikipedia summary")),
        P("For Rasuwagadhi and Timure it came far too late. Farther down the river, every minute counted.",
          m(0, v(TIMURE_V)),
          m("Farther down", v(BETRA_V, places=[BETRAWATI]), cut=True)),
        P("In Trishuli, a headteacher named Rajendra Dawadi moved about nine hundred children out of his school. Local reports say the flood reached it ten minutes later.",
          m(0, v(TRISHULI_V, compare={**CMP, "until": "Local reports"}), step("moved about", places=[TRISHULI]), step("Local reports"), cut=True)),
        P("Across the border, Tibetan officials said about twenty minutes passed between the collapse and the surge, and that a warning in that window could have saved lives.",
          m(0, v(VALLEY, places=[GYIRONG]), cut=True),
          stat("about twenty", "~20 minutes", "From collapse to surge, Tibetan officials said", "Chinese officials via Asianet, Sep 2026", "Not independently verified")),
        P("The Kathmandu Post summed it up in its headline: the alert went out thirty-eight minutes after the collapse, and it was not enough.",
          clip("the alert went", "Nepal sent its disaster alert 38 minutes after the glacier collapse. It wasn't enough", KPOST, "It wasn't enough")),
    ]},
    {"title": "The Valley Remembers", "mood": "curious", "paragraphs": [
        P("None of this was new to this valley. On April 25, 2015, at 11:56 in the morning, a magnitude 7.8 earthquake shook Nepal, about seventy kilometres west of here.",
          m(0, v(NEPAL_V, places=[EPICENTRE, LIRUNG]), cut=True),
          stat("a magnitude", "M 7.8", "The Gorkha earthquake, 25 April 2015, 11:56", HIMAL)),
        P("On the south side of the same mountain, a hanging block of glacier broke loose. Within minutes, the debris buried almost all of Langtang village.",
          m(0, v(LANGTANG_V, date="2014-10-20/2014-11-21"), step("a hanging", places=[LIRUNG]), step("Within minutes", places=[LANGTANG]), cut=True)),
        P("ICIMOD found that the eight highest villages of the valley were destroyed, not just Langtang.",
          m(0, v(LANGTANG_V), cut=True)),
        P("Langtang was a trekking village, with fifty-five guesthouses. Its people call the valley a beyul, a hidden sacred refuge, and Langtang Lirung its protector.",
          photo(0, "File:Langtang Khola Rasuwa District.jpg", "The Langtang valley"),
          photo("Its people", "File:Lirung (3to4).jpg", "Langtang Lirung")),
        P("The blast of air in front of it flattened buildings that had survived and knocked down a forest of grown trees. Here is the village from orbit, the autumn before and the autumn after.",
          m("Here is", v(LANGTANG_V, compare={"before": "2014-10-20", "after": "2015-10-07", "source": "landsat", "seconds": 2.0}), cut=True, text="Landsat 8")),
        P("Officially 306 people died: at least 175 of about 370 villagers who were there, 82 other Nepalis and 49 foreign trekkers. The villagers say it was closer to five hundred.",
          chart(0, "Langtang, 25 April 2015: official toll", "", [["Villagers", 175], ["Other Nepalis", 82], ["Foreign trekkers", 49]], HIMAL, reveal=["82 other", "49 foreign"]),
          stat("The villagers", "~500", "The villagers' own count of the dead", HIMAL)),
        P("They rebuilt it themselves, about a hundred metres up the valley. This is Langtang last February.",
          photo(0, "File:Langtang Village, February 2026.jpg", "Langtang village, February 2026")),
        P("Then, last year, the danger came from the other side of the border. On July 8, 2025, a lake on top of a glacier in Tibet burst, about thirty-six kilometres above Rasuwagadhi.",
          m(0, v(VALLEY, highlight=["China"], places=[RASUWAGADHI]), cut=True)),
        P("It sat at 5,150 metres and had grown quickly from December to June. The Kathmandu Post called it previously unnoticed. After it burst, it still covered 0.61 square kilometres.",
          stat(0, "0.75 km²", "The lake before it burst, at 5,150 metres", KP25)),
        P("The flood took the Friendship Bridge at Rasuwagadhi, wrecked the dry port and hit hydropower plants down the river. Police counted nine dead and nineteen missing.",
          m(0, v(RASUWA_V, compare={"before": "2024-10-15/2024-11-30", "after": "2025-10-15/2025-11-10", "seconds": 2.0, "until": "Police counted"}), step("wrecked the", places=[RASUWAGADHI]), step("Police counted"), cut=True)),
        P("A disaster specialist at ICIMOD, the regional mountain research centre, told the paper: \"The acceleration of these types of events is completely unprecedented.\"",
          clip("told the paper", "The acceleration of these types of events is completely unprecedented in the Hindu Kush Himalayan region.", "Saswata Sanyal, ICIMOD, to the Kathmandu Post, 2025", "completely unprecedented")),
        P("The road along the river was still being repaired when this summer's flood came down it. So what exactly broke this time, and why?",
          m(0, v(TIMURE_V)),
          m("So what", v(SOURCE), cut=True)),
    ]},
    {"title": "What Fell", "mood": "curious", "paragraphs": [
        P("This is the source, around five thousand two hundred metres up on the north face. A year before. And after: a scar where the ice and rock used to be.",
          m(0, v(SOURCE, compare={**CMP, "until": "And after"}), step("on the north", places=[SRC]), step("And after"), cut=True)),
        P("How much fell is still argued. The geologist Ranjan Kumar Dahal gives a conservative satellite estimate of twenty-five million cubic metres. Others put it at forty, a hundred, or a hundred and forty-two million.",
          m(0, v(SOURCE)),
          chart("a conservative", "How much fell? Estimates, million m³", "", [["Dahal, conservative", 25], ["Upper estimates", 40], ["Other experts", 100], ["HiRISK, preliminary", 142]], DAHAL + "; HiRISK", reveal=["forty,", "a hundred,", "a hundred and"])),
        P("His team describes the main avalanche as about 1.3 kilometres long and sixty to seventy metres thick. Two days later, a smaller slide fell from the same place.",
          stat(0, "60-70 m", "Thickness of the main avalanche, about 1.3 km long", DAHAL)),
        P("Even the smallest figure, Dahal says, is about ten times the volume of the Great Pyramid.",
          stat(0, "~10×", "The Great Pyramid's volume, in the smallest estimate", DAHAL)),
        P("The Chamoli disaster in northern India in 2021, which left about two hundred people dead or missing, was around twenty-seven million cubic metres.",
          m(0, v(HIMALAYA_V, places=[CHAMOLI, LIRUNG]), cut=True)),
        P("Why did it fall? A preliminary study from the Chinese Academy of Sciences used Sentinel-2 images and found that the glacier's upper and middle parts had been moving relatively fast for the past two years.",
          m(0, v(SOURCE, date="2026-08-12"), cut=True, text="12 August 2026, two weeks before")),
        P("It found no rain trigger: 8.8 millimetres in the three days before. Winter had been 0.38 degrees above average, summer 0.58.",
          stat(0, "8.8 mm", "Rain in the 72 hours before: not the trigger", CAS, "Winter +0.38 °C, summer +0.58 °C above average")),
        P("The same study found something else. Seismic instruments picked up unusual signals that morning, at about 6:04, 6:50 and again from 8:15. Some matched dust and small slides that local people reported. The researchers say that is not enough to call them a warning.",
          m(0, v(SOURCE, date="2026-08-12")),
          chart("unusual signals", "Unusual signals, morning of 26 August", " min before", [["06:04", 153], ["06:50", 107], ["08:15", 22]], CAS, highlight=2, reveal=["6:50", "8:15."]),
          m("Some matched", v(near(85.50, 28.32, 0.08)), text="The debris track")),
        P("The researchers list several processes working together, from freezing and thawing inside the rock to damage left by the 2015 earthquake.",
          m(0, v(LANGTANG_V, places=[LIRUNG]))),
        P("The glaciers here have been shrinking for decades. A 2026 study found that Langtang's glaciers retreated one and a half times faster after 2000 than before it.",
          photo(0, "File:Lirung.jpg", "Lirung glacier"),
          stat("one and a half", "1.5×", "Faster retreat of Langtang glaciers, 2000-2023 against 1964-2000", "Silwal et al., 2026")),
        P("As the lower ice melted away, the glaciologist Bethan Davies notes, some glaciers were left hanging on steep rock, without the ice that used to hold them from below.",
          photo(0, "File:Le Langtang Lirung (Himalaya, Népal) (8448200379).jpg", "Langtang Lirung")),
        P("Scientists say warming likely made a collapse like this more probable. They do not say it caused this one on its own.",
          m(0, v(SOURCE))),
        P("Most of the people the flood reached were nowhere near the ice. Many were at work, some of them inside the mountain.",
          m(0, v(SYABRU_V, places=[CHILIME]), cut=True)),
    ]},
    {"title": "Power in the Path", "mood": "tension", "paragraphs": [
        P("These two rivers are some of Nepal's most important power lines. Hydropower plants and their tunnels sit all along the Bhotekoshi and the Trishuli.",
          m(0, v(PATH_V, places=[CHILIME, TRISHULI], routes=[PATH]), cut=True)),
        P("Twelve hydropower projects were damaged. About 430 megawatts went offline, roughly a tenth of the country's hydro and solar output.",
          stat(0, "~430 MW", "Offline after the flood, about 10.6 % of Nepal's hydro and solar output", "Ministry of Energy, via Wikipedia summary")),
        P("Many of these plants send the river through tunnels cut into the rock. When the flood came, people were working inside them.",
          m(0, v(SYABRU_V)),
          m("When the flood", v(TIMURE_V), cut=True)),
        P("In the first weeks, officials said more than nine hundred people at these projects were missing, some of them believed trapped underground.",
          stat(0, "900+", "Missing at 12 hydropower projects, first weeks", "Government of Nepal, via Wikipedia summary")),
        P("On September 17, the disaster authority reported that teams had dug through 250 metres of tunnel at the Chilime plant and found five bodies. At Upper Trishuli-1, five more were still trapped, waiting for cutting equipment.",
          clip("250 metres", "Five bodies were recovered after teams broke through the 250-metre tunnel and cleared access to the control room.", "NDRRMA Situation Report 16, Sep 17, 2026", "250-metre tunnel"),
          clip("At Upper", "At Upper Trishuli-1, five bodies remain trapped inside the tunnel, with recovery pending the availability of cutting equipment.", "NDRRMA Situation Report 16, Sep 17, 2026", "cutting equipment")),
        P("On August 31, the army set off a controlled blast inside a tunnel at Upper Trishuli 3A to reach the workers missing there.",
          m(0, v(near(85.25, 28.0, 0.08)), text="The Trishuli valley")),
        P("There were survivors. On September 4, nine days after the flood, rescuers pulled two people out alive from a tunnel, and a Chinese worker the next day.",
          m(0, v(SYABRU_V, places=[CHILIME]))),
        P("Projects still under construction were hit as well, about 3,800 megawatts of planned capacity.",
          stat(0, "3,795 MW", "Planned capacity at hit projects under construction", "Ministry of Energy, via Wikipedia summary")),
        P("Some of these plants had only just been repaired after the 2025 flood.",
          m(0, v(RASUWA_V))),
        P("Nepal sells electricity to India and counts on its rivers to grow. Should it keep building in valleys like this one?",
          m(0, v({"lon": 84.4, "lat": 27.3, "span": 3.2}, highlight=["Nepal", "India"])),
          ask=("Should it", "Keep building dams in these valleys?")),
    ]},
    {"title": "The Missing", "mood": "calm", "paragraphs": [
        P("Nepal's police counted 1,456 dead and 5,285 missing by October 14. The number of dead kept climbing for seven weeks.",
          chart(0, "Confirmed dead in Nepal", "", [["Aug 31", 903], ["Sep 12", 1386], ["Oct 14", 1456]], "NDRRMA; Kathmandu Post; Nepal Police", reveal=["kept climbing"], kind="line")),
        P("Missing does not always mean dead. Officials say the lists include unidentified bodies and people who have since been found.",
          m(0, v(TRISHULI_V))),
        P("Search and rescue ended on October 5, with more than 13,000 people rescued. Then came identification. By October 1, DNA had been taken from 1,334 bodies, and 112 had been identified.",
          stat(0, "13,795", "People rescued by the end of search and rescue, 5 October", "Government of Nepal, via Wikipedia summary"),
          stat("By October", "112 of 1,334", "Bodies identified by DNA, by 1 October", "Kathmandu Post, Oct 2026")),
        P("UNICEF counted about 84,000 people affected, 32,000 of them children. More than a hundred children lost both parents.",
          stat(0, "84,000", "People affected, about 32,000 of them children", "UNICEF, via Wikipedia summary"),
          m("More than", v(TRISHULI_V))),
        P("In September the disaster authority counted 636 foreign nationals among the missing: trekkers, pilgrims and workers.",
          stat(0, "636", "Foreign nationals among the missing, 20 September", "NDRRMA, via Asianet")),
        P("Nepal's law made families wait twelve years before a missing person could be declared dead. In October the cabinet proposed cutting that to forty-five days.",
          stat("In October", "12 years → 45 days", "Before a missing person can be declared dead (proposed)", "Kathmandu Post, Oct 2026")),
        P("On the Chinese side the official figures were 43 dead and 519 missing by mid-September. Videos and eyewitness posts from Tibet were removed from Chinese social media, according to the BBC and the New York Times, and police punished at least ten people for what they called misleading posts.",
          m(0, v(VALLEY, highlight=["China"], places=[GYIRONG]), cut=True),
          stat("Videos", "43 dead, 519 missing", "Tibet, official figures, mid-September", "Chinese authorities, via Wikipedia summary")),
        P("At first Nepal turned down rescue teams from several countries, pointing to the crowded response after the 2015 earthquake. Later it let in experts from India, China, Australia and South Korea.",
          m(0, v(NEPAL_V, highlight=["Nepal"], places=[KATHMANDU]), cut=True)),
        P("Aid came from India, China, the United States, Australia, the Gulf states and others. The Loss and Damage Fund, set up for climate disasters, gave twenty million dollars.",
          stat(0, "$20 million", "From the Loss and Damage Fund", "Wikipedia summary of donor announcements")),
        P("In Nepal, the first rumours blamed a Chinese dam. The satellite images showed the mountain itself.",
          m(0, v(SOURCE, compare={**CMP, "until": "The satellite"}), step("The satellite"), cut=True)),
        P("The government counts 7,570 houses destroyed and puts reconstruction at about 4.8 billion dollars, for a country whose whole economy is around forty billion.",
          stat(0, "$4.8 billion", "To rebuild, by the government's assessment", GOV, "7,570 houses destroyed")),
        P("Langtang is one valley. How many more look like it?",
          m(0, v(HIMALAYA_V, places=[LIRUNG]), cut=True)),
    ]},
    {"title": "The Next Valley", "mood": "calm", "paragraphs": [
        P("In February 2021, a rock and ice avalanche in Chamoli, India, sent a flood through two hydropower projects.",
          m(0, v(HIMALAYA_V, places=[CHAMOLI]))),
        P("In October 2023, a glacial lake in Sikkim burst and destroyed the 1,200 megawatt Teesta III dam.",
          m(0, v(HIMALAYA_V, places=[LHONAK]))),
        P("A year and a half later, the government approved rebuilding it.",
          m(0, v(HIMALAYA_V, places=[LHONAK]))),
        P("In August 2024, floods from glacial lakes wiped out much of Thame, a village near Everest. It came in daylight, and no one died.",
          m(0, v(HIMALAYA_V, places=[THAME]))),
        P("ICIMOD counts five significant glacial lake floods in the Everest region in less than fifty years.",
          stat(0, "5", "Major glacial lake floods near Everest in under 50 years", "ICIMOD, Oct 2025")),
        P("In July 2025, Rasuwagadhi. In August 2026, Rasuwagadhi again, and worse than all of them together.",
          m(0, v(HIMALAYA_V, places=[LIRUNG])),
          m("In August", v(RASUWA_V, compare={**CMP, "hold": 0.3}), cut=True)),
        P("In 2023, ICIMOD projected that the region's glaciers could lose thirty to fifty percent of their volume by 2100, even if warming is held to one and a half or two degrees. At three degrees, glaciers in the eastern Himalaya, which includes Nepal, could lose up to three quarters.",
          m(0, v(HIMALAYA_V), cut=True, text="The Hindu Kush Himalaya"),
          stat("thirty to fifty", "30-50 %", "Glacier volume the region could lose by 2100 at 1.5-2 °C", ICIMOD),
          photo("even if", "File:Snow-capped Mountains at Kyanjin Gompa Rasuwa.jpg", "Glaciers above Kyanjin Gompa, Langtang"),
          stat("At three", "Up to 75 %", "Eastern Himalaya glacier volume lost by 2100 at 3 °C", ICIMOD),
          m("which includes", v(NEPAL_V, highlight=["Nepal"]), cut=True)),
        P("The same report found that the region's glaciers lost mass sixty-five percent faster in the 2010s than in the decade before.",
          stat(0, "65 %", "Faster glacier loss in 2011-2020 than in the decade before", ICIMOD)),
        P("Shrinking ice does not mean every glacier will fall. But it leaves more ice hanging on steeper rock, and more lakes behind loose walls, above valleys where people live and work.",
          m(0, v(SOURCE)),
          m("above valleys", v(SYABRU_V), cut=True)),
        P("Nepal says it will rebuild its warning system on the border with China. In September its disaster authority and ICIMOD published a list of ten points for action.",
          m(0, v(RASUWA_V, places=[RASUWAGADHI, GYIRONG_PORT]))),
        P("This flood showed the hard part. The danger started on one side of a border and above every station, and it moved faster than an alert could travel. Yet the glacier's movement was visible from space before it fell.",
          m(0, v(SOURCE, date="2026-08-12")),
          m("and it moved", v(VALLEY), cut=True),
          m("Yet the", v(SOURCE, compare={**CMP, "hold": 0.3}), cut=True)),
        P("We will keep following these valleys from orbit. So who should watch the ice above a river that two countries share, and who should have the power to pull the alarm?",
          m(0, v(PATH_V, routes=[PATH])),
          ask=("So who", "Who should watch the ice?")),
    ]},
]

# ---- beats: a new real picture at least every ~6 s. Gaps are filled from views of the place the sentence is about.
sys.path.insert(0, str(HERE.parent.parent / "pipeline"))
from schema import Paragraph  # noqa: E402

MAX_WORDS = 10


def sat(view, label=None, date=AFTER):
    return m(0, v(view, date=date), text=label)


def pic(name, label=None):
    return photo(0, name, label)


POOLS = {
    "source": [sat(near(85.52, 28.30, 0.08), "Langtang Lirung, north face"), sat(near(85.50, 28.32, 0.08), "The debris track"),
               sat(near(85.48, 28.335, 0.08), "The Lhende river"), pic("File:Lirung (3to4).jpg", "Langtang Lirung")],
    "border": [sat(near(85.40, 28.32), "The Lhende valley"), sat(near(85.378, 28.28, 0.05), "Rasuwagadhi"),
               sat(near(85.33, 28.39, 0.08), "Gyirong, Tibet"), sat(near(85.43, 28.335), "Toward the border")],
    "gorge": [sat(near(85.367, 28.253, 0.05), "Timure"), sat(near(85.35, 28.20), "The Bhotekoshi gorge"),
              sat(near(85.343, 28.16, 0.05), "Syafrubesi"), sat(near(85.30, 28.10), "Below Dhunche"),
              pic("File:NH42 Trishuli Corridor towards Syaphru.jpg", "The road to Syafrubesi, 2024")],
    "lower": [sat(near(85.207, 28.072), "Mailung"), sat(near(85.186, 27.973), "Betrawati"), sat(near(85.148, 27.923), "Trishuli"),
              sat(near(85.11, 27.86), "Devighat"), sat(near(85.219, 28.033), "Ramche")],
    "langtang": [pic("File:Langtang Khola Rasuwa District.jpg", "The Langtang river"), pic("File:Kyanjin Gompa Village Rasuwa.jpg", "Kyanjin Gompa, up the valley"),
                 sat(near(85.509, 28.2158, 0.08), "Langtang village", date="2025-10-15/2025-11-10"), pic("File:Langtang Khola Rasuwa Jilla.jpg", "Langtang valley")],
}
POOLS["border2025"] = [sat(near(85.40, 28.32), "The Lhende valley, autumn 2025", date=BEFORE),
                       sat(near(85.378, 28.28, 0.05), "Rasuwagadhi, autumn 2025", date=BEFORE),
                       sat(near(85.367, 28.253, 0.05), "Timure, autumn 2025", date=BEFORE)]
POOLS["himalaya"] = [pic("File:Snow-capped Mountains at Kyanjin Gompa Rasuwa 2.jpg", "Glaciers of the Langtang range"),
                     pic("File:Snow-capped Mountains at Kyanjin Gompa Rasuwa 3.jpg", "Glaciers of the Langtang range"),
                     pic("File:Snow-capped Mountains at Kyanjin Gompa Rasuwa 4.jpg", "Glaciers of the Langtang range"),
                     pic("File:Snow-capped Mountains at Kyanjin Gompa Rasuwa 5.jpg", "Glaciers of the Langtang range"),
                     pic("File:Snow-capped Mountains at Kyanjin Gompa Rasuwa 6.jpg", "Glaciers of the Langtang range")]
counters = dict.fromkeys(POOLS, 0)


def topic_of(text, chapter):
    if chapter == "Not an Earthquake" and not re.search(r"flood|kilometres into Nepal", text):
        return "source"
    if re.search(r"Chamoli|Sikkim|Thame|Everest|region's glaciers|ICIMOD projected|Shrinking ice|the region", text):
        return "himalaya"
    if re.search(r"Chinese Academy|same study|researchers list", text):
        return "source"
    if chapter == "The Valley Remembers" and re.search(r"2025|lake|Friendship|unnoticed|Kathmandu Post|specialist|road along|burst", text):
        return "border2025"
    if chapter == "The Next Valley" and not re.search(r"Rasuwagadhi|border|China", text):
        return "himalaya"
    if re.search(r"Trishuli|Devighat|Betrawati|Mailung|India|school|headteacher|children", text):
        return "lower"
    if re.search(r"Langtang village|villagers|blast of air|rebuilt", text) or (chapter == "The Valley Remembers" and re.search(r"2015|earthquake|Langtang", text)):
        return "langtang"
    if re.search(r"Timure|Syafrubesi|Bhotekoshi|gorge|tunnel|Chilime|power|plants|megawatts|road along", text):
        return "gorge"
    if re.search(r"Rasuwagadhi|Gyirong|Tibet|Chinese|China|border|port|Port|lake|customs|vehicles|Korala|premier", text):
        return "border"
    if re.search(r"ice|glacier|scar|rock|mountain|Lirung|fell|source|north face", text):
        return "source"
    return None


CHAPTER_DEFAULT = {"Not an Earthquake": "source", "Within Minutes": "border", "Thirty-Eight Minutes": "lower", "The Valley Remembers": "langtang",
                   "What Fell": "source", "Power in the Path": "gorge", "The Missing": "lower", "The Next Valley": "source"}


def topic(para_text, at, chapter):
    """The sentence under the new picture decides; failing that the paragraph, then the chapter."""
    seen, sentence = 0, para_text
    for part in re.split(r"(?<=[.?!])\s+", para_text):
        k = len(part.split())
        if seen <= at < seen + k:
            sentence = part
            break
        seen += k
    return topic_of(sentence, chapter) or topic_of(para_text, chapter) or CHAPTER_DEFAULT[chapter]


def _phrase_index(words, phrase):
    want = phrase.split()
    bare = [w.strip('.,;:!?"') for w in words]
    hits = [i for i in range(len(bare)) if bare[i:i + len(want)] == [w.strip('.,;:!?"') for w in want]]
    return hits[0] if hits else None


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
        stops = sorted(marks | {0}) + [n]
        words = para["text"].split()
        blocks = [(min(idx), max(idx)) for idx in pm.step_indices() if len(idx) > 1]
        anchors = pm.anchor_indices()
        for sh, start in zip(para["shots"], anchors):
            later = [x for x in anchors if x > start]
            nxt = min(later) if later else n
            if sh["type"] in ("document", "chart"):  # a document or a chart holds until the next hand-placed shot
                blocks.append((start, nxt))
            for st in (sh.get("map") or {}).get("steps", []):  # a wipe keeps the screen until it has finished
                if st.get("compare"):
                    until = st["compare"].get("until")
                    k = _phrase_index(words, until) if until else start
                    blocks.append((k if k is not None else start, nxt))
        new = []
        for a, b in zip(stops, stops[1:]):
            inside = any(lo <= a and b <= hi for lo, hi in blocks)
            parts = 0 if inside else (b - a - 1) // MAX_WORDS
            for j in range(1, parts + 1):
                at = a + (b - a) * j // (parts + 1)
                group = topic(para["text"], at, ch["title"])
                shot = json.loads(json.dumps(POOLS[group][counters[group] % len(POOLS[group])]))
                counters[group] += 1
                shot["at"] = at
                new.append(shot)
        if new:
            pos = dict(zip(map(id, para["shots"]), anchors))
            para["shots"] = sorted(para["shots"] + new, key=lambda sh: pos.get(id(sh), sh["at"] if isinstance(sh["at"], int) else 0))

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
    "title": "The Langtang Collapse",
    "voice": "am_michael",
    "music": "procedural",
    "map_style": "satellite",
    "look": "none",
    "sources": ["episodes/langtang-collapse/research.md and factcheck.md"],
    "thumbnail": {"text": "38 MINUTES"},
    "chapters": chapters,
    "youtube": {
        "title": "Nepal's Flood Warning Came 38 Minutes Too Late",
        "description": "On 26 August 2026 a block of ice and rock broke off Langtang Lirung, on Nepal's border with Tibet, and became a flood that ran about 100 km down the Bhotekoshi and Trishuli rivers. We follow it from orbit with Sentinel-2 and Landsat images: the scar on the mountain, the border crossing at Rasuwagadhi, the 38 minutes before the text alerts, the same valley's disasters in 2015 and 2025, the hydropower tunnels in its path, and what the shrinking glaciers of the Himalaya mean for the next valley.",
        "tags": ["Nepal flood", "Langtang", "Langtang Lirung", "glacier collapse", "Rasuwa", "Bhotekoshi", "Trishuli", "Himalaya", "satellite images", "Sentinel-2", "Nepal Tibet", "early warning"],
        "pinned_comment": "Who should watch the ice above a river two countries share, and who should have the power to pull the alarm?",
    },
}
out = HERE / "script.json"
out.write_text(json.dumps(script, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
words = sum(len(p["text"].split()) for c in chapters for p in c["paragraphs"])
print(f"{words} words, {len(chapters)} chapters, {sum(len(p['shots']) for c in chapters for p in c['paragraphs'])} shots")
