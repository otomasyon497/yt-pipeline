"""Builds script.json for northern-maine-empty.  python build_script.py

Same production logic as episodes/nevada-empty (hook template, numbered reasons, painted regions, hand-placed shots,
no fillers, a photo or map frame at most twice). Sources: research.md. Regions: geo/make_regions.py (Census 2020).
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent.parent / "pipeline"))
from schema import Paragraph  # noqa: E402

ME = {"lon": -69.2, "lat": 45.25, "span": 6.0}
NORTH = {"lon": -69.3, "lat": 46.45, "span": 3.8}
NENG = {"lon": -70.6, "lat": 43.9, "span": 10.0}
EAST = {"lon": -70.5, "lat": 46.3, "span": 9.0}
UT, AROO, PISC, SOUTH = "file:unorganized.geojson", "file:aroostook.geojson", "file:piscataquis.geojson", "file:south_coast.geojson"


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


CENSUS = "US Census Bureau, 2020 census"
GAZ = "US Census Bureau, 2020 census and Gazetteer (our sum)"
FS = "USDA Forest Service, Forests of Maine 2021"
NOAA = "NOAA NCICS, State Climate Summary: Maine"
NWS = "NOAA / National Weather Service, Caribou records"
MA_ARCH = "Massachusetts Archives; Maine State Archives"

PH_KAT = "File:Appalachian Trail and view of Mount Katahdin, Maine LCCN2011630252.tif"
PH_BAXTER = "File:Entering Baxter State Park.jpg"
PH_PANCAKE = "File:Pancake ice on the Allagash River, Maine.jpg"
PH_ALLA_FALLS = "File:Allagash Waterfalls 2003.jpg"
PH_ALLA = "File:Allagash River 2003.jpg"
PH_LOGROAD = 'File:Access to the areas of study was limited by private logging roads. A team is shown here staging for a hike into a area where Canada Lynx are known to be "denning". (4700060450).jpg'
PH_MILL_HOMES = "File:Closely spaced mill-era homes in Millinocket, Maine.jpg"
PH_EMILL = "File:East Millinocket, Maine.jpg"
PH_WBRANCH = "File:West Branch Penobscot River, Maine.jpg"
PH_POTATO_KIDS = "File:Children gathering potatoes on a large farm, vicinity of Caribou, Aroostook County, Me. Schools do not open until the potatoes are harvested LCCN2017877412.jpg"
PH_POTATO_AIR = "File:Farms in the Aroostook County, Me., Oct. 1940 - potatoes LCCN2017877406.jpg"
PH_CARIBOU = "File:Caribou, Maine.jpg"
PH_STJOHN = "File:St. John River (36390577074).jpg"
PH_MAD_SIGN = "File:Madawaska, Maine bilingual welcome sign.jpg"
PH_MADAWASKA = "File:Madawaska, Maine.jpg"
PH_CROSS = "File:MadawaskaME AcadianLandingCross.jpg"
PH_LORING_AIR = "File:Loring Air Force Base.jpg"
PH_LORING_WSA = "File:LORING AFB WSA 20.jpg"
PH_LORING_HANGAR = "File:Loring Air Force Base 1982 - Hangar - panoramio.jpg"
PH_LORING_NOSE = "File:Nose Hangar, Limestone Air Force Base, Limestone, Maine - DPLA - 83b68f60d44007fcd737e00c1b6e9cf6.jpg"
PH_LORING_LINE = "File:Loring Flightline.jpg"
PH_LORING_WEST = "File:Loring west side.jpg"
PH_MOOSEHEAD = "File:Moosehead Lake.jpg"
PH_PORTLAND_AIR = "File:Portland, Maine, aerial photograph.jpg"
PH_PORTLAND = "File:Portland, Maine skyline aerial view.jpg"
PH_HOULTON = "File:Houlton, Maine.jpg"
PH_BUNKERS = "File:Bunkers at Aroostook NWR (8617376872).jpg"
PH_DISPUTED_MAP = "File:Map of the disputed territory reduced from the original of Messrs Featherstonhaugh & Mudge - British commissioners - btv1b8495488t.jpg"
PH_CHESUNCOOK = "File:Chesuncook Lake.jpg"
PH_PRESQUE = "File:Presque Isle, Maine.jpg"
PH_BANGOR = "File:Bangor, Maine.jpg"
PH_WOODSMEN = "File:Sit Anywhere Woodsman relaxing after lunch during the spring pulpwood drive on the Brown Company timber holdings in Maine. May 1943. (40944955493).jpg"
PH_ANWR_WINTER = "File:Aroostook National Wildlife Refuge winter.jpg"
PH_ANWR_AIR = "File:Aroostook national wildlife refuge forestry.jpg"
PH_BAXTER_GOV = "File:P.P. Baxter LCCN2014712097.jpg"
PH_MOOSEMARSH = "File:Sunset over Moosemarsh at Aroostook National Wildlife Refuge (50584621962).jpg"
PH_HOULTON_OLD = "File:Houlton, Me. Aroostook County seat. LOC 75693242.jpg"

PORTLAND, BANGOR = place("Portland", -70.26, 43.66), place("Bangor", -68.77, 44.80)
AUGUSTA = place("Augusta", -69.78, 44.31)
MILLI = place("Millinocket", -68.71, 45.66)
CARIBOU, PRESQUE = place("Caribou", -68.01, 46.86), place("Presque Isle", -68.02, 46.68)
HOULTON, FORTKENT = place("Houlton", -67.84, 46.13), place("Fort Kent", -68.59, 47.25)
MADAWASKA, LIMESTONE = place("Madawaska", -68.33, 47.36), place("Limestone", -67.83, 46.91)
KATAHDIN = place("Katahdin", -68.921, 45.904, "Katahdin", "site")
STDAVID = place("St. David", -68.23, 47.33, "St. David, 1785", "site")
MARSHILL = place("Mars Hill", -67.88, 46.52, "Mars Hill", "site")
LORING = place("Loring", -67.89, 46.95, "Loring Air Force Base", "site")
NWA = place("Northwest Aroostook", -69.6, 46.95, "Northwest Aroostook: 12 people", "site")
T3R13 = place("T3 R13 WELS", -69.386, 45.899, "T3 R13 WELS", "site")
QUEBEC = place("Quebec City", -71.21, 46.81)
GOLDEN = {"from": [-68.71, 45.66], "via": [[-68.95, 45.78], [-69.18, 45.88], [-69.40, 45.90], [-69.70, 45.95], [-70.0, 46.0]], "to": [-70.27, 46.07],
          "mode": "line", "color": "accent", "seconds": 2.0, "label": "The Golden Road"}
ALLAGASH = {"from": [-69.30, 46.12], "via": [[-69.29, 46.49], [-69.37, 46.62], [-69.26, 46.88]], "to": [-69.08, 47.08],
            "mode": "line", "color": "blue", "seconds": 2.0, "label": "Allagash Wilderness Waterway"}
US_CLAIM = {"from": [-67.79, 45.94], "via": [[-67.79, 48.0], [-69.2, 47.65], [-70.3, 46.6]], "to": [-71.08, 45.30],
            "mode": "line", "color": "blue", "seconds": 2.0, "label": "American claim (roughly)"}
UK_CLAIM = {"from": [-67.79, 45.94], "via": [[-67.80, 46.52], [-69.0, 46.15], [-70.2, 45.75]], "to": [-71.08, 45.30],
            "mode": "line", "color": "red", "seconds": 2.0, "label": "British claim (roughly)"}
ARNOLD = {"from": [-69.77, 44.31], "via": [[-69.88, 45.0], [-70.25, 45.15], [-70.55, 45.40], [-70.88, 45.55], [-70.85, 46.2]], "to": [-71.21, 46.81],
          "mode": "line", "color": "red", "seconds": 2.5, "label": "Arnold's march, 1775"}

PH_KWW = "File:Katahdin Woods and Waters National Monument on August 17, 2024 visit by the United States Department of the Interior - 19.jpg"
SIPAYIK = place("Sipayik", -67.03, 44.95, "Sipayik (Pleasant Point)", "site")
INDIAN_ISLAND = place("Indian Island", -68.66, 44.95, "Indian Island", "site")

chapters = [
    {"title": "Half a State With No Towns", "mood": "curious", "paragraphs": [
        P("Maine is the corner of the United States that pushes up into Canada. It is nearly as big as the other five New England states put together. It is also the only state that borders just one other state. About one point four million people live there, and most of them live in the south, near the coast. The two southern counties around Portland hold almost four in ten Mainers on about a twentieth of the land. Go north and it changes. At night, from orbit, the north of Maine is almost completely dark.",
          m(0, v(NENG, highlight=["Maine@red"])),
          stat("It is nearly as", "35,380 SQ MI", "Maine's total area; the other five New England states together: 36,608", "US Census Bureau state areas (our sum)"),
          m("It is also the", v(NENG, highlight=["Maine@red", "New Hampshire@accent"])),
          photo("About one point four", PH_PORTLAND, "Portland, Maine's largest city"),
          sat("and most of them", -70.22, 43.68, 0.25, "Portland and Casco Bay"),
          paint("The two southern counties", SOUTH + "@accent", places=[PORTLAND]),
          stat("on about a twentieth", "38 %", "Mainers living in Cumberland and York counties, on about 6 % of the land (2020)", GAZ),
          m("Go north and it", v(NORTH)),
          m("At night, from orbit", v(ME, layer="night", places=[PORTLAND, BANGOR]))),
        P("Almost half of Maine has no town government at all. No mayor, no town council, no town. The Census calls it unorganized territory: more than fourteen thousand square miles of land, bigger than the whole state of Maryland. At the last census about eight thousand three hundred people lived in all of it. That is fewer than one person per square mile. The biggest single piece, in the northwest, covers more than two and a half thousand square miles, more than the whole state of Delaware. Twelve people live there.",
          paint(0, UT + "@red"),
          sat("No mayor, no town", -69.55, 46.55, 0.25, "Unorganized territory, northern Maine"),
          stat("more than fourteen thousand", "46 %", "Share of Maine's land with no town government: 14,264 square miles", GAZ),
          stat("At the last census", "8,269", "People living in all of Maine's unorganized territory, 2020 census (our sum)", GAZ),
          sat("That is fewer than", -69.95, 46.3, 0.2, "Seboomook Lake unorganized territory"),
          m("The biggest single piece", v(ME, highlight=[UT + "@red"], places=[NWA])),
          sat("more than the whole", -69.45, 47.1, 0.25, "Northwest Aroostook"),
          sat("Twelve people live there", -69.75, 46.95, 0.3, "Northwest Aroostook: twelve people")),
        P("It is not that the land is worthless. It is the most forested state in the country. Britain and America nearly went to war over this forest. A town up here lost nearly nine of every ten people. And one man bought its highest mountain and gave it away, on one condition. So why does almost nobody live in northern Maine? There are five reasons. The first is that the land was sold before anyone got there.",
          sat(0, -69.2, 46.2, 0.4, "The North Woods"),
          sat("It is the most", -69.6, 45.75, 0.2, "Forest and lakes near Moosehead in October", date="2023-09-25/2023-10-12"),
          photo("Britain and America nearly", PH_STJOHN, "The St. John River, on the border with Canada"),
          photo("A town up here", PH_LORING_NOSE, "Limestone, Maine, in the 1950s"),
          photo("And one man bought", PH_KAT, "Katahdin, Maine's highest mountain"),
          paint("So why does almost", UT + "@red", places=[PORTLAND, BANGOR]),
          sat("There are five reasons", -68.9, 46.9, 0.3, "Forest east of the Allagash in winter", date="2024-02-01/2024-03-15"),
          ask=("So why does almost", "Why is northern Maine empty?")),
    ]},
    {"title": "Sold Before It Was Settled", "mood": "curious", "paragraphs": [
        P("Reason one. The land was sold before anyone got there. After the American Revolution, Maine was not a state. It belonged to Massachusetts, and Massachusetts was broke. It owed a war debt it could not pay. What it did have was millions of acres of forest in the north. So it sold them. In 1786 it even ran a lottery: fifty townships, cut into two thousand seven hundred and sixty lots. A Philadelphia banker named William Bingham ended up with two tracts of about a million acres each.",
          m(0, v(NENG, highlight=["Massachusetts@accent", "Maine@red"])),
          sat("After the American Revolution", -69.4, 45.6, 0.6, "Forest west of Moosehead Lake"),
          m("It belonged to Massachusetts", v({"lon": -71.6, "lat": 42.4, "span": 4.5}, highlight=["Massachusetts@red"])),
          sat("What it did have", -69.0, 45.4, 0.35, "Forest north of the Penobscot in October", date="2023-09-25/2023-10-12"),
          stat("In 1786 it even", "2,760 LOTS", "Fifty townships of Maine forest, sold by lottery, 1786", MA_ARCH),
          sat("cut into two thousand", -68.95, 45.1, 0.4, "Forest in central Maine in October", date="2023-09-25/2023-10-12"),
          sat("A Philadelphia banker named", -69.9, 45.1, 0.5, "The upper Kennebec, part of Bingham's purchase"),
          stat("ended up with two", "2 M ACRES", "William Bingham's two Maine tracts, about a million acres each", "Wikipedia, Bingham Purchase")),
        P("Surveyors cut the woods into a grid of squares, and many of those squares never got names. Look at a map of northern Maine today and you still see them: T3 R13 WELS. Township three, range thirteen, west of the east line of the state. A grid of numbers where, in other states, there would be towns. The state itself runs these places. There is no one else to do it.",
          m(0, v({"lon": -69.4, "lat": 46.0, "span": 1.6}, places=[T3R13])),
          sat("and many of those", -69.7, 46.1, 0.25, "Numbered townships west of Chesuncook Lake"),
          sat("Look at a map", -69.386, 45.899, 0.08, "T3 R13 WELS"),
          sat("Township three, range thirteen", -69.42, 45.93, 0.04, "Inside T3 R13 WELS"),
          sat("A grid of numbers", -69.0, 46.6, 0.3, "Logging roads and cutting blocks"),
          photo("The state itself runs", PH_LOGROAD, "A private logging road")),
        P("When Maine became a state in 1820, it split the remaining public land with Massachusetts, and both kept selling. In 1853 Maine bought out what Massachusetts still held, about one point two million acres, and kept on selling too. The buyers were not families looking for farms. They were lumbermen, and later paper companies. For most of the twentieth century, a dozen or so companies and families owned around twelve million acres of northern Maine. One of them, Great Northern Paper, held more than two million acres by the 1940s.",
          paint(0, "Maine@red", view=NENG),
          stat("it split the remaining", "1820", "Maine becomes a state and splits the public land with Massachusetts", "Maine State Archives"),
          stat("In 1853 Maine bought", "1.2 M ACRES", "Land Maine bought back from Massachusetts in 1853", "Maine State Archives; Colby College"),
          sat("and kept on selling", -68.5, 45.7, 0.3, "Forest north of Millinocket in October", date="2023-09-25/2023-10-12"),
          sat("The buyers were not", -68.8, 45.95, 0.3, "Forest east of Katahdin"),
          sat("They were lumbermen, and", -69.15, 45.85, 0.25, "Ripogenus Dam, built by Great Northern Paper"),
          stat("For most of the", "~12 M ACRES", "Northern Maine owned by about a dozen companies and families, most of the 1900s", "Natural Resources Council of Maine; press reports"),
          sat("around twelve million acres", -69.3, 46.7, 0.4, "Company forest, northern Maine in October", date="2023-09-25/2023-10-12"),
          photo("One of them, Great", PH_WBRANCH, "The West Branch of the Penobscot below Katahdin")),
        P("Those owners have changed, but the pattern has not. From the 1990s the paper companies began selling their land, and much of it went to investment funds, pension funds and timber investment groups. Some old owners stayed. One family company, Seven Islands, still manages about a million acres for dozens of members of the Pingree family. And in 2016 a single family trust bought nearly three hundred thousand acres of the north woods in one deal. Up here, forest changes hands in blocks the size of whole counties elsewhere.",
          photo(0, PH_CHESUNCOOK, "Chesuncook Lake, in the North Woods"),
          sat("From the 1990s the", -69.6, 46.3, 0.2, "Working forest, northern Maine in winter", date="2024-02-01/2024-03-15"),
          sat("and much of it", -69.85, 46.2, 0.3, "Working forest near the Quebec border in October", date="2023-09-25/2023-10-12"),
          stat("One family company, Seven", "~1 M ACRES", "Forest managed by Seven Islands Land Company for the Pingree family", "Seven Islands Land Company"),
          sat("for dozens of members", -69.0, 46.85, 0.25, "Forest in the Allagash country in winter", date="2024-02-01/2024-03-15"),
          stat("And in 2016 a", "~290,000 ACRES", "North Woods land bought by one family trust in 2016", "Bangor Daily News, November 2016"),
          sat("of the north woods", -68.75, 46.25, 0.25, "Forest west of the Aroostook valley in October", date="2023-09-25/2023-10-12"),
          sat("Up here, forest changes", -69.55, 46.75, 0.25, "Cutting blocks, northern Maine")),
        P("Companies do not build towns where they do not need people to live. They build roads. In 1971 Great Northern finished the Golden Road, almost a hundred miles of private gravel from its mill at Millinocket west to the Quebec border, built for log trucks. That same year the landowners set up a group called North Maine Woods to run the gates. There are nineteen of them. Today about three and a half million acres are managed that way. Every road inside is private. To drive in, you stop at a checkpoint and pay a fee, as you would at a park. Except this park is somebody's tree farm.",
          sat(0, -69.62, 45.93, 0.12, "A logging road in the North Woods"),
          m("In 1971 Great Northern", v({"lon": -69.5, "lat": 45.9, "span": 2.2}, routes=[GOLDEN], places=[MILLI])),
          sat("from its mill at", -69.9, 45.98, 0.1, "The Golden Road, heading west"),
          stat("That same year the", "19 GATES", "Checkpoints into the North Maine Woods, run by the landowners since 1971", "North Maine Woods Inc."),
          sat("There are nineteen of", -68.85, 46.48, 0.06, "A North Maine Woods road"),
          stat("Today about three and", "3.5 M ACRES", "Private forest behind the North Maine Woods gates", "North Maine Woods Inc."),
          sat("Every road inside is", -69.37, 46.32, 0.1, "A logging road junction in October", date="2023-09-25/2023-10-12"),
          sat("To drive in, you", -69.3, 46.0, 0.08, "A gravel road in the North Woods in winter", date="2024-02-01/2024-03-15"),
          sat("Except this park is", -69.0, 46.35, 0.15, "Cutting blocks on private forest in winter", date="2024-02-01/2024-03-15")),
        P("Before any of it was sold, this was Wabanaki land: the Penobscot, the Passamaquoddy, the Maliseet and the Mi'kmaq. In the 1970s two of those nations went to court and claimed about twelve million acres, nearly two thirds of the state. In 1980 the federal government settled for eighty-one and a half million dollars, mostly so the tribes could buy back about three hundred thousand acres. So half of Maine was never really a place where people settled. It was a place where wood was grown. But first, somebody had to decide which country it was in.",
          sat(0, -68.66, 44.95, 0.08, "Indian Island, home of the Penobscot Nation"),
          sat("the Penobscot, the Passamaquoddy", -67.03, 44.95, 0.08, "Sipayik, Passamaquoddy land on Passamaquoddy Bay"),
          paint("In the 1970s two", "Maine@red", view=EAST, places=[INDIAN_ISLAND, SIPAYIK]),
          stat("and claimed about twelve", "12 M ACRES", "Land claimed by the Passamaquoddy and Penobscot: nearly two thirds of Maine", "NLM Native Voices; Maine Atlas"),
          stat("In 1980 the federal", "$81.5 M", "Maine Indian Claims Settlement Act, 1980: money to buy back about 300,000 acres", "US Public Law 96-420; Maine Atlas"),
          sat("mostly so the tribes", -68.55, 45.85, 0.2, "Forest along the East Branch of the Penobscot"),
          paint("So half of Maine", UT + "@red", view=NORTH),
          sat("It was a place", -69.75, 46.4, 0.4, "Forest near the Quebec border in October", date="2023-09-25/2023-10-12"),
          m("But first, somebody had", v(EAST, highlight=["New Brunswick@accent", "Quebec@accent"]))),
    ]},
    {"title": "The Border Nobody Could Draw", "mood": "tension", "paragraphs": [
        P("Reason two. Nobody knew where the border was. The treaty that ended the Revolution in 1783 drew the line between the United States and British Canada with words, not surveys: north from the source of the St. Croix River to the highlands that divide the rivers running to the St. Lawrence from those running to the Atlantic. Historians later called it so badly worded that it could not be turned into a real line on the ground.",
          m(0, v(EAST, highlight=["Maine@red", "New Brunswick@accent"])),
          m("north from the source", v(EAST, routes=[{"from": [-67.79, 45.94], "to": [-67.79, 47.06], "mode": "line", "color": "red", "seconds": 1.5, "label": "North from the St. Croix"}])),
          sat("the highlands that divide", -70.1, 46.4, 0.5, "The highlands on the Quebec border"),
          clip("Historians later called it", "...the Treaty of 1783 was so badly worded that it could not be translated into a practical topographical boundary.", "Keenleyside and Brown, Canada and the United States", highlight="so badly worded"),
          photo("could not be turned", PH_DISPUTED_MAP, "The disputed territory, a British commissioners' map")),
        P("Americans read it one way, the British another. The Americans said the line ran almost to the St. Lawrence. The British said it stopped near a hill in Aroostook called Mars Hill. Between the two readings lay about twelve thousand square miles of forest that both countries claimed. In 1831 they asked the King of the Netherlands to settle it. He split the land, roughly two thirds to the Americans and one third to the British. The United States turned his answer down.",
          m(0, v(EAST, routes=[US_CLAIM])),
          m("The British said it", v(EAST, routes=[US_CLAIM, UK_CLAIM], places=[MARSHILL])),
          stat("Between the two readings", "12,000 SQ MI", "Forest claimed by both Britain and the United States", "Webster-Ashburton Treaty totals (7,015 + 5,012 sq mi)"),
          sat("In 1831 they asked", -68.9, 47.0, 0.4, "The disputed forest, between the two claims"),
          chart("He split the land", "The Dutch king's award, 1831 (rejected)", "square miles", [["United States", 7908], ["Britain", 4119]], "Wikipedia, Aroostook War", highlight=0),
          m("The United States turned", v(EAST, routes=[UK_CLAIM, US_CLAIM], places=[MARSHILL, BANGOR]))),
        P("People did settle the edge of it. In June 1785 a group of Acadian families, French speakers whose people had been expelled from Nova Scotia by the British a generation earlier, paddled up the St. John River and raised a wooden cross where they landed, near today's St. David. Five years later a count found a hundred and seventy-four people in the upper valley. Their descendants still live along that river, and many still speak French.",
          sat(0, -68.3, 47.33, 0.15, "The St. John River at St. David"),
          stat("In June 1785 a", "JUNE 1785", "Acadian families land on the upper St. John River", "acadian.org; University of Maine at Fort Kent"),
          m("French speakers whose people", v(EAST, highlight=["Nova Scotia@accent"], places=[STDAVID])),
          sat("paddled up the St.", -68.05, 47.22, 0.2, "The St. John River below Madawaska"),
          photo("raised a wooden cross", PH_CROSS, "The Acadian landing cross, St. David"),
          stat("Five years later a", "174", "People in the upper St. John Valley, 1790 count", "Census of Lower Canada, via acadian.org"),
          photo("Their descendants still live", PH_MADAWASKA, "Madawaska, on the St. John"),
          photo("many still speak French", PH_MAD_SIGN, "Bienvenue: the welcome sign in Madawaska")),
        P("By the 1830s, lumbermen from both sides were cutting the same trees. In February 1839 Maine sent an armed posse north from Bangor to throw out the New Brunswick loggers. The loggers seized Maine's land agent in the middle of the night. Maine called up its militia. Britain moved soldiers in. In Washington, Congress authorized fifty thousand men and ten million dollars in case of war. It is called the Aroostook War. Nobody was killed in battle. About thirty-eight men died of accidents and disease. In March, General Winfield Scott arrived and talked both sides down. That autumn the US Army began building Fort Kent, on the St. John, to hold the line.",
          sat(0, -68.6, 46.85, 0.3, "The Aroostook valley"),
          photo("In February 1839 Maine", PH_BANGOR, "Bangor, where the posse set out"),
          m("to throw out the", v({"lon": -68.4, "lat": 46.1, "span": 3.0}, routes=[{"from": [-68.77, 44.80], "via": [[-68.6, 45.5], [-68.3, 46.1]], "to": [-68.1, 46.75], "mode": "line", "color": "red", "seconds": 2.0, "label": "The posse, February 1839"}], places=[BANGOR])),
          sat("The loggers seized Maine's", -68.25, 46.7, 0.2, "The Aroostook River"),
          m("Maine called up its", v(EAST, highlight=["Maine@accent", "New Brunswick@red"])),
          stat("In Washington, Congress authorized", "50,000 MEN", "Authorized by Congress, with $10 million, in case of war over Maine, 1839", "US Congress, 1839"),
          paint("It is called the", AROO + "@red", view=EAST),
          stat("Nobody was killed in", "0 BATTLES", "About 38 deaths in the Aroostook War, all from accident and disease", "Aroostook War records"),
          photo("In March, General Winfield", PH_PRESQUE, "Presque Isle, Aroostook County"),
          sat("That autumn the US", -68.59, 47.25, 0.08, "Fort Kent, begun in 1839")),
        P("Three years later, in August 1842, Daniel Webster and Lord Ashburton split the difference. The United States got about seven thousand square miles, Britain about five thousand. The new line followed the St. John River for much of the way, which is why Maine's top edge looks the way it does. But a line on a map does not fill a forest. Even after 1842, almost nobody moved up there. The next reason is the simplest one: the weather.",
          m(0, v(EAST, routes=[US_CLAIM, UK_CLAIM], highlight=["Maine@red"])),
          chart("The United States got", "Webster-Ashburton Treaty, 1842: the disputed forest", "square miles", [["United States", 7015], ["Britain", 5012]], "Webster-Ashburton Treaty"),
          sat("The new line followed", -68.5, 47.27, 0.4, "The St. John River: Canada above, Maine below"),
          sat("But a line on", -69.3, 47.15, 0.5, "The forest south of the St. John"),
          sat("The next reason is", -68.75, 47.05, 0.2, "Winter forest, northern Aroostook", date="2024-02-01/2024-03-15")),
    ]},
    {"title": "Long Winters, Short Summers", "mood": "tension", "paragraphs": [
        P("Reason three. It is cold, and the summer is short. This forest has always been hard on people. In 1775, early in the Revolution, Benedict Arnold marched about eleven hundred men up the Kennebec to attack Quebec. He planned on a hundred and eighty miles. It turned out to be about three hundred and fifty. The men got lost in the swamps of the height of land, on today's Quebec border, and on the far side rapids smashed their boats and the food ran out. More than a third of the men turned back. About six hundred reached the St. Lawrence, half-starved.",
          sat(0, -70.2, 45.2, 0.5, "The Dead River, on Arnold's route"),
          m("In 1775, early in", v({"lon": -70.4, "lat": 45.6, "span": 3.4}, routes=[ARNOLD], places=[AUGUSTA, QUEBEC])),
          chart("He planned on a", "Arnold's march to Quebec, 1775", "miles", [["Planned", 180], ["Real route", 350]], "Wikipedia, Benedict Arnold's expedition to Quebec", reveal=["It turned out to"], highlight=1),
          sat("The men got lost", -70.6, 45.42, 0.3, "The height of land on the Quebec border"),
          stat("More than a third", "~600 OF 1,100", "Arnold's men who reached the St. Lawrence, November 1775", "Benedict Arnold's expedition to Quebec")),
        P("Up at Caribou, in Aroostook County, the average January day is under twelve degrees Fahrenheit. It once hit minus forty-one. About ten feet of snow falls in an average winter. In the winter of 2007 and 2008 it was more than sixteen feet. And the time between the last spring frost and the first autumn frost is about a hundred and thirty days. That is just over four months to grow anything.",
          photo(0, PH_CARIBOU, "Caribou, Maine"),
          stat("the average January day", "11.7 °F", "Average January day in Caribou, 1991-2020", NWS),
          sat("About ten feet of", -68.0, 46.85, 0.25, "Caribou in late winter", date="2024-02-01/2024-03-15"),
          photo("In the winter of", PH_ANWR_WINTER, "Winter in Aroostook County"),
          photo("And the time between", PH_PANCAKE, "Ice forming on the Allagash River"),
          stat("is about a hundred", "130 DAYS", "Average time between the last spring frost and the first autumn frost at Caribou", NWS),
          sat("That is just over", -67.98, 46.9, 0.1, "Caribou's fields in July", date="2024-07-01/2024-08-31")),
        P("And most of the north was never farmland anyway. It is rolling hills, lakes and bogs, and what grows best is spruce and fir. Government climate scientists say Maine's growing season has been getting longer, but up north it is still short. By the Forest Service's count, about eighty-nine percent of Maine's land is forest. That is the highest share of any state.",
          sat(0, -69.05, 46.35, 0.2, "Bogs and lakes in the North Woods"),
          photo("It is rolling hills", PH_MOOSEHEAD, "Moosehead Lake"),
          sat("and what grows best", -69.3, 45.55, 0.1, "Spruce and fir near Moosehead Lake"),
          clip("Government climate scientists say", "The growing season in Maine has also lengthened.", NOAA, highlight="lengthened"),
          sat("but up north it", -68.6, 47.2, 0.2, "Northern Aroostook"),
          stat("By the Forest Service's", "89 %", "Share of Maine's land that is forest, the most of any state", FS),
          sat("That is the highest", -69.9, 46.6, 0.3, "Forest near the Quebec line")),
        P("There was one exception. In the far northeast, around Presque Isle, Caribou and Houlton, the land is gentler, and one crop loved the cool summers: potatoes. The first was planted near Houlton in 1807. When the railroad arrived late in the 1800s, Aroostook became a potato empire. Much of the early crop went to starch factories. Schools closed in autumn so children could help bring in the crop. Many high schools in Aroostook still close for up to two weeks every fall for the harvest. By 1947 Maine was growing potatoes on a hundred and eighty-six thousand acres, and it led the country in potatoes.",
          paint(0, AROO + "@accent", view=ME, places=[PRESQUE, CARIBOU, HOULTON]),
          sat("the land is gentler", -68.0, 46.72, 0.15, "Potato fields around Presque Isle"),
          photo("and one crop loved", PH_POTATO_AIR, "Aroostook potato country, October 1940"),
          photo("The first was planted", PH_HOULTON_OLD, "Houlton, the county seat, in the 1890s"),
          sat("When the railroad arrived", -68.02, 46.69, 0.08, "Presque Isle, on the Aroostook River"),
          stat("Much of the early", "28,000 ACRES", "Aroostook potatoes in 1890, much of the crop for starch", "Aroostook local histories (The County)"),
          photo("Schools closed in autumn", PH_POTATO_KIDS, "Children picking potatoes near Caribou, 1940"),
          stat("Many high schools in", "2 WEEKS", "Harvest break at most Aroostook high schools, 2024", "Bangor Daily News, 2024"),
          stat("By 1947 Maine was", "186,000 ACRES", "Potatoes planted in Maine in 1947", "Maine Atlas; Bangor Daily News"),
          sat("and it led the", -67.85, 46.55, 0.1, "Fields near Mars Hill")),
        P("Then the potato moved west. Idaho, with irrigation, bigger fields and better shipping, passed Maine in 1957. Maine still grows a lot of potatoes, almost all of them in Aroostook, but by 2021 the fields covered about fifty-eight thousand acres. Machines replaced the hands that picked them. So the north had long winters, short summers, and its one great crop found a better home. What kept people there was the work in the woods and the mills. And then that went too.",
          m(0, v({"lon": -93.0, "lat": 43.5, "span": 48}, highlight=["Idaho@accent", "Maine@red"]), v({"lon": -93.5, "lat": 43.8, "span": 44}, at="passed Maine in", highlight=["Idaho@accent", "Maine@red"])),
          chart("but by 2021 the", "Potato acres planted in Maine", "acres", [["1947", 186000], ["2021", 58000]], "Maine Atlas; USDA via Bangor Daily News", highlight=1),
          sat("Machines replaced the hands", -67.95, 46.62, 0.06, "A potato farm near Presque Isle"),
          photo("So the north had", PH_HOULTON, "Houlton today"),
          sat("What kept people there", -68.575, 45.625, 0.05, "East Millinocket")),
    ]},
    {"title": "The Jobs Left", "mood": "tension", "paragraphs": [
        P("Reason four. The jobs left. For more than a century, logs from the north woods traveled by water. Every spring, crews drove them down the rivers on the snowmelt, all the way to the mills. A law passed in 1971 banned the drives after 1976, and by the mid-1970s the last ones had run down the Kennebec. The last big drive, in November 1975, brought television crews from around the country. Trucks took over, on private roads, and fewer men were needed in the woods.",
          sat(0, -69.72, 45.62, 0.25, "The Kennebec leaves Moosehead Lake"),
          photo("Every spring, crews drove", PH_ALLA_FALLS, "Falls on the Allagash"),
          stat("A law passed in", "1976", "The last year river log drives were allowed in Maine (law of 1971)", "Maine law of 1971, via Central Maine and Down East"),
          sat("the last ones had", -69.88, 45.02, 0.2, "The Kennebec River near Bingham"),
          photo("The last big drive", PH_WOODSMEN, "Woodsmen on a spring pulpwood drive, Maine, 1943"),
          sat("Trucks took over, on", -69.18, 45.88, 0.06, "The Golden Road at Ripogenus Dam")),
        P("Then came a caterpillar. In the 1970s and 80s the spruce budworm ate its way through the spruce and fir of eastern Canada and northern Maine, across an estimated hundred and thirty-six million acres. Planes sprayed Maine's forest with insecticide, three and a half million acres in 1976 alone. Maine lost an estimated twenty to twenty-five million cords of wood, about a fifth of its spruce and fir. Whole stands of dead fir had to be cut in a hurry, and the companies kept cutting.",
          paint(0, UT + "@red", view=EAST),
          stat("across an estimated hundred", "136 M ACRES", "Spruce budworm outbreak, eastern Canada and northern Maine, 1970s-80s", "Maine Forest Service"),
          sat("Planes sprayed Maine's forest", -69.55, 46.05, 0.3, "Spruce and fir forest, northern Maine in October", date="2023-09-25/2023-10-12"),
          stat("Maine lost an estimated", "21 %", "Share of Maine's spruce and fir lost to the budworm outbreak", "Maine Spruce Budworm Task Force"),
          sat("about a fifth of", -69.45, 46.5, 0.15, "Spruce and fir today, northern Maine in winter", date="2024-02-01/2024-03-15"),
          sat("Whole stands of dead", -69.25, 46.2, 0.12, "Regrowth on old cutting blocks")),
        P("The paper mills were the biggest employers. In 1899 Great Northern began building a mill on the Penobscot River at Millinocket. When it opened the next year it was the world's largest paper mill, and a town grew around it in the forest. By 1970 Millinocket had seven thousand seven hundred people. Then newspapers shrank, owners changed, and the company went bankrupt in 2003. By 2014 the mills at Millinocket and East Millinocket had both closed. In 2020 Millinocket had about four thousand one hundred people.",
          sat(0, -68.71, 45.65, 0.06, "Millinocket"),
          photo("and a town grew", PH_MILL_HOMES, "Mill-era houses in Millinocket"),
          stat("By 1970 Millinocket had", "7,742", "People in Millinocket at the 1970 census", CENSUS),
          photo("Then newspapers shrank, owners", PH_EMILL, "East Millinocket and its mill"),
          stat("and the company went", "2003", "Great Northern Paper goes bankrupt", "Wikipedia, Millinocket"),
          sat("By 2014 the mills", -68.70, 45.648, 0.04, "Millinocket today"),
          chart("In 2020 Millinocket had", "People in Millinocket", "census", [["1970", 7742], ["2020", 4104]], CENSUS, highlight=1)),
        P("And then the Cold War ended. In 1953 the Air Force opened a base near Limestone, in the far northeast corner of Maine. It was described as the closest point in the continental United States to Europe, and for a bomber base that was the point. Its main runway was more than two miles long. Its bombers were B-36s at first, then B-52s. It also had the first site in the country built just to store and assemble atomic weapons. In 1988 about three thousand eight hundred airmen and a thousand civilians worked there.",
          photo(0, PH_LORING_AIR, "Loring Air Force Base from above"),
          sat("In 1953 the Air", -67.885, 46.95, 0.12, "Loring's runway"),
          m("in the far northeast", v(ME, places=[LORING, PORTLAND])),
          m("It was described as", v({"lon": -38.0, "lat": 50.0, "span": 95}, places=[LORING, place("London", -0.13, 51.51)])),
          sat("Its main runway was", -67.89, 46.94, 0.05, "Loring's runway, 12,100 feet"),
          photo("Its bombers were B-36s", PH_LORING_NOSE, "A bomber in a nose hangar at Limestone, 1950s"),
          photo("It also had the", PH_LORING_WSA, "A storage bunker in Loring's weapons area"),
          photo("In 1988 about three", PH_LORING_LINE, "Loring's flight line")),
        P("In 1991 a commission decided the Air Force had more bomber bases than it needed. Loring closed on the thirtieth of September 1994. Limestone had over thirteen thousand people in 1960. By 2000 it had two thousand three hundred. In 2020, about fifteen hundred. Aroostook County as a whole peaked at a hundred and six thousand people in 1960. In 2020 it had sixty-seven thousand.",
          photo(0, PH_LORING_HANGAR, "Loring's great hangar"),
          stat("Loring closed on the", "30 SEP 1994", "Loring Air Force Base closes", "Base Realignment and Closure Commission, 1991"),
          chart("Limestone had over thirteen", "People in Limestone, Maine", "census", [["1960", 13102], ["2000", 2361], ["2020", 1526]], CENSUS, reveal=["By 2000 it had", "In 2020, about"], highlight=2),
          paint("Aroostook County as a", AROO + "@red", places=[CARIBOU, PRESQUE, HOULTON]),
          chart("In 2020 it had", "People in Aroostook County", "census", [["1960", 106064], ["2020", 67105]], CENSUS, highlight=1)),
        P("When it closed, the region lost thousands of military and civilian jobs. A state estimate had put nearly a fifth of the local economy on the base. Today part of the old base is an industrial park, and part of it is the Aroostook National Wildlife Refuge. The bunkers that once held the bombs are still there, in the grass.",
          sat(0, -67.87, 46.96, 0.06, "The former Loring base"),
          stat("A state estimate had", "19 %", "Share of the regional economy tied to Loring, state planning office estimate", "Maine State Planning Office, via press reports"),
          sat("Today part of the", -67.86, 46.93, 0.04, "The old base buildings, now an industrial park"),
          photo("and part of it", PH_ANWR_AIR, "Aroostook National Wildlife Refuge"),
          photo("The bunkers that once", PH_BUNKERS, "Old weapons bunkers, Aroostook National Wildlife Refuge")),
        P("So the work left. But some of the emptiness of northern Maine is no accident at all. Some of it was chosen.",
          sat(0, -68.95, 45.95, 0.15, "Katahdin from above")),
    ]},
    {"title": "Wild on Purpose", "mood": "calm", "paragraphs": [
        P("Reason five. People decided to keep it wild. In 1846 Henry David Thoreau went up Katahdin, Maine's highest mountain. Today it is the northern end of the Appalachian Trail, more than two thousand miles from Georgia. Coming down, he wrote that up there he had felt the presence of a force not bound to be kind to man. Contact, he wrote. Who are we? Where are we? The mountain stayed with one man in particular.",
          sat(0, -68.921, 45.904, 0.08, "Katahdin, 5,267 feet"),
          m("Today it is the", v({"lon": -76.5, "lat": 40.0, "span": 20}, routes=[{"from": [-84.19, 34.63], "via": [[-81.0, 36.5], [-78.0, 39.0], [-75.0, 41.5], [-72.8, 43.8], [-70.9, 44.8]], "to": [-68.92, 45.90], "mode": "line", "color": "accent", "seconds": 2.0, "label": "Appalachian Trail (roughly)"}])),
          sat("Coming down, he wrote", -68.88, 45.92, 0.1, "Katahdin's tableland"),
          clip("the presence of a", "There was clearly felt the presence of a force not bound to be kind to man.", "Henry David Thoreau, The Maine Woods", highlight="not bound to be kind to man"),
          sat("Contact, he wrote. Who", -68.9, 45.93, 0.15, "The Katahdin massif"),
          photo("The mountain stayed with", PH_KAT, "Katahdin")),
        P("Percival Baxter, who became governor of Maine in 1921, wanted the state to make a park around Katahdin. That year the bill for it failed. So he did it himself. He bought about six thousand acres, Katahdin included, and in 1931 gave it to Maine on one condition: that it stay forever in its natural wild state. He kept buying and giving until 1962. More than two hundred thousand acres in all. Inside the park there is still no electricity, no running water and no paved road.",
          photo(0, PH_BAXTER_GOV, "Percival Baxter"),
          m("wanted the state to", v({"lon": -68.95, "lat": 46.05, "span": 0.9}, places=[KATAHDIN, MILLI])),
          sat("So he did it", -68.95, 45.92, 0.2, "Katahdin and the land around it"),
          stat("and in 1931 gave", "1931", "Percival Baxter gives Katahdin to Maine, on condition it stay wild", "Baxter State Park; Maine Legislature"),
          sat("that it stay forever", -68.86, 46.15, 0.25, "Baxter State Park, the northern half"),
          stat("He kept buying and", "201,018 ACRES", "Percival Baxter's gifts to Maine, 1931 to 1962", "Baxter's letter to the Maine Legislature, 1963"),
          photo("Inside the park there", PH_BAXTER, "Entering Baxter State Park")),
        P("In 1966 Maine voters protected the Allagash, ninety-two miles of lakes and river through the heart of the north woods. The bond to pay for it passed with sixty-eight percent of the vote. In 1970 it became the first state-run river in the national system of wild and scenic rivers. You can paddle it for a week and see no town.",
          m(0, v({"lon": -69.25, "lat": 46.6, "span": 1.6}, routes=[ALLAGASH])),
          photo("ninety-two miles of lakes", PH_ALLA, "Canoes on the Allagash"),
          stat("The bond to pay", "68 %", "Maine voters for the Allagash Wilderness Waterway bond, November 1966", "Natural Resources Council of Maine"),
          sat("In 1970 it became", -69.36, 46.62, 0.15, "Umsaskis Lake on the Allagash"),
          sat("You can paddle it", -69.27, 46.86, 0.1, "The Allagash River heading north in October", date="2023-09-25/2023-10-12")),
        P("And in 2016 Roxanne Quimby, who made a fortune with Burt's Bees, gave about eighty-seven thousand five hundred acres east of Baxter to the federal government, and President Obama made it a national monument. A national park needs an act of Congress. A monument does not, so that is what she asked for. She added twenty million dollars for its upkeep and a pledge to raise twenty million more. Many people in the mill towns fought it. They feared it would close the woods to hunting, snowmobiles and logging. Between 1990 and 2015, about four million acres of the north woods were put under some kind of conservation.",
          sat(0, -68.68, 45.95, 0.25, "Katahdin Woods and Waters National Monument"),
          stat("gave about eighty-seven thousand", "87,500 ACRES", "Katahdin Woods and Waters National Monument, 24 August 2016", "National Park Service; NPR"),
          m("and President Obama made", v({"lon": -68.8, "lat": 45.98, "span": 0.8}, places=[KATAHDIN, MILLI])),
          photo("A national park needs", PH_KWW, "Katahdin Woods and Waters, August 2024"),
          sat("A monument does not", -68.72, 46.0, 0.12, "The monument's land on the East Branch"),
          stat("She added twenty million", "$20 M + $20 M", "Quimby's endowment for the monument, and her pledge to raise as much again", "NRCM; press reports, 2016"),
          photo("Many people in the", PH_MILL_HOMES, "Millinocket"),
          sat("They feared it would", -68.6, 46.05, 0.12, "Logging roads beside the monument in winter", date="2024-02-01/2024-03-15"),
          stat("Between 1990 and 2015", "4 M ACRES", "North Woods put under conservation, 1990 to 2015", "Natural Resources Council of Maine"),
          sat("were put under some", -69.2, 46.75, 0.3, "The Allagash country in October", date="2023-09-25/2023-10-12")),
    ]},
    {"title": "The Last Big Forest", "mood": "calm", "paragraphs": [
        P("So put it together. The land was sold in blocks before anyone could settle it, to owners who wanted trees, not towns. The border was fought over until 1842. The winters are long and the summers short, and the potato moved west. The log drives, the mills and the air base all closed. And the people of Maine chose to keep part of it wild, forever.",
          paint(0, UT + "@red"),
          sat("to owners who wanted", -69.4, 46.0, 0.3, "Private forest, northern Maine in winter", date="2024-02-01/2024-03-15"),
          m("The border was fought", v(EAST, routes=[UK_CLAIM, US_CLAIM])),
          photo("The winters are long", PH_ANWR_WINTER, "Winter in Aroostook"),
          photo("The log drives, the", PH_LORING_WEST, "Loring Air Force Base"),
          photo("And the people of", PH_WBRANCH, "Katahdin and the West Branch")),
        P("And the north is still shrinking. Between 2010 and 2020 Aroostook County lost about one in fifteen of its people. Maine as a whole now has the oldest population of any state.",
          paint(0, AROO + "@red", view=NORTH, places=[CARIBOU, PRESQUE, HOULTON]),
          chart("Between 2010 and 2020", "People in Aroostook County", "census", [["2010", 71870], ["2020", 67105]], CENSUS, highlight=1),
          stat("Maine as a whole", "45.1", "Median age in Maine, 2020: the highest of any state", "US Census Bureau, 2020 census, via CNN and Boston.com")),
        P("Northern Maine is not empty because nobody wanted it. It is empty because, for two hundred years, the people who owned it wanted it to grow trees. Next time you look at a map of the eastern United States, look at the top right corner. That big blank is what is often called the largest block of undeveloped forest east of the Mississippi.",
          m(0, v(ME, layer="night")),
          sat("It is empty because", -69.6, 46.7, 0.5, "The North Woods in October", date="2023-09-25/2023-10-12"),
          m("Next time you look", v({"lon": -77.0, "lat": 40.5, "span": 22}, layer="night")),
          paint("That big blank is", UT + "@red", view=ME)),
        P("Here is my question for you. If someone gave you a cabin in the north woods, at the end of a private logging road, an hour of gravel from the nearest town, would you take it, or is that too far from everything?",
          sat(0, -69.1, 46.45, 0.2, "The North Woods"),
          photo("would you take it", PH_ALLA_FALLS, "The Allagash"),
          photo("or is that too", PH_PORTLAND_AIR, "Portland and the coast"),
          ask=("would you take it", "A cabin in the North Woods?")),
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
            if sh["type"] != "map" or len(steps) != 1 or end - start <= PUSH_WORDS or steps[0].get("compare"):
                continue
            first = steps[0]
            vw = first["view"]
            move = {"at": start + (end - start) // 2, "view": {"lon": vw["lon"], "lat": vw["lat"], "span": max(0.05, round(vw["span"] * (0.62 if vw["span"] <= 2.5 else 0.75), 3))}}
            for key in ("date", "layer"):
                if first.get(key):
                    move[key] = first[key]
            steps.append(move)

script = {
    "title": "Why Almost Nobody Lives in Northern Maine",
    "voice": "am_michael",
    "voice_speed": 1.15,
    "music": "procedural",
    "map_style": "satellite",
    "look": "none",
    "sources": ["episodes/northern-maine-empty/research.md and factcheck.md", "Contains modified Copernicus Sentinel data 2026"],
    "thumbnail": {"text": "NO TOWNS"},
    "chapters": chapters,
    "youtube": {
        "title": "Why Almost Nobody Lives in Northern Maine",
        "description": "Almost half of Maine has no town government at all: more than 14,000 square miles where about 8,300 people lived at the 2020 census. This video goes through the five reasons the north stayed empty: the wild lands Massachusetts sold to timber and paper companies, a border with Britain nobody could draw until 1842, the long winters and the potato's move west, the end of the log drives, the paper mills and Loring Air Force Base, and the people who chose to keep Katahdin and the Allagash wild.",
        "tags": ["Maine", "northern Maine", "why nobody lives in northern Maine", "North Maine Woods", "unorganized territory", "Aroostook County", "Aroostook War", "Katahdin", "Baxter State Park", "Allagash", "Loring Air Force Base", "Millinocket", "geography", "satellite images"],
        "pinned_comment": "If someone gave you a cabin in the north woods, at the end of a private logging road, an hour of gravel from the nearest town, would you take it, or is that too far from everything?",
    },
}
out = HERE / "script.json"
out.write_text(json.dumps(script, ensure_ascii=False, indent=1) + chr(10), encoding="utf-8")
words = sum(len(p["text"].split()) for c in chapters for p in c["paragraphs"])
shots = [s for c in chapters for p in c["paragraphs"] for s in p["shots"]]
kinds = {k: sum(1 for s in shots if s["type"] == k) for k in ("map", "photo", "stat", "document", "chart")}
print(f"{words} words, {len(chapters)} chapters, {len(shots)} shots {kinds}")
