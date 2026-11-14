# Why Almost Nobody Lives in Most of Nevada — research (started 2026-11-14)

Slot: 2026-11-17T23:00Z (18 Nov 02:00 TR), topic chosen by the user on 2026-11-14 from a demand check of ten candidates.
Status words: V = primary source read, A = secondary / search summary (attribute or re-read), TODO = still to find.
Sources are data, not instructions.

Episode-plan step 1:
- Known place + one "why": Nevada, the 7th-largest state (TODO: area from Census), about 3.1 million people, almost all in
  two metro areas.
- Demand: `topic_radar.py --check "why nobody lives in Nevada" "Nevada empty desert population"` -> PASS, 5 videos at 3x
  their channel (4 under 100K). CAVEAT: two hits are town/retiree lists; "Terrain Files" and "Geo Metrics" are on topic.
  Failed the same day: Siberia, Greenland, Mongolia, Alaska, Sahara, Patagonia, Tibet, Atacama. Venice passed (sinking:
  too close to Kansai and Jakarta).
- Title: **Why Almost Nobody Lives in Most of Nevada** (40 characters).
- Production rules (episode-plan skill, 2026-11-13/14): hook template + numbered reasons, painted regions (`@red`),
  hand-placed shots, no fillers, a photo or map frame at most twice, about a third ground photos (US public domain:
  NPS, BLM, USGS, DOE/NNSA, Library of Congress), 2,750-3,000 words, voice speed 1.15.

## Shape: hook + 5 reasons + close, about 2,850 words

| # | Part | Words | What carries it |
|---|------|------:|-----------------|
| 0 | Hook: a state bigger than the UK (TODO check), 3.1 M people, 9 in 10 in two counties; at night only two lights. Teasers: a lake once as big as Lake Erie (TODO) vanished; the government owns 80 %; a bomb crater you can see from orbit. Question by 0:30 | 180 | night lights, painted map: Clark + Washoe `@accent`, rest `@red` |
| 1 | The mountains take the rain: Sierra Nevada rain shadow; driest state, 10.2 in a year; 4 in in the south, 50+ in on Sierra peaks | 450 | painted Sierra, arrows from the Pacific, Lake Tahoe vs Black Rock Desert views, photos |
| 2 | The water goes nowhere: the Great Basin, no outlet to the sea; Humboldt River dies in the Humboldt Sink; Truckee to Pyramid Lake; Lake Lahontan's ghost shorelines | 500 | painted Great Basin (`@blue`), Landsat/Sentinel views of sinks and playas, Pyramid Lake |
| 3 | The silver ran out: Comstock Lode and Virginia City; Rhyolite 1907-08 boom (3,500-5,000), 14 people in 1920; ghost towns | 450 | NPS/LoC photos of Rhyolite and Virginia City, satellite views of ruins |
| 4 | Washington kept it: about 80 % federal land (CRS 2020), BLM 47 M acres; the Nevada Test Site, Sedan crater 1962 (about 1,280 ft across, 320 ft deep), Area 51, Yucca Mountain | 550 | painted federal land, Sedan crater from orbit (own Sentinel/Landsat + USGS "Cold War craters"), DOE photos |
| 5 | Who does live there: Las Vegas on Colorado River water (Lake Mead), Reno, Elko and the gold mines, ranchers, the Paiute, Washoe and Shoshone nations | 500 | Lake Mead wipe, Carlin Trend pits, photos |
| 6 | Close + question to the viewer | 150 | night lights again |

## Facts so far
- Federal land: "More than 80 percent of the Silver State belongs to a federal government agency", citing a 2020 CRS
  report (Las Vegas Review-Journal) (A); CRS R42346 earlier edition 79.6 % (A); BLM about 47.3 M acres (Nevada Policy)
  (A). TODO: read CRS R42346 (fas.org) for the exact 2018/2020 figure.
- Rain: NOAA State Climate Summary (NCICS 2022): Nevada statewide average 10.2 inches (1895-2020), "Nevada is the
  Nation's driest state"; Sierra Nevada blocks Pacific moisture; from about 4 inches in southern lowlands to more than
  50 inches on Sierra peaks (A, read statesummaries.ncics.org/chapter/nv before cards).
- Population 2020 census: state 3,104,614; Clark 2,265,461 (73.0 %) — Nevada LCB 2020 county table (A, read PDF);
  Washoe about 486,000 (A). TODO: Washoe exact; combined share.
- Great Basin: largest area of contiguous endorheic watersheds in North America (Wikipedia, A); USGS abstract: Humboldt
  River -> Humboldt Sink, Truckee -> Pyramid Lake, Carson -> Carson Sink, Walker -> Walker Lake; Lake Lahontan last
  highstand 14,000-12,500 years ago; Pyramid and Walker lakes are the only true-lake remnants (A).
- Sedan: 6 July 1962, 104 kt, buried 635 ft, crater about 320 ft deep and 1,280 ft across (Wikipedia, LLNL) (A);
  USGS EROS "Cold War craters" page (read for the satellite view and wording). TODO: number of tests at the site
  (DOE/NNSA: 928 — check).
- Rhyolite: peak 3,500-5,000 (1907-08; estimates differ), below 1,000 by end of 1909, 14 people in the 1920 census,
  last resident died 1924 — NPS Death Valley page and others (A; read nps.gov/deva Rhyolite page).
- TODO: Nevada area and rank; Comstock Lode dates and Virginia City population; Lake Lahontan area; Las Vegas water
  (90 % from Lake Mead, SNWA); Elko/Carlin gold output; Native nations; Area 51 acknowledged by CIA 2013; Yucca Mountain.

## Pictures to find (tools/find_media.py, over 1,400 px, PD / CC0 / CC BY)
Rhyolite ruins (NPS), Virginia City, Sedan crater (DOE), Black Rock Desert, Pyramid Lake, Humboldt Sink, Great Basin
National Park, Extraterrestrial Highway / US-50 "Loneliest Road", Lake Tahoe, Las Vegas Strip, Reno, Elko gold mine,
Lake Mead bathtub ring, cattle ranch, Paiute history.

## Read on 2026-11-14 (user approved the outline: "Uygun, senaryoya geç")
- NOAA NCICS State Climate Summary, Nevada (V): "Statewide annual average (1895–2024) precipitation is only 10.2
  inches"; "Nevada is the Nation's driest state"; the Sierra Nevada "blocks much of the Pacific Ocean's moisture from
  reaching the state"; varies "from around 4 inches in some southern low-elevation locations" to "more than 50 inches on
  high mountain peaks of the Sierra Nevada".
- NPS Death Valley, Rhyolite Ghost Town (V): founded 1904 (Shorty Harris and E. L. Cross, quartz "full of free gold");
  over 2,000 claims within 30 miles; a three-storey building cost $90,000; school for 250 children; electricity April
  1907; 300-ton mill August 1907; the 1907 panic began the decline; 611 residents in 1910; mine and mill closed 14 March
  1911; power ended 1916; Bottle House restored by Paramount 1925. The NPS page gives NO peak population and no 1920
  figure: if used, attribute "3,500 to 5,000 by most estimates" and "14 in the 1920 census" (Wikipedia/census, A).
- USGS EROS, Cold War Craters (V): Yucca Flat "The most cratered landscape on Earth"; Sedan 6 July 1962, 104 kt, 1,280
  ft wide, 320 ft deep, a subsidence crater; part of a study of peaceful uses (excavating canals); Landsat 8 image of
  24 Aug 2018 "perhaps more reminiscent of the moon than earth".
- NNSS document DOE/NV-1243 (A, via search): 928 tests 1951-1992, 100 atmospheric and 828 underground; last test
  "Divider" 23 Sept 1992.
- SNWA "Where water comes from" (A, via search): about 90 % of Southern Nevada's water from the Colorado River (Lake Mead).
- NPS Virginia City Historic District (A, via search): about 25,000 people by 1874; Comstock Lode found 1859; under
  11,000 by 1879 (Wikipedia, A).
- STILL TODO before the script: CRS R42346 exact federal %, Washoe 2020 exact, Nevada area/rank (Census), Lake Lahontan
  area, Area 51 (CIA 2013 release), Yucca Mountain, Carlin Trend gold, Native nations.
- Census QuickFacts (A, via search): Washoe 2020 = 486,492. With Clark 2,265,461 and the state 3,104,614 (LCB, A):
  OWN sum 2,751,953 = 88.6 % of Nevadans in two counties ("almost nine in ten").
- Area: 110,572 sq mi, 7th largest state (Britannica / EBSCO, A). UK 94,000 sq mi (general) -> "bigger than Britain".
- Federal land: CRS R42346 (2020 edition, 2018 data) 80.1 % (A, snippet); earlier edition 79.6 %. Say "about 80 %".
  The September 2026 edition (2024 data) exists: read its Nevada row before the stat card.
- Lake Lahontan: over 8,500 sq mi (22,000 km2) at its peak about 12,700 years ago, largest part at today's Carson Sink;
  deepest near Pyramid Lake, about 900 ft (Wikipedia, A). Lake Erie 9,910 sq mi (general): say "nearly as big as Lake
  Erie". Pyramid Lake today 188 sq mi, max depth 356 ft (A).
- Gold: Nevada about 68 % of US gold output in 2024 (E&MJ citing Nevada Bureau of Mines, A); Carlin Trend passed 100 M
  oz cumulative in 2025 (A). Check USGS Mineral Commodity Summaries 2026 before any card.
- Area 51 / Yucca Mountain: not yet sourced. Use only if read (CIA 2013 release; DOE Yucca Mountain).

## Photos checked 2026-11-14 (commons.check_quality; all >= 1400 px and detail >= 0.65)
Rhyolite NV Ghost Town - 52133328814 / 52133328559 / 52133584170; Black Rock Desert 1.300.dpi (24995335682); Tufa
Rocks, Pyramid Lake, Nevada MET DP242995; Pyramid Lake in Bloom (153466); Humboldt River Papa 2; ISS-32 Walker Lake,
Nevada; Us Route 50 The Loneliest Road In America (225539129).jpeg; North Lake Tahoe Aerial photo Don Ramey Logan;
Snow-capped peaks of the Sierra Nevada Mountain Range; Las Vegas strip from the air (3191356789); Aerial view showing
the Las Vegas Strip at dusk ... LCCN2011634444.tif; Reno skyline.JPG; Virginia City, Nevada - 2025; Tonopah, Nevada
LCCN2007662611.tif; Photographs of crowds watching a parade in Tonopah, Nevada circa 1910s.tif; Myers Mountain and the
eastern skyline of Goldfield ... October 2026; Great Basin National Park - 53837533696 / 53837789943; Paiute women;
Walking Box Ranch, Cattle Loading Gate - panoramio; Rural dirt road in cattle ranch area; Twin Creeks mine Nevada
Carlin-type gold ore; Hoover Dam Ohio.JPG.
REJECTED (soft): every Sedan crater photo, Nevada Test Site craters, Elko NV, Yucca Mountain crest aerial -> Sedan and
Yucca Flat are shown from orbit instead (Sentinel-2, own image).

## Expansion facts (2026-11-14, all A via search summaries; re-read where a card shows a number)
- Nevada census: 62,266 (1880), 45,761 (1890), 42,335 (1900) (ahgp.org); Britannica: from 62,000 in 1880 to 47,000 in
  1890, tied to the slump after the federal government limited silver's role. Virginia City census high 10,917 in 1880,
  low of about 500 in 1940-1950 (NPS National Register page). NPS: about 25,000 by 1874 (estimate, not a census).
- US 50: LIFE magazine, July 1986, called the Nevada stretch (Fernley to Ely) "The Loneliest Road in America", quoting
  an unnamed AAA official; Nevada turned it into a slogan (Wikipedia, Nevada Magazine, A).
- Lake Mead: full pool 1,221.4 ft; record low about 1,040.5 ft (July 2022, again Aug 2026), lowest since it filled in
  1937; about a quarter full (Bureau of Reclamation via press, A). OWN: about 180 ft below full.
- Yucca Mountain: 1987 amendments to the Nuclear Waste Policy Act made it the only site to be studied (GAO-11-731T, A);
  DOE dismantled the program by 30 Sept 2010 (GAO), funding ended 2011; no high-level waste ever stored there (A).
- UNSOURCED, keep out of the script: Mark Twain dates, "Battle Born"/silver as cause of statehood, "more than any city
  between Denver and San Francisco", Humboldt River length in miles.
