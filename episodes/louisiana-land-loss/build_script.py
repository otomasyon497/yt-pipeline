"""Builds script.json for louisiana-land-loss (beats are easier to review here than in the JSON).  python build_script.py

Sources: research.md + verification.md (USGS SIM 3381, CPRA releases, WWNO / Louisiana Illuminator, ASCE, Louisiana OCD,
Columbia/CPI, EarthRights, The Lens, InvestigateTV, NASA Earth Observatory, Jankowski 2017, LSU) and our own Landsat land
measurement (tools/louisiana_landloss.py -> landloss.json). Coordinates: OpenStreetMap, checked on the storyboard.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
AFTER = "2026-10-01/2026-11-10"  # the clear autumn window (summers are stormy)
LS = "landsat"
# Single clear days from the Sentinel-2 archive (2026-11-12): composites left seams in the Jakarta episode.
LA_DAY = "2026-10-13/2026-10-13"    # tiles 15RXN, 15RYN, 16RBT, 16RCT: 0 % cloud, one pass along the whole coast
NOLA_DAY = "2026-10-23/2026-10-23"  # tile 16RBU, 0 % cloud


def day_for(view):
    lon, lat, span = view["lon"], view["lat"], view["span"]
    if span > 2:
        return None
    if lat > 29.8 and lon > -90.3:
        return NOLA_DAY
    return LA_DAY


LOUISIANA = {"lon": -90.9, "lat": 29.9, "span": 4.5}
USA_GULF = {"lon": -90.5, "lat": 31.0, "span": 14}
COAST = {"lon": -90.4, "lat": 29.45, "span": 2.6}
IJC_W = {"lon": -90.49, "lat": 29.405, "span": 0.14}  # Landsat wipe
IJC_V = {"lon": -90.487, "lat": 29.40, "span": 0.05}
ROAD_V = {"lon": -90.48, "lat": 29.42, "span": 0.04}
NEWISLE_V = {"lon": -90.776, "lat": 29.711, "span": 0.04}
BARATARIA_W = {"lon": -89.98, "lat": 29.53, "span": 0.3}
MBSD_V = {"lon": -89.955, "lat": 29.645, "span": 0.05}
BIRDSFOOT_W = {"lon": -89.25, "lat": 29.13, "span": 0.4}
VENICE_V = {"lon": -89.36, "lat": 29.28, "span": 0.06}
NEPTUNE_V = {"lon": -89.52, "lat": 29.375, "span": 0.08}
FOURCHON_V = {"lon": -90.19, "lat": 29.12, "span": 0.08}
LEEVILLE_V = {"lon": -90.21, "lat": 29.25, "span": 0.06}
GRANDISLE_V = {"lon": -89.99, "lat": 29.235, "span": 0.08}
WAXLAKE_W = {"lon": -91.38, "lat": 29.48, "span": 0.3}
WAXLAKE_V = {"lon": -91.445, "lat": 29.50, "span": 0.08}


def near(lon, lat, span=0.05):
    return {"lon": lon, "lat": lat, "span": span}


def place(name, lon, lat, label=None, kind="site", icon=None):
    d = {"name": name, "lon": lon, "lat": lat, "kind": kind, "label": label if label is not None else name}
    if icon:
        d["icon"] = icon
    return d


IJC = place("Isle de Jean Charles", -90.4886, 29.3992, "Isle de Jean Charles", "city")
POINTE = place("Pointe-aux-Chenes", -90.5534, 29.4977, "Pointe-aux-Chenes", "city")
NEWISLE = place("The New Isle", -90.776, 29.711, "The New Isle", "city")
HOUMA = place("Houma", -90.7195, 29.5958, "Houma", "city")
MBSD = place("Mid-Barataria", -89.9626, 29.6482, "Mid-Barataria diversion site", "site")
MYRTLE = place("Myrtle Grove", -89.9512, 29.6372, "Myrtle Grove", "site")
WILLS = place("Wills Point", -90.0059, 29.7469, "Mid-Breton site", "site")
VENICE = place("Venice", -89.3587, 29.2791, "Venice: end of the road", "city")
HEAD = place("Head of Passes", -89.2509, 29.1517, "Head of Passes", "site")
LOUTRE = place("Pass a Loutre lighthouse", -89.0371, 29.1901, "Pass a Loutre lighthouse", "site")
NEPTUNE = place("Neptune Pass", -89.51184, 29.37167, "Neptune Pass", "site")
FOURCHON = place("Port Fourchon", -90.1892, 29.1232, "Port Fourchon", "port")
LEEVILLE = place("Leeville", -90.2108, 29.2505, "Leeville", "city")
GOLDEN = place("Golden Meadow", -90.2601, 29.3791, "Golden Meadow", "city")
GRANDISLE = place("Grand Isle", -89.9873, 29.2366, "Grand Isle", "city")
WAXLAKE = place("Wax Lake Delta", -91.4463, 29.5010, "Wax Lake Delta", "site")
ATCH = place("Atchafalaya Delta", -91.3025, 29.4535, "Atchafalaya Delta", "site")
MORGAN = place("Morgan City", -91.2068, 29.6994, "Morgan City", "city")
NOLA = place("New Orleans", -90.0629, 29.9575, "New Orleans", "city")
LA23 = {"from": [-90.05, 29.91], "to": [-89.3587, 29.2791], "mode": "line", "seconds": 4, "label": "Highway 23, 72 miles",
        "via": [[-89.99, 29.80], [-89.96, 29.65], [-89.85, 29.55], [-89.73, 29.47], [-89.60, 29.40], [-89.50, 29.35], [-89.42, 29.30]]}
MOVE = {"from": [-90.4886, 29.3992], "to": [-90.776, 29.711], "mode": "line", "seconds": 3, "label": "About 40 miles"}
LA1 = {"from": [-90.26, 29.38], "to": [-90.19, 29.12], "mode": "line", "seconds": 3, "label": "LA-1",
       "via": [[-90.23, 29.32], [-90.21, 29.25], [-90.20, 29.18]]}

CMP_IJC = {"before": "1985-09-14/1985-09-18", "after": "2026-10-10/2026-10-28", "source": LS, "seconds": 1.6, "label_before": "1985", "label_after": "2026"}
CMP_BARATARIA = {"before": "1985-08-31", "after": AFTER, "source": LS, "seconds": 1.6, "label_before": "1985", "label_after": "2026"}
CMP_BIRDSFOOT = {"before": "1985-10-01/1985-11-30", "after": AFTER, "source": LS, "seconds": 1.8, "label_before": "1985", "label_after": "2026"}
CMP_WAXLAKE = {"before": "1984-10-01/1984-10-31", "after": AFTER, "source": LS, "seconds": 2.0, "label_before": "1984", "label_after": "2026"}


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


USGS = "USGS, Couvillion et al., SIM 3381, 2017"
CPRA = "Coastal Protection and Restoration Authority"
WWNO = "WWNO / Louisiana Illuminator, Jul 18, 2025"
OCD = "Louisiana Office of Community Development"
OWN = "Our measurement, Landsat 5, 8 and 9"
NASA_EO = "NASA Earth Observatory"

PH_LEVEE = "File:Grand Isle Louisiana Levee Repair Work, January 2023 - 01.jpg"  # PD, USACE
PH_IDA = "File:Grand Isle - 10-6-21 - 002.jpg"  # CC BY 2.0, Louisiana Sea Grant, five weeks after Ida
PH_IDA2 = "File:Grand Isle - 10-6-21 - 017.jpg"  # CC BY 2.0
PH_DELTA_ASTER = "File:Mississippi River Delta (ASTER).jpg"  # PD, NASA/METI
PH_WAXLAKE = "File:Sea Grant - Wax Lake Outlet.5.jpg"  # CC BY 2.0
PH_PLANT = "File:Wetland Days - Port Sulphur Louisiana 5 November 2021 - 01.jpg"  # CC BY 2.0
PH_BARATARIA = "File:Barataria Bay (95-054-2).jpeg"  # PD, NASA Stennis 1995

chapters = [
    {"title": "Don't Do It", "mood": "tension", "paragraphs": [
        P("In 2016, the United States government paid to move a whole community away from the sea, in what was called the first federally funded move of its kind. The community lived on a narrow island at the end of a single road in southern Louisiana: Isle de Jean Charles.",
          m(0, v(USA_GULF, places=[IJC])), m("southern Louisiana", v(COAST, places=[IJC])),
          m("Isle de Jean Charles", v(IJC_V, places=[IJC]), cut=True)),
        P("This is the island from orbit in 1985. And this is the same place this autumn. By the state's count, the land around it has shrunk from more than twenty-two thousand acres to about three hundred and twenty. We measured it ourselves. In a box around the island, land and marsh above water fell from about three thousand three hundred hectares in 1985 to about one thousand eight hundred this October. Nearly half is gone.",
          m(0, v(IJC_W, compare={**CMP_IJC, "until": "And this"}), step("And this", places=[IJC]), cut=True),
          stat("the land around", "22,000 -> 320 acres", "Land around Isle de Jean Charles, by the state's count", OCD),
          m("We measured", v(near(-90.49, 29.40, 0.1), places=[IJC]), cut=True),
          stat("from about three", "-45%", "Land and marsh above water in a box around the island, 1985 -> 2026", OWN, "About 3,300 ha -> 1,800 ha")),
        P("Thirty-seven families took the deal and moved about forty miles inland, to a new subdivision built for them in the sugar-cane fields. One of them, Amy Handon, told The New York Times this year what she would say to the next town offered the same thing.",
          m(0, v(IJC_V, places=[IJC], routes=[MOVE])),
          m("to a new", v(NEWISLE_V, places=[NEWISLE]), cut=True),
          m("One of them", v(near(-90.77, 29.705, 0.035)), cut=True)),
        P("Not everyone left. Chris Brunet stayed on the island. I never expected that relocation was going to happen in my lifetime, he told Floodlight last year.",
          m(0, v(near(-90.49, 29.395, 0.04), places=[IJC])),
          clip("I never", "\"I never expected that relocation was going to happen in my lifetime.\"", "Chris Brunet, Isle de Jean Charles, to Floodlight, 2025", highlight="in my lifetime"),
          m("he told Floodlight", v(near(-90.485, 29.405, 0.04)), cut=True)),
        P("Don't do it.",
          clip(0, "\"This was supposed to be a model.\" ... \"Don't do it.\"", "Amy Handon, former Isle de Jean Charles resident, to The New York Times, 2026", highlight="Don't do it.")),
        P("Louisiana has lost about two thousand square miles of land since 1932, nearly the size of Delaware. It had a plan to let its own river build some of it back. In 2025 it cancelled that plan. Why would a state do that?",
          m(0, v(COAST)),
          stat("about two thousand", "2,006 sq mi", "Coastal Louisiana land lost, 1932-2016 (about a quarter of it)", USGS),
          m("It had a plan", v(near(-90.0, 29.66, 0.12), places=[MBSD]), cut=True),
          ask=("Why would", "Why cancel the cure?")),
    ]},
    {"title": "The Cancelled Cure", "mood": "tension", "paragraphs": [
        P("The plan was called the Mid-Barataria Sediment Diversion. Here, on the west bank of the Mississippi below New Orleans, the state was building a gate in the levee, three hundred feet wide.",
          m(0, v(near(-90.0, 29.8, 0.5), places=[NOLA, MBSD])),
          m("Here, on", v(MBSD_V, places=[MBSD]), cut=True)),
        P("Open it, and the river would carry its mud into Barataria Bay, the way it did for thousands of years before the levees. The state's own models said it would build about twenty square miles of land over fifty years. Critics said far less. Our own images show how much it needs it: in a box over the bay, sixteen percent less land and marsh than in 1990, and that box includes the river and its leveed banks, which do not change.",
          m(0, v(BARATARIA_W), step("the way", places=[place("Barataria Bay", -89.97, 29.51, "Barataria Bay", "sea")]), cut=True),
          m("The state's own", v(near(-89.95, 29.56, 0.15)), cut=True),
          stat("about twenty", "~20 sq mi", "Land the diversion was modelled to build in 50 years (critics: far less)", WWNO),
          m("Our own images", v(near(-90.03, 29.58, 0.25)), cut=True),
          stat("sixteen percent", "-16%", "Land and marsh in a box over Barataria Bay, 1990 -> 2026", OWN)),
        P("Construction began in 2023. The price rose to nearly three billion dollars, most of it from the settlement over the 2010 Deepwater Horizon oil spill.",
          m(0, v(near(-89.96, 29.65, 0.035), places=[MBSD])),
          m("most of it", v(near(-90.03, 29.56, 0.09)), cut=True)),
        P("The idea was not new. The state first considered it in 1984, and its legislature approved it in 2017. The Barataria Basin alone had lost about four hundred and thirty square miles of land since 1932. A fishing guide, Ryan Lambert, told The Lens the estuary is literally eating itself.",
          m(0, v(near(-89.97, 29.60, 0.2))),
          stat("about four hundred", "~432 sq mi", "Land lost in the Barataria Basin since 1932", "BTNEP, via ASCE, Sep 2026"),
          clip("A fishing guide", "\"The estuary is literally eating itself.\"", "Ryan Lambert, fishing guide, to The Lens, May 13, 2025", highlight="literally eating itself")),
        P("But fresh river water and mud would also change the bay itself, and the oyster and shrimp towns that live on its salt water. They fought the project in court and on the steps of the state Capitol. Governor Jeff Landry said its damage to the fisheries would break our culture.",
          m(0, v(near(-89.92, 29.50, 0.12))),
          m("They fought", v(near(-89.70, 29.48, 0.08)), cut=True)),
        P("Four hundred million dollars had been set aside to soften the damage to the fisheries. It was not enough to end the fight. In April 2025 the state's coastal chairman paused the work, and weeks later the Army Corps suspended a permit.",
          m(0, v(near(-89.88, 29.45, 0.09))),
          stat("set aside", "$400 million", "Set aside to soften Mid-Barataria's impact on fisheries", WWNO),
          m("In April 2025", v(near(-89.96, 29.64, 0.06), places=[MBSD]), cut=True)),
        P("On July 17, 2025, the state ended it. The authority's chairman, Gordon Dove, said they had made the difficult decision to terminate the Mid-Barataria project. Six hundred and eighteen million dollars had already been spent. A month later, Dove wrote that the decision was not made lightly.",
          m(0, v(near(-89.962, 29.648, 0.04), places=[MBSD])),
          clip("The authority's", "\"...we've made the difficult decision to terminate the Mid-Barataria project.\"", "Gordon Dove, chairman, " + CPRA + ", Jul 17, 2025", highlight="terminate the Mid-Barataria project"),
          m("to terminate", v(near(-89.95, 29.66, 0.05)), cut=True),
          stat("Six hundred", "$618.5 million", "Already spent on Mid-Barataria when it was cancelled", CPRA + ", Jul 17, 2025")),
        P("The head of the state's oyster task force, Mitch Jurisich, celebrated. We killed the beast that was going to kill us, he said, and that's the best.",
          m(0, v(near(-89.68, 29.43, 0.06))),
          clip("We killed", "\"...we killed the beast that was going to kill us, and that's the best.\"", "Mitch Jurisich, Louisiana Oyster Task Force, to WWNO, Jul 2025", highlight="we killed the beast"),
          m("and that's the best", v(near(-89.66, 29.45, 0.05)), cut=True)),
        P("James Karst, of the Coalition to Restore Coastal Louisiana, saw it differently. The need has not changed, he said. There's only one thing that has changed, and that is the political landscape.",
          m(0, v(near(-90.05, 29.55, 0.1))),
          clip("The need", "\"The need has not changed. There's only one thing that has changed and that is the political landscape.\"", "James Karst, Coalition to Restore Coastal Louisiana, to WWNO, Jul 2025", highlight="The need has not changed"),
          m("There's only one", v(near(-90.08, 29.58, 0.07)), cut=True)),
        P("Amanda Moore, of the National Wildlife Federation, went further. We needed Mid-Barataria, frankly, many decades ago.",
          m(0, v(near(-90.0, 29.62, 0.08))),
          clip("We needed", "\"We needed Mid-Barataria, frankly, many decades ago.\"", "Amanda Moore, National Wildlife Federation, to WWNO, Jul 2025", highlight="many decades ago")),
        P("Kristi Trail, an engineer who leads the Pontchartrain Conservancy, told the American Society of Civil Engineers: The what went wrong is purely politics.",
          m(0, v(near(-89.97, 29.66, 0.045))),
          clip("The what", "\"The 'what went wrong' is purely politics.\"", "Kristi Trail, to ASCE Civil Engineering Source, Sep 2026", highlight="purely politics")),
        P("Three months later its sister project on the east bank, Mid-Breton, was cancelled too. To understand why the river matters so much, look at how this coast was made, and how it is coming apart.",
          m(0, v(near(-90.0, 29.75, 0.08), places=[WILLS])),
          m("look at how", v(COAST), cut=True)),
    ]},
    {"title": "How a Delta Disappears", "mood": "curious", "paragraphs": [
        P("For thousands of years the Mississippi built this land. Every spring it flooded, spread its mud across the marsh, and every few centuries it jumped to a new course and built a new lobe of delta.",
          m(0, v(LOUISIANA)), photo("every few", PH_DELTA_ASTER, "The Mississippi's Bird's Foot delta, NASA ASTER")),
        P("After the great flood of 1927, the river was walled in by levees. Its mud now shoots past the marsh and drops off the edge of the continental shelf.",
          m(0, v(near(-89.9, 29.85, 0.4), places=[NOLA])),
          m("drops off", v(BIRDSFOOT_W, places=[HEAD]), cut=True)),
        P("In 2013, NOAA's chart office retired thirty-one place names in Plaquemines Parish, bays and bayous that no longer existed. Yellow Cotton Bay. English Bay. Bay Jacquin. They had become open water.",
          m(0, v(near(-89.75, 29.45, 0.3))),
          m("Yellow Cotton", v(near(-89.68, 29.40, 0.1)), cut=True),
          m("They had become", v(near(-89.62, 29.37, 0.08)), cut=True)),
        P("Upstream, tens of thousands of dams hold back more sediment. And across the marsh, oil and gas companies dredged canals to reach their wells. One study counted more than thirty-five thousand wells on land in coastal Louisiana.",
          m(0, v(near(-90.3, 29.45, 0.2))),
          m("dredged canals", v(near(-90.35, 29.38, 0.08)), cut=True),
          stat("more than thirty-five", "35,000+", "Oil and gas wells on land in coastal Louisiana", "Turner & McClenachan, 2018")),
        P("In one basin, Barataria, a 2023 study blamed about forty percent of the loss on the levees, about forty percent on oil and gas extraction, and about twenty percent on dams.",
          m(0, v(near(-90.02, 29.55, 0.25))),
          chart("blamed", "What drove land loss in the Barataria Basin", " %", [["Levees", 40], ["Oil and gas extraction", 40], ["Dams", 20]],
                "Edmonds et al., Nature Sustainability, 2023 (via LSU)", reveal=["about forty percent on oil", "twenty percent"], highlight=0)),
        P("The ground also sinks. Soft delta mud compacts under its own weight. A study of two hundred and seventy-four marsh sites found the water rising against the land by about twelve millimetres a year on average, several times the global rise of the sea. In the Mississippi Delta itself, the average was about thirteen.",
          m(0, v(near(-90.45, 29.35, 0.08))),
          stat("about twelve", "~12 mm a year", "Water rising against the land, average of 274 marsh sites", "Jankowski, Tornqvist & Fernandes, Nature Communications, 2017")),
        P("And then come the hurricanes. Every big storm tears away marsh that was already weak.",
          m(0, v(near(-90.1, 29.25, 0.15), places=[GRANDISLE])), photo("Every big", PH_IDA, "Grand Isle, five weeks after Hurricane Ida, 2021")),
        P("A 2026 study from Louisiana State University found that where marsh keeps disappearing, it is mostly not drowning. At about eighty-two percent of those sites, it is being eaten away at the edges. Much of the loss we see, one of the authors said, has been driven by human activity.",
          m(0, v(near(-90.30, 29.30, 0.08))),
          stat("About eighty-two", "~82%", "Of sites with persistent marsh loss erode at the edges (~10% drown)", "Wilson, Quirk et al., Nature Communications, Apr 2026"),
          clip("Much of", "\"Much of the loss we see \u2014 both globally and in Louisiana \u2014 has been driven by human activity.\"", "Tracy Quirk, LSU, Apr 2026", highlight="driven by human activity"),
          m("one of the authors", v(near(-90.36, 29.34, 0.06)), cut=True)),
        P("The same study found the other side too. Where the river's mud still reaches the marsh, in the Bird's Foot, the marsh is gaining one to three centimetres a year.",
          m(0, v(near(-89.25, 29.15, 0.15))),
          stat("one to three", "+1-3 cm a year", "Marsh gain in the Bird's Foot where river sediment reaches it", "Wilson, Quirk et al., Nature Communications, Apr 2026")),
        P("Put it together and the US Geological Survey counted about two thousand square miles gone between 1932 and 2016. At the worst, a football field of land every thirty-four minutes. More recently, through 2016, one every hundred minutes.",
          m(0, v(near(-90.6, 29.4, 0.6))),
          chart("At the worst", "Louisiana land loss: one football field every...", " min", [["At the peak", 34], ["2010-16", 100]], USGS, reveal=["More recently"], highlight=1),
          m("one every hundred", v(near(-90.2, 29.4, 0.3)), cut=True)),
        P("The USGS scientist behind that count, Brady Couvillion, warned in 2017 that the slowdown came in years without a major hurricane. The most recent observations are promising, he said, but it is not clear that they will persist. Since then, three major hurricanes, Laura, Zeta and Ida, have hit this coast, and several smaller ones.",
          m(0, v(near(-90.15, 29.35, 0.2))),
          clip("The most recent", "\"The most recent observations are promising, but it is not clear that they will persist.\"", "Brady Couvillion, USGS, Jul 12, 2017", highlight="not clear that they will persist"),
          m("he said, but", v(near(-90.25, 29.45, 0.15)), cut=True),
          m("Since then", v(COAST, places=[GRANDISLE, FOURCHON]), cut=True)),
    ]},
    {"title": "The Island That Left", "mood": "calm", "paragraphs": [
        P("Back to Isle de Jean Charles. Its people, members of the Jean Charles Choctaw Nation, have lived here since about 1840. The road to the island was built across the marsh in the 1950s. Today water laps at both sides of it.",
          m(0, v(IJC_V, places=[IJC])), m("The road", v(ROAD_V, places=[POINTE]), cut=True)),
        P("When the Army Corps of Engineers drew a ninety-eight-mile hurricane levee for this parish around 2000, the island was left outside it. Protecting it, the Corps found, would cost more than moving everyone.",
          m(0, v(near(-90.55, 29.45, 0.3), places=[IJC, POINTE])),
          m("would cost", v(near(-90.50, 29.40, 0.07)), cut=True)),
        P("The former chief, Albert Naquin, put it simply. We lose land, every hurricane we lose land. And now all we have is the little bitty strip of houses and the road.",
          m(0, v(near(-90.483, 29.405, 0.035), places=[IJC])),
          clip("We lose", "\"We lose land, every hurricane we lose land. And now all we have is the little bitty strip of houses and the road.\"", "Albert Naquin, then chief, Jean Charles Choctaw Nation, to Columbia Journalism Investigations, 2022", highlight="the little bitty strip of houses and the road"),
          m("And now", v(near(-90.485, 29.395, 0.035), places=[IJC]), cut=True)),
        P("In January 2016, the Department of Housing and Urban Development awarded Louisiana nearly ninety-three million dollars, forty-eight million of it to resettle the island. The state bought five hundred and fifteen acres of farmland near Schriever for eleven point seven million.",
          stat(0, "$48.3 million", "Federal money to resettle Isle de Jean Charles (of $92.6M, Jan 2016)", "HUD; " + OCD),
          m("The state bought", v(NEWISLE_V, places=[NEWISLE]), cut=True)),
        P("The state's recovery chief, Pat Forbes, was proud of the houses. If everything on the coast was built like this, he said in 2022, everyone would be home right now.",
          m(0, v(near(-90.778, 29.713, 0.035), places=[NEWISLE])),
          clip("If everything", "\"If everything on the coast was built like this, everyone would be home right now.\"", "Pat Forbes, Louisiana Office of Community Development, to WWNO, Feb 2022", highlight="everyone would be home"),
          m("he said in 2022", v(near(-90.772, 29.716, 0.035)), cut=True)),
        P("Between 1992 and 2021, Terrebonne Parish was hit by fifteen hurricanes and two flood disasters. The tribe had wanted to rebuild its community together. The grant went to the state, which opened it to every island resident, and families began moving in August 2022. Forty-two households were eligible. Thirty-seven took part.",
          m(0, v(near(-90.78, 29.715, 0.035))),
          m("families began", v(near(-90.775, 29.708, 0.035), places=[NEWISLE]), cut=True)),
        P("The new houses had problems, residents told Floodlight: leaking doors, missing insulation. We should not have this many complaints, one of them, Kristi Naquin, said. We should not have this many problems.",
          m(0, v(near(-90.772, 29.712, 0.035))),
          clip("We should", "\"We should not have this many complaints. We should not have this many problems.\"", "Kristi Naquin, New Isle resident, to Floodlight, 2025", highlight="this many problems"),
          m("Kristi Naquin,", v(near(-90.768, 29.71, 0.035)), cut=True)),
        P("The tribe filed a civil-rights complaint with HUD, and withdrew it in January 2026, citing cuts to the department's civil-rights enforcement. Its decision to withdraw, it said, does not reflect on the validity of its allegations.",
          m(0, v(near(-90.80, 29.73, 0.06))),
          clip("Its decision", "\"Our decision to withdraw the complaint does not reflect on the validity of our allegations.\"", "Jean Charles Choctaw Nation, via EarthRights International, May 18, 2026", highlight="does not reflect on the validity"),
          m("does not reflect", v(IJC_V, places=[IJC]), cut=True)),
        P("The state's position is that it did not force anyone to leave the island. In July 2025 it handed the running of the new subdivision to a regional planning commission.",
          m(0, v(near(-90.776, 29.711, 0.05), places=[NEWISLE])),
          m("In July 2025", v(near(-90.79, 29.72, 0.07)), cut=True)),
        P("Some families stayed on the island. Chris Brunet is one of them. There's less land, he said, and more water.",
          m(0, v(near(-90.49, 29.40, 0.035), places=[IJC])),
          clip("There's less", "\"There's less land,\" he said, \"and more water.\"", "Chris Brunet, Isle de Jean Charles, to Columbia Journalism Investigations, 2022")),
    ]},
    {"title": "The End of the Road", "mood": "curious", "paragraphs": [
        P("Farther east, a different road runs out of land. Highway 23 follows the Mississippi south from New Orleans for seventy-two miles, to Venice, the last town you can drive to on the river.",
          m(0, v(near(-89.7, 29.6, 1.0), places=[NOLA, VENICE], routes=[LA23])),
          m("to Venice", v(VENICE_V, places=[VENICE]), cut=True)),
        P("Beyond it lies the Bird's Foot, the delta's newest lobe. This is it in 1985. And this is it this October. The marsh between the river's passes is breaking apart.",
          m(0, v(BIRDSFOOT_W, compare={**CMP_BIRDSFOOT, "until": "And this"}), step("And this", places=[HEAD]), cut=True),
          m("is breaking", v(near(-89.20, 29.12, 0.12), places=[LOUTRE]), cut=True)),
        P("The old Pass a Loutre lighthouse, first lit in 1855, stood about a mile inland twenty-five years ago, InvestigateTV reported this month. Now it stands several hundred feet offshore. The state wants to spend a hundred and seventy-six million dollars of oil-spill money to dredge the pass and feed the marsh again.",
          m(0, v(near(-89.04, 29.19, 0.06), places=[LOUTRE])),
          m("Now it stands", v(near(-89.037, 29.19, 0.035)), cut=True),
          stat("a hundred and seventy-six", "$176 million", "Planned Bird's Foot Delta restoration, still waiting for permits", "InvestigateTV, Nov 10, 2026")),
        P("A state scientist, Todd Baker, calls it the terminal end of the Mississippi Flyway, the route of millions of migrating birds. We don't have a delta like this anywhere else in North America, he said.",
          m(0, v(near(-89.28, 29.17, 0.1))),
          clip("We don't", "\"We don't have a delta like this anywhere else in North America.\"", "Todd Baker, " + CPRA + ", to InvestigateTV, Nov 2026", highlight="anywhere else in North America")),
        P("Then, in 2019, the river showed what it can still do. High water widened a break in the east bank below Port Sulphur. The new channel, Neptune Pass, took a large share of the river's flow at high water and began building a small delta of its own: about six million cubic yards of new sediment between 2019 and 2022, The Lens reported.",
          m(0, v(near(-89.65, 29.45, 0.25))),
          m("Neptune Pass", v(NEPTUNE_V, places=[NEPTUNE]), cut=True)),
        P("Ships need that water in the main channel, so the Army Corps planned a stone structure to throttle it. Alex Kolker, a scientist who studies it, said: I think we would all prefer a Louisiana with more land instead of less, but no one wants to see a barge run aground.",
          m(0, v(near(-89.57, 29.42, 0.05))),
          clip("I think", "\"I think we would all prefer a Louisiana with more land instead of less, but no one wants to see a barge run aground.\"", "Alex Kolker, LUMCON, to The Lens, May 13, 2025", highlight="no one wants to see a barge run aground"),
          m("but no one wants", v(near(-89.55, 29.40, 0.05)), cut=True)),
        P("Plaquemines Parish took the oil companies to court for the canals. In 2025 a jury ordered Chevron to pay seven hundred and forty-four point six million dollars. In April 2026 the US Supreme Court ruled the case can be moved to federal court. The verdict is now in limbo.",
          m(0, v(near(-89.75, 29.50, 0.2))),
          stat("seven hundred", "$744.6 million", "Jury award against Chevron, Plaquemines Parish, 2025", "Gray DC; Louisiana Illuminator, Apr 2026"),
          m("In April 2026", v(near(-89.9, 29.62, 0.15)), cut=True)),
    ]},
    {"title": "The Road to the Oil", "mood": "tension", "paragraphs": [
        P("Louisiana's attorney general, Liz Murrill, said it doesn't matter whether the case is in state court or federal court. She is confident the outcome will be the same. Chevron said it looks forward to litigating these cases in federal court, where they belong.",
          m(0, v(near(-89.82, 29.52, 0.08))),
          clip("whether the case", "\"It doesn't matter whether this case is in state court or federal court \u2014 I am confident the outcome will be the same.\"", "Liz Murrill, Louisiana attorney general, Apr 17, 2026", highlight="the outcome will be the same"),
          m("She is confident", v(near(-89.85, 29.58, 0.1)), cut=True),
          m("Chevron said", v(near(-89.80, 29.55, 0.12)), cut=True),
          clip("where they belong", "\"Chevron looks forward to litigating these cases in federal court, where they belong.\"", "Chevron, Apr 17, 2026", highlight="where they belong")),
        P("West of the river, Louisiana Highway 1 runs down Bayou Lafourche to Port Fourchon, the base that supplies many of the oil platforms in the Gulf. By federal estimates, it serves about ninety percent of the deepwater rigs and platforms.",
          m(0, v(near(-90.22, 29.30, 0.4), routes=[LA1], places=[GOLDEN, FOURCHON])),
          m("Bayou Lafourche", v(near(-90.25, 29.35, 0.12), places=[GOLDEN]), cut=True),
          m("the base that", v(FOURCHON_V, places=[FOURCHON]), cut=True),
          stat("By federal", "~90%", "Gulf deepwater rigs and platforms served from Port Fourchon", "BSEE estimate")),
        P("The old road sits barely above the marsh, and the marsh is turning into open water around it. So the state is lifting it into the air. The second stretch, about eight miles from Golden Meadow to Leeville, costs about four hundred and sixty-three million dollars and is due in 2027, the state's transport department says.",
          m(0, v(LEEVILLE_V, places=[LEEVILLE])),
          stat("about four hundred", "$463 million", "LA-1 lifted, Golden Meadow to Leeville (~8 mi), due 2027", "Louisiana DOTD, via press"),
          m("is due in", v(near(-90.24, 29.32, 0.06), places=[GOLDEN]), cut=True)),
        P("On August 29, 2021, Hurricane Ida came ashore near Port Fourchon with winds of a hundred and fifty miles an hour. On Grand Isle, the state's only inhabited barrier island, most buildings were damaged.",
          m(0, v(near(-90.05, 29.2, 0.3), places=[FOURCHON, GRANDISLE])),
          m("On Grand Isle", v(GRANDISLE_V, places=[GRANDISLE]), cut=True),
          photo("most buildings", PH_IDA2, "Grand Isle, October 2021")),
        P("The Army Corps rebuilt the island's levee. In January 2023 its crews were still at work.",
          photo(0, PH_LEVEE, "Levee repair on Grand Isle, January 2023"),
          m("In January", v(near(-89.98, 29.24, 0.05)), cut=True)),
    ]},
    {"title": "Where the Land Still Grows", "mood": "curious", "paragraphs": [
        P("There is one big place where Louisiana's coast is still growing on its own. Here, at the mouth of the Atchafalaya River, a third of the Mississippi's water reaches the sea through a side channel, and it still carries its mud.",
          m(0, v(LOUISIANA, places=[WAXLAKE])),
          m("Here, at", v(near(-91.40, 29.56, 0.5), places=[WAXLAKE, ATCH]), cut=True)),
        P("Part of that water arrives through the Wax Lake Outlet, a channel dug in 1941 to protect Morgan City from floods. It carries about forty percent of the Atchafalaya's flow.",
          m(0, v(near(-91.32, 29.64, 0.2), places=[MORGAN])),
          m("It carries", v(near(-91.40, 29.58, 0.15)), cut=True)),
        P("This is the Wax Lake and Atchafalaya deltas in 1984. And this is this October. New land first rose above the water here in 1973, after a great flood. We measured them too. Since 1985 the two deltas have gained about eleven and a half thousand hectares, about a hundred and fifteen square kilometres. That is close to what scientists at Louisiana State University estimate.",
          m(0, v(WAXLAKE_W, compare={**CMP_WAXLAKE, "until": "And this", "hold": 0.4}), step("And this", places=[WAXLAKE, ATCH]), cut=True),
          photo("after a great", PH_WAXLAKE, "Wax Lake Outlet, 2016"),
          m("We measured them", v(WAXLAKE_V, places=[WAXLAKE]), cut=True),
          stat("Since 1985", "+115 km²", "Land gained by the Wax Lake and Atchafalaya deltas, 1985 -> 2026", OWN, "About 11,500 ha"),
          m("That is close", v(near(-91.30, 29.46, 0.1), places=[ATCH]), cut=True)),
        P("It is not enough to balance the losses, only about a tenth of them. But it is the proof the scientists keep pointing to: when the river is allowed to reach the marsh, Louisiana builds land.",
          m(0, v(near(-91.40, 29.50, 0.12))),
          photo("when the river", PH_PLANT, "Planting marsh grass, Port Sulphur, 2021")),
    ]},
    {"title": "What Now", "mood": "calm", "paragraphs": [
        P("In April 2026, Louisiana adopted a one-point-five-billion-dollar coastal plan for the year, with a hundred and forty-three projects: rebuilt barrier islands, marsh, levees. The next fifty-year master plan is due in 2029. In a document from April, the state says the flood-risk numbers it uses for that plan still include the two diversions it cancelled.",
          stat(0, "$1.54 billion", "Louisiana coastal plan for fiscal 2027, 143 projects", CPRA + ", Apr 27, 2026"),
          m("The next", v(COAST)),
          m("In a document", v(near(-90.1, 29.6, 0.5))),
          clip("still include the", "\"...all currently available risk outputs still include the two mid-basin diversions.\"", CPRA + ", 2029 Master Plan new project development, 2026", highlight="still include the two mid-basin diversions")),
        P("The board adopted the plan unanimously. Coastal restoration, the governor said, rises above politics. So far, the state's projects have restored or nurtured about fifty-five thousand acres and more than seventy miles of barrier islands, InvestigateTV reported this month.",
          clip(0, "\"The unanimous passage of this measure shows that coastal restoration rises above politics.\"", "Gov. Jeff Landry, " + CPRA + ", Apr 27, 2026", highlight="rises above politics"),
          m("So far", v(near(-90.2, 29.12, 0.4))),
          stat("about fifty-five", "55,000 acres", "Restored or nurtured by state coastal projects (+70 mi of barrier islands)", "InvestigateTV, Nov 3, 2026")),
        P("Foster Creppel, who runs a business in Plaquemines and supported the diversion, put the choice plainly. If we continue fighting over it, we really don't have a chance.",
          m(0, v(near(-89.95, 29.60, 0.15))),
          clip("If we", "\"If we continue fighting over it, we really don't have a chance.\"", "Foster Creppel, Plaquemines Parish, to InvestigateTV, Nov 2026", highlight="we really don't have a chance")),
        P("Mark Davis, of Tulane University, sees what Louisiana still has to lose. If I'm sitting in Miami, he said, I don't have a coast I can try to keep between me and hurricane landfalls.",
          m(0, v(near(-90.1, 29.35, 0.5))),
          clip("If I'm", "\"If I'm sitting in Miami, I don't have a coast I can try to keep between me and hurricane landfalls.\"", "Mark Davis, Tulane University, to InvestigateTV, Nov 2026", highlight="a coast I can try to keep"),
          m("I can try", v(near(-90.25, 29.25, 0.3)), cut=True)),
        P("On Isle de Jean Charles, the road is still there, and so are a few families. Forty miles inland, the people who left are learning to live by new rules.",
          m(0, v(IJC_W, places=[IJC]), cut=True),
          m("so are a few", v(near(-90.488, 29.398, 0.04), places=[IJC]), cut=True),
          m("Forty miles", v(NEWISLE_V, places=[NEWISLE]), cut=True)),
        P("If it were your call, would you open the river and change the fishing towns for good, or keep today's coast and watch it shrink?",
          m(0, v(COAST, places=[IJC, MBSD])),
          m("open the river", v(near(-89.97, 29.64, 0.12), places=[MBSD]), cut=True),
          m("or keep today's", v(near(-90.45, 29.38, 0.25)), cut=True),
          ask=("If it", "Open the river, or keep today's coast?")),
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
    "ijc": [(-90.487, 29.40), (-90.48, 29.42), (-90.553, 29.497), (-90.50, 29.38), (-90.46, 29.43), (-90.52, 29.44), (-90.44, 29.38),
            (-90.53, 29.40)],
    "newisle": [(-90.776, 29.711), (-90.81, 29.739), (-90.72, 29.596), (-90.75, 29.68)],
    "barataria": [(-89.955, 29.645), (-90.0, 29.55), (-89.93, 29.48), (-90.10, 29.50), (-90.08, 29.45), (-90.05, 29.60), (-90.12, 29.58),
                  (-89.90, 29.55)],
    "birdsfoot": [(-89.36, 29.28), (-89.25, 29.15), (-89.16, 29.16), (-89.30, 29.05), (-89.40, 29.15), (-89.20, 29.25), (-89.58, 29.41),
                  (-89.65, 29.47)],
    "lafourche": [(-90.19, 29.12), (-90.21, 29.25), (-90.26, 29.38), (-89.99, 29.235), (-90.25, 29.22), (-90.30, 29.26), (-90.30, 29.30),
                  (-90.15, 29.30)],
    "delta": [(-91.445, 29.50), (-91.30, 29.45), (-91.38, 29.55), (-91.50, 29.47), (-91.25, 29.50), (-91.376, 29.69)],
    "coast": [(-90.4, 29.45), (-90.9, 29.5), (-89.9, 29.5), (-90.2, 29.3), (-90.6, 29.35), (-89.6, 29.4)],
}
SPANS = {"coast": [0.3, 0.45, 0.6, 0.35], None: [0.05, 0.07, 0.09, 0.06, 0.08, 0.1]}
LABELS = {"ijc": "Isle de Jean Charles", "newisle": "Terrebonne Parish", "barataria": "Barataria Bay", "birdsfoot": "Plaquemines Parish",
          "lafourche": "Southeast Louisiana", "delta": "Atchafalaya Bay", "coast": "Coastal Louisiana"}
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
    if re.search(r"Wax Lake|Atchafalaya|growing|grows|1973", text):
        return "delta"
    if re.search(r"New Isle|Schriever|miles inland|subdivision|houses had|complaint|HUD", text):
        return "newisle"
    if re.search(r"Isle de Jean Charles|island|Island|Naquin|Brunet|Handon|Choctaw|tribe", text):
        return "ijc"
    if re.search(r"Venice|Bird's Foot|Highway 23|Neptune|Plaquemines|Chevron|Flyway|passes|Kolker|Baker", text):
        return "birdsfoot"
    if re.search(r"Fourchon|Highway 1|Lafourche|Leeville|Golden Meadow|Grand Isle|Ida|levee repair", text):
        return "lafourche"
    if re.search(r"Barataria|diversion|oyster|shrimp|Jurisich|Karst|Dove|Mid-Breton|gate in the levee", text):
        return "barataria"
    return None


CHAPTER_DEFAULT = {"Don't Do It": "ijc", "The Cancelled Cure": "barataria", "How a Delta Disappears": "coast",
                   "The Island That Left": "ijc", "The End of the Road": "birdsfoot", "The Road to the Oil": "lafourche",
                   "Where the Land Still Grows": "delta", "What Now": "coast"}


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

BASEMAP_NAMED = {"New Orleans", "Houma"}
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
    "title": "Vanishing Louisiana",
    "voice": "am_michael",
    "music": "procedural",
    "map_style": "satellite",
    "look": "none",
    "sources": ["episodes/louisiana-land-loss/research.md, verification.md and factcheck.md", "Landsat data courtesy of the U.S. Geological Survey", "Contains modified Copernicus Sentinel data 2026"],
    "thumbnail": {"text": "DON'T DO IT"},
    "chapters": chapters,
    "youtube": {
        "title": "Louisiana Had a Plan to Save Its Coast. It Cancelled It",
        "description": "Louisiana has lost about 2,000 square miles of land since 1932. In 2016 the US paid for the first time to move a whole community, Isle de Jean Charles, away from the sea; in 2025 the state cancelled the Mid-Barataria sediment diversion after spending $618 million. From orbit with Landsat and Sentinel-2 images we follow the island, Barataria Bay, the Bird's Foot delta at the end of Highway 23, LA-1 to Port Fourchon, and the Wax Lake and Atchafalaya deltas, the one place where the coast still grows, and measure the land ourselves.",
        "tags": ["Louisiana", "coastal land loss", "Isle de Jean Charles", "climate relocation", "Mid-Barataria", "sediment diversion", "Mississippi River delta", "Bird's Foot delta", "Wax Lake Delta", "Port Fourchon", "Grand Isle", "satellite images", "Landsat", "Sentinel-2"],
        "pinned_comment": "Open the river and change the fishing towns for good, or keep today's coast and watch it shrink?",
    },
}
out = HERE / "script.json"
out.write_text(json.dumps(script, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
words = sum(len(p["text"].split()) for c in chapters for p in c["paragraphs"])
print(f"{words} words, {len(chapters)} chapters, {sum(len(p['shots']) for c in chapters for p in c['paragraphs'])} shots")
