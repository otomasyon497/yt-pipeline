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
