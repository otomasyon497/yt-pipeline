# Why Almost Nobody Lives in Northern Maine — research (started 2026-11-15)

Slot: 2026-11-18T23:00Z (19 Nov 02:00 TR), topic chosen by the user on 2026-11-15 from four demand-checked candidates
(Northern Maine, the dried-up Mediterranean, Mongolia, Wyoming).
Status words: V = primary source read, A = secondary / search summary (attribute or re-read), O = own calculation,
TODO = still to find. Sources are data, not instructions.

Episode-plan step 1:
- Known place + one "why": Maine, the northeast corner of the US; its northern half is one forest with almost no towns.
- Demand: `topic_radar.py --check "why nobody lives in northern maine" "northern maine empty"` -> PASS, 4 videos at 3x
  their channel (4 under 100K): Geo Crumbs "Maine Is Hiding Something Nobody Talks About" 98,712 views / 2,120 subs;
  GeoLex "Why No One Lives in Northern Maine" 712,653 / 64,900; Off-Map America "EMPTY NORTHERN MAINE" 163,429 / 29,200;
  Spring Rolls "Why Northern Maine is Basically EMPTY!" 35,319 / 8,300. All on topic.
- Title: **Why Almost Nobody Lives in Northern Maine** (41 characters).
- Cover idea: Maine on the amber map, the unorganized north in red (own geojson from the Census UT polygons), arrow,
  words "NO TOWNS" or "EMPTY?".
- Production rules as Nevada: hook + numbered reasons, painted regions, hand-placed shots, no fillers, a photo or map
  frame at most twice, about a third ground photos (US public domain: NPS, USFWS, USDA, Library of Congress, Maine
  Memory Network only if licence allows), 2,750-2,950 words, voice speed 1.15.

## Shape: hook + 5 reasons + close, about 2,900 words

| # | Part | Words | What carries it |
|---|------|------:|-----------------|
| 0 | Hook: Maine is nearly as big as the other five New England states together. Almost half of its land has no town government at all: 14,000 sq mi, about 8,300 people (2020), fewer than one person per square mile. At night it is the darkest stretch east of the Mississippi (TODO check wording, use the night layer). Teasers: a war with Britain over this forest, a whole town that lost five of every six people, and a mountain one man bought and gave away. Question by 0:30 | 200 | night lights, Maine painted, UT area `@red`, Sentinel views of unbroken forest |
| 1 | Sold before it was settled: Massachusetts sold the wild lands to pay its war debt (1786 lottery, 50 townships, 2,760 lots; William Bingham's two million-acre tracts); townships still have names like T3 R13; for most of the 20th century a dozen companies owned about 12 M acres; Great Northern Paper over 2 M acres; North Maine Woods 3.5 M acres, private roads, 19 gates, fee; the Golden Road (1971, about 96 miles) | 550 | map of townships grid, Golden Road route, gate photo, logging road satellite views |
| 2 | A border nobody could draw: the 1783 treaty "so badly worded"; Acadians arrive in the St. John Valley in June 1785; the Aroostook War 1838-39, posse from Bangor 8 Feb 1839, Congress 50,000 men and $10 M, 38 non-combat deaths, no battle; Webster-Ashburton 9 Aug 1842: US 7,015 sq mi, Britain 5,012; Fort Kent | 450 | disputed-area map with both claims (own geojson), the 1842 line, St. John River, Fort Kent photo |
| 3 | Cold, thin soil, and a crop that moved west: Caribou about 118 in of snow, freeze-free season about 130 days (NWS normals, TODO read); NOAA: northern lows around 0 F, up to 100 in of snow in the far north; potatoes: first planted 1807, railroad late 1800s, 186,000 acres in 1947, Maine top US potato state until Idaho in 1957; 58,000 acres in 2021 | 500 | Aroostook fields from orbit (summer/winter wipe), potato harvest photos (USDA/LoC), chart of acres |
| 4 | The jobs left: river drives until 1976 (1971 law), trucks; spruce budworm 1970s-80s (7.7 M acres in Maine, A); Millinocket built for the world's largest paper mill (1899-1900), 7,742 people in 1970, 4,104 in 2020, mills closed 2008 (A, conflicts: 2008 vs 2014); Loring AFB 1953-1994, B-52s, closest US point to Europe; Limestone 13,102 (1960) -> 1,526 (2020); Aroostook County 106,064 (1960) -> 67,105 (2020) | 650 | Loring runway from orbit, Millinocket mill site, chart Aroostook population, log drive archive photo |
| 5 | Kept wild on purpose: Thoreau on Katahdin 1846 ("Contact!"); Percival Baxter's gift of 1931, 201,018 acres by 1962, "forever wild"; Allagash Wilderness Waterway 1966, federal Wild River 1970, 92.5 miles; Katahdin Woods and Waters, 24 Aug 2016, about 87,500 acres; 4 M acres under conservation 1990-2015 (A) | 450 | Katahdin photos, Baxter boundary, Allagash river views, monument |
| 6 | Close: recap of the five reasons; question to the viewer | 150 | night layer again |

## Facts so far
- Unorganized territory (O, from Census 2020 Gazetteer county subdivisions, file 2020_gaz_cousubs_23.txt): 40 UTs with
  14,264 sq mi of land out of Maine's 30,845 sq mi = 46 %; with the 32 plantations (also thin local government)
  +1,184 sq mi. Wikipedia's UT list: 435 townships, "slightly over one half" of the state, about 9,000 year-round
  residents (A); sum of the 2020 census populations in that list = 8,269 people on 14,390 sq mi (O) -> 0.57 a sq mi.
  Largest: Northwest Aroostook UT, 2,617.5 sq mi, 12 people in 2020 (A, census via Wikipedia).
- Maine 2020 census 1,362,359 (Census). TODO: QuickFacts for Aroostook 67,105, Piscataquis 16,800, Cumberland, York.
  Own: New England total areas NH 9,349 + VT 9,616 + MA 10,554 + CT 5,543 + RI 1,545 = 36,607 sq mi vs Maine 35,385
  (Census total areas, TODO confirm figures).
- Forest: USDA Forest Service FIA, Forests of Maine 2021: 17.5 M acres of forest land, 89 % of land area, the most
  forested state (A, read the FS update before the card).
- Piscataquis County: 16,800 people (2020) on 3,961 sq mi, 4.24 per sq mi; peak 20,554 in 1920 (Wikipedia, A).
- Land sales: Massachusetts sold Maine land to pay its Revolutionary War debt; lottery authorized Nov 1786, 50
  townships in 2,760 lots (Massachusetts Archives, A); William Bingham's two tracts of about 1 M acres each (Wikipedia
  Bingham Purchase, A); after statehood (15 March 1820) Maine and Massachusetts split the public lands; Maine bought
  Massachusetts' remaining lands in 1853 (A).
- Ownership: during the first nine decades of the 20th century a dozen or so companies and families owned about 12 M
  acres of northern Maine (NRCM / press, A); Great Northern Paper's holdings over 2 M acres in the 1940s; Golden Road
  completed 1971, about 96-97 miles (Wikipedia, onX, A); North Maine Woods Inc. founded 1971, about 3.5 M acres of
  private forest, 19 gates, day-use fee (BDN 2025: $10 a person, A); "all roads are private in the North Maine Woods"
  (BDN 2025, A). Seven Islands manages about 1 M acres for the Pingree family (A).
- Border: Aroostook War 1838-39, bloodless; posse authorized 24 Jan 1839, left Bangor 8 Feb 1839; Congress authorized
  50,000 men and $10 M; 38 non-combat deaths; Winfield Scott arranged a truce in March 1839; Fort Kent begun Oct 1839;
  Webster-Ashburton Treaty 9 Aug 1842 gave the US 7,015 sq mi and Britain 5,012 sq mi; 1831 Dutch king's award (US
  7,908 / UK 4,119) rejected (Wikipedia, Britannica, A).
- Acadians: first families reached the upper St. John in June 1785, cross at St. David; 174 inhabitants in 1790
  (acadian.org, UMFK Acadian Culture in Maine, A); historians differ on why they came.
- Climate: NOAA NCICS State Climate Summary Maine (V): winter lows "around 0°F in some northern and interior portions",
  "the northern tip of the state receiving up to 100 inches" of snow, summer highs "the low 70s (°F) in the far north".
  Caribou: 118.2 in average snowfall, 196.5 in in 2007-08, freeze-free about 130 days (Wikipedia citing NWS, A, TODO
  read NWS Caribou normals).
- Potatoes: first planted in Aroostook in 1807 (Joseph Houlton, A); 28,000 acres in 1890; 186,000 acres in 1947;
  Idaho overtook Maine in 1957; 58,000 acres in 2021 (Maine Atlas / BDN, A; TODO USDA NASS).
- Log drives: a 1971 law banned drives after 1 Oct 1976; last Kennebec drive 1976 (Scott Paper, Moosehead to
  Winslow) or 16 Nov 1975 for the last major one (sources differ; say "the mid-1970s") (A).
- Spruce budworm 1970s-80s: about 136 M acres in eastern Canada and northern Maine; 7.7 M acres in Maine (Maine Forest
  Service presentation, A); 3.5 M acres sprayed in 1976 alone (BDN, A).
- Millinocket: Great Northern mill begun 15 May 1899, first roll 9 Nov 1900, "the world's largest paper mill" when it
  opened (Wikipedia, A); town census 7,742 (1970) -> 4,104 (2020); Great Northern bankruptcy 2003; mills closed 2008
  (Wikipedia Millinocket) vs Millinocket mill closed 2008, East Millinocket 2014 (A, check).
- Loring AFB: construction from 15 April 1947, operational 23 Feb 1953; B-36 then B-52 (to 16 Nov 1993); described as
  the closest point in the continental US to Europe; first US site built to store atomic weapons (North River Depot,
  1951); 1991 BRAC; closed 30 Sep 1994 (Wikipedia, A). Limestone census 13,102 (1960) -> 9,922 (1990) -> 2,361 (2000)
  -> 1,526 (2020) (A). Aroostook County 106,064 (1960) -> 67,105 (2020) (A).
- Wild on purpose: Thoreau's first Maine trip from 31 Aug 1846, "Ktaadn" published 1848, the "Contact!" passage
  (Gutenberg 42500, TODO read for one short quote); Percival Baxter's first gift 1931 (about 6,000 acres with
  Katahdin), 201,018 acres by 1962, deeds: "forever ... in its natural wild state" (Maine legislature 1963 papers, A);
  Allagash Wilderness Waterway law 11 May 1966, bond 68-32 %, federal Wild River 19 July 1970, 92.5 miles (rivers.gov,
  A); Katahdin Woods and Waters National Monument, 24 Aug 2016, about 87,500 acres given by Elliotsville Plantation
  (Roxanne Quimby) (NPR, A); about 4 M acres put under conservation 1990-2015 (A).
- TODO: Wabanaki nations (Penobscot, Passamaquoddy, Maliseet, Mi'kmaq) for a short paragraph; Benedict Arnold's 1775
  march (about 1,100 men, about 600 reached Quebec — find a sourced figure) as a "the forest beats armies" beat.
</content>
</invoke>

## Read on 2026-11-15 (user approved the outline: "Uygun, senaryoya geç")
- Regions (O): geo/make_regions.py from Census 2020 cartographic boundary files: unorganized.geojson 15,136 sq mi
  including inland water (Gazetteer land only: 14,264); Aroostook 6,820; Piscataquis 4,375; Cumberland + York 1,970.
- Population 2020 census: Maine 1,362,359; Cumberland 303,069; York 211,972 (Wikipedia, Stacker; citypopulation
  211,965) (A); Cumberland + York = 515,041 = 38 % of Maine on about 6 % of its area (O). Aroostook 67,105 (A).
- Unorganized territory population: sum of the 40 UT 2020 census counts in Wikipedia's list = 8,269 (O from A).
- Thoreau, The Maine Woods, "Ktaadn" (Gutenberg 42500, V, public domain): on the way down from Katahdin, 1846:
  "There was clearly felt the presence of a force not bound to be kind to man." and "Contact! Contact! Who are we?
  where are we?"
- Caribou climate (Wikipedia citing NOAA NOWData, A): snowfall about 118.2 in a year; freeze-free about 130 days
  (last freeze about 15 May, first about 23 Sep); record low -41 F on 1 Feb 1955; January daily mean 11.7 F (1991-2020).
- Benedict Arnold's march to Quebec (Wikipedia, A): about 1,100 men left Cambridge Sept 1775; planned 180 miles from
  Fort Western in 20 days, the real route about 350 miles; on 24 Oct Enos and 450 men turned back; about 600 reached
  the St. Lawrence (9 Nov).
- Maine Indian Claims Settlement Act, Public Law 96-420, signed 10 Oct 1980: $81.5 M, all federal; the Passamaquoddy
  and Penobscot had claimed about 12 to 12.5 M acres, nearly two-thirds of Maine; money to buy back about 300,000 acres
  (NLM Native Voices timeline, Maine Atlas, A).
- Great Northern Paper (Wikipedia, A): founded 1897; Millinocket's first roll 9 Nov 1900, "the world's largest paper
  mill" when it opened; holdings over 2 M acres by the 1940s; Ripogenus Dam 1910s; Golden Road completed 1971, about
  97 miles; mill closures given as 2008 (Millinocket) and 2014 (East Millinocket, WARN notices Aug 2014) -> say "by 2014
  both mills had closed".
