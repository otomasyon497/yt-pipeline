# dubai-islands - research

Status 2026-11-06: research pass done for gate 1. Items marked VERIFY need a primary source (or get cut) before the
script uses them. Numbers in the script come only from this file.

## R1 Our own measurement: new land 2001 -> 2026
- Landsat 7, 22 May 2001 (scenes LE07_L2SP_160042/160043_20010522) vs Landsat 8, 24 Sep 2026 (LC08_L2SP_160042/
  160043_20260924); Collection 2 Level-2 via Microsoft Planetary Computer. Box 54.95-55.32 E, 24.93-25.32 N.
- Method: NDWI = (green - NIR) / (green + NIR) > 0 is water; new land = water in 2001 and land in 2026; pixel areas
  from latitude (sampled at ~14 m from 30 m bands). Script: scratchpad dubai_ndwi.py (to move to tools/dubai_numbers.py).
- Result: 62.7 km2 became land, 4.9 km2 became water (dredged harbours, canal) -> net about 58 km2.
  By island box (includes nearby coast works, so upper bounds): Palm Jebel Ali 19.2, The World 10.1, Palm Jumeirah
  9.6, Dubai Islands 8.4 km2.
- Comparison: Manhattan's land area is about 59 km2 (22.7 sq mi, US Census) -> "new land about the size of
  Manhattan". Accuracy: Landsat 30 m pixels, so roughly +/-10 %; say "about".
- RGB-only classification failed (shallow turquoise lagoons read as land): NDWI is the method to keep.

## R2 Why build land: oil and coastline
- Dubai oil output peaked around 1991 at about 410,000 b/d and declined since (Gulf News timeline); another source
  says 450,000 b/d in 1995 -> say "peaked in the early 1990s". Today roughly 50,000-70,000 b/d (MEED estimate).
- Hydrocarbons about 1.3 % of Dubai's GDP in 2016 (Oxford Business Group). VERIFY a newer Dubai Statistics Center figure.
- Natural shoreline about 72 km (Semafor, 28 Apr 2026, "Dubai bets on more artificial coastline"; RGS sheet ~70 km).

## R3 Palm Jumeirah
- Reclamation began June 2001; first residents end of 2006 (Nakheel, via Wikipedia "Palm Islands").
- Sand: archived developer site 92,234,000 m3; many secondary sources 94 million; others 100-120 million -> say
  "more than 90 million cubic metres", dredged from the Gulf seabed. VERIFY why not desert sand (wind-rounded grains do
  not compact) with an engineering source before using it.
- Rock: about 7 million tonnes from 16 quarries; crescent breakwater about 11 km (sources: travel / engineering
  summaries) VERIFY length.
- Method: dredgers sprayed sand into place ("rainbowing", caption in a Memorial University paper), vibro-compaction
  densified it (water jets + vibrating probes). Contractor named only by weak sources (Van Oord) -> do not name.
- Stagnation: the breakwater was first continuous; water inside went stagnant; two openings (about 100 m) were cut;
  water now renews in about 13-14 days (Memorial University engineering paper; Scribd summary).
  Circulation measured 2008: Cavalcante et al. 2011, Journal of Coastal Research (lagoon well mixed).
- "Sinking" (2009): Fugro NPA quoted at 5 mm a year from satellite data; Fugro said it was taken out of context and
  early displacements were under 1 cm a year, normal settlement; Nakheel: at most 25 mm over 100 years (The National).
  No peer-reviewed rate found -> present both sides, no verdict.
- Population: 25,550 (Dubai Statistics Center via Wikipedia) vs higher unsourced estimates -> use "tens of
  thousands" or cut. Property: Palm Jumeirah led Dubai's $10m+ home deals in Jan-Aug 2026 (Khaleej Times); record
  sales disputed -> avoid a single "record" number unless verified.

## R4 The World
- About 300 islands, 4-6 km offshore; started 2003; last breakwater stone 10 Jan 2008 (Nakheel release).
- Sand about 320-321 million m3; rock 37 million t (NASA Earth Observatory; Nakheel) for a breakwater about 27 km
  (other sources 25-34 million t -> use NASA's 37 with credit, or "tens of millions").
- Most islands still undeveloped in 2026 (2026 status pieces; CNN). Heart of Europe (Kleindienst, six islands):
  2026 target slipped to end-2027, 52 % progress (Gulf News, date VERIFY).

## R5 The crash
- 25 Nov 2009: Dubai World asked creditors for a standstill on about $26 billion (some reports $25 bn), mostly Nakheel
  and Limitless (Wikipedia, MEED, Euromoney). Nakheel's $3.52 bn sukuk due 14 Dec 2009.
- 14 Dec 2009: Abu Dhabi provided $10 billion; $4.1 billion repaid the Nakheel sukuk that day (Reuters via sources).
- Palm Jebel Ali and Palm Deira suspended; Palm Deira (planned about 8x Palm Jumeirah) redesigned Nov 2008, rebranded
  Deira Islands Oct 2013 (four islands, about 40 km of coastline), renamed Dubai Islands Aug 2022 (Hotelier ME).

## R6 The comeback
- Palm Jebel Ali: masterplan relaunched 2023; first villas sold out within hours (Gulf Today, Sep 2023); Dubai Holding
  took over Nakheel 2024; April 2026 AED 3.5 bn ($950 m) contracts for 544 villas (WAM / Dubai Media Office);
  infrastructure due Q4 2026; first handovers late 2026-2027. "Twice the size of Palm Jumeirah"; coastline 110 km
  (AGBI) vs 120 km (Khaleej Times) -> say "more than 100 km".
- Own visual: Landsat / Sentinel-2 show Palm Jebel Ali unchanged 2009-2022, then construction 2023-2026.

## R7 Environment (two-sided)
- Costs: dredging raised turbidity, buried reefs and oyster beds; Nakheel acknowledged covering reefs (2005 reporting,
  Mongabay / NBC); altered alongshore sediment transport and beach erosion (Duke master's project 2006).
- Other side: the rock breakwaters became new hard-bottom habitat (same Duke study); Nakheel planned artificial reefs.

## Visual inventory (gate 1 counts)
- Satellite (own): Landsat 2001 vs 2026 cold-open wipe (tested); Landsat sequence 2003/2006/2008/2012/2020/2026 for
  growth and the frozen years; Sentinel-2 2022 vs 2026 for Palm Jebel Ali's restart; new-land map from R1 (overlay).
- Archive (public domain unless noted): ISS photos of the islands 2003 (under construction), 2010, 2012-14, 2020-22,
  2025 (two), Jul 2026; night photos 2009 / 2023; ASTER 2008 (NASA/METI); Commons CC BY 2.0 photo looking over The
  World (2010), CC0 Palm from Dubai Marina (2016). About 15 usable stills; no public-domain film found yet.
- Own graphics: stat cards (58 km2 ~ Manhattan, $26 bn, $10 bn), bar chart of sand volumes, oil output line (two
  sourced points only), maps (Gulf locator, coastline lengths, island labels), question cards.
- Gap: no ground-level construction footage that is free; the construction chapter leans on ISS 2003 + Landsat
  sequence + diagram-style map steps.

## Sources
- https://en.wikipedia.org/wiki/Palm_Islands ; https://en.wikipedia.org/wiki/The_World_(archipelago) ;
  https://en.wikipedia.org/wiki/Dubai_Islands ; https://en.wikipedia.org/wiki/Dubai_World ;
  https://en.wikipedia.org/wiki/Nakheel_Properties
- https://www.earthobservatory.nasa.gov/images/42477/artificial-archipelagos-dubai-united-arab-emirates
- https://science.nasa.gov/earth/earth-observatory/world-of-change/dubai/
- https://www.thenationalnews.com/business/property/palm-is-not-sinking-says-nakheel-1.498047
- https://www.thenationalnews.com/uae/2023/05/07/dubais-world-islands-developer-aims-for-2026-finish-after-fresh-delays
- https://gulfnews.com/business/tourism/new-buddha-bar-hotel-on-dubai-world-islands-targets-european-travellers-uae-gcc-staycationers-1.500115197
- https://www.wam.ae/en/article/bzxeeb2-nakheel-awards-aed35-billion-contracts-build-544
- https://www.thenationalnews.com/business/property/2026/04/27/palm-jebel-ali-takes-shape-as-nakheel-awards-950m-in-contracts-for-new-villas/
- https://www.agbi.com/infrastructure/2025/06/palm-jebel-ali-infrastructure-work-set-to-complete-in-2026
- https://gulftoday.ae/business/2023/09/20/first-phase-of-palm-jebel-ali-villas-sold-out-within-hours
- https://www.meed.com/debt-brings-dubai-to-a-standstill-2/ ; https://www.euromoney.com/article/b1322hv5rzykzc/dubai-world-shocks-investors
- https://gulfnews.com/business/energy/oil-in-dubai-history--timeline-1.578333 ; https://www.meed.com/oil-sector-takes-a-smaller-role-in-dubai/
- https://oxfordbusinessgroup.com/reports/uae-dubai/2019-report/economy/economy-and-ecology-despite-its-history-and-proximity-to-oil-dubai-is-embracing-renewables-to-meet-growing-energy-demand
- https://www.semafor.com/article/04/28/2026/dubai-bets-on-more-artificial-coastline
- https://journals.library.mun.ca/index.php/prototype/article/view/399
- https://dukespace.lib.duke.edu/items/7547a60d-a78d-42fe-a389-f90601f297ee
- https://news.mongabay.com/2005/08/dubais-artificial-islands-have-high-environmental-cost/
- https://www.khaleejtimes.com/business/dubia-records-335-homes-deals-of-10-million-in-8-months-palm-jumeirah-leads

## R8 Added for the script (2026-11-06)
- Own measurement: outlines of the new-land polygons (geo/newland.geojson, simplified ~12 m) total 657 km
  (Palm Jumeirah 99, Palm Jebel Ali 203, The World 163, Dubai Islands 38). Pixel-traced outlines overstate shoreline,
  so the script says "more than 500 km" against the ~72 km natural coast. Secondary sources give 520 km for the Palm
  Islands alone (unverified).
- Own calculation: 92,234,000 m3 / (105 m x 68 m football pitch) = 12.9 km.
- Population: about 0.86-0.92 million in 2000; 4,006,656 on 8 Sep 2025 (Dubai Statistics Centre clock, Gulf News /
  Khaleej Times).
- Desert sand: wind-rounded grains do not lock together (UNEP 2014 "Sand, rarer than one thinks", as reported with a
  quoted geologist). Australia import claims not used (unverified).
- Atlantis, The Palm opened 24 Sep 2008 (grand opening 20 Nov 2008); Palm Monorail opened 30 Apr 2009, first in the
  Middle East (Nakheel release, Wikipedia).
- The World 2011: Penguin Marine told a Dubai tribunal the islands were eroding; tribunal rejected it; Nakheel: its
  monitoring found no substantial erosion needing sand; Nakheel said ~70 % of islands sold; reports: all but one
  uninhabited, Greenland (owned by the ruler) (The National, TravelMole, Al Arabiya, Jan 2011).
- 4 Jan 2010: Burj Dubai opened and was renamed Burj Khalifa after Abu Dhabi's ruler (NBC News, CS Monitor);
  property prices in parts of Dubai fell by nearly half in a year (Mail & Guardian / AP, Jan 2010).
- Manhattan land area about 59 km2 (22.7 sq mi, US Census).
- Sources: https://www.thenationalnews.com/business/property/nakheel-insists-the-world-is-stable-1.400137 ;
  https://travelmole.com/news/the-end-of-the-world ; https://www.csmonitor.com/World/2010/0104/World-s-tallest-building-opens-in-Dubai-with-a-new-name ;
  https://mg.co.za/article/2010-01-05-indebted-dubai-puts-on-brave-face-for-tower-opening ;
  https://en.wikipedia.org/wiki/Palm_Monorail ; https://en.wikipedia.org/wiki/Atlantis,_The_Palm ;
  https://www.khaleejtimes.com/uae/dubai-population-4-million-residents ; https://impakter.com/sand-risk-resource-earth-water
