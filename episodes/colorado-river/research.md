# colorado-river: research dossier

Status: core facts verified 2026-11-04 (sources below). Items marked (to verify) need a second source before the
script uses them. Units: US first (feet, acre-feet = AF, million acre-feet = MAF); 1 AF = 1,233.48 m3, so
1 MAF = 1.2335 km3.

## Thesis (tested so far, holds)
The Colorado River was divided in 1922 on the assumption of about 16.4 MAF a year; since 2000 it has carried about
12.4 MAF. The two big reservoirs absorbed the gap until 2026, when both hit record lows, the states failed to agree
on new rules, and Interior imposed the first cuts of the new era on the Lower Basin alone. The fight is now in
court and may reach the Supreme Court, because the Upper and Lower Basin read the 1922 Compact differently.

## Sources
- [R1] Interior press release, 21 Aug 2026: https://www.doi.gov/pressreleases/interior-department-finalizes-plans-2027-2028-colorado-river-operations
- [R2] Reclamation, Post-2026 operations and decision documents: https://www.usbr.gov/ColoradoRiverBasin/post2026/index.html
- [R3] Greenberg Traurig analysis (Aug 2026): https://www.gtlaw.com/en/insights/2026/8/interiors-post-2026-colorado-river-operating-framework-draws-immediate-legal-challenge
- [R4] The Nevada Independent, Nevada sues (24 Aug 2026): https://thenevadaindependent.com/article/nevada-sues-interior-over-cuts-to-already-meager-colorado-river-water-allocation
- [R5] Nevada Governor's press release: https://www.gov.nv.gov/press-releases/nevada-files-lawsuit-against-department-of-the-interior-over-colorado-river-operations-record-of-decision/
- [R6] Arizona joins the suit (16 Oct 2026): https://www.newsfromthestates.com/article/arizona-joins-nevada-lawsuit-over-colorado-river-cuts ;
  Burgum's response: https://www.abc15.com/news/local-news/interior-secretary-warns-arizona-over-colorado-river-lawsuit
- [R7] IBWC Minute 334 (signed 2 Sep 2026): https://www.wateronline.com/doc/united-states-and-mexico-announce-colorado-river-cooperative-agreement-0001
- [R8] Reclamation daily data (public domain), Lake Powell = 919, Lake Mead = 921; parameters 49 elevation, 17 storage,
  89 area, 42 total release, 29 inflow: https://www.usbr.gov/uc/water/hydrodata/reservoir_data/919/csv/49.csv
  (downloaded 2026-11-04, last value 2 Nov 2026)
- [R9] Reclamation, October 2026 Most Probable 24-Month Study, 6 maf Lake Powell release scenario (15 Oct 2026):
  https://www.usbr.gov/lc/region/g4000/24mo_6.pdf
- [R10] NASA Earth Observatory, "Lake Powell drops to record low levels" (Sep 2026):
  https://science.nasa.gov/earth/earth-observatory/lake-powell-drops-to-record-low-levels/
- [R11] ABC15, October rise: https://www.abc15.com/news/local-news/lake-mead-and-lake-powell-water-levels-rising-in-october-but-long-term-outlook-remains-dire
- [R12] USGS SIR 2022-5017, Jones & Root 2022, Lake Powell elevation-area-capacity 2018: https://pubs.usgs.gov/publication/sir20225017
- [R13] USGS data releases: modified topobathymetric DEM of Lake Powell (doi:10.5066/P9H60YCF); 2018 EAC tables
  (doi:10.5066/P9O3IPG3); 2017 multibeam bathymetry 2 m (doi:10.5066/P90BU2VS). ScienceBase blocks curl from the PC
  (Cloudflare challenge): test from Actions in step 4.
- [R14] Reclamation technical memo, Glen Canyon Dam interim operating guidance for low reservoir levels (26 Mar 2024):
  https://www.usbr.gov/uc/DocLibrary/Memos/20240326-EstablishmentInterimOperatingGuidanceGlenCanyonDamLowReservoirLevels-TechnicalDecisionMemo-508-TSC.pdf
- [R15] Richter et al. 2024, "New water accounting reveals why the Colorado River no longer reaches the sea",
  Communications Earth & Environment, doi:10.1038/s43247-024-01291-0 (CC BY 4.0)
- [R16] CPR News, "If Colorado River compact heads to Supreme Court, 'everybody loses'" (9 Sep 2026):
  https://www.cpr.org/2026/09/09/colorado-river-supreme-court-stakes/
- [R17] The Colorado Sun, legal battles ahead (27 Mar 2026): https://coloradosun.com/2026/03/27/colorado-river-states-potential-water-cuts-legal-battles/
- [R18] SNWA, Intake No. 3: https://www.snwa.com/where-southern-nevada-gets-its-water/our-regional-water-system/intake-no-3.html
- [R19] Colorado River Compact, 1922 (text): https://www.usbr.gov/lc/region/pao/pdfiles/crcompct.pdf
- [R20] Natural flow 2000-2018 vs 1906-2018 (Kuhn/Fleck, from Reclamation natural flow data):
  https://inkstain.net/2020/03/how-dry-was-2000-2018-on-the-colorado-compared-to-normal
- [R21] Eos, Upper Basin governors' statement after the Final EIS: https://eos.org/articles/the-colorado-river-basin-is-running-out-of-water-not-everyone-is-happy-with-the-governments-suggested-solution
- [R22] Colorado Water Conservation Board, Colorado River Commissioner's Corner: https://cwcb.colorado.gov/colorado-river-commissioners-corner
- [R23] FOX 10 Phoenix, Arizona's cut: https://www.fox10phoenix.com/news/arizona-faces-30-colorado-river-water-cut-new-federal-plan

## The decision (21 Aug 2026)
- Interior adopted a Record of Decision: a Decision Framework for operating Lake Powell and Lake Mead through 2036,
  with operating guidelines in two-year periods, and issued the 2027-2028 Operating Guidelines [R1][R3]. Final EIS
  31 Jul 2026; the NEPA process began June 2023 [R1].
- Reason given: drought, historically low reservoirs, Glen Canyon Dam infrastructure concerns and the inability of
  the seven states to reach a cooperative agreement [R3]. Reclamation: "consensus on long-term operations did not
  materialize" [R2].
- Lake Powell: releases follow actual hydrology to keep at least 3,510 ft [R1][R3]. WY 2027 starts in the "Lower
  Elevation Infrastructure Protection Range" (3,510-3,540 ft); release 6.0-7.0 MAF, set in April 2027 [R1][R9].
- Lake Mead: shortage in 2027 and 2028; Lower Basin consumptive use capped at 6.25 MAF a year, a 1.25 MAF cut from
  normal allocations [R1][R3]. Split (Lower Basin states' May proposal) [R1][R3][R4]:
  Arizona -760,000 AF (2.8 -> 2.04 MAF, -27.1 %); California -440,000 AF (4.4 -> 3.96 MAF, -10 %);
  Nevada -50,000 AF (300,000 -> 250,000 AF, -16.7 %). Plus at least 700,000 AF of voluntary conservation over the two
  years [R1].
- Upper Basin (Colorado, Utah, Wyoming, New Mexico): no mandatory cuts, voluntary conservation goals; they are to
  operate Flaming Gorge, Aspinall and Navajo to protect Glen Canyon Dam [R1][R4].
- Mexico: Minute 334, signed 2 Sep 2026 in El Paso, runs to 31 Dec 2028 and replaces Minutes 323 and 330; Mexico's
  deliveries drop by 250,000 AF a year in 2027 and 2028 (of 1.5 MAF) [R7].
- Burgum: "Forty million people, millions of acres of farmland and ranchland, industries that power the American
  West" [R1].

## Record lows (Reclamation daily data [R8], NGVD29 operating datum)
- Lake Powell: 3,516.62 ft on 15 Sep 2026; old record 3,519.92 ft (13 Apr 2023). First new record 15 Aug 2026 [R10].
  Full pool 3,700 ft; peak 3,708.34 ft (14 Jul 1983). End of September 2026: 5.16 MAF, 22 % of live capacity
  (Reclamation Glen Canyon page).
- Lake Mead: 1,037.16 ft on 22 Oct 2026; old record 1,040.58 ft (28 Jul 2022). First new record early August 2026
  (1,040.5 ft on 7 Aug, press). Peak 1,225.83 ft (24 Jul 1983).
- Combined storage: 11.95 MAF on 16 Sep 2026, the lowest since Lake Powell began filling in 1963 [R1][R8]; peak
  52.49 MAF (19 Jul 1983); 46.45 MAF on 1 Jan 2000.
- 2 Nov 2026: Powell 3,533.46 ft (6.04 MAF), Mead 1,039.06 ft (6.91 MAF) [R8].

## Why 2026 was so bad
- Winter 2025-26: lowest observed snowpack on record [R1]. Observed April-July 2026 unregulated inflow to Powell:
  1.14 MAF, 18 % of average; preliminary WY 2026 unregulated inflow 3.72 MAF, 39 % of average [R9]. August 2026
  unregulated inflow about 0.001 MAF (table, [R9]).
- WY 2026 Glen Canyon release cut from 7.48 to 6.0 MAF [R8][R9] (our check: the smallest water-year release since
  1966). Drought Response Operations: 0.66-1.0 MAF extra from Flaming Gorge to Powell by April 2027 [R9].
- About 26 years of multidecadal drought [R1].
- Since 2000 natural flow at Lees Ferry has averaged about 12.4 MAF; 2000-2018 averaged 12.47 MAF, 15.5 % below the
  1906-2018 average of 14.76 MAF [R20]. The Compact's negotiators assumed about 16.4 MAF from the gauge years then
  available (to verify: primary source).

## October 2026: rain, briefly
- 20-22 Oct storms over northern Arizona and southern Utah: unregulated inflow into Powell reached 65,000 cfs, the
  second-highest October daily inflow since 1963 [R11]. Powell rose from 3,518.34 ft (1 Oct) to 3,533.46 ft (2 Nov)
  [R8]. Mead set its record low on 22 Oct and rose about 2 ft by 2 Nov [R8].
- ABC15: this year's average level is the lowest on record; Powell "remains at serious risk of reaching 'dead pool'"
  [R11].

## Outlook (Reclamation October 2026 Most Probable, 6 maf release [R9])
- Powell: low 3,516.28 ft end of February 2027, then 3,548.86 ft in June 2027 with a 7.8 MAF WY 2027 inflow
  (forecast made before the late-October storms).
- Mead: falls to 1,007.73 ft at the end of July 2027 (would be a new record by about 30 ft). (The 7 maf scenario
  is higher for Mead: check before quoting a range.)
- Evaporation WY 2026: Lake Mead 457,000 AF, Lake Powell 181,000 AF [R9].

## The dam and its limits
- Glen Canyon Powerplant: 1,320 MW rated [R14]. Below 3,490 ft (minimum power pool) water can pass only through the
  four river outlet works, which bypass the turbines; Reclamation is working to minimise cavitation damage there and
  the dam "was not envisioned to operate solely through the outlet works for an extended period" [R14].
- Dead pool (no water can leave by gravity): Powell 3,370 ft; Mead 895 ft (to verify both with Reclamation).
- Lake Powell capacity at full pool (3,702.91 ft NAVD88 = 3,700 ft NGVD29): 25,160,000 AF in 2018, 6.79 %
  (1,833,000 AF) less than in 1963 because of sediment; area at full pool 159,200 acres; full pool first reached
  in 1980; more than 4 million visitors a year [R12].
- Las Vegas: Intake No. 1 stops working at 1,050 ft (exposed 2022); No. 2 works to 1,000 ft; Intake No. 3 with the
  Low Lake Level Pumping Station (2020) keeps drawing water even below 895 ft [R18] (to verify elevations).

## Who uses the water (2000-2019 averages, [R15], CC BY 4.0)
- More than 40 million people and more than two million hectares of cropland depend on the river.
- Irrigated agriculture: 74 % of direct human uses, 52 % of all consumption (including reservoir evaporation and
  riparian/wetland use); three times all other direct uses combined.
- Cattle feed crops (alfalfa and other hay): 46 % of all direct water consumption.
- Calendar 2026 diversions (projected): Metropolitan Water District (Southern California) 0.793 MAF; Central
  Arizona Project 0.943 MAF; Southern Nevada 0.200 MAF [R9].
- Southern Nevada used 198,000 AF in 2025; it cut Colorado River use about 40 % over 25 years while adding more than
  800,000 residents (SNWA via [R4]).

## The Compact fight (give both sides)
- 1922 Compact: 7.5 MAF a year of consumptive use for each basin; the Upper Division "will not cause the flow of the
  river at Lee Ferry to be depleted below an aggregate of 75,000,000 acre-feet for any period of ten consecutive
  years" [R19]. Mexico treaty 1944: 1.5 MAF a year.
- Lower Basin reading: the obligation is 82.5 MAF over ten years (75 + half of the 1.5 MAF a year owed to Mexico);
  Upper Basin reading: 75 MAF is the whole obligation [R16]. UCRC and Arizona officials expected the ten-year flow at
  Lee Ferry to dip below 82.5 MAF by October 2026; Eric Kuhn calls it the "first tripwire" [R16]. The Compact has
  never been enforced; crossing 82.5 gives the Lower Basin a legal argument, not an automatic consequence [R16].
- Our check [R8]: Glen Canyon releases WY 2017-2026 sum to 80.0 MAF (WY 2016-2025: 83.0 MAF).
- Upper Basin position: the Upper Division states are in full compliance with the Compact and their uses must not be
  curtailed [R22]; their water users already live with whatever the snowpack brings (to verify with a quote). The
  federal government lacks authority to mandate upstream cuts; the states coordinate through the Upper Colorado River
  Commission (Colorado Sun via search, to verify).
- Lower Basin position: Nevada and Arizona say Interior put the whole burden on three states and should have
  analysed alternatives with Upper Basin cuts [R4][R6]. Nevada: Interior did not analyse the economic impact on
  Southern Nevada's $180 billion economy [R4].

## Into court
- 24 Aug 2026: Nevada, the Colorado River Commission of Nevada and SNWA sue in U.S. District Court for the District
  of Nevada under the APA, NEPA and the "Law of the River"; they ask the court to vacate the ROD, the Final EIS and
  the guidelines [R3][R4]. Nevada's worst case: cuts of up to 213,556 AF of its 300,000 AF if Lower Basin shortages
  reach the framework's 3.6 MAF outer limit after 2028 [R4]. Gov. Joe Lombardo: Southern Nevada "could lose more than
  70 percent of its already meager Colorado River allocation" [R4].
- 16 Oct 2026: the Arizona Department of Water Resources moves to intervene; CAP files its own motion [R6]. Gov. Katie
  Hobbs calls the cuts "draconian" [R6]. Burgum says the suit will be tossed because "you can't be injured in
  theory" [R6].
- Experts warn a Supreme Court compact case would take years and "everybody loses" [R16].

## Own calculations (show on screen as our analysis)
1. Combined storage, Reclamation data [R8]: 46.45 MAF on 1 Jan 2000 -> 11.95 MAF on 16 Sep 2026. Lost 34.5 MAF
   (74 %), about 42.5 km3. The low is 23 % of the 1983 peak (52.49 MAF).
2. Lake Powell's surface, Reclamation area series [R8]: 146,563 acres (593 km2) on 1 Jan 2000 -> 54,620 acres
   (221 km2) on 15 Sep 2026, 63 % smaller. At the 1983 peak: 167,575 acres (678 km2).
3. Evaporation vs the cuts, Reclamation's own numbers [R9]: WY 2026 evaporation from Mead and Powell = 638,000 AF:
   84 % of Arizona's 760,000 AF cut, 51 % of the whole 1.25 MAF Lower Basin cut, 2.1 times Nevada's entire allocation.
4. Ten-year flow past Glen Canyon Dam [R8]: 80.0 MAF for WY 2017-2026, below the Lower Basin's 82.5 MAF reading
   and above the Upper Basin's 75 MAF.
5. (Step 4) Future shoreline of Lake Powell at 3,490 ft (power stops) and 3,370 ft (dead pool) from the USGS
   topobathymetric DEM [R13], areas from the 2018 EAC tables [R12]; datum: NAVD88 = NGVD29 + 2.91 ft at Powell.
Scratch scripts (session scratchpad, levels.py): move into tools/colorado_numbers.py in step 4.

## Still to verify / research
- Hoover Dam and Lake Mead basics (completion 1936, height, 2,080 MW, capacity), Glen Canyon Dam basics (gates
  closed 1963, completed 1966, height), Mead and Powell dead pools, the Compact's 16.4 MAF assumption (primary).
- CAP canal length and lift, Imperial Irrigation District (largest single user), Upper Basin consumptive use.
- A direct Upper Basin quote after the ROD (UCRC or a governor).
- Whether the 7 maf scenario changes the Mead outlook; Interior's court response (due end of October 2026).

## Visual inventory
(step 2)
