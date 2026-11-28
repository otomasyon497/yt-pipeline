# Northern Idaho: research (round 1, 2026-11-28)

Slot: 7 Dec 2026 23:00 UTC. Working title: "Why Almost Nobody Lives in Northern Idaho". Rivals: competitors.md.
Scope: Idaho north of the Salmon River (the Pacific-time half): Boundary, Bonner, Kootenai, Shoshone, Benewah, Latah,
Clearwater, Nez Perce, Lewis, Idaho counties.

## Facts (round 1; [CHECK] = read primary in round 2)
- R1 Land: federal 61.65 % of Idaho (32.63 of 52.93 M acres, CRS 2012 via Ballotpedia) [CHECK CRS R42346].
  Frank Church-River of No Return Wilderness 2,366,757 acres, largest contiguous wilderness in the lower 48 (USFS);
  core of a 3.3 M acre roadless area (Wikipedia); Selway-Bitterroot next to it.
- R2 Roads: US 95 the only road linking the panhandle with the rest of Idaho (Wikipedia US 95 in Idaho); the old White
  Bird grade the only north-south link for ~40 years, new grade 1975; US 95 mostly two-lane, 538 mi in Idaho.
  US 12 over Lolo Pass completed 1962, dedicated 19 Aug 1962 [CHECK ISHS ref 286].
  Time zones: Pacific north of the Salmon River main channel, Mountain south (49 CFR 71).
- R3 Mullan Road 1859-62, 624 mi Fort Benton - Fort Walla Walla, over Fourth of July Pass; later the railroad, US 10,
  I-90 (Kootenai County; Wikipedia).
- R4 Gold and the Nez Perce: Elias Pierce, gold on the Clearwater 1860; ~15,000 miners (NPS); Lewiston founded at
  the confluence; 1863 treaty cut the reservation by ~90 % ("thief treaty", NPS), the root of the 1877 war.
- R5 Capital: Idaho Territory 1863, capital Lewiston; legislature voted Dec 1864 to move it to Boise; seal and
  archives taken from Lewiston 1865 by acting governor C. DeWitt Smith with soldiers from Fort Lapwai; territorial
  supreme court confirmed Boise 1866 (ISHS ref 344; Wikipedia Idaho Territory) [CHECK]. Northern lawmakers asked for a
  territory of north Idaho + eastern Washington (ISHS) [CHECK later annexation votes, e.g. the 1887 bill].
- R6 Shape: Montana Territory 1864 took the Bitterroot crest as its border; the straight line north from about the
  116th meridian (GeoLex; Wikipedia Idaho) [CHECK].
- R7 Silver Valley: ~1.2 bn oz silver since 1884 (ISU 1.18 bn; Mining.com) -> say "more than a billion ounces";
  1892 and 1899 labour wars: 29 Apr 1899 union men blew up the Bunker Hill & Sullivan concentrator at Wardner (3,000 lb
  dynamite), martial law, the bullpen; Gov. Steunenberg killed by a bomb at his gate in Caldwell 30 Dec 1905 (Harry
  Orchard) (Wikipedia; ISHS ref 210/447).
- R8 Sunshine Mine fire 2 May 1972, 173 underground, 91 died (CO and smoke), cause never found; led to the 1977 Mine
  Safety and Health Act (MSHA; Spokesman 2022).
- R9 Bunker Hill smelter: baghouse fire 3 Sep 1973, ran without controls; children's blood lead among the highest ever
  measured in the US (EPA); smelter closed 1981 [CHECK 1981/1982]; NPL 1983, 21 sq mi; barriers on 7,000+ properties (EPA).
- R10 Big Burn 20-21 Aug 1910: ~3 M acres in N Idaho / W Montana, ~85 dead (sources 78-87), a third of Wallace burned;
  Ed Pulaski saved all but 5 or 6 of ~45 men in a mine tunnel (Wikipedia; PBS; NWCG) -> say "about eighty-five".
- R11 Timber: Potlatch's sawmill at Potlatch (world's largest white-pine mill) closed 1983 (Idaho Capital Sun);
  Jaype plywood near Pierce closed 2000, 215 jobs (Spokesman); Orofino mills 2016 (NPR).
- R12 Lake Pend Oreille ~1,150 ft deep (Navy); Farragut Naval Training Station 1942-46, 293,381 recruits, second
  largest in the US (Idaho Military Museum; NPS); Navy Acoustic Research Detachment at Bayview [CHECK start year],
  quarter-scale submarine models (NAVSEA).
- R13 People: Idaho 2020 census 1,839,106 [CHECK]; Kootenai 171,362 (2020) -> 188,323 (2024), +9.9 % (Census QuickFacts).

## Own measurements (round 2)
- M1 Share of Idahoans north of the Salmon River, and its share of Idaho's land (Kontur 2023 H3, CC BY 4.0).
- M2 How much of the north's population sits within a few km of I-90 / US 95; the largest empty area (no settled
  hexagon) between Grangeville and the Montana line.
- M3 Drive Sandpoint -> Boise inside Idaho vs via Washington/Oregon (OSRM public demo; distances only).

## Gate-1 outline (~2,750 words, ~17 min)
- Hook: the panhandle on the map; the top half runs on a different clock; Boise is quicker to reach by leaving the
  state. "But": a valley that gave a billion ounces of silver and then poisoned its children; a fire that burned an
  area the size of Connecticut in two days; a capital taken away by soldiers. Question: why almost nobody lives here?
- 1. The wall in the middle: mountains, the largest wilderness in the lower 48, one road (White Bird), Lolo 1962, M3.
- 2. The land is not for sale: 62 % federal; national forests; the Big Burn 1910 and Pulaski (story).
- 3. A territory run from far away: gold 1860, the Nez Perce treaty 1863, the capital taken 1865, the border on the
  Bitterroots, the north asking to join Washington.
- 4. Silver, dynamite and lead: Silver Valley, 1899, Steunenberg 1905, Sunshine 1972, Bunker Hill 1973, Superfund.
- 5. When the mills closed: timber boom and bust (Potlatch 1983, Pierce 2000, Orofino 2016).
- 6. Where people do live, and the new rush: M1, Coeur d'Alene growth, the Navy lake; ending question.

## Round 2 (2026-11-28)
- M1 DONE (geo/measure_population.py -> .txt; 2020 census block groups, Census county land): Idaho 1,839,106 on
  82,645 sq mi land. North (10 counties) 363,642 = 19.8 % of people on 25.4 % of land (20,992 sq mi: more than VT
  9,217 + NH 8,953 land). Kootenai 171,362 = 47.1 % of the north's people on 5.9 % of its land. 63.7 % of the north
  within 25 km (~15 mi) of Coeur d'Alene, Lewiston or Moscow. Idaho County 16,541 on 8,477 sq mi (NJ land 7,354).
- M3 DONE (geo/drive_osrm.txt): Sandpoint -> Boise 423 mi inside Idaho vs 496 mi via WA/OR, both ~9.2 h (OSRM).
- R14 Border with Canada 45 mi (International Boundary Commission; Britannica: state ~45 mi wide there).
- R15 1887: Congress sent Cleveland a bill to return north Idaho to Washington Territory on 1 Mar 1887; pocket veto
  after Gov. Stevenson's telegram (Wikipedia Idaho Territory; Spokesman 2015). Statehood 3 Jul 1890.
  University of Idaho founded 30 Jan 1889 (Stevenson signed Council Bill 20), credited with stopping the annexation
  push (UI catalog; Wikipedia); opened 1892.
- R16 Nez Perce War: White Bird Canyon 17 Jun 1877 first battle, Nez Perce victory (US Army); 126 days, 1,170+ mi,
  four states; Bear Paw, surrender 5 Oct 1877, ~40 mi short of Canada (NPS).
- R17 Lake Coeur d'Alene: ~75 M metric tons of metal-rich sediment on the lakebed (USGS OFR 93-656); wastes
  discharged straight into the South Fork until 1968; lake left out of Superfund (NASEM 2022).
- R18 Port of Lewiston: most inland West Coast seaport, 465 river miles, 8 locks and dams; wheat, peas, lentils,
  paper (Port of Lewiston).
- R19 Wallace: last stoplight on I-90 Seattle-Boston, removed when the viaduct opened 12 Sep 1991; funeral for it
  (ITD; Jalopnik). Wallace 1910 evacuation trains to Spokane and Missoula; soldiers kept men on the fire line (Wikipedia; Spokesman).
- R20 Kellogg 3,811 (1970) -> 2,314 (2020) (census via Wikipedia). Silver Mountain gondola 3.1 mi, longest single
  stage in North America, 30 years old in 2020 (Shoshone News-Press; resort).
- R21 Aryan Nations compound near Hayden Lake (from the 1970s); Keenan v. Aryan Nations, Kootenai County jury
  $6.3 M, 7 Sep 2000; bankruptcy; compound demolished May 2001, later a peace park (SPLC; ABC; Spokesman).
- R22 Salmon "River of No Return": one-way freight scows, broken up for lumber at the end (USFWS rivers; Britannica).
  Hells Canyon 7,993 ft, deepest river gorge in North America [CHECK USFS].
- R23 National forests: Idaho Panhandle ~2.94 M acres, Nez Perce-Clearwater ~4.07 M (USFS LAR table 28) -> "about
  seven million acres". 10 a.m. policy 1935 (USFS history). Pulaski tool 1911.
- Narration v3: drafts/narration.md, 2,706 words (~16.2 min at 2.78 w/s). Hook 5/6 (ONE NUM flags "one in five").
