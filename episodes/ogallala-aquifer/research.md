# Ogallala aquifer: research (2026-11-09)

Episode 9 candidate, picked by the user from the topic radar (docs/topic-radar-2026-11-08.md). Frame: the water under eight
states that turned the Dust Bowl into farmland, and the farmers now choosing how fast to stop pumping it.
Status: first pass from searches and the pages noted below. Read the primary PDFs before the script (open items at the end).

## Sources
- [R1] USGS, McGuire and Strauch, SIR 2023-5143 (abstract read 2026-11-09 on usgs.gov): the High Plains aquifer underlies
  111.8 million acres (about 175,000 square miles) in parts of Colorado, Kansas, Nebraska, New Mexico, Oklahoma, South
  Dakota, Texas and Wyoming. Declines began soon after substantial irrigation started (about 1950). Predevelopment to 2019:
  by well, a rise of 86 ft to a decline of 265 ft; area-weighted average decline 16.5 ft. 2017 to 2019: average rise 0.1 ft.
  Recoverable water in 2019: about 2.91 billion acre-feet, a decline of about 286.4 million acre-feet since predevelopment
  and a rise of 1.6 million from 2017 to 2019. Latest aquifer-wide USGS figures found: years to 2019.
- [R1b] USGS raster of mapped water-level change, predevelopment to 2019 (data.usgs.gov, USGS:6499c01dd34ef77fcb02b220;
  DOI 10.5066/P9WPP01S): the episode's own map. pubs.usgs.gov answers 403 to the PC; use tools.yml on Actions.
- [R2] Steward et al., PNAS 110(37), 2013, doi 10.1073/pnas.1220351110, via the K-State release and phys.org (paper itself
  not read yet): Kansas: 30 % of the groundwater pumped so far, another 39 % over the next 50 years on existing trends;
  recharge is 15 % of current pumping; 500-1,300 years on average to refill. A model's projection, say so.
- [R3] Kansas Geological Survey, "2023 Status of the High Plains Aquifer in Kansas", Technical Series 25, release 6 Dec 2023:
  in some areas less than 40 % of the original thickness remains; levels could hold for one to two decades with pumping cut 18-32 %
  in the most imperiled areas. Sheridan-6: average annual decline 0.5 ft in 2013-2022 against 2.0 ft in 2002-2012. About 1,400 wells
  measured each year. GMD3 use since 2019 about 13 % below 2005-2018. Wichita County pumping down about 40 %.
- [R4] Hays Post, Jan 2026: KGS and Kansas DWR crews measure about 1,400 wells in 48 counties, first week of January, each year.
- [R5] Sheridan 6 LEMA: voluntary, five-year, about 55 inches per right from 2013 (first of its kind per sources), target about
  20 %. Results differ by metric: 18.5-25.7 % (K-State interim), about 24 % (KGS, 23 % efficiency and 1 % acreage), 35 %
  over four years (KGS 2017 release), "nearly 30 %" (Gary Moss, K-State 2023). Pick KGS's report figure and name it.
  Farm Progress: profits held; KGS: decline slowed sharply, halted in 2015. Districtwide GMD4 LEMA of 2018 has had no significant effect so far.
- [R6] KCUR / HPPR, 2 Feb 2026: GMD3 (Garden City) proposes cutting pumping 5 % a year for 20 years, 27.7 % in total per engineer
  Trevor Ahring, inside a 25-year legally binding LEMA, to stabilize the aquifer. More than 200 farmers heard it. Roger Holmes: three inches
  less water could mean about 50 fewer bushels of corn an acre, up to $200 an acre; "It's going to affect my son." State deadline July 2026, or the state may order cuts.
- [R7] Kansas 2024 law (Kansas Reflector, KCUR): Gov. Laura Kelly signed; all five districts must submit plans by 1 July 2026.
  Kansas long pursued "planned depletion" (KCUR, 2023). SW Kansas GMD fell 1.52 ft Jan 2024 to Jan 2025, preliminary (blue-community.net; find the KGS original).
- [R8] Sipriano v. Great Spring Waters of America, 1 S.W.3d 75 (Tex. 1999), from case summaries and FindLaw: Texas's rule of capture dates from
  Houston & Texas Central Railway v. East (1904): a landowner may pump as much as they choose without liability to neighbours whose wells
  go dry. The court declined to overturn it, leaving it to the Legislature; Justice Hecht's concurrence: "for now". Groundwater districts since SB 1 (1997).
- [R9] T. Boone Pickens, Mesa Water, Roberts County: 2000s plan to pipe Ogallala water to Dallas-Fort Worth (about 330-385 miles per company
  releases); project suspended; rights sold to Canadian River Municipal Water Authority, reported at $103 million (2011). LOWER CONFIDENCE: blog and
  old pieces, acreages differ. Do not use without a better source.
- [R10] Scanlon et al., PNAS 2012 via Texas Climate News / CS Monitor: many Panhandle pivots could idle within decades, farming shifting to dryland
  crops. Old, recent Texas reporting not found yet.
- [R11] Frank Zybach: first center pivot built 1948 near Strasburg, Colorado, patent 22 July 1952 (ASABE, National Inventors Hall of Fame; check
  the number 2,604,359 at the USPTO). Licensed to Valley 1954 (Valmont today), 5 % royalty until the patent ended in 1969; commercial spread from the 1960s.
- [R12] Newsweek, May 2026: about 30 % of US irrigation groundwater, about a fifth of US agricultural output. Press figures; find USGS or USDA originals.

## Own numbers (tools/ogallala_numbers.py)
- About 9 % of the whole aquifer's water gone, 286.4 of about 3,196 million acre-feet: the honest aquifer-wide figure, and the reason for the chapter below.
- The worst well fell 16 times the average: the average hides where it happens.

## Visual inventory
- Landsat, metadata checked 2026-11-09 (Planetary Computer, under 5 % cloud, June-Sept): Garden City KS 10 scenes 1984-86 (1985-08-30, 1986-07-16), 11 in 2000, 22 in
  2025-26 (2026-08-07). Sherman/Dallam TX 5 / 4 / 13 (1986-08-17, 2026-08-07). Lubbock TX 2 / 4 / 12 (1986-09-11, 2026-08-16). Images not yet looked at.
- USGS water-level raster as a map layer, the aquifer outline, state highlights; Sentinel-2 close views of pivots, feedlots, Garden City.
- Film and photos: NARA / LoC Dust Bowl public domain (find_media), USDA and NASA pivot images. Prefer PD / CC0 (memory: no credits in descriptions).

## Open before the script
1. Look at real wipes first: pivots may have GROWN in Kansas since 1985. Find fields that visibly dried (Texas Panhandle likely), otherwise the hook must change. No story without the picture.
2. What happened at the 1 July 2026 deadline: GMD3's plan and the state's answer. Not found yet; it is the ending.
3. Read SIR 2023-5143 for state totals, and the PNAS paper.
4. Recent Texas reporting and a better source for Pickens, or drop him.
