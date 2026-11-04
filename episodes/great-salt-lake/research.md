# great-salt-lake: research dossier

Sources are numbered R1... Every number in the script must trace to a line here. Own calculations show their maths.

## Sources
- R1 USGS NWIS daily values, site 10010000 "Great Salt Lake at Saltair Boat Harbor" (south arm), parameter 62614
  (lake surface elevation, ft above NGVD 1929), public domain:
  https://waterservices.usgs.gov/nwis/dv/?format=rdb&sites=10010000&parameterCd=62614 (read 2026-11-05; values after
  mid-2025 are provisional, flag P). North arm: site 10010100 (same parameter).
- R2 Salt Lake Tribune, "What happens if Great Salt Lake..." (2026-08-16): mid-August 2026 level 4,190.40 ft; 2021 low
  4,190.20 ft; all-time low 4,188.5 ft (November 2022).
- R3 Utah News Dispatch / Missoula Current, "Great Salt Lake not expected to hit new low in 2026" (2026): state officials
  do not expect a 2026 record, but call a 2027 record "unavoidable" after a repeat of the dry 2025-2026 winter.
- R4 Utah Public Radio, "Will the Great Salt Lake hit a new record low this year?" (2026-05-15): University of Utah
  atmospheric scientist Derek Mallia on dust events from the exposed lakebed.

- R5 Wurtsbaugh et al. 2017, "Decline of the world's saline lakes", Nature Geoscience, doi:10.1038/ngeo3052 (press:
  ScienceDaily 2017-10-23, USU Today): water development since the 1850s lowered the lake about 11 ft and cut its area
  by nearly half (water balance); agriculture over 60 % (one account 63 %) of the basin's water use; about 29 % more
  water needed for a healthy lake. Same 11 ft in the 2016 white paper "Impacts of Water Development on Great Salt Lake
  and the Wasatch Front" (lake down 48 %, 11 ft since 1847). Verify the DOI page before citing on screen.
- R6 Utah Division of Water Resources (water.utah.gov/?p=11): West Desert Pumping Project cost $60 million; pumps ran
  April 1987 to June 1989, 26 months (Deseret News 2011 / KSL); New York Times 1987-04-11, "Pumping is begun to create a
  second Great Salt Lake". USGS WRI 91-4117 report on the project (pubs.usgs.gov/wri/1991/4117/report.pdf, public domain:
  candidate document shot).
- R7 Dust: about 800 square miles of lakebed exposed (Salt Lake Tribune 2024-10-16; University of Utah survey 2018);
  arsenic among the elements of concern; Grineski et al. (U of U): dust hits disadvantaged communities hardest; Putman
  et al. (USGS, GeoHealth): arsenic a contaminant of concern by ingestion; Kevin Perry (U of U) told lawmakers dust
  concentrations have on occasion violated national air standards. Other side: Utah Division of Air Quality says the
  Wasatch Front meets the PM10 standard and a decade of monitoring shows no rise in airborne arsenic (deq.utah.gov).
- R8 Economy: 2012 study for the Great Salt Lake Advisory Council: $1.32 billion annual output, 7,706 jobs; state
  materials: $1.9 billion a year; brine shrimp about $57 million (2012), 35-40 % of the world's brine shrimp eggs; the
  lake adds 5-8 % of Utah's snowfall (lake effect); ECONorthwest 2019: the lake's demise could cost $1.7-2.2 billion a
  year and 5,368 jobs. Magnesium: one source says all U.S. magnesium for aluminium comes from the lake (verify).
- R9 Great Salt Lake Commissioner, Strategic Plan (2024-01-15, greatsaltlake.utah.gov): target range 4,198-4,205 ft;
  about 1 million acre-feet a year of extra water in drought, 471,000 in normal years; strike team: healthy (4,198 ft)
  by 2055 with 800,000 extra acre-feet a year (Fox13); a resolution for a 4,198-ft goal was rejected by the legislature;
  the lake ended water year 2025 at its third-lowest level in over 120 years, about 7 ft below 4,198 (Fox13).

## Levels (R1, south arm, daily means; own reading of the USGS series)
| | Level (ft) | Date |
|---|---|---|
| All-time low (since 1847; daily-mean low in this series) | 4,188.5 | 7 Nov 2022 |
| Same trough, next winter | 4,189.2 | 3 Jan 2023 |
| **2026 low so far** | **4,189.4** (provisional) | **10 Oct 2026** |
| 2021 low | 4,190.2 | 18 Oct 2021 |
| 2025 low | 4,191.0 | 28 Sep 2025 |
| 1963 low (the record before 2021) | 4,191.35 | 15 Oct 1963 |
| Peak of the series | 4,211.6 | 3 Jun 1986 (4,211.5 on 15 Apr 1987) |
| Latest reading | 4,190.0 (provisional) | 3 Nov 2026 |
| 2026 spring high | 4,192.6 | 2 Apr 2026 |

Own calculations:
1. 2026 low vs the record: 4,189.4 - 4,188.5 = 0.9 ft, so "less than a foot above the all-time low".
2. Drop since the 1986 peak: 4,211.6 - 4,189.4 = 22.2 ft.
3. Spring rise in 2026: 4,192.6 - lowest before it (to compute from the series: winter 2025-26 low) - to do.
4. Below the healthy range (R9): 4,198 - 4,189.4 = 8.6 ft under its lower edge in October 2026.
5. Pumping irony (R6): $60 million spent in 1987-1989 to lower the lake; it now sits 22.2 ft below its 1986 peak.
Caution: R2's "4,190.40 in mid-August" and R1 agree (August 2026 readings ~4,190.4); the 2026 October low below the
2021 low happened after R3 was written (R3 expected no 2026 record; still true: 4,189.4 > 4,188.5).

## Visual inventory (step 2, preliminary)
- Levels for compare dates (R1): 2000-09-15 4,201.2 ft; 2017-06-09 4,195.5 (the highest since Sentinel-2 began in
  2015); 2022-11-07 4,188.5 (record); 2026-10-10 4,189.4.
- MODIS compare (whole lake, about 1.5-2 degrees): a clear day around Sep 2000 vs Oct 2026 (11.8 ft lower); pick the
  days by eye in GIBS like colorado-river.
- Sentinel-2 compares (close views): June 2017 vs October 2026 (6.1 ft lower) on Farmington Bay, Antelope Island's
  shore and Bear River Bay; one-day windows covering each box (sentinel._covering_day or a hand-picked "D/D").
- The railroad causeway (1959) splitting the pink north arm from the blue-green south arm: one S2 view.
- Documents (public domain): USGS WRI 91-4117 (the West Desert Pumping Project); USGS lake-level fact sheets.
- Archival: search Commons for the 1983-1987 flooding and the pumping station (photos / films, licence-checked).

## To research next (step 1 continues)
- Causes: share of the decline from upstream water use (Wurtsbaugh et al. 2017: ~11 ft from consumptive use), the
  2025-2026 record-low snowpack (links to colorado-river), evaporation.
- People and health: dust from the exposed bed (arsenic and other metals; studies by Perry, Mallia et al.), exposed
  area in square miles at today's level, 2.5 million people in the Wasatch Front.
- Economy and nature: brine shrimp (cysts for aquaculture), minerals (magnesium, potash, lithium), lake-effect snow for
  ski resorts, about 10 million migratory birds; the railroad causeway (1959) splitting a pink north arm from a green
  south arm (visible from orbit).
- History: the 1983-1987 flood (4,211 ft), the West Desert Pumping Project (1987-1989) pumping lake water into the desert.
- Policy 2022-2026: Utah's laws and spending, the Great Salt Lake Commissioner, targets (healthy range ~4,198 ft).
- Visuals: Sentinel-2 dates (high water 2017-2019? vs Nov 2022 vs Oct 2026), MODIS 2000 vs 2026; public-domain federal
  documents (USGS fact sheets) for document shots; Commons archival photos/film of the 1980s flood and the pumps.
