"""Builds script.json for ogallala-aquifer (beats are easier to review here than in the JSON).  python build_script.py"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
PDF = "https://pubs.usgs.gov/sir/2023/5143/sir20235143.pdf"
PATENT = "https://patentimages.storage.googleapis.com/70/bc/59/aef70234ffb83e/US2604359.pdf"  # US 2,604,359, public domain
AQ = "file:aquifer.geojson"
W24 = "2024-07-01/2024-08-31"  # the summer of the hook's "after" image, so close views match it
WHOLE = {"lon": -100.8, "lat": 37.8, "span": 26}
PANHANDLE = {"lon": -102.2, "lat": 36.0, "span": 1.9}
KANSAS_W = {"lon": -100.9, "lat": 38.0, "span": 1.9}
KSN_W = {"lon": -100.45, "lat": 39.3, "span": 1.9}
KANSAS_ALL = {"lon": -100.7, "lat": 38.65, "span": 4.4}
DALLAM = {"lon": -102.6, "lat": 36.1, "span": 0.28}
GOODLAND = {"lon": -101.7, "lat": 39.35, "span": 0.28}
GARDEN = {"lon": -100.95, "lat": 37.85, "span": 0.3}
HOXIE = {"lon": -100.45, "lat": 39.35, "span": 0.3}
MULESHOE = {"lon": -102.72, "lat": 34.23, "span": 0.3}


def place(name, lon, lat, label=None, kind="site", icon=None):
    d = {"name": name, "lon": lon, "lat": lat, "kind": kind, "label": label or name}
    if icon:
        d["icon"] = icon
    return d


DALHART = place("Dalhart", -102.52, 36.06, "Dalhart, Texas", "city")
STRATFORD = place("Stratford", -102.07, 36.34, "Stratford, Texas", "city")
GARDEN_CITY = place("Garden City", -100.87, 37.97, "Garden City, Kansas", "city")
TOPEKA = place("Topeka", -95.68, 39.05, "Topeka", "capital")
STRASBURG = place("Strasburg", -104.32, 39.74, "Strasburg, Colorado", "site")
SHERIDAN = place("Hoxie", -100.44, 39.35, "Sheridan County, Kansas", "site")
MULE = place("Muleshoe", -102.72, 34.23, "Muleshoe, Texas", "city")


def m(at, *steps, text=None, keep=False):
    s = {"type": "map", "at": at, "map": {"steps": list(steps)}}
    if keep:
        s["map"]["keep"] = True
    if text:
        s["on_screen_text"] = text
    return s


def v(view, at=None, date=None, **kw):
    if date is None and view["span"] <= 2:  # undated close views use multi-day mosaics with seams
        date = W24
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


def doc(at, page, source, title=None, highlight=None, pdf=PDF):
    d = {"pdf": pdf, "page": page, "source": source}
    if title:
        d["title"] = title
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


USGS = "USGS, SIR 2023-5143"
LEWIS = "Earl Lewis, Kansas chief engineer, High Plains Journal, Nov 7, 2026"
KRPS = "Kansas Public Radio, Oct 19, 2026"
KCUR = "KCUR / HPPR, Feb 2, 2026"
KGS = "Kansas Geological Survey, 2023"
STATELINE = "Stateline, Feb 1, 2024"

chapters = [
    {"title": "It Looks Like Success", "mood": "tension", "paragraphs": [
        P("This is the Texas Panhandle on August 17, 1986. Each dark circle is one irrigated field. Now the same place, on the same day of the year, in 2024.",
          m(0, v(DALLAM, date=W24, compare={"before": "1986-08-17", "after": "2024-08-17", "source": "landsat", "seconds": 2.6, "until": "Now the same"}),
            step("Each dark", places=[DALHART]), step("Now the same"), text="Real satellite images · Landsat")),
        P("We measured it. In 1986 about one sixth of this land was actively green. In 2024, more than half.",
          stat("We measured", "17% to 58%", "Land actively green near Dalhart, Texas, 1986 and 2024", "Our measurement, Landsat 5 and 9", "Share of a 28-mile-wide box with NDVI over 0.5")),
        P("Thirty miles away, near Stratford, nine percent became fifty-five. Those two pairs compare different satellites, but the older one alone shows the climb: near Dalhart, seventeen percent by 2010 had already reached forty-six. Researchers who mapped the whole Landsat record found the same pattern: irrigation grew across this aquifer, even where water was already short.",
          chart(0, "Land actively green, summer", "%", [["Stratford 1986", 9], ["Stratford 2024", 55.1], ["Dalhart 1986", 17], ["Dalhart 2024", 58.5]], "Our measurement, Landsat 5 and 9", highlight=1),
          m("Researchers", v(WHOLE, highlight=[AQ]), text="Deines et al., 2019: 34 years of Landsat maps")),
        P("From orbit, this is a triumph. But the water for those circles comes from below, and on September 30, the state of Kansas told the farmers above it that their rescue plan was not good enough.",
          m(0, v(DALLAM, date=W24)),
          m("But the water", v(WHOLE, highlight=[AQ]), step("the state of Kansas", highlight=["Kansas"]), text="The High Plains aquifer")),
        P("So how can land look this healthy while its water runs out? And who gets to decide when to stop?",
          m(0, v(PANHANDLE)), ask=("So how", "How long can green circles stay green?")),
    ]},
    {"title": "The Rejection", "mood": "tension", "paragraphs": [
        P("The man who said no is Earl Lewis, the chief engineer of Kansas's water division. The plan came from Groundwater Management District 3, around Garden City.",
          stat(0, "Sept 30, 2026", "Earl Lewis, Kansas chief engineer, says no", LEWIS),
          m("The plan came", v(KANSAS_W, places=[GARDEN_CITY]))),
        P("Why push so hard? Parts of that district have lost up to thirty feet of water in ten years. At its thickest, the aquifer under Kansas is only a little over three hundred feet.",
          m(0, v(GARDEN, date=W24)),
          stat("up to thirty", "Up to 30 feet", "Lost in ten years in parts of District 3", KRPS, "The aquifer's maximum thickness in Kansas: just over 300 feet")),
        P("Kansas had set the rules three years earlier. In 2023 the legislature passed a law, 34 to 6 in the Senate and 116 to 6 in the House: every district must file a plan by July 1, 2026.",
          m(0, v({"lon": -98.4, "lat": 38.5, "span": 7}, highlight=["Kansas"], places=[TOPEKA])),
          stat("34 to 6", "HB 2279", "Every Kansas groundwater district must file a plan", LEWIS, "Senate 34 to 6, House 116 to 6")),
        P("Lewis had said what he wanted, in a letter the November before: groundwater levels that stop falling within twenty years.",
          stat(0, "20 years", "What the chief engineer asked for", LEWIS)),
        P("District 3 filed on time. Lewis read it, and his answer was blunt: under this plan, levels would not stabilize at any point in the next sixty years.",
          m(0, v(GARDEN, date=W24, places=[GARDEN_CITY])),
          stat("his answer", "60 years", "Levels still falling under the district's plan", LEWIS)),
        P("He added that continued depletion \"is not in the public interest\", and that without cuts the harm would be \"brutal and irreversible in our lifetimes.\"",
          clip("and that without", "brutal and irreversible in our lifetimes", LEWIS, "brutal and irreversible")),
        P("The district's engineer says the state objected too late, and the district is appealing. To see why both sides are this dug in, we need to go back to this same corner of Texas, ninety years ago.",
          stat(0, "3 years", "How long the state sat in on the meetings, the district's engineer says", KRPS),
          m("To see why", v(PANHANDLE, places=[STRATFORD]))),
    ]},
    {"title": "The Same Land in 1935", "mood": "curious", "paragraphs": [
        P("This is Stratford, Texas, in 1935. Stratford is about thirty miles from the circles you just saw.",
          photo(0, "File:Dust storm approaching Stratford, Texas.jpg", "Stratford, Texas, 1935")),
        P("Plows had stripped the grass, the rain failed, and the soil took off. Here is a farm north of Dalhart in those years.",
          photo("Here is", "File:Dust Bowl farm. Coldwater District, north of Dalhart, Texas.jpg", "North of Dalhart, Texas")),
        P("Sand buried fences and machinery. Families walked away. This land was the Dust Bowl.",
          photo(0, "File:Dust Bowl - Dallas, South Dakota 1936.jpg", "Buried machinery, 1936"),
          photo("Families", "File:Abandoned Dust Bowl Home - Dorothea Lange.jpg", "Abandoned farmhouse")),
        P("Yet the answer was already underneath it. Pumps were reaching water in Texas so quickly that by 1951 wells had already dropped more than fifty feet in places.",
          m(0, v(WHOLE, highlight=[AQ])),
          stat("by 1951", "50+ feet", "Water-level declines in parts of Texas, 1938 to 1951", USGS)),
        P("Then came a machine. In 1947 a Colorado farmer named Frank Zybach watched workers hauling irrigation pipe by hand, and thought a sprinkler could walk by itself.",
          m(0, v({"lon": -103.2, "lat": 39.2, "span": 5}, places=[STRASBURG])),
          doc("Frank Zybach", 4, "U.S. Patent 2,604,359, 1952", "Frank L. Zybach: self-propelled sprinkling irrigating apparatus", "Frank L. Zybach, Strasburg", pdf=PATENT),
          photo("thought a sprinkler", "File:Center pivot sprinkler irrigation system located on a winter wheat cover crop in Morton, Texas (24996240242).jpg", "A center pivot today")),
        P("He built one in 1948, near Strasburg, and patented it in 1952: a long arm of pipe on wheels, turning around a well. That is why the fields are round.",
          stat("patented", "July 22, 1952", "Frank Zybach's self-propelled sprinkler is patented", "ASABE; National Inventors Hall of Fame"),
          doc("a long arm", 1, "U.S. Patent 2,604,359, 1952", "Frank L. Zybach: self-propelled sprinkling irrigating apparatus", "SELF-PROPELLED SPRINKLING IRRIGATING APPARATUS", pdf=PATENT),
          m("That is why", v(DALLAM, date=W24))),
        P("A pivot does not need flat ground or a canal. It needs a well. Watch what that did to western Kansas, from 1986 to this summer. Here the green share went from about ten percent to thirty-eight.",
          photo(0, "File:Circular irrigation sprinklers 01.jpg", "It only needs a well"),
          m("Watch what", v(GOODLAND, date="2026-07-01/2026-08-31", compare={"before": "1986-07-16", "after": "2026-07-06", "source": "landsat", "seconds": 2.2, "until": "Here the"}),
            step("Here the"), text="Near Goodland, Kansas")),
    ]},
    {"title": "A Sea With No Surface", "mood": "curious", "paragraphs": [
        P("So what is under there? Not an underground lake. It is sand and gravel washed off the Rockies, with water in the gaps.",
          m(0, v(WHOLE, highlight=[AQ]), text="Ogallala / High Plains aquifer"),
          m("washed off", v({"lon": -103.5, "lat": 39, "span": 9}))),
        P("It lies under parts of eight states, about 175,000 square miles, from South Dakota to Texas.",
          m(0, v(WHOLE, highlight=[AQ]), text="Parts of eight states")),
        P("That water supplies about thirty percent of the groundwater used for irrigation in the United States.",
          stat("thirty percent", "30%", "Of US irrigation groundwater", "Steward et al., PNAS, 2013")),
        P("In 2019 it still held about 2.9 billion acre-feet. That sounds like plenty, and across the whole aquifer it nearly is. We added up the federal figures: about nine percent has gone since 1950.",
          stat(0, "2.91 billion", "Acre-feet of recoverable water in 2019", USGS),
          stat("We added", "9%", "Of the aquifer's water gone since about 1950", "Our calculation from " + USGS, "286.4 of about 3,196 million acre-feet")),
        P("Nine percent. If that were the whole story, nobody in Kansas would be fighting. So why is a state engineer talking about land becoming unusable?",
          m(0, v(KANSAS_W)), ask=("Nine percent", "Is 9% a crisis, or a false alarm?")),
    ]},
    {"title": "Two States, One Hole", "mood": "tension", "paragraphs": [
        P("Because that average hides nearly everything. This is the government's own map of the change, about 1950 to 2019. Gray means almost nothing happened.",
          {"type": "document", "at": "This is", "document": {"pdf": PDF, "page": 10, "rects": [[0.27, 0.46, 0.5, 0.78]], "source": USGS, "title": "Water-level change, about 1950 to 2019"}},
          {"type": "document", "at": "Gray means", "document": {"pdf": PDF, "page": 10, "rects": [[0.3, 0.13, 0.66, 0.3]], "source": USGS, "title": "Gray: almost no change"}}),
        P("Most of Nebraska is gray on this map. Its average fell less than half a foot, and one well there rose eighty-six feet.",
          m(0, v({"lon": -100, "lat": 41.6, "span": 8}, highlight=["Nebraska"])),
          chart("Its average", "Average water-level decline since about 1950", " ft", [["Nebraska", 0.4], ["Kansas", 27.3], ["Texas", 44.1]], USGS, highlight=0)),
        P("Now go south. Kansas fell an average of twenty-seven feet. Texas, forty-four.",
          chart(0, "Average water-level decline since about 1950", " ft", [["Nebraska", 0.4], ["Kansas", 27.3], ["Texas", 44.1]], USGS, reveal=["twenty-seven", "forty-four"], highlight=2)),
        P("One Texas well dropped two hundred sixty-five feet: sixteen times the average for the whole aquifer.",
          stat(0, "265 feet", "The largest decline at one well, in Texas", USGS, "Sixteen times the aquifer's 16.5-foot average")),
        P("Add up the lost water by state and it gets sharper. Of 286 million acre-feet gone, Texas accounts for about fifty-nine percent. Kansas, twenty-five. Nebraska, under one.",
          chart("Of 286", "Water lost since about 1950", " million acre-feet", [["Texas", 169.6], ["Kansas", 72], ["Nebraska", 2.7]], USGS + "; shares are our calculation", reveal=["Kansas, twenty-five", "Nebraska, under"], highlight=0)),
        P("Even the good news can mislead. From 2017 to 2019 the aquifer as a whole gained water: 1.6 million acre-feet. But Nebraska gained 4.3 million, while Texas lost 2.7 million.",
          stat(0, "+1.6 million", "Acre-feet, the whole aquifer, 2017 to 2019", USGS),
          chart("But Nebraska", "Change in stored water, 2017 to 2019", " million acre-feet", [["Nebraska gained", 4.3], ["Texas lost", 2.7]], USGS, reveal=["Texas lost"], highlight=1)),
        P("Part of the gap is simple geology. The aquifer is thickest under Nebraska. In the south it is thinner, and what comes back each year is small.",
          m(0, v({"lon": -100, "lat": 41.6, "span": 8}, highlight=["Nebraska"])),
          m("In the south", v(PANHANDLE))),
        P("A Kansas study put numbers on that: recharge replaces about fifteen percent of what is pumped. If you drained the aquifer there, refilling it would take five hundred to thirteen hundred years.",
          stat("recharge", "15%", "Of current pumping is replaced by recharge, Kansas", "Steward et al., PNAS, 2013"),
          stat("If you drained", "500-1,300 years", "To refill a depleted aquifer in Kansas, on average", "Steward et al., PNAS, 2013")),
        P("That study also projected, in 2013, that nearly seventy percent of the water under Kansas would be gone in fifty years on existing trends. That was a model, not a measurement.",
          stat(0, "69%", "Of Kansas's groundwater gone by about 2063 on 2013 trends", "Steward et al., PNAS, 2013", "A projection")),
        P("And depth is what matters to a farmer. In some parts of Kansas, less than forty percent of the aquifer's original thickness remains. A well gets weaker long before it is empty.",
          stat("less than", "Under 40%", "Of the original thickness left in some Kansas areas", KGS),
          m("A well gets", v(GARDEN, date=W24))),
    ]},
    {"title": "What the Water Built", "mood": "curious", "paragraphs": [
        P("This water does not stop at the field. Water that costs little more than the fuel to pump it grows cheap cattle feed, and cheap feed drew the feedlots to southwest Kansas.",
          m(0, v(GARDEN, date=W24), text="Near Garden City, Kansas"),
          photo("cheap feed", "File:Garden City, Kansas (5638320394).jpg", "Garden City, Kansas, from orbit")),
        P("In 1980 what was described as the world's largest beef plant opened at Holcomb, just outside Garden City. A 2021 Associated Press count put Kansas feedlots at 2.5 million cattle, eating more than 6.5 billion pounds of corn a year.",
          m(0, v({"lon": -100.99, "lat": 37.99, "span": 0.2}, date=W24, places=[place("Holcomb", -100.99, 37.99, "Holcomb, Kansas", "city")])),
          stat("A 2021", "2.5 million", "Cattle in Kansas feedlots", "Associated Press, 2021", "Eating more than 6.5 billion pounds of corn a year")),
        P("And it runs the towns. In Kansas, this aquifer supplies seventy to eighty percent of the water residents use each day.",
          stat("seventy", "70-80%", "Of the water Kansas residents use each day", STATELINE)),
        P("Guymon, Oklahoma has about thirteen thousand people and eighteen wells. It has committed some four and a half million dollars to find new ones, with no guarantee of water.",
          m(0, v({"lon": -101.48, "lat": 36.68, "span": 1.4}, places=[place("Guymon", -101.48, 36.68, "Guymon, Oklahoma", "city")]))),
        P("Its interim city manager said it plainly in 2024: \"We're running out of water.\"",
          clip("said it plainly", "We're running out of water.", "Micheal Shannon, Guymon interim city manager, to Stateline, 2024", "running out")),
        P("Farther southwest, Clovis, New Mexico and its neighbors are building a pipeline of more than eight hundred million dollars, to bring in river water from a reservoir. The head of their water authority says these towns could not last long without it.",
          m(0, v({"lon": -103.2, "lat": 34.4, "span": 1.4}, places=[place("Clovis", -103.2, 34.4, "Clovis, New Mexico", "city")])),
          stat("more than eight", "$800 million+", "A pipeline to replace groundwater in eastern New Mexico", STATELINE)),
        P("The researchers behind those Landsat maps looked ahead too. On current trends, about a quarter of today's irrigated land on the aquifer could not be irrigated by 2100, and thirteen percent of that land may not suit dryland crops either.",
          m(0, v(WHOLE, highlight=[AQ])),
          stat("about a quarter", "24%", "Of irrigated land may lose irrigation by 2100", "Deines et al., Agricultural Water Management, 2020", "A projection")),
    ]},
    {"title": "The Biggest Pump Wins", "mood": "tension", "paragraphs": [
        P("Texas holds the largest share of the loss, and Texas has an unusual law. Since 1904, a landowner there may pump as much groundwater as they like, even if a neighbor's well runs dry.",
          m(0, v({"lon": -101.5, "lat": 34.4, "span": 7}, highlight=["Texas"])),
          stat("Since 1904", "1904", "Texas adopts the rule of capture for groundwater", "Houston & T.C. Ry. v. East")),
        P("It is called the rule of capture. In 1999 landowners whose wells had gone dry took a bottled-water company to the Texas Supreme Court. The court left the rule standing, and said changing it was a job for the legislature.",
          m(0, v({"lon": -101.5, "lat": 34.4, "span": 7}, highlight=["Texas"]), text="The rule of capture"),
          stat("In 1999", "1999", "Texas Supreme Court keeps the rule of capture", "Sipriano v. Great Spring Waters of America")),
        P("In 2001 the oilman T. Boone Pickens saw what that could mean. His company leased about 150,000 acres in the Panhandle, and planned to sell water to Dallas-Fort Worth through a 385-mile pipeline.",
          m(0, v({"lon": -100.8, "lat": 35.84, "span": 1.5}, places=[place("Roberts County", -100.8, 35.84, "Roberts County, Texas", "site")])),
          m("through a 385-mile", v({"lon": -98.8, "lat": 34.2, "span": 7}, routes=[{"from": [-100.8, 35.84], "to": [-96.8, 32.78], "mode": "line", "label": "385 miles", "seconds": 1.6}]))),
        P("He had no city buyer at the time, and the project was later suspended. Still, it showed how Texas treats this water: as something a landowner can sell.",
          stat(0, "200,000", "Acre-feet a year Pickens planned to sell", "AAPG Explorer, July 2001")),
        P("Texas does have local groundwater districts, which can limit pumping. But look at the target for four Panhandle counties here: forty percent of the water left, after fifty years.",
          m(0, v(PANHANDLE, places=[DALHART])),
          stat("But look", "40% left", "After 50 years: the district's goal for four Panhandle counties", "Texas Water Journal, on North Plains GCD", "Dallam, Sherman, Hartley and Moore")),
        P("So in that target, most of the water can go, as long as it goes on schedule.",
          m(0, v(DALLAM, date=W24))),
    ]},
    {"title": "What Running Out Looks Like", "mood": "calm", "paragraphs": [
        P("So what does the end look like? Go south to Muleshoe, Texas. Wells around there once drew about a thousand gallons a minute. In 2021 Tim Black's gave about fifty.",
          m(0, v({"lon": -102.6, "lat": 34.3, "span": 1.6}, places=[MULE])),
          stat("about a thousand", "1,000 to 50", "Gallons a minute, wells near Muleshoe, Texas", "Associated Press, 2021")),
        P("He stopped growing mostly corn and turned to cattle on native grass. His verdict on the old days, to the Associated Press: \"We wasted the hell out of the water.\"",
          m(0, v(MULESHOE, date=W24)),
          clip("to the Associated", "We wasted the hell out of the water.", "Tim Black, farmer, to the Associated Press, 2021", "wasted")),
        P("An hour southwest of Amarillo, Chris Grotegrut has put about three quarters of his family's 11,000 acres back into native grass. That is the land's old cover, the one the plows removed before the Dust Bowl.",
          m(0, v(PANHANDLE)),
          stat("three quarters", "75%", "Of one family's 11,000 acres, back in native grass", "Associated Press, 2021")),
        P("And here is something we cannot explain yet. All seven areas we measured came in less green this summer than last. Near Dalhart, about fifteen percent. One summer is not a trend. It could be drought, or a planting calendar. We will keep measuring.",
          stat("Near Dalhart,", "15%", "Land actively green near Dalhart, July 30, 2026", "Our measurement, Landsat 8", "All seven areas measured were down on 2025"),
          m("One summer", v(DALLAM, date="2026-07-01/2026-08-31"))),
        P("If you want to see the next measurement, subscribe. We come back to these places from orbit.",
          m(0, v(DALLAM, date="2026-07-01/2026-08-31"))),
    ]},
    {"title": "The Farmers Who Cut Anyway", "mood": "curious", "paragraphs": [
        P("But there is a place where the story turned. In 2013, farmers in Sheridan County, northwest Kansas, did something nobody made them do. They capped their own pumping for five years.",
          m(0, v({"lon": -100.45, "lat": 39.3, "span": 1.9}, places=[SHERIDAN])),
          m("They capped", v(HOXIE, date=W24))),
        P("The target was a twenty percent cut. They reached about twenty-three.",
          stat(0, "23%", "Average cut, first five years, Sheridan 6", STATELINE, "Target: 20%")),
        P("And the aquifer answered. From 2002 to 2012 levels fell about two feet a year. From 2013 to 2022, about half a foot.",
          chart("From 2002", "Average yearly water-level decline, Sheridan 6", " ft", [["2002-2012", 2.0], ["2013-2022", 0.5]], KGS, highlight=1)),
        P("Farm income held up, say the reports on the program: they swapped some corn for wheat and sorghum, and spent less on pumping.",
          m(0, v(HOXIE, date=W24), text="Sheridan County, Kansas")),
        P("Others followed. Wichita County has cut pumping by about forty percent. Outside Garden City, Gina and Marc Gigot, whose father dug the well more than fifty years ago, had stopped growing corn on their farm by 2024.",
          stat(0, "40%", "Pumping cut in Wichita County, Kansas", KGS),
          m("Outside Garden", v(GARDEN, date=W24, places=[GARDEN_CITY]))),
        P("Garden City planned to send them treated wastewater, so they could switch off some wells next to the city's own. Yet they say the state must force others to cut back. Even the Farm Bureau's president said in 2024, \"we don't have decades.\"",
          m(0, v(GARDEN, places=[GARDEN_CITY])),
          clip("Even the Farm", "we don't have decades to fix this problem", "Joe Newland, Kansas Farm Bureau president, to Stateline, 2024", "decades")),
        P("Towns are moving too. Dodge City, about twenty-eight thousand people, sends about 1.8 billion gallons of treated wastewater to irrigate three thousand acres of crops. A sixty million dollar project there aims to push treated water back into the aquifer.",
          m(0, v({"lon": -100.02, "lat": 37.76, "span": 0.3}, date=W24, places=[place("Dodge City", -100.02, 37.76, "Dodge City, Kansas", "city")])),
          stat("A sixty", "$60 million", "Dodge City's project to recharge the aquifer", STATELINE)),
        P("So the fix exists, and farmers proved it. Why not everywhere? Because a cut that looks fine on a map hits people one field at a time.",
          m(0, v({"lon": -100.45, "lat": 39.3, "span": 1.9})),
          m("Because a cut", v(GARDEN, date=W24)),
          ask=("Why not", "Would you cut your own water first?")),
    ]},
    {"title": "Too Much, Too Little", "mood": "tension", "paragraphs": [
        P("Kansas has known for a long time. A report to its legislature warned in 1955: \"Ground-water mining is a serious problem.\"",
          clip("Ground-water", "Ground-water mining is a serious problem.", "Kansas legislature report, 1955, via Stateline", "serious problem")),
        P("The state created its groundwater districts in 1972, and for decades its answer stayed local and voluntary, a policy often called planned depletion. Burke Griggs, a former state water lawyer, on those local efforts: \"None of them have achieved much.\"",
          stat(0, "1972", "Kansas creates groundwater management districts", LEWIS),
          clip("on those local", "None of them have achieved much.", "Burke Griggs, Washburn University, to Stateline, 2024", "achieved much")),
        P("In 2024 Governor Laura Kelly said some communities were a generation away from running out of water. She still preferred local agreement, \"rather than the state wielding that heavy hammer.\" Two years earlier, a bigger water bill had sunk on an amendment from Joe Newland, the same Farm Bureau president.",
          m(0, v({"lon": -95.68, "lat": 39.05, "span": 0.3}, places=[TOPEKA])),
          clip("She still", "rather than the state wielding that heavy hammer", "Gov. Laura Kelly to Stateline, 2024", "heavy hammer"),
          stat("Two years", "2022", "A larger Kansas water bill sinks on an amendment", STATELINE)),
        P("In February, more than two hundred farmers came to hear District 3's plan: cut pumping five percent a year for twenty years, 27.7 percent in all, according to its engineer.",
          m(0, v(KANSAS_W, places=[GARDEN_CITY])),
          stat("27.7", "27.7%", "The district's first proposal, over twenty years", KCUR)),
        P("Roger Holmes, a longtime farmer there, did the math on his own land. Three inches less water could mean about fifty fewer bushels of corn an acre, up to two hundred dollars.",
          stat("about fifty", "$200 an acre", "One farmer's estimate of the cost of three inches less", KCUR)),
        P("He said he would be dead in ten years. His concern was who comes next. His words: \"It's going to affect my son.\"",
          clip("His concern", "It's going to affect my son.", "Roger Holmes, farmer, to KCUR, 2026", "my son")),
        P("And the district has been cutting. The Kansas survey found use there since 2019 running nearly thirteen percent below the years before. For the district, that is progress. For the chief engineer, it is not enough.",
          m(0, v(KANSAS_W, places=[GARDEN_CITY])),
          stat("nearly thirteen", "13% less", "Water use in District 3 since 2019, against 2005-2018", KGS)),
        P("The plan filed in July gave some areas with deep water fifty years to cut thirty percent. The district also asked the state for ten million dollars a year to pay landowners for saving water.",
          m(0, v(GARDEN, date=W24)),
          stat("ten million", "$10 million", "A year: what the district asked of the state", KRPS)),
        P("That is what Lewis rejected. He says that in most of the district, after fifty years, groundwater would be on the verge of unusable, even under the district's own plan.",
          stat("He says", "50 years", "Then groundwater near unusable in most of the district, Lewis says", LEWIS)),
        P("Now go north, to the district around Sheridan County. There the complaint runs the other way. Farmers and the Kansas Farm Bureau say the cuts go too far, some as deep as forty-four percent, and that they violate water rights.",
          m(0, v(KSN_W, places=[SHERIDAN])),
          stat("forty-four", "44%", "Pumping cuts in some areas of northwest Kansas", KRPS)),
        P("Their case is not small. Irrigation rights can make land worth almost twice as much, by the district's own testimony. So a cut in water is also a cut in what a family owns. The state denied the Bureau's request.",
          stat("almost twice", "Nearly 2x", "What irrigation rights can add to the value of land", KRPS)),
        P("So one Kansas district is told it does too little, and another that it does too much. Both are looking at the same falling water.",
          m(0, v(KANSAS_ALL, places=[GARDEN_CITY, SHERIDAN]))),
    ]},
    {"title": "What Happens Next", "mood": "calm", "paragraphs": [
        P("District 3 will appeal to the Kansas Secretary of Agriculture, and hopes to start parts of its plan meanwhile.",
          m(0, v(KANSAS_W, places=[GARDEN_CITY]))),
        P("Every January, crews drive back out to about fourteen hundred wells. One of them, Brownie Wilson of the Kansas survey, feeds a steel tape down each well, and the wet part of the tape gives him the water level. Some of his wells have dropped more than a hundred feet since 2001.",
          stat(0, "1,400 wells", "Measured each January across western Kansas", KGS),
          stat("Some of his", "100+ feet", "Drop in some Kansas wells since 2001", STATELINE, "Brownie Wilson, Kansas Geological Survey")),
        P("The Kansas survey says levels in the worst areas could hold steady for a decade or two, with pumping cuts of eighteen to thirty-two percent. So this is still a choice.",
          stat("eighteen", "18-32%", "Cuts that could hold levels for one to two decades", KGS)),
        P("From orbit you will not see it being made. The circles will stay green right up until they don't. That is the trap: it looks the same, until the pump runs dry.",
          m("The circles", v(DALLAM, date=W24, compare={"before": "1986-08-17", "after": "2024-08-17", "source": "landsat", "seconds": 2.6, "until": "That is the trap"}),
            step("That is the trap"))),
        P("So who should decide how fast it goes: the farmers who own the wells, or a state thinking about the people who come after them?",
          m(0, v(GARDEN)), ask=(0, "Farmers, or the state: who decides?")),
    ]},
]

# ---- beats: a new real picture at least every ~5.5 s. Gaps are filled from a pool of pictures of the chapter's own subject.
sys.path.insert(0, str(HERE.parent.parent / "pipeline"))
from schema import Paragraph  # noqa: E402

MAX_WORDS = 10


def sat(lon, lat, span, label=None):
    return m(0, v({"lon": lon, "lat": lat, "span": span}, date=W24), text=label)


def pic(name, label=None):
    return photo(0, name, label)


PIVOTS = [pic("File:Circular irrigation sprinklers 02.jpg", "A center pivot"),
          pic("File:Center pivot sprinkler irrigation system located on a winter wheat cover crop in Morton, Texas (24996240242).jpg", "A center pivot today"),
          sat(-102.7, 36.2, 0.08, "Round, because the arm turns around a well"), sat(-101.6, 39.3, 0.08, "Round fields, seen from orbit")]
DUST = [pic("File:Dust storm descends over the Texas Panhandle town of Stratford in 1935. (24490688603).jpg", "Stratford, Texas, 1935"), pic("File:Dust Bowl Oklahoma.jpg", "Oklahoma, the Dust Bowl years"), pic("File:Dust Bowl winds pile up against barn in Kansas.jpg", "Kansas, the Dust Bowl years"),
        pic("File:Dust bowl, Texas Panhandle, TX fsa.8b27276 edit.jpg", "Texas Panhandle"), pic("File:Dust Bowl in Texas County, Oklahoma.jpg", "Texas County, Oklahoma")]
TX = [sat(-102.7, 36.2, 0.14, "Near Dalhart, Texas"), sat(-102.07, 36.34, 0.2, "Near Stratford, Texas"), sat(-102.0, 35.95, 0.16, "Near Dumas, Texas"), sat(-102.4, 34.8, 0.18, "Near Hereford, Texas"),
      sat(-101.7, 34.2, 0.2, "Near Plainview, Texas"), sat(-101.9, 33.8, 0.16, "North of Lubbock, Texas"), sat(-102.4, 33.6, 0.18, "Near Levelland, Texas"), sat(-102.75, 34.05, 0.16, "Near Muleshoe, Texas"),
      sat(-102.45, 35.95, 0.14, "The Texas Panhandle"), sat(-101.9, 36.15, 0.18, "The Texas Panhandle"), sat(-102.1, 34.5, 0.16, "Near Dimmitt, Texas"), sat(-101.75, 34.55, 0.18, "Near Tulia, Texas")]
KS = [sat(-100.72, 37.72, 0.16, "Southwest Kansas"), sat(-100.9, 38.5, 0.18, "Near Scott City, Kansas"), sat(-101.35, 37.6, 0.18, "Near Ulysses, Kansas"), sat(-100.85, 37.5, 0.14, "Near Sublette, Kansas"),
      sat(-100.25, 37.8, 0.16, "Near Dodge City, Kansas"), sat(-100.9, 37.1, 0.18, "Near Liberal, Kansas"), sat(-101.35, 38.48, 0.16, "Near Leoti, Kansas"), sat(-101.25, 37.95, 0.16, "Near Lakin, Kansas"),
      sat(-100.55, 37.9, 0.14, "Southwest Kansas"), sat(-101.0, 38.1, 0.16, "Finney County, Kansas"), sat(-100.6, 37.45, 0.16, "Southwest Kansas"), sat(-101.75, 37.95, 0.18, "Near Syracuse, Kansas")]
KSN = [sat(-100.6, 39.35, 0.14, "Sheridan County, Kansas"), sat(-100.3, 39.45, 0.14, "Sheridan County, Kansas"), sat(-101.05, 39.4, 0.16, "Near Colby, Kansas"), sat(-100.85, 39.1, 0.16, "Near Oakley, Kansas"),
       sat(-101.6, 39.25, 0.15, "Near Goodland, Kansas"), sat(-100.75, 39.25, 0.12, "Northwest Kansas")]
NE = [m(0, v({"lon": -100, "lat": 41.6, "span": 8}, highlight=["Nebraska"])), sat(-99.5, 41.0, 0.2, "Central Nebraska"), sat(-101.2, 40.9, 0.18, "Western Nebraska"), sat(-98.2, 40.9, 0.18, "Eastern Nebraska")]
GUYMON = [sat(-101.48, 36.68, 0.2, "Guymon, Oklahoma"), sat(-101.3, 36.75, 0.16, "Near Guymon, Oklahoma"), sat(-101.65, 36.6, 0.16, "Near Guymon, Oklahoma")]
CLOVIS = [sat(-103.2, 34.4, 0.2, "Clovis, New Mexico"), sat(-103.35, 34.3, 0.16, "Near Clovis, New Mexico"), sat(-103.05, 34.5, 0.16, "Near Clovis, New Mexico")]
GROUPS = {"tx": TX, "ks": KS, "ksn": KSN, "ne": NE, "dust": DUST, "pivot": PIVOTS, "guymon": GUYMON, "clovis": CLOVIS}
counters = dict.fromkeys(GROUPS, 0)


def topic_of(text, chapter):
    if "Guymon" in text or "interim city manager" in text:
        return "guymon"
    if "Clovis" in text or "water authority" in text:
        return "clovis"
    if chapter == "The Same Land in 1935":
        if re.search(r"Zybach|machine|arm of pipe|[Pp]ivot|a well|He built|round", text):
            return "pivot"
        if "Pumps" in text:
            return "tx"
        if "Kansas" in text or "green share" in text:
            return "ks"
        if re.search(r"1935|Plows|Sand|Dust Bowl|farm north|Families", text):
            return "dust"
        return None
    if re.search(r"Sheridan|northwest|north,|They capped|twenty percent cut|aquifer answered|Farm income", text):
        return "ksn"
    if "Nebraska" in text and "Texas" not in text and "Kansas" not in text:
        return "ne"
    tx = len(re.findall(r"Texas|Panhandle|Muleshoe|Amarillo|Dalhart|Stratford|Pickens|rule of capture|Black|Grotegrut", text))
    ks = len(re.findall(r"Kansas|District|district|Garden City|Holmes|Lewis|Holcomb|Dodge|Gigot|Wichita County|Griggs|Kelly|chief engineer|Bureau", text))
    if tx or ks:
        return "tx" if tx > ks else "ks"
    return None


CHAPTER_DEFAULT = {"It Looks Like Success": "tx", "The Same Land in 1935": "dust", "The Biggest Pump Wins": "tx", "What Running Out Looks Like": "tx", "The Farmers Who Cut Anyway": "ksn"}


def topic(para_text, at, chapter):
    """The sentence under the new picture decides; failing that the paragraph, then the chapter."""
    seen, sentence = 0, para_text
    for part in re.split(r"(?<=[.?!])\s+", para_text):
        k = len(part.split())
        if seen <= at < seen + k:
            sentence = part
            break
        seen += k
    return topic_of(sentence, chapter) or topic_of(para_text, chapter) or CHAPTER_DEFAULT.get(chapter, "ks")



for ch in chapters:
    for para in ch["paragraphs"]:
        pm = Paragraph.model_validate(para)
        marks = set(pm.anchor_indices())
        for idx in pm.step_indices():
            marks |= set(idx)
        if pm.ask_index() is not None:
            marks.add(pm.ask_index())
        n = len(para["text"].split())
        stops = sorted(marks | {0}) + [n]
        no_fill = para["text"].startswith("Because that average")
        blocks = [(min(idx), max(idx)) for idx in pm.step_indices() if len(idx) > 1]
        para_words = para["text"].split()
        for sh in para["shots"]:  # a wipe keeps the screen until it has finished
            for st in (sh.get("map") or {}).get("steps", []):
                until = (st.get("compare") or {}).get("until")
                if until:
                    want = until.split()
                    bare = [w.strip('.,;:!?"') for w in para_words]
                    hits = [i for i in range(len(bare)) if bare[i:i + len(want)] == want]
                    if hits:
                        blocks.append((hits[0], len(para_words)))
        for sh, start in zip(para["shots"], pm.anchor_indices()):
            for phrase in (sh.get("chart") or {}).get("reveal", []):
                want = phrase.split()
                hits = [i for i in range(len(para_words)) if para_words[i:i + len(want)] == want]
                if hits:
                    blocks.append((start, hits[0]))
        anchors = pm.anchor_indices()
        for sh, start in zip(para["shots"], anchors):  # a document holds until the next hand-placed shot
            if sh["type"] == "document":
                later = [x for x in anchors if x > start]
                blocks.append((start, min(later) if later else n))
        new = []
        for a, b in zip(stops, stops[1:]):
            inside = any(lo <= a and b <= hi for lo, hi in blocks)  # a shot still running its own steps or chart reveal
            parts = 0 if (no_fill or inside) else (b - a - 1) // MAX_WORDS
            for j in range(1, parts + 1):
                at = a + (b - a) * j // (parts + 1)
                group = topic(para["text"], at, ch["title"])
                shot = json.loads(json.dumps(GROUPS[group][counters[group] % len(GROUPS[group])]))
                counters[group] += 1
                shot["at"] = at
                new.append(shot)
        if new:
            pos = dict(zip(map(id, para["shots"]), pm.anchor_indices()))
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
    "title": "The Ogallala Aquifer",
    "voice": "am_michael",
    "music": "procedural",
    "map_style": "satellite",
    "look": "none",
    "sources": ["episodes/ogallala-aquifer/research.md and factcheck.md; own numbers: tools/ogallala_numbers.py, tools/ogallala_green.py"],
    "thumbnail": {"text": "UNUSABLE?"},
    "chapters": chapters,
    "youtube": {
        "title": "Kansas Rejected Farmers' Plan to Save Their Water",
        "description": "From orbit, the circles of the High Plains look like a triumph: we measured far more green land near Dalhart, Texas in 2024 than in 1986. Below them, the water under eight states is falling, and on September 30, 2026 the Kansas chief engineer rejected the plan of the farmers around Garden City, saying levels would not stabilize in sixty years. We follow it from the Dust Bowl to the wells, the Texas law that lets the biggest pump win, and the Kansas farmers who cut their own water and proved it works.",
        "tags": ["Ogallala aquifer", "High Plains aquifer", "Kansas water", "groundwater", "irrigation", "center pivot", "Dust Bowl", "Texas Panhandle", "rule of capture", "satellite images", "Garden City Kansas", "water crisis"],
        "pinned_comment": "Who should decide how fast the water goes: the farmers who own the wells, or the state?",
    },
}
out = HERE / "script.json"
out.write_text(json.dumps(script, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
words = sum(len(p["text"].split()) for c in chapters for p in c["paragraphs"])
print(f"{words} words, {len(chapters)} chapters, {sum(len(p['shots']) for c in chapters for p in c['paragraphs'])} shots")
