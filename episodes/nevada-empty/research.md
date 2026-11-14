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
