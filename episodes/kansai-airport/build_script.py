"""Builds script.json for kansai-airport (beats are easier to review here than in the JSON).  python build_script.py

First episode under the production logic of 2026-11-13 (episode-plan step 1, cover-map): a known place and one
"why", painted map steps (highlight + arrows) open the chapters, our own Landsat series is the evidence.
Sources: research.md (JSCE 2008, ACI 2022, Funk & Mesri 2015, press reports of the operator's Dec 2024 figures).
Coordinates: OpenStreetMap / the airport reference point, to be checked on the storyboard.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
LS = "landsat"
# One clear Sentinel-2 day over Osaka Bay from one satellite (S2B, tiles 53SMT/SMU/SNU, under 1 % cloud, found 2026-11-13).
KIX_DAY = "2026-10-09/2026-10-09"


def day_for(view):
    lon, lat, span = view["lon"], view["lat"], view["span"]
    if span > 2 or not (134.9 <= lon <= 135.7 and 34.3 <= lat <= 34.8):
        return None  # far places (Narita, Chubu, Kitakyushu): the clearest recent day of that view
    return KIX_DAY


JAPAN = {"lon": 136.5, "lat": 36.0, "span": 16}
KANSAI = {"lon": 135.45, "lat": 34.62, "span": 1.5}
BAY = {"lon": 135.28, "lat": 34.53, "span": 0.95}  # the cover's view
KIX_W = {"lon": 135.235, "lat": 34.43, "span": 0.22}  # Landsat wipes
KIX_V = {"lon": 135.238, "lat": 34.434, "span": 0.1}
TERMINAL_V = {"lon": 135.244, "lat": 34.435, "span": 0.035}
ISLAND2_V = {"lon": 135.218, "lat": 34.445, "span": 0.06}
BRIDGE_V = {"lon": 135.283, "lat": 34.418, "span": 0.06}
RINKU_V = {"lon": 135.30, "lat": 34.41, "span": 0.05}
ITAMI_V = {"lon": 135.438, "lat": 34.785, "span": 0.06}
KOBE_AP_V = {"lon": 135.224, "lat": 34.633, "span": 0.06}
NARITA_V = {"lon": 140.386, "lat": 35.765, "span": 0.09}
CHUBU_V = {"lon": 136.805, "lat": 34.858, "span": 0.08}
KITAKYUSHU_V = {"lon": 131.035, "lat": 33.846, "span": 0.08}
ISLANDS = "file:kix.geojson"


def near(lon, lat, span=0.05):
    return {"lon": lon, "lat": lat, "span": span}


def place(name, lon, lat, label=None, kind="site", icon=None):
    d = {"name": name, "lon": lon, "lat": lat, "kind": kind, "label": label if label is not None else name}
    if icon:
        d["icon"] = icon
    return d


KIX = place("Kansai Airport", 135.244, 34.435, "Kansai Airport", "site")
KIX2 = place("Second island", 135.215, 34.444, "Second island", "site")
ITAMI = place("Itami Airport", 135.438, 34.785, "Itami Airport", "site")
KOBE = place("Kobe", 135.195, 34.69, "Kobe", "city")
OSAKA = place("Osaka", 135.502, 34.694, "Osaka", "city")
NARITA = place("Narita Airport", 140.386, 35.765, "Narita Airport", "site")
TOKYO = place("Tokyo", 139.77, 35.68, "Tokyo", "city")
RINKU = place("Rinku Town", 135.2985, 34.4105, "Rinku Town", "city")
EPICENTRE = place("1995 epicentre", 135.035, 34.598, "1995 epicentre", "site")
KOBE_AP = place("Kobe Airport", 135.224, 34.633, "Kobe Airport, 2006", "site")
CHUBU = place("Chubu Centrair", 136.805, 34.858, "Chubu Centrair, 2005", "site")
KITAKYUSHU = place("Kitakyushu Airport", 131.035, 33.846, "Kitakyushu, 2006", "site")
BRIDGE = {"from": [135.262, 34.427], "to": [135.2985, 34.4105], "mode": "line", "seconds": 2, "label": "Bridge, 3.75 km"}
OFFSHORE = {"from": [135.31, 34.41], "to": [135.262, 34.427], "color": "red", "label": "5 km", "bend": 0.2}
TO_ISLANDS = {"from": [135.0, 34.62], "to": [135.225, 34.445], "color": "red", "bend": 0.25}

CMP_85_95 = {"before": "1985-06-01/1985-06-10", "after": "1995-08-01/1995-08-07", "source": LS, "seconds": 1.8, "label_before": "1985", "label_after": "1995"}
CMP_95_26 = {"before": "1995-08-01/1995-08-07", "after": "2026-05-02/2026-05-08", "source": LS, "seconds": 1.8, "label_before": "1995", "label_after": "2026"}
CMP_85_89 = {"before": "1985-06-01/1985-06-10", "after": "1989-05-28/1989-06-03", "source": LS, "seconds": 1.8, "label_before": "1985", "label_after": "1989"}
CMP_89_95 = {"before": "1989-05-28/1989-06-03", "after": "1995-08-01/1995-08-07", "source": LS, "seconds": 1.8, "label_before": "1989", "label_after": "1995"}
CMP_95_04 = {"before": "1995-08-01/1995-08-07", "after": "2004-08-09/2004-08-15", "source": LS, "seconds": 1.8, "label_before": "1995", "label_after": "2004"}
CMP_04_26 = {"before": "2004-08-09/2004-08-15", "after": "2026-05-02/2026-05-08", "source": LS, "seconds": 1.8, "label_before": "2004", "label_after": "2026"}


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


OPERATOR = "Kansai Airports, measurements of December 2025"
JSCE = "Suzuki & Okuda, Kansai International Airport Co., JSCE, 2008"
FUNK = "Funk & Mesri, J. Geotech. Geoenviron. Eng., ASCE, 2015"
AIRSPACE = "Air & Space / Smithsonian, June 2018"
KAP = "Kansai Airports, Technologies for Offshore Airports"

chapters = [
    {"title": "An Island That Was Not There", "mood": "curious", "paragraphs": [
        P("This is Osaka Bay in 1985. Open water. Ten years later there is an island here, three miles from the shore, with an airport on it. Japan built it from nothing. And it has been sinking ever since.",
          m(0, v(KIX_W, compare={**CMP_85_95, "until": "Ten years later"}), step("Ten years later", places=[KIX]), cut=True),
          m("Japan built it", v(BAY, highlight=[ISLANDS], arrows=[TO_ISLANDS], places=[OSAKA]), cut=True)),
        P("By the operator's own measurements, the ground under the first island has dropped almost fourteen meters since the fill began. That is forty-five feet, the height of a four-storey building. Last year it went down five centimeters more.",
          m(0, v(KIX_V, places=[KIX]), cut=True),
          stat("almost fourteen", "13.72 m", "Average settlement of the first island since construction began (45 ft)", OPERATOR),
          m("the height of", v(TERMINAL_V), cut=True),
          stat("Last year", "5 cm", "Settlement of the first island in 2025, average of 17 points", OPERATOR)),
        P("Then Japan built a second island beside it. That one is sinking four times as fast.",
          m(0, v(KIX_W, compare={**CMP_95_26, "until": None}), cut=True)),
        P("Thirty-four million passengers used this airport last year. So why did Japan build its airport in the sea, why did the forecasts miss, and how long can it last?",
          m(0, v(TERMINAL_V, places=[KIX]), cut=True),
          m("So why did", v(BAY, highlight=[ISLANDS], places=[OSAKA, KOBE]), cut=True),
          ask=("So why did", "Why build an airport in the sea?")),
    ]},
    {"title": "A City With No Room", "mood": "calm", "paragraphs": [
        P("Osaka already had an airport. Itami sits inland, north of the city, with houses on every side. The first jet landed there in 1964. Almost at once the neighbours began to protest and to sue over the noise, and in the end Japan's supreme court awarded them compensation.",
          m(0, v(KANSAI, places=[ITAMI, OSAKA, KOBE])),
          m("Itami sits", v(ITAMI_V, places=[ITAMI]), cut=True),
          m("Almost at once", v(near(135.44, 34.79, 0.12)), cut=True)),
        P("Near Tokyo, the government had tried to build a new airport on farmland at Narita, and met years of protest from the people who lived there. Planners in Osaka did not want a second Narita.",
          m(0, v(JAPAN, places=[NARITA, TOKYO, OSAKA])),
          m("on farmland", v(NARITA_V, places=[NARITA]), cut=True),
          m("Planners in Osaka", v(KANSAI, places=[OSAKA, ITAMI]), cut=True)),
        P("So they looked at the one place where nobody lived: the bay. The first plan put the airport off Kobe. Kobe said no. The site moved south, five kilometers out to sea, placed so that planes would arrive and leave entirely over water, around the clock. The airport's own engineers later called it a radical solution to the noise problems of Itami.",
          m(0, v(BAY, places=[OSAKA, KOBE])),
          m("Kobe said no", v(near(135.2, 34.66, 0.25), places=[KOBE]), cut=True),
          m("The site moved", v(BAY, highlight=[ISLANDS], arrows=[OFFSHORE], places=[KOBE, OSAKA]), cut=True),
          clip("The airport's own", "\"Kansai International Airport was built five kilometers out to sea on Osaka Bay as a radical solution to the noise problems of Osaka (Itami) Airport.\"", "S. Suzuki and Y. Okuda, Kansai International Airport Co., in JSCE Civil Engineering, 2008", highlight="a radical solution to the noise problems")),
        P("We had to decide to build offshore because there were few viable options, an urban planning professor, Hiro Ishikawa, told This Week in Asia last year. There was one problem with the site. There was no land there.",
          clip(0, "\"We had to decide to build offshore because there were few viable options.\"", "Hiro Ishikawa, emeritus professor, Meiji University, to This Week in Asia, 2025", highlight="few viable options"),
          m("There was one", v(KIX_W, date="1985-06-01/1985-06-10"), cut=True)),
    ]},
    {"title": "Building on a Sponge", "mood": "curious", "paragraphs": [
        P("The water at the site is about twenty meters deep. Under it lies about twenty meters of soft clay, and that clay is seventy percent water. Put weight on it and the water is squeezed out, the way it leaves a sponge. The operator expected this layer to shrink to two thirds of its thickness.",
          m(0, v(KIX_W, date="1985-06-01/1985-06-10"), cut=True),
          stat("seventy percent", "70 %", "Share of water in the soft clay under the bay, by volume", KAP),
          m("The operator expected", v(BAY, highlight=[ISLANDS], dim=True), cut=True)),
        P("Left alone, that would take decades. So the builders gave the water a way out. They drove one million columns of sand into the clay, each twenty meters long, two and a half meters apart. That was more than all of Japan had installed in the thirty-five years before. It worked: a process of decades was over within a year.",
          m(0, v(near(135.238, 34.43, 0.14)), cut=True),
          stat("one million columns", "1,000,000", "Sand drains under the first island, 20 m long, 2.5 m apart", KAP),
          m("That was more", v(JAPAN, highlight=[ISLANDS], places=[OSAKA]), cut=True),
          m("It worked", v(KIX_V), cut=True)),
        P("In 1987 they started a wall around an empty rectangle of sea, built of rubble and forty-eight thousand concrete blocks. This is our own image from May 1989. The wall is finished. Inside it there is still water.",
          m(0, v(KIX_W, compare={**CMP_85_89, "until": "This is our own"}), step("This is our own", places=[place("Seawall, 1989", 135.24, 34.43, "Seawall, 1989", "site")]), cut=True)),
        P("Then came the fill. Soil dredged from the bay, rock quarried from mountains nearby, more barged in from China and Korea, until the new ground was thirty meters deep. A bridge nearly four kilometers long tied the island to the shore. On September fourth, 1994, the airport opened.",
          m(0, v(KIX_W, compare={**CMP_89_95, "until": "Soil dredged"}), step("Soil dredged"), cut=True),
          stat("thirty meters deep", "30 m", "Depth of the reclaimed ground on the first island", KAP),
          m("A bridge nearly", v(BRIDGE_V, routes=[BRIDGE], places=[RINKU]), cut=True),
          m("On September fourth", v(TERMINAL_V, places=[KIX]), cut=True)),
        P("But the sand drains reached only the soft top layer. Under it lies something older. For two million years the sea here rose and fell by more than a hundred meters as ice ages came and went, laying down clay, then sand, then clay again. That stack is up to four hundred meters thick. Nobody can drain it. The operator's own page says the airport is managed on the assumption that long-term subsidence will continue.",
          m(0, v(KIX_V), cut=True),
          m("For two million", v(KANSAI, highlight=[ISLANDS], dim=True), cut=True),
          stat("up to four hundred", "400 m", "Thickness of the older clay and sand layers under the islands", KAP),
          clip("The operator's own", "\"...the airport facilities are managed with the assumption that long-term subsidence will continue.\"", "Kansai Airports, Technologies for Offshore Airports (3)", highlight="long-term subsidence will continue")),
    ]},
    {"title": "The Forecast That Missed", "mood": "tension", "paragraphs": [
        P("The planners knew the island would sink, and they piled on enough soil to allow for it. The plan was that after fifty years the ground would still stand thirteen feet above the sea. By 1990, before a single building stood on it, the island had sunk twenty-seven feet instead of the nineteen predicted.",
          m(0, v(KIX_V, places=[KIX]), cut=True),
          chart("By 1990", "Sinking of the first island by 1990", "feet", [["Predicted", 19], ["Measured", 27]], AIRSPACE, reveal=["twenty-seven feet"], highlight=1)),
        P("A spokeswoman for the operator, Yukako Handa, told Air and Space magazine that the engineers simply could not believe the gap between their laboratory estimates and what the seabed really did. By opening day the ground had already gone down almost ten meters. Parts of the island reached the fifty-year limit within six years, and at least a hundred and fifty million dollars went into raising the seawall.",
          m(0, v(near(135.262, 34.447, 0.05)), cut=True),
          stat("almost ten meters", "9.82 m", "Settlement of the first island before the airport opened in 1994", OPERATOR),
          stat("at least a hundred", "$150 million+", "Spent to raise the seawall as the island sank", AIRSPACE)),
        P("An island does not sink evenly. So the terminal, a mile long, stands on nine hundred columns, each with its own gauge. When one drops, it is jacked up and steel plates are slid underneath. The middle of the building has a basement, which makes it lighter than the wings, so the builders packed iron ore under it as ballast. It still sank less than its neighbours, and had to be levelled.",
          m(0, v(TERMINAL_V, places=[KIX]), cut=True),
          stat("nine hundred columns", "900", "Columns under Terminal 1, each monitored and jacked up when needed", KAP),
          m("The middle of", v(near(135.247, 34.437, 0.04)), cut=True)),
        P("The sinking reached things nobody had drawn. Rain was meant to run off the runway and out to sea through pipes, downhill. As the ground settled, the slope disappeared. The airport installed thirty-seven large pumps to push its own rainwater out, and in 2007 it covered the whole first runway with new asphalt, twenty-five centimeters thick on average, to give the water a slope again.",
          m(0, v(near(135.228, 34.42, 0.05)), cut=True),
          clip("As the ground", "\"...with the progression of uneven settlement... the angle of the drainage pipes has gradually lessened, hampering the flow of rainwater into the ocean.\"", "S. Suzuki and Y. Okuda, Kansai International Airport Co., in JSCE Civil Engineering, 2008", highlight="the angle of the drainage pipes has gradually lessened"),
          stat("thirty-seven large", "37 pumps", "Installed at ten sites, 3,300 cubic meters a minute", JSCE),
          stat("twenty-five centimeters", "160,000 tons", "Asphalt laid on Runway A in 2007-2008, 25 cm thick on average", "Kansai Airports")),
        P("And yet the island held. In January 1995, four months after opening, the Kobe earthquake struck about twenty kilometers away and killed more than six thousand people. The airport was not damaged.",
          m(0, v(BAY, highlight=[ISLANDS], places=[EPICENTRE, KOBE])),
          m("The airport was", v(KIX_V, places=[KIX]), cut=True)),
    ]},
    {"title": "They Did It Again", "mood": "curious", "paragraphs": [
        P("One runway was not enough. In 1999 work began on a second island, in deeper water. This time the builders drove one point two million sand drains. This is our image from 2004, with the new island still being filled. Its runway, four kilometers long, opened in August 2007.",
          m(0, v(BAY, highlight=[ISLANDS], places=[KIX2])),
          stat("one point two", "1.2 million", "Sand drains under the second island", KAP),
          m("This is our image", v(KIX_W, compare={**CMP_95_04, "until": "Its runway"}), step("Its runway", places=[KIX2]), cut=True)),
        P("By the time that runway opened, the seabed under it had already gone down almost twelve meters. It has gone down six more since. In 2025 the second island sank twenty centimeters, four times as fast as the first.",
          m(0, v(KIX_W, compare={**CMP_04_26, "until": None}), cut=True),
          stat("almost twelve meters", "17.67 m", "Settlement under the second island: 11.71 m before 2007, 5.96 m since", OPERATOR),
          chart("In 2025 the", "Sinking in 2025", "cm", [["First island", 5], ["Second island", 20]], OPERATOR, reveal=["twenty centimeters"], highlight=1)),
        P("An engineering professor at the University of Illinois, Gholamreza Mesri, has studied both islands for years. In a 2015 paper with a colleague he forecast that by the year 2100 the seabed under the first island will have settled about fifteen point seven meters, and under the second, almost twenty-five. The operator makes no such promise. It says only that it will keep measuring, with the guidance of experts.",
          m(0, v(ISLAND2_V, places=[KIX2]), cut=True),
          stat("about fifteen point", "15.7 m / 24.9 m", "Forecast settlement of the seabed by 2100, first and second island", FUNK),
          m("The operator makes", v(KIX_V), cut=True)),
    ]},
    {"title": "The Sea Comes Over the Wall", "mood": "tension", "paragraphs": [
        P("A sinking island in a typhoon sea needs its walls to keep up. In 2004 a run of typhoons brought the highest tides and waves the airport had recorded. Waves came over the seawall and destroyed a road behind it. The company raised the walls by one to two meters along eleven kilometers.",
          m(0, v(BAY, highlight=[ISLANDS], places=[OSAKA])),
          m("In 2004 a run", v(near(135.21, 34.412, 0.05)), cut=True),
          clip("Waves came over", "\"Waves flowed over the airport's seawalls, destroying a road behind the seawall.\"", "S. Suzuki and Y. Okuda, Kansai International Airport Co., in JSCE Civil Engineering, 2008", highlight="destroying a road behind the seawall"),
          stat("one to two meters", "+1-2 m", "Seawalls raised along about 11 km after the 2004 typhoons", JSCE)),
        P("The sea was also coming from below. The island is made of crushed rock, and the water inside it rose and fell with the tide, into basements. So between 2004 and 2006 the company built a wall underground, about thirty meters deep, all the way around the island.",
          m(0, v(KIX_V), cut=True),
          stat("about thirty meters", "11 km", "Underground cut-off wall around the island, about 30 m deep, 2004-2006", JSCE),
          m("all the way", v(near(135.255, 34.425, 0.06)), cut=True)),
        P("Then came September fourth, 2018, twenty-four years to the day after the airport opened. Typhoon Jebi pushed the sea over the walls and across a runway. A tanker of about two thousand six hundred tons, the Houn Maru, dragged its anchor and hit the only bridge. By most reports about three thousand passengers were stuck on the island overnight, and left the next morning by boat.",
          m(0, v(KIX_W, places=[KIX]), cut=True),
          m("pushed the sea", v(near(135.235, 34.424, 0.05)), cut=True),
          m("A tanker of", v(BRIDGE_V, routes=[BRIDGE], places=[RINKU]), cut=True),
          stat("about three thousand", "~3,000", "Passengers stranded overnight on 4 Sep 2018, by most press reports", "Press reports, Sep 2018"),
          m("and left the", v(near(135.23, 34.55, 0.4), routes=[{"from": [135.262, 34.44], "to": [135.224, 34.633], "mode": "line", "seconds": 2, "label": "Boats to Kobe Airport"}], places=[KOBE_AP]), cut=True)),
        P("The walls went up again. Within three years, with planes still landing, the operator raised the seawalls along more than six kilometers, laid wave-breaking blocks along nearly five, and went on raising the first runway.",
          m(0, v(near(135.215, 34.409, 0.05)), cut=True),
          stat("more than six", "6 km", "Seawalls raised after Typhoon Jebi; blocks placed along 4.7 km", "Kansai Airports, via ACI Asia-Pacific, May 2022")),
    ]},
    {"title": "Who Pays", "mood": "calm", "paragraphs": [
        P("None of this was cheap. When the airport opened, its cost was put at about eight billion dollars. By 2008, with the repairs, the second island and its runway, the figure was about twenty billion.",
          m(0, v(KIX_V, places=[KIX]), cut=True),
          chart("By 2008", "What the airport had cost", "$ billion", [["At opening, 1994", 8], ["By 2008", 20]], AIRSPACE, reveal=["about twenty billion"], highlight=1)),
        P("The airport carried that as debt, and for years it charged some of the highest landing fees in the world to pay the interest. In 2016 the state handed the running of the airport to a private group led by Orix of Japan and Vinci of France. Two years later that group was paying the transport ministry about three hundred and fifty million dollars a year for the right.",
          m(0, v(near(135.255, 34.44, 0.05)), cut=True),
          m("In 2016", v(KANSAI, highlight=[ISLANDS], places=[OSAKA, ITAMI, KOBE]), cut=True),
          stat("about three hundred", "$350 million", "Paid each year to Japan's transport ministry for operating rights (2018)", AIRSPACE)),
        P("And the passengers came. Twenty-six million in 2016. Thirty-four million in 2025, most of them from abroad. A fully loaded Airbus A380, the operator likes to point out, weighs less than three ten-thousandths of one percent of the soil it lands on.",
          m(0, v(TERMINAL_V, places=[KIX]), cut=True),
          chart("Twenty-six million", "Passengers a year", "million", [["2016", 26], ["2025", 34.1]], "Air & Space, 2018; Kansai Airports traffic figures", reveal=["Thirty-four million"], highlight=1),
          m("A fully loaded", v(near(135.235, 34.424, 0.06)), cut=True)),
    ]},
    {"title": "Will It Last", "mood": "curious", "paragraphs": [
        P("The operator gives no official lifetime for the islands. The first one now sinks a few centimeters a year, not half a meter. We knew from the start that the airport would subside, Professor Ishikawa said, and we considered the various impacts in the design.",
          m(0, v(KIX_V, places=[KIX]), cut=True),
          clip("We knew from", "\"We knew from the start that the airport would subside, and we considered the various impacts in the design.\"", "Hiro Ishikawa, emeritus professor, Meiji University, to This Week in Asia, 2025", highlight="We knew from the start")),
        P("Japan kept building this way. Chubu, near Nagoya, in 2005. Kobe, the city that said no, in 2006. Kitakyushu the same year. All of them on islands made in the sea.",
          m(0, v(JAPAN, places=[CHUBU, KOBE_AP, KITAKYUSHU])),
          m("Chubu, near", v(CHUBU_V, places=[CHUBU]), cut=True),
          m("Kobe, the city", v(KOBE_AP_V, places=[KOBE_AP]), cut=True),
          m("Kitakyushu the same", v(KITAKYUSHU_V, places=[KITAKYUSHU]), cut=True)),
        P("So here is the question. If your city had no room left for an airport, would you build one on the sea, knowing it would sink?",
          m(0, v(KIX_W, places=[KIX]), cut=True),
          m("would you build", v(BAY, highlight=[ISLANDS], arrows=[TO_ISLANDS]), cut=True),
          ask=("If your city", "Would you build it, knowing it would sink?")),
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
    "kix": [(135.244, 34.435), (135.262, 34.447), (135.215, 34.409), (135.215, 34.444), (135.235, 34.458), (135.20, 34.428),
            (135.255, 34.425), (135.228, 34.42), (135.25, 34.443), (135.222, 34.432), (135.208, 34.438), (135.24, 34.418),
            (135.268, 34.436), (135.232, 34.447), (135.205, 34.418), (135.248, 34.455)],
    "shore": [(135.30, 34.41), (135.32, 34.43), (135.285, 34.395), (135.34, 34.45), (135.27, 34.38), (135.36, 34.47)],
    "city": [(135.438, 34.785), (135.50, 34.69), (135.45, 34.76), (135.47, 34.72), (135.42, 34.80), (135.52, 34.66)],
    "bay": [(135.24, 34.44), (135.30, 34.48), (135.20, 34.50), (135.33, 34.42), (135.26, 34.52), (135.18, 34.42)],
}
SPANS = {"bay": [0.3, 0.45, 0.6, 0.35], None: [0.05, 0.07, 0.09, 0.06, 0.08, 0.1]}
LABELS = {"kix": "Kansai International Airport", "shore": "Osaka Bay shore", "city": "Osaka", "bay": "Osaka Bay"}
PHOTOS = {}
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
FAMILY = {}


def filler(group, t):
    for name, label in PHOTOS.get(group, []):
        fam = FAMILY.get(name, name)
        uses = photo_uses.get(fam, [])
        if len(uses) < PHOTO_MAX and all(t - u >= PHOTO_GAP for u in uses):
            photo_uses.setdefault(fam, []).append(t)
            return pic(name, label)
    return next_view(VIEW_PLACE.get(group, group))



def topic_of(text, chapter):
    if re.search(r"Itami|Osaka already|grown around|flight paths|Narita|farmland", text):
        return "city"
    if re.search(r"bridge|shore|Rinku|boat|tanker", text):
        return "shore"
    if re.search(r"bay|Bay|typhoon|Typhoon|sea |tide|Kobe said", text):
        return "bay"
    if re.search(r"island|airport|terminal|runway|wall|fill|clay|drain|pump|column|sink|sank|settle", text):
        return "kix"
    return None


CHAPTER_DEFAULT = {"An Island That Was Not There": "kix", "A City With No Room": "city", "Building on a Sponge": "kix",
                   "The Forecast That Missed": "kix", "They Did It Again": "kix", "The Sea Comes Over the Wall": "bay",
                   "Who Pays": "kix", "Will It Last": "kix"}

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


BASEMAP_NAMED = {"Osaka", "Kobe", "Tokyo"}
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
    "title": "Why Japan's $20 Billion Airport Is Sinking",
    "voice": "am_michael",
    "music": "procedural",
    "map_style": "satellite",
    "look": "none",
    "sources": ["episodes/kansai-airport/research.md and factcheck.md", "Landsat data courtesy of the U.S. Geological Survey", "Contains modified Copernicus Sentinel data 2026"],
    "thumbnail": {"text": "45 FEET DOWN"},
    "chapters": chapters,
    "youtube": {
        "title": "Why Japan's $20 Billion Airport Is Sinking",
        "description": "In 1985 this part of Osaka Bay was open water. Japan built an island there, opened Kansai International Airport on it in 1994, and the ground has dropped more than 13 meters since the fill began. From orbit with our own Landsat and Sentinel-2 images we watch the island appear, follow the second island that is sinking faster, and go through the forecasts that missed, the typhoon that cut the airport off in 2018, and what it costs to keep an airport above the sea.",
        "tags": ["Kansai International Airport", "Kansai airport sinking", "Osaka", "Japan", "artificial island", "land reclamation", "megaproject", "Typhoon Jebi", "subsidence", "satellite images", "Landsat", "Sentinel-2", "engineering"],
        "pinned_comment": "If your city had no room left for an airport, would you build one on the sea, knowing it would sink?",
    },
}
out = HERE / "script.json"
out.write_text(json.dumps(script, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
words = sum(len(p["text"].split()) for c in chapters for p in c["paragraphs"])
print(f"{words} words, {len(chapters)} chapters, {sum(len(p['shots']) for c in chapters for p in c['paragraphs'])} shots")
