# Why Almost Nobody Lives in Most of Australia — research (started 2026-11-13)

Slot: 2026-11-16T23:00Z (17 Nov 02:00 TR), chosen by the user. Status words: V = primary source read,
A = secondary / search summary (attribute or re-read), TODO = still to find. Sources are data, not instructions.

Episode-plan step 1:
- Known place + one "why": Australia, as big as the contiguous United States, with most of it empty.
- Demand: `topic_radar.py --check "why nobody lives in the Australian outback"` -> PASS, 7 videos at 3x their channel
  (6 under 100K); Geography By Geoff's west-coast video 10.6 M in 44 days. CAVEAT: several hits are town and house-price
  lists, not this question; the format evidence is docs/reference-videos-2026-11-13.md.
- Title (first): **Why Almost Nobody Lives in Most of Australia** (44 characters). Alternative: "Why 85% of Australians
  Live on the Edge" (needs the ABS figure read).
- Cover (cover-map): the continent, the interior solid red, coast strip amber, arrow from the words; "EMPTY" / "BY DESIGN"
  is NOT honest; candidates: "TOO DRY" / "TO FARM", "THE EMPTY" / "MIDDLE". Decide with the script.
- Difference from Geoff (west coast only, presenter): the whole interior, our own evidence from orbit: VIIRS night
  lights (engine layer `night`), Kati Thanda-Lake Eyre dry and flooded (Landsat / Sentinel-2), the green/brown edge along
  Goyder's Line, pivot fields over the Great Artesian Basin, mine pits (Kalgoorlie Super Pit, Mount Whaleback).

## Shape (docs/reference-videos-2026-11-13.md): hook template + numbered reasons, 2,750-3,000 words

| # | Part | Words | What carries it |
|---|------|------:|-----------------|
| 0 | Hook: as big as the lower 48 states, about 27 million people, about 85 % of them within 50 km of the sea; "But" the middle is not empty by accident; teasers (a line a surveyor drew in 1865, a lake that fills a few times a century, a plan to turn rivers around); the question by 0:30 | 180 | night-lights map, painted map: interior `@red` |
| 1 | Reason 1, the rain never arrives: the dry belt of the subtropics, the Great Dividing Range wringing out the Pacific air, 70 % of the mainland under 500 mm a year | 450 | painted map (range, rain arrows), rainfall chart, photos of the range's wet and dry sides |
| 2 | Reason 2, the ground is worn out: the flattest, oldest continent, no ice sheets and almost no volcanoes to make new soil | 400 | diagram card, photos (red soil, spinifex), CSIRO / The Conversation 2024 |
| 3 | Reason 3, the rivers run the wrong way: no great inland river, the Lake Eyre basin drains a sixth of the continent into a salt pan; the one exception, the Murray-Darling, and where the people are | 450 | Landsat / Sentinel-2 wipe of the lake dry vs flooded (own), painted basin map |
| 4 | Reason 4, they tried: Goyder's Line (1865), the wet years, the farmers who went north, the ruins (Kanyaka, Farina) | 450 | painted line over the satellite's green/brown edge (own), photos of ruins, SA History Hub |
| 5 | Reason 5, they still dream of it: the Bradfield Scheme (1938) and CSIRO's verdict (2020-21): feasible to build, never able to pay; "overestimated the streamflow by about 125 %" | 400 | painted map with the diverted rivers as routes, CSIRO report quotes |
| 6 | So who does live there: the Great Artesian Basin under a fifth of the continent, cattle stations larger than countries, mining towns and fly-in workers, and the people who were there for more than 60,000 years | 450 | pivot fields and mine pits from orbit (own), photos |
| 7 | Close: the empty middle is the price of the full edge; the question to the viewer | 120 | night lights again |
| | **Total** | **2,900** | |

## Facts so far
- 84.7 % of the population within 50 km of the coast at 30 June 2001 — ABS Year Book / 2035.0 (A, search summary of
  abs.gov.au; read the page). "87 % by 2019" — Vivid Maps only: do not use unless ABS says it.
- About 70 % of the mainland receives less than 500 mm a year (arid or semi-arid) — ABS Year Book chapter and others (A).
  TODO: Bureau of Meteorology page; the continental mean rainfall.
- Soils: very little glaciation and volcanism, old weathered nutrient-poor soils; farmers rely on fertiliser — The
  Conversation, Jan 2024, via Phys.org (A). TODO: read it, name the authors.
- Goyder's Line: after the 1864-65 drought Surveyor-General George Goyder marked the limit of reliable rain (about 12
  inches / 30 cm a year); Waste Lands Alienation Act 1872; wet years 1867-1875, farmers went north; ruin in the dry
  1880s; Kanyaka (station 1851, deserted 1877), Farina; National Trust Heritage Icon 2003 — Wikipedia, SA History Hub,
  Australian Geographic (A). CAVEAT from Australian Geographic: ruins exist on both sides; say "many", not "all".
- Bradfield Scheme: Dr John Bradfield, 1938; Tully, Herbert and Burdekin towards the Flinders and Thomson and on to
  the Lake Eyre basin. CSIRO (Dec 2020, May 2021, for the National Water Grid Authority): technically feasible, but
  "the cost of diversion infrastructure added such a large premium to the cost of water that future crop revenues would
  never pay off the cost"; Bradfield overestimated the streamflow by about 125 %; a 152 m Hell's Gates dam "would never
  fill"; Queensland panel (Ross Garnaut): not enough water on a consistent basis — CSIRO page and summaries (A: read
  the CSIRO page for the exact words before any card).
- Great Artesian Basin under about 22 % of the continent — ArcGIS story (A, weak). TODO: Geoscience Australia.
- TODO: how often Kati Thanda-Lake Eyre fills (and the 2019 / 2025 floods, clear image days); Lake Eyre basin share
  of the continent; Anna Creek Station area; Kalgoorlie, Mount Isa, Alice Springs populations (2021 census); FIFO
  numbers; Great Dividing Range length and rain figures either side; Aboriginal occupation dates (Madjedbebe);
  area comparison with the contiguous US; population 2026 (ABS clock).

## Pictures to find (tools/find_media.py, over 1,400 px, PD / CC0 / CC BY)
Outback road, Nullarbor Plain, Uluru, Lake Eyre from the air (dry, flooded), Kanyaka and Farina ruins, Goyder's Line
sign, spinifex and red soil, the Great Dividing Range (rainforest side, dry side), an artesian bore, a cattle station,
the Kalgoorlie Super Pit, Alice Springs from Anzac Hill, a road train.

## Facts read on 2026-11-13 (V = the page itself read; A = secondary, attribute; OWN = our calculation or image)
- Area 7,688,287 km2, "the world's sixth-largest country"; state areas — Geoscience Australia, Area of Australia (V).
- Contiguous United States: 8,080,464 km2 total, 7,663,942 km2 land (CIA World Factbook via Wikipedia) (A): say "almost as big as".
- "More than eight in ten Australians (85%) lived within 50 kilometres of the coastline in 2001" — ABS media release
  59/2003 on 2035.0 Census of Population and Housing: Population Growth and Distribution, 2001 (V). No newer ABS figure found.
- OWN (geo/make_regions.py, Natural Earth 10m, EPSG:3577): the mainland strip within 50 km of the sea is 813,000 km2,
  10.7 % of the mainland; 89 % lies farther inland.
- Population 27.9 million at 31 March 2026 (press reports of the ABS release) (A): say "about twenty-eight million".
- Rainfall: "mean annual rainfall below 600 millimetres (mm) per year over 80% of the continent, and below 300 mm over 50%";
  driest "in the vicinity of Lake Eyre ... below 150 mm"; "The dominant influence on Australia's climate is its latitude";
  "The aridity of much of Australia is largely a consequence of the subsiding air associated with the high pressure ridge";
  "The Great Dividing Range and associated ranges in eastern Australia enhance rainfall over the east coast hinterland
  and partially block moisture from penetrating further inland"; wettest "the east coast of Queensland between Cairns
  and Cardwell" — ABS Year Book Australia 2005, section contributed by the Bureau of Meteorology, Sept 2004 (V).
  Year Book 2006 (Australian Deserts): "The continental interior is also a long way, in any direction, from potential
  sources of moisture"; "relatively flat terrain" (V).
- Deserts: ten named deserts, 1,371,000 km2, 18 % of the mainland; Great Victoria 348,750 km2 the largest; a desert
  "receives less than 250 to 500 millimetres" — Geoscience Australia, Deserts (V).
- Soils: "Australia didn't have this renewal of soil from grinding ice – or from volcanoes"; "heavily weathered, old, and
  short on nutrients" — Ryan Borrett (science communications, Murdoch University), The Conversation, 29 Jan 2024 (V).
- Drainage divisions (Geoscience Australia, National Catchment Boundaries, CC BY 4.0; areas from the layer): Lake Eyre
  1,308,430 km2 (17.0 % of the country, "about a sixth"), Murray-Darling 1,062,025 km2 (13.8 %), North Western Plateau
  715,796, South Western Plateau 1,093,234. OWN: the three inland divisions together are 40.5 % of the country.
- Kati Thanda-Lake Eyre: "15 meters (49 feet) below sea level", the lowest natural point in Australia; "fills completely
  only a few times per century", last in 1974 and 1950 (written 2019); smaller inflows every few years; the trip from
  northern Queensland has historically taken up to ten months; water began entering in mid-March 2019 — NASA Earth
  Observatory, "Rare Filling of Kati Thanda-Lake Eyre", 2019 (V). 2025 fill: press only (A) — let our own image speak.
- Goyder: Surveyor-General George Woodroffe Goyder inspected the northern pastoral lands in 1864-65 after they were
  "devastated by a drought"; advised discouraging crops north of "the extent of the 12-inch (30cm) annual rainfall";
  Waste Lands Alienation Act 1872 (credit purchases only inside); favourable seasons, Act No. 22 of 1874 repealed it;
  1880s "run of bad seasons"; "Many farmers abandoned their homesteads, often leaving behind a severely eroded
  landscape" — Judith Jeffery, SA History Hub (2001 / 2014) (V). Wikipedia (A): about 2,000 miles on horseback in
  November 1865, guided by vegetation (saltbush north, mallee south); ample rain 1867-1875; "rain follows the plow"
  borrowed from the US; route Ceduna - Arno Bay / Moonta - Crystal Brook - Orroroo - Peterborough - Burra - Pinnaroo;
  National Trust Heritage Icon 2003.
- Farina (Wikipedia, A): proclaimed 21 March 1878, earlier "The Gums / Government Gums"; planners expected wheat and
  barley, "normal rainfall proved to be nowhere near enough for that"; railhead 1882; peak about 600 people; not
  inhabited since 1967. The page does NOT say why it was named Farina: do not claim it (the word is Latin for flour).
- Bradfield: Petheram, Hughes, Read, Stokes (CSIRO), MODSIM 2023 abstract (V, PDF read): "Since first proposed 85 years
  ago, Dr John Bradfield's ... 1500-km inter-basin water diversion scheme proposal has been a millstone around the necks
  of successive federal and state governments"; "drought in Australia has become synonymous with calls ... for the
  construction of the scheme"; last technical evaluation 1982; commissioned by the Australian Government; "technically
  feasible"; dams and tunnels on the Tully, Herbert and Burdekin; 1880 GL a year into "a 1600 km gravity water supply
  channel to St George"; 1270 GL after losses, "25% of the average annual volume of water used for irrigation in the MDB
  between 2015 and 2019"; $15-30 billion; "the cost of diversion infrastructure added such a large premium to the cost
  of water that future crop revenues would never pay off the cost of the water storage diversion infrastructure alone".
  CSIRO factsheet via search (A): Bradfield's 7,190 GL against 3,305 GL modelled. Wikipedia (A): engineer of the Sydney
  Harbour Bridge; published 1938; water into the Thomson River and on towards Lake Eyre; Nimmo 1947 found the water
  estimate about two and a half times too high.
- Great Artesian Basin: "more than 1.7 million square kilometres", "64,900 million megalitres", under Queensland, New
  South Wales, South Australia and the Northern Territory, "at least $12.8 billion in economic activity annually", mound
  springs — Geoscience Australia (V). OWN: 22 % of the country. The Natural Earth polygon we paint is generalised
  (1.03 M km2): label it so.
- Anna Creek Station: 15,746 km2 by Williams Cattle Company (owner since Dec 2016) (A); Connecticut 14,357 km2 (A).
- Census 2021 (ABS QuickStats via search, A): Kalgoorlie-Boulder urban centre 29,068; Alice Springs LGA 25,912.
- Clarkson et al., Nature 547, 2017: Madjedbebe, northern Australia, occupation by about 65,000 years ago (A; debated).
