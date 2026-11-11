"""Builds script.json for outer-banks (beats are easier to review here than in the JSON).  python build_script.py

Sources: research.md (NPS, NCDOT, NPR via WUNC, Public Radio East, Island Free Press, USGS) and our own Landsat shoreline
measurement (tools/outer_banks_shoreline.py -> shoreline.json). Coordinates: approximate, checked on the storyboard.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
AFTER = "2026-10-20/2026-11-08"  # after the October nor'easter
LS = "landsat"

OBX = {"lon": -75.75, "lat": 35.55, "span": 2.2}
HATTERAS = {"lon": -75.6, "lat": 35.45, "span": 0.75}
RODANTHE_V = {"lon": -75.468, "lat": 35.595, "span": 0.07}
SCURVES_V = {"lon": -75.475, "lat": 35.618, "span": 0.06}
PEA_V = {"lon": -75.495, "lat": 35.716, "span": 0.07}
BUXTON_V = {"lon": -75.522, "lat": 35.258, "span": 0.07}
AVON_V = {"lon": -75.50, "lat": 35.352, "span": 0.07}
RODANTHE_W = {"lon": -75.47, "lat": 35.60, "span": 0.11}  # Landsat wipes: 30 m pixels need a wider frame
PEA_W = {"lon": -75.49, "lat": 35.715, "span": 0.11}
BUXTON_W = {"lon": -75.525, "lat": 35.26, "span": 0.11}
ISABEL_V = {"lon": -75.715, "lat": 35.215, "span": 0.09}
OREGON_V = {"lon": -75.535, "lat": 35.775, "span": 0.06}
FERRY_V = {"lon": -75.62, "lat": 35.65, "span": 0.45}
USA_V = {"lon": -78.5, "lat": 35.4, "span": 9}


def near(lon, lat, span=0.05):
    return {"lon": lon, "lat": lat, "span": span}


def place(name, lon, lat, label=None, kind="site", icon=None):
    d = {"name": name, "lon": lon, "lat": lat, "kind": kind, "label": label if label is not None else name}
    if icon:
        d["icon"] = icon
    return d


RODANTHE = place("Rodanthe", -75.468, 35.594, "Rodanthe", "city")
BUXTON = place("Buxton", -75.535, 35.267, "Buxton", "city")
AVON = place("Avon", -75.510, 35.352, "Avon", "city")
HATTERAS_VILLAGE = place("Hatteras", -75.690, 35.219, "Hatteras Village", "city")
LIGHTHOUSE = place("Cape Hatteras Lighthouse", -75.5289, 35.2506, "Cape Hatteras Lighthouse", "site")
VISITOR = place("Pea Island Visitor Center", -75.4930, 35.7167, "Pea Island Visitor Center", "site")
STUMPY = place("Stumpy Point", -75.771, 35.698, "Stumpy Point", "port")
RALEIGH = place("Raleigh", -78.64, 35.78, "Raleigh", "capital")
FERRY = {"from": [-75.468, 35.594], "to": [-75.771, 35.698], "mode": "line", "seconds": 3, "label": "Emergency ferry"}

CMP_RODANTHE = {"before": "1985-08-16", "after": "2026-10-27", "source": LS, "seconds": 2.6}
CMP_PEA = {"before": "1985-08-16", "after": "2026-10-27", "source": LS, "seconds": 2.4}
CMP_BUXTON = {"before": "1985-08-16", "after": "2026-10-27", "source": LS, "seconds": 2.4}
CMP_ISABEL = {"before": "2003-07-01/2003-09-15", "after": "2003-09-19/2003-11-20", "source": LS, "seconds": 2.2,
              "label_before": "SUMMER 2003", "label_after": "AFTER ISABEL, 2003"}
CMP_BRIDGE = {"before": "2021-09-01/2021-11-30", "after": "2023-09-01/2023-11-30", "seconds": 2.2}


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


NPS = "National Park Service, Cape Hatteras National Seashore, Aug 2026"
NPS_LH = "National Park Service, Moving the Cape Hatteras Lighthouse"
NPR = "NPR, Sep 17, 2026"
NCDOT = "NCDOT, Oct 2026"
OWN = "Our measurement, Landsat 5, 8 and 9"
IFP = "Island Free Press; Dare County, 2026"
PRE = "Public Radio East, Oct 30, 2026"
USGS = "US Geological Survey"

PH_COLLAPSE = "File:Photo of March 13, 2023, collapsed house at 23228 East Point Dr., Rodanthe.jpg"
PH_SITE = "File:Site of the 23228 East Point Dr., Rodanthe, house collapse on March 14, 2023--less than 24 hours after collapse.jpg"
PH_DEBRIS = "File:National Park Service employees collect house collapse debris - 52750036938.jpg"
PH_LH_BEFORE = "File:Cape Hatteras Lighthouse Restoration Project 02-24-2024 - 53554250733.jpg"  # NPS, PD; the 1999 pre-move aerials on Commons are too soft
PH_LH_NOW = "File:Lighthouse at Cape Hatteras National Seashore. NPS-Michael B. Edwards (18497979278).jpg"  # 2004, NPS
PH_LH_PATH = "File:FEMA - 8383 - Photograph by Mark Wolfe taken on 09-20-2003 in North Carolina.jpg"  # after Isabel, 20 Sep 2003
PH_DEBRIS2 = "File:Photo of debris associated with house collapse at 24131 Ocean Dr., Rodanthe - 53753242008.jpg"
PH_DEBRIS3 = "File:Photo of debris associated with house collapse at 24131 Ocean Dr., Rodanthe - 53753021681.jpg"
PH_DEBRIS4 = "File:National Park Service employees collect house collapse debris - 52749539471.jpg"
PH_DEBRIS5 = "File:National Park Service employees look for house collapse debris on beach north of the Rodanthe Pier.jpg"
PH_DEBRIS6 = "File:Collected debris associated with March 13 house collapse.jpg"
PH_LH_2020 = "File:Cape Hatteras Lighthouse inspection 12-06-2020 - 53554408139.jpg"
PH_LH_SHADOW = "File:Cape Hatteras Lighthouse shadow (50068811063).jpg"
OCEAN = "File:Photo of debris associated with house collapse at 24131 Ocean Dr., Rodanthe - {}.jpg"
PH_OCEAN_A, PH_OCEAN_B, PH_OCEAN_C, PH_OCEAN_D = (OCEAN.format(n) for n in ("53752082612", "53753328604", "53753328699", "53753321449"))
PH_TRUCK = "File:Truck travels along beach north of Rodanthe Pier.jpg"
PH_CREW = "File:Vehicles and staff on beach collecting beach debris.jpg"
PH_VOL = "File:Volunteers clean up beach debris.jpg"
PH_VOL2 = "File:Volunteers participate in beach debris cleanup - 52752007055.jpg"
PH_NOURISH = "File:Buxton beach nourishment in progress, July 2022.jpg"
PH_BONNER = "File:Outer Banks Scenic Byway - Herbert C. Bonner Bridge and Oregon Inlet - NARA - 7720871.jpg"

chapters = [
    {"title": "The Front Row", "mood": "tension", "paragraphs": [
        P("Sometime in the night of June 2, 2026, a beach house on Ocean Drive in Buxton, North Carolina, fell into the Atlantic. It was the thirty-second house lost on this national seashore since 2020.",
          m(0, v(USA_V, places=[RALEIGH]), step("in Buxton", view=BUXTON_V, places=[BUXTON]), cut=False),
          stat("It was the", "32 houses", "Collapsed on Cape Hatteras National Seashore beaches since 2020", NPS)),
        P("Twenty of them stood in Buxton and twelve in Rodanthe. Six went on a single day in September 2025. Five more went on one day that October. And four more fell in two days this February.",
          m(0, v(HATTERAS, places=[BUXTON, RODANTHE])),
          stat("Six went", "6, then 5", "Buxton houses lost on 30 September and 28 October 2025", NPS),
          photo("Five more", PH_COLLAPSE, "Rodanthe, March 2023")),
        P("This is the shore at Rodanthe in August 1985. And this is the same shore this October. We measured where the water line sits in Landsat images, year by year.",
          m(0, v(RODANTHE_W, compare={**CMP_RODANTHE, "until": "And this"}), step("And this"), step("We measured", places=[RODANTHE]),
            text="Real satellite images · Landsat", cut=True)),
        P("Since 1985 it has moved about a hundred and fifty-five metres inland. That is about five hundred feet, or roughly twelve feet a year.",
          stat(0, "~155 m", "How far the shoreline at Rodanthe moved inland, 1985 to 2026", OWN, "About 510 feet; tides move a single day's line by tens of metres"),
          m("That is about", v(RODANTHE_V, date=AFTER, places=[RODANTHE]), cut=True)),
        P("It did not move evenly. By 2000 the line had already gone about a hundred metres. Then it slowed for twenty years, and since 2022 it has picked up again: about thirty metres more in four years.",
          m(0, v(RODANTHE_V, places=[RODANTHE])),
          chart("By 2000", "Rodanthe shoreline, metres inland of 1985", " m", [["1990", 37], ["2000", 99], ["2010", 121], ["2018", 118], ["2022", 127], ["2026", 155]], OWN, highlight=5,
                reveal=["Then it slowed", "and since 2022"])),
        P("These islands have always moved. What is new is what we built on them that cannot move: a lighthouse, a road, and the houses along it.",
          m(0, v(HATTERAS)),
          photo("a lighthouse", PH_LH_NOW, "Cape Hatteras Lighthouse")),
        P("One of the three was moved out of the way. The other two are still waiting, and the rules tell them to wait. Why does the government pay for a house only after the ocean has taken it?",
          m(0, v(BUXTON_V, places=[LIGHTHOUSE])),
          ask=("Why does", "Would you wait for your house to fall?")),
    ]},
    {"title": "Islands That Walk", "mood": "curious", "paragraphs": [
        P("The Outer Banks are barrier islands: narrow ribbons of sand between the Atlantic and the shallow sounds behind them.",
          m(0, v(OBX, places=[RODANTHE, BUXTON, STUMPY]), text="The Outer Banks, North Carolina")),
        P("The US Geological Survey describes how they move. In a storm, waves push sand over the dunes and drop it on the far side. Storm after storm, the island rolls toward the mainland. Geologists call it barrier island rollover. Wind moves sand as well, and inlets open, close and wander along the coast. Storms can also hit from behind. In 2019 Hurricane Dorian flooded North Core Banks, farther south, from the sound side, and a study led by the USGS found the island lost about eighteen percent of its sand above water.",
          m(0, v(near(-75.49, 35.68, 0.1))),
          m("drop it on", v(near(-75.47, 35.63, 0.06)), cut=True),
          stat("Geologists call", "Rollover", "How a barrier island moves toward the mainland", USGS),
          m("In 2019", v({"lon": -76.17, "lat": 34.96, "span": 0.35}, places=[place("North Core Banks", -76.20, 34.93, "North Core Banks", "site")]), cut=True)),  # North Core Banks (audit: a filler showed Hatteras Village here)
        P("Sometimes a storm cuts straight through. In September 2003, Hurricane Isabel opened a new inlet north of Hatteras Village, where an old inlet had closed in the 1930s.",
          m(0, v(ISABEL_V, compare={**CMP_ISABEL, "until": "Hurricane Isabel"}), step("Hurricane Isabel"), step("where an old", places=[HATTERAS_VILLAGE]))),
        P("It was about two thousand feet wide and fifteen feet deep, in three channels. The village was cut off for two months. The Army Corps of Engineers pumped sand into the gap, and the road reopened on November 22. Elsewhere Isabel buried Highway 12 under as much as three feet of sand.",
          stat(0, "~2,000 ft", "Width of the inlet Hurricane Isabel cut in September 2003", "NPS; NC records"),
          m("The village", v(near(-75.69, 35.22, 0.06), places=[HATTERAS_VILLAGE]), cut=True),
          stat("Elsewhere", "Up to ~3 ft", "Sand Isabel left on parts of Highway 12, 2003", USGS)),
        P("For an island, moving is how it survives a rising sea. For a road, a lighthouse or a house on pilings, it is a disaster. And the first building here to face that choice was the tallest.",
          m(0, v(HATTERAS)),
          photo("And the first", PH_LH_SHADOW, "Cape Hatteras Lighthouse")),
    ]},
    {"title": "The Lighthouse That Moved", "mood": "curious", "paragraphs": [
        P("The Cape Hatteras Lighthouse was finished in 1870, about fifteen hundred feet from the ocean. The National Park Service calls it the tallest brick lighthouse in the United States.",
          photo(0, PH_LH_NOW, "Cape Hatteras Lighthouse"),
          stat("about fifteen", "1,500 ft", "From the ocean when the lighthouse was finished, 1870", NPS_LH)),
        P("By 1970 the ocean was a hundred and twenty feet away. The tower before it, built in 1803 about a mile from the shore, was finally lost to a storm in 1980.",
          stat(0, "120 ft", "From the ocean in 1970", NPS_LH),
          m("The tower", v(BUXTON_V, places=[LIGHTHOUSE]), cut=True)),
        P("People tried to hold the line. In 1936 the Coast Guard built groins, then gave up and moved the light to a steel tower in the woods. In the 1960s and 70s came new sand and three more groins. In 1980 the Park Service studied a seawall.",
          m(0, v(near(-75.52, 35.255, 0.06))),
          stat("In 1936", "1936", "The Coast Guard builds groins, then moves the light inland", NPS_LH),
          m("In the 1960s", v(near(-75.515, 35.262, 0.06)), cut=True),
          stat("In 1980", "1980", "A seawall is studied to hold the old site", NPS_LH)),
        P("Moving it was first rejected as impractical. In 1988 the National Academy of Sciences looked at ten options and recommended moving it. It took almost another decade before Congress paid for it. In January 1997 a review by North Carolina State University endorsed the move, and money followed the next year. The tower had stood since 1870 on a floating foundation of yellow pine timbers, laid in fresh water under the sand.",
          photo(0, PH_LH_2020, "Cape Hatteras Lighthouse"),
          stat("In 1988", "10 options", "Reviewed by the National Academy of Sciences, 1988: move it", NPS_LH)),
        P("In June 1999, crews lifted 4,830 tons of brick onto rails and pushed it five feet at a time. Sixty sensors watched the tower as it rolled. Twenty-three days later it stood 2,900 feet to the southwest. It cost 11.8 million dollars, and it was lit again on November 13. The keepers' houses had gone first, between February and April.",
          photo(0, PH_LH_BEFORE, "4,830 tons of brick"),
          stat("Twenty-three", "2,900 ft", "Moved southwest in 23 days, June-July 1999", NPS_LH),
          stat("It cost", "$11.8 million", "Cost of the move", "National Park Service")),
        P("Today it stands about fifteen hundred feet from the ocean again. Here is that corner of Buxton in August 1985, and this October. Just north of the old site runs Old Lighthouse Road. One of the houses that fell this February stood on it.",
          photo(0, PH_LH_PATH, "After Hurricane Isabel, September 2003"),
          m("Here is", v(BUXTON_W, compare={**CMP_BUXTON, "until": "and this"}), step("and this", places=[LIGHTHOUSE]), step("Just north", places=[BUXTON]), cut=True),
          m("One of the", v(near(-75.515, 35.262, 0.06)), cut=True)),
        P("The lighthouse got out of the way. The road beside it could not, or not easily.",
          m(0, v(BUXTON_V, places=[LIGHTHOUSE, BUXTON]))),
    ]},
    {"title": "The Only Road", "mood": "tension", "paragraphs": [
        P("Highway 12 is the only road onto Hatteras Island. Its northern gate is Oregon Inlet. The Bonner Bridge crossed it from 1963. It was designed to last about thirty years and stayed in service for fifty-six. In December 2013 the current scoured the sand around its supports so badly that it was closed for ten days, and the state ran an emergency ferry instead.",
          m(0, v(HATTERAS)),
          m("Its northern", v(OREGON_V), cut=True),
          photo("The Bonner", PH_BONNER, "The Bonner Bridge over Oregon Inlet"),
          m("In December", v({"lon": -75.548, "lat": 35.772, "span": 0.035}, places=[STUMPY]), cut=True)),  # closer on the old bridge line: OREGON_V came back 22 s later
        P("Its replacement, the Marc Basnight Bridge, opened in February 2019: 2.8 miles long, built to last a hundred years, at a reported cost of about 252 million dollars. At its highest it rises ninety feet above the inlet.",
          m(0, v({"lon": -75.55, "lat": 35.78, "span": 0.12}, date="2026-10-20/2026-11-08")),
          stat("at a reported", "$252 million", "The Marc Basnight Bridge, opened February 2019", "NCDOT; news reports")),
        P("South of the bridge the road runs along Pea Island, a wildlife refuge, with the ocean on one side and the sound on the other. In August 2011, Hurricane Irene cut through it.",
          m(0, v(near(-75.50, 35.70, 0.12))),
          m("In August", v(PEA_V), cut=True)),
        P("Near Rodanthe the road followed an eroding stretch called the S-curves. The fix was to leave the island. Since July 2022, a 2.4-mile bridge has carried the road out over Pamlico Sound and back. Reports put its cost at about 145 million dollars. The bridge skipped the S-curves, but not the rest of the road.",
          m(0, v(SCURVES_V, compare={**CMP_BRIDGE, "until": "The fix"}), step("The fix", view=SCURVES_V), step("Since July", view=SCURVES_V, places=[RODANTHE]), step("out over", view=SCURVES_V), cut=True),
          stat("Reports put", "2.4 miles", "The Rodanthe 'Jug Handle' Bridge, opened July 2022", "NCDOT", "About $145 million, as reported")),
        P("This autumn showed what is left. On September 24 a nor'easter washed out about a thousand feet of road near the Pea Island Visitor Center. For the first time since December 2013, the state ran an emergency ferry from Rodanthe to Stumpy Point on the mainland.",
          m(0, v(PEA_V, places=[VISITOR])),
          m("For the first", v(FERRY_V, places=[RODANTHE, STUMPY], routes=[FERRY]), cut=True)),
        P("The road reopened on October 3. On October 19 the ocean closed it again, this time damaging more than twelve hundred feet of pavement. The ferry came back, and by October 26 it had carried 1,451 vehicles and 2,416 passengers, around the clock. Each ferry takes only a few vehicles, and the state asked drivers for patience. The county ran park-and-ride buses at both ends. Visitors were ordered off the island.",
          m(0, v(PEA_V, places=[VISITOR])),
          stat("damaging", "1,200+ ft", "Pavement damaged near the Pea Island Visitor Center, October 2026", NCDOT),
          stat("The ferry", "1,451 vehicles", "Carried by the emergency ferry by October 26", NCDOT)),
        P("It reopened on October 29 with one lane, controlled by flaggers, behind rebuilt dunes and sandbags. The state is now discussing moving a one-mile section west. Here is that spot in August 1985, and this October. We measured about a hundred metres of retreat here since 1985. On an island this narrow, west does not go very far.",
          m(0, v(PEA_V)),
          m("Here is", v(PEA_W, compare={**CMP_PEA, "until": "and this"}), step("and this", places=[VISITOR]), step("We measured"), cut=True),
          stat("On an island", "~100 m", "Shoreline retreat at the Pea Island Visitor Center, 1985 to 2026", OWN, "About 330 feet")),
    ]},
    {"title": "Two Villages", "mood": "tension", "paragraphs": [
        P("In December 2024 the Park Service sent Congress a report on its erosion hotspots. Rodanthe and Buxton are where the houses have fallen.",
          m(0, v(HATTERAS, places=[RODANTHE, BUXTON]))),
        P("A Park Service scientist put the average loss at Rodanthe at nine to twelve feet a year between 1998 and 2022. Our own measurement since 1985 lands in the same range.",
          stat(0, "9-12 ft", "Average yearly shoreline loss at Rodanthe, 1998-2022", "Cape Hatteras National Seashore scientist, via WRAL"),
          m("Our own", v(RODANTHE_V, places=[RODANTHE]), cut=True)),
        P("In Rodanthe, Richard Foreman's house stands about twenty feet up on stilts. It was a rental. Now it stands in the middle of the beach. Four neighbouring houses have fallen in the last two years, NPR reported in September. Inside, he said, it looked as if they had just left for dinner, with everything still there. NPR counted at least half a dozen homes here in imminent danger.",
          m(0, v(RODANTHE_V)),
          photo("Four", PH_SITE, "Rodanthe, the morning after a collapse, March 2023")),
        P("In Buxton, Michael McDaniel bought his house in 2011 for about half a million dollars. When he bought it, there were about two hundred and fifty feet of dune in front of it, NPR reported. If it falls, his flood insurance would pay up to 250,000 dollars for the house and up to 100,000 for what is inside. More than ninety percent of the houses that fell in Dare County since 2020 were assessed at over 250,000 dollars, NPR found.",
          m(0, v(BUXTON_V, places=[BUXTON])),
          stat("about two", "~250 ft", "Dune in front of one Buxton house when it was bought in 2011", NPR),
          m("If it falls", v(near(-75.515, 35.262, 0.06)), cut=True)),
        P("The Park Service keeps the list by address. In two days this February it was 46201, 46215 and 46219 Tower Circle Road and 46285 Old Lighthouse Road, all in Buxton. In June it was 46000 Ocean Drive.",
          m(0, v(BUXTON_V, places=[BUXTON])),
          stat("In June", "46000 Ocean Drive", "Buxton, collapsed overnight, 2 June 2026", NPS)),
        P("When a house falls, the debris spreads along the beach. The Park Service says owners' cleanups have not always restored the beach, so it cleans up and seeks the cost back. NPR counted more than 480 tons of debris collected in eighteen months. After one Rodanthe house fell in March 2025, crews hauled about seventy truckloads off the beach in three days.",
          photo(0, PH_DEBRIS, "Park Service crews collect debris, Rodanthe"),
          stat("NPR counted", "480+ tons", "Debris the Park Service collected in 18 months", NPR)),
        P("So why are these houses left standing until they fall?",
          m(0, v(RODANTHE_V))),
    ]},
    {"title": "Paid to Wait", "mood": "tension", "paragraphs": [
        P("Most flood insurance for American homes comes from one place: FEMA's National Flood Insurance Program. And it pays when a house collapses, not before.",
          stat(0, "After, not before", "When federal flood insurance pays for a house on a collapsing shore", NPR)),
        P("Foreman told NPR that if the insurer settled with him now, he would have the house torn down tomorrow. Waiting, he said, means it will fall in a storm and be scattered for miles.",
          m(0, v(RODANTHE_V, places=[RODANTHE])),
          photo("Waiting", PH_COLLAPSE)),
        P("Tearing a house down costs at least thirty thousand dollars. Moving one can cost hundreds of thousands. A collapse can pay up to two hundred and fifty thousand dollars for the building and up to a hundred thousand for what is inside.",
          stat(0, "$30,000+", "The least it costs to tear a threatened house down", NPR),
          chart("Moving one", "One threatened house, in dollars", "", [["Owner pays to tear it down", 30000], ["Insurance pays on collapse: house", 250000], ["Insurance pays on collapse: contents", 100000]], NPR, highlight=1,
                reveal=["A collapse", "and up to"])),
        P("A policy analyst at the Coastal States Organization told NPR the homeowner is incentivized to wait for collapse and get a payout. In Buxton, McDaniel put it this way: if it is teetering, you have to sit and wait for it to fall in the ocean.",
          m(0, v(BUXTON_V))),
        P("It was not always like this. From 1988 to 1994, a rule called Upton-Jones paid owners to move or demolish houses that were about to fall. More than four hundred homes in twenty-seven states were moved or torn down under it. Congress repealed it in 1994. Lawmakers worried about the cost; one said that policyholder benefits come at the government's expense.",
          stat("More than", "400+ homes", "Moved or demolished under Upton-Jones, 1988-1994, in 27 states", NPR),
          m("Congress", v(USA_V)), ),
        P("At a 1990 hearing, the man who handled those claims in North Carolina said many owners had repaired their houses instead, to rent them out another season. He saw no particular incentive for early action.",
          m(0, v(HATTERAS))),
        P("A bipartisan bill introduced in 2025 would bring a version of it back, capped at two hundred and fifty thousand dollars. As of September it was stalled in the House. FEMA says it cannot change the rule without Congress, and it did not answer NPR's question about what the waiting costs taxpayers.",
          stat(0, "Since 2025", "A bill to pay before collapse, stalled in the House", NPR),
          m("FEMA says", v(USA_V)), ),
        P("Dare County's manager put the arithmetic simply. It is money they are going to spend either way, he told NPR, and it is cheaper to tear it down.",
          m(0, v(BUXTON_V, places=[BUXTON]))),
        P("The waiting has a public cost too. NPR counted more than half a million dollars of federal and county cleanup spending since 2020. A longtime flood insurance agent told NPR that collapses leave a legacy of hazard on the beach, and that it is almost impossible to get everything.",
          stat(0, "$500,000+", "Federal and county cleanup spending since 2020", NPR),
          photo("A longtime", PH_DEBRIS, "Collecting debris, Rodanthe")),
        P("Chellie Pingree, a congresswoman from Maine, told NPR that people should not have to wait for their home to collapse into the water before they can get help.",
          m(0, v(USA_V))),
    ]},
    {"title": "Sand or Retreat", "mood": "calm", "paragraphs": [
        P("There is another answer: bring the beach back. Between June 2017 and February 2018, Dare County pumped 2.6 million cubic yards of sand onto 2.9 miles of Buxton's shore. NPR reported that the earlier sand lasted less than three years.",
          m(0, v(BUXTON_V)),
          stat("Dare County", "2.6 million yd³", "Sand pumped onto 2.9 miles of Buxton beach, 2017-2018", "Dare County; Island Free Press")),
        P("Our measurement shows it. Buxton's shoreline jumped about thirty metres out to sea. By 2024 the gain was gone, and the shore sat behind its 2014 line again.",
          chart(0, "Buxton shoreline, metres inland of 1985", " m", [["2014", 72], ["2018", 39], ["2022", 59], ["2024", 81], ["2026", 86]], OWN, highlight=1,
                reveal=["By 2024"])),
        P("A second round followed in 2022, with 1.2 million more cubic yards in Buxton, under a contract of about 26 million dollars for Buxton and Avon together. Now the county plans a bigger one for Buxton and Avon: up to about sixty-five million dollars if FEMA pays its share of about thirty million, or about forty-five million without it. Most of the money comes from two percent of the county's six percent tax on vacation stays, and the county wants a reserve of one and a half times a year of that tax.",
          m(0, v(near(-75.51, 35.31, 0.12), places=[BUXTON, AVON])),
          stat("up to about", "$45-65 million", "Planned Buxton and Avon beach nourishment, 2026", IFP, "About $30.4 million of it expected from FEMA")),
        P("Rodanthe has no such project. A study put its cost at about forty million dollars, and the county says the village's tax base is too small to carry it.",
          m(0, v(RODANTHE_V, places=[RODANTHE])),
          stat("A study", "~$40 million", "Estimated cost of nourishing Rodanthe's beach", IFP)),
        P("A scientist at East Carolina University told NPR that beach nourishment is temporary: you are buying sand to buy time. There is no way to maintain homes where they currently are, he said. The only solution is to back off the front line.",
          m(0, v(BUXTON_V))),
        P("That has started, house by house. In 2023 the Park Service bought two houses on East Beacon Road in Rodanthe, with conservation money and no taxpayer dollars, and paid 72,500 dollars to remove them.",
          m(0, v(RODANTHE_V)),
          stat("and paid", "$72,500", "To remove two houses the Park Service bought in Rodanthe, 2023", NPS)),
        P("On October 30, more than a million dollars from FEMA and the state was approved to buy three more houses in Rodanthe, if the owners agree. One is a local landmark called the Black Pearl, threatened by erosion for more than a decade. If the sales go through, the land will stay open beach.",
          stat(0, "$1 million+", "To buy and demolish three Rodanthe houses: FEMA $793,000, state $258,000", PRE),
          m("If the sales", v(RODANTHE_V, places=[RODANTHE]), cut=True)),
        P("Not every stretch is retreating. At Avon, between the two villages, our measurement shows the shoreline about where it was in 1985.",
          m(0, v(AVON_V, places=[AVON])),
          stat("our measurement", "~0 m", "Shoreline change at Avon, 1985 to 2026", OWN)),
    ]},
    {"title": "Who Decides", "mood": "calm", "paragraphs": [
        P("In 1999 the lighthouse question ended with one decision: move it. From the Academy's report to the move took eleven years. A quarter of a century later it still stands, about fifteen hundred feet from the water.",
          photo(0, PH_LH_NOW),
          m("A quarter", v(BUXTON_V, places=[LIGHTHOUSE]), cut=True)),
        P("The road and the houses face the same question, asked again after every storm: hold the line with sand and sandbags, or move back while there is still somewhere to go.",
          m(0, v(PEA_V, places=[VISITOR])),
          m("or move back", v(HATTERAS), cut=True)),
        P("Moving back is not free either. It means buying out owners, paying for demolition, and losing a beach town's tax base one lot at a time. Holding the line means pumping sand every few years, and the county's own finance chief says those projects will cost more as they go.",
          m(0, v(RODANTHE_V)),
          m("Holding the", v(BUXTON_V), cut=True)),
        P("The Park Service expects more than a hundred homes on these islands to be at risk within a decade. At Rodanthe, our line has moved about thirty metres since 2022 alone. We will keep measuring this shore from orbit, year after year.",
          stat(0, "100+ homes", "At risk on North Carolina barrier islands within a decade (Park Service)", NPR),
          m("We will keep", v(RODANTHE_W, compare={**CMP_RODANTHE, "hold": 0.4}), cut=True)),
        P("So who should decide when a house comes down: the owner, the county, or an insurer that pays only after the ocean has decided?",
          m(0, v(OBX, places=[RODANTHE, BUXTON])),
          ask=("So who", "Owner, county or insurer: who decides?")),
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


# Filler pictures. Every map view is generated once (a point along that shore x a frame width), so no crop comes back;
# a photo is used at most PHOTO_MAX times and never within PHOTO_GAP seconds of its last use (ep 11 v1 cycled five
# photos 8-12 times each). A village's photos only go under sentences about that village.
SEC_WORD = 0.43
PHOTO_MAX, PHOTO_GAP = 3, 110.0  # gap in estimated seconds; real speech runs faster than SEC_WORD (v2 repeats came back 35-54 s apart)
SHORES = {
    "rodanthe": [(-75.462, 35.575), (-75.465, 35.585), (-75.467, 35.592), (-75.470, 35.600), (-75.473, 35.609), (-75.476, 35.617), (-75.479, 35.626)],
    "buxton": [(-75.527, 35.248), (-75.521, 35.257), (-75.516, 35.266), (-75.511, 35.276), (-75.507, 35.288), (-75.503, 35.300),
               (-75.540, 35.244), (-75.555, 35.240), (-75.536, 35.262), (-75.545, 35.270)],
    "avon": [(-75.503, 35.330), (-75.506, 35.342), (-75.509, 35.354), (-75.512, 35.366)],
    "pea": [(-75.480, 35.680), (-75.486, 35.694), (-75.491, 35.708), (-75.497, 35.722), (-75.505, 35.737), (-75.514, 35.750), (-75.524, 35.762)],
    "island": [(-75.47, 35.62), (-75.49, 35.52), (-75.51, 35.42), (-75.55, 35.27), (-75.62, 35.24), (-75.70, 35.22)],
}
SPANS = {"island": [0.14, 0.22, 0.3, 0.18], None: [0.05, 0.07, 0.09, 0.06, 0.08, 0.1]}
LABELS = {"rodanthe": "Rodanthe", "buxton": "Buxton", "avon": "Avon", "pea": "Pea Island", "island": "Hatteras Island"}
PHOTOS = {
    "houses": [(PH_DEBRIS2, "Debris after a collapse, Ocean Drive, Rodanthe"), (PH_OCEAN_A, "After a collapse, Ocean Drive, Rodanthe"),
               (PH_DEBRIS4, "Park Service crews, Rodanthe"), (PH_OCEAN_B, "Ocean Drive, Rodanthe"),
               (PH_DEBRIS5, "Searching for debris north of the Rodanthe Pier"), (PH_TRUCK, "North of the Rodanthe Pier"),
               (PH_DEBRIS6, "Collected debris, Rodanthe"), (PH_OCEAN_C, "Ocean Drive, Rodanthe"), (PH_CREW, "Collecting debris, Rodanthe"),
               (PH_DEBRIS3, "Ocean Drive, Rodanthe"), (PH_VOL, "Volunteers clean the beach, Rodanthe"), (PH_OCEAN_D, "Ocean Drive, Rodanthe"),
               (PH_VOL2, "Beach cleanup, Rodanthe")],
    "lighthouse": [(PH_LH_NOW, "Cape Hatteras Lighthouse"), (PH_LH_2020, "Cape Hatteras Lighthouse, 2020"),
                   (PH_LH_SHADOW, "Cape Hatteras Lighthouse"), (PH_LH_BEFORE, "Cape Hatteras Lighthouse")],
    "sand": [(PH_NOURISH, "Pumping sand north of Buxton, July 2022")],
}
VIEW_PLACE = {"houses": "rodanthe", "lighthouse": "buxton", "sand": "buxton"}
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
FAMILY = {PH_OCEAN_A: "ocean", PH_OCEAN_B: "ocean", PH_OCEAN_C: "ocean", PH_OCEAN_D: "ocean"}


def filler(group, t):
    for name, label in PHOTOS.get(group, []):
        fam = FAMILY.get(name, name)
        uses = photo_uses.get(fam, [])
        if len(uses) < PHOTO_MAX and all(t - u >= PHOTO_GAP for u in uses):
            photo_uses.setdefault(fam, []).append(t)
            return pic(name, label)
    return next_view(VIEW_PLACE.get(group, group))


def village(text):
    hits = {k: len(re.findall(k, text, re.I)) for k in ("Rodanthe", "Buxton", "Avon")}
    return max(hits, key=hits.get).lower() if any(hits.values()) else None


def topic_of(text, chapter):
    if re.search(r"lighthouse|Lighthouse(?! Road)|tower|groin|seawall|Academy|brick|1870|1999|keepers", text):
        return "lighthouse"
    if re.search(r"nourish|sand onto|cubic|pumped|pumping", text):
        return "sand"
    if re.search(r"Pea Island|Oregon|Bonner|Basnight|ferry|Stumpy|nor'easter|Visitor Center|sandbags|one lane", text):
        return "pea"
    if re.search(r"Avon", text):
        return "avon"
    if re.search(r"debris|collapse|fall|fell|insur|payout|FEMA|torn down|tear|stilts|rental|house", text):
        return "houses" if village(text) in (None, "rodanthe") else village(text)
    if re.search(r"Buxton", text):
        return "buxton"
    if re.search(r"Rodanthe|S-curves|Jug|Pamlico", text):
        return "rodanthe"
    return None


CHAPTER_DEFAULT = {"The Front Row": "houses", "Islands That Walk": "island", "The Lighthouse That Moved": "lighthouse",
                   "The Only Road": "pea", "Two Villages": "rodanthe", "Paid to Wait": "houses", "Sand or Retreat": "buxton",
                   "Who Decides": "island"}


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
    if t == "houses" and village(para_text) not in (None, "rodanthe") and village(sentence) is None:
        t = village(para_text)  # "the houses" in a paragraph about Buxton are Buxton's
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
    "title": "The Outer Banks",
    "voice": "am_michael",
    "music": "procedural",
    "map_style": "satellite",
    "look": "none",
    "sources": ["episodes/outer-banks/research.md and factcheck.md", "Landsat data courtesy of the U.S. Geological Survey"],
    "thumbnail": {"text": "PAID TO WAIT"},  # final cover: hand-made from the NPS photo, see PLAN.md
    "chapters": chapters,
    "youtube": {
        "title": "32 Houses Fell Into the Atlantic. Insurance Paid Only After",
        "description": "Since 2020, 32 houses have collapsed into the Atlantic on Cape Hatteras National Seashore, 20 in Buxton and 12 in Rodanthe. We measured the shoreline in Landsat images from 1985 to 2026: at Rodanthe it moved about 155 metres inland. We follow the lighthouse that was moved in 1999, Highway 12 and its bridges and closures in autumn 2026, the flood-insurance rule that pays only after a house falls, and the choice between pumping sand and moving back.",
        "tags": ["Outer Banks", "Rodanthe", "Buxton", "Hatteras Island", "coastal erosion", "houses collapse", "NC 12", "Cape Hatteras Lighthouse", "flood insurance", "FEMA", "beach nourishment", "satellite images", "Landsat"],
        "pinned_comment": "Owner, county or insurer: who should decide when a house on a collapsing shore comes down?",
    },
}
out = HERE / "script.json"
out.write_text(json.dumps(script, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
words = sum(len(p["text"].split()) for c in chapters for p in c["paragraphs"])
print(f"{words} words, {len(chapters)} chapters, {sum(len(p['shots']) for c in chapters for p in c['paragraphs'])} shots")
