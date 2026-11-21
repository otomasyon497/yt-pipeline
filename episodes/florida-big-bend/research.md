# Why Almost Nobody Lives on Florida's Big Bend Coast (research, started 2026-11-21)

Demand: PASS (214x, 185x, 28.8x). Competitors: competitors.md. Status: OK = primary/official read; CHECK = secondary
or sources disagree; OWN = our measurement (scratch tools, reproducible).
Raw files (scratchpad bigbend/src): NHC TCRs Idalia/Helene/Debby (PDF text), cedarkey_monthly.json (NOAA CO-OPS),
co-est2024 / sub-est2024_12 (Census), shelf.json (ETOPO), nws1896.pdf.

## The shelf (the spine)
| Fact | Value | Source | Status |
|---|---|---|---|
| Gradient | Big Bend marsh coast "such a low gradient (1:5,000) that it has been referred to as an incipient epicontinental sea (Hine et al., 1988)"; barrier coast to the south ~1:2,000 | USGS OFR 01-303 (Hine et al. 2001), shelf.html (read via curl) | OK (short quote ok) |
| Wave energy | marsh coast has lower wave energy than the sandy coast; both low-energy vs most US Gulf/east coasts; small Gulf fetch | USGS OFR 01-303 | OK |
| Sediment | "Big Bend region ... is considered sediment-starved" | Wood & Hine 2003 (J. Coastal Res.), USGS pubs 70180962 abstract | OK (abstract) |
| Distance to the 10 m contour | Keaton Beach 21 km, St Marks 26 km, Steinhatchee 26 km, Cedar Key 25 km, Crystal River 36 km; vs Pensacola Beach 1.5 km, Miami Beach 2.0 km, Panama City Beach <0.5 km, Clearwater 12 km, Naples 12 km | NOAA ETOPO 2022 60s, scratch shelf.py (rays from shore, 0.1 km steps) | OWN (60 arc-sec grid ~1.8 km: say "about") |
| Depth 5 km out | Cedar Key ~1.7 m, Keaton Beach ~2.5 m, Steinhatchee ~3.6 m; Pensacola ~22 m, Miami ~83 m | same | OWN |
| Depth 50 km out | Cedar Key ~16 m, Steinhatchee ~16 m; Pensacola ~101 m | same | OWN |

## Protected coast
| Fact | Value | Source | Status |
|---|---|---|---|
| Big Bend Seagrasses Aquatic Preserve | 984,325 acres ("nearly 1 million"), largest in Florida; Apalachee Bay to the Withlacoochee, >150 miles; Wakulla, Jefferson, Taylor, Dixie, Levy; established 1985; one of the largest contiguous seagrass meadows in the Gulf | FDEP / floridaaquaticpreserves.org page | OK |
| St Marks NWR | Executive Order 5740, 31 Oct 1931, "St. Marks Migratory Bird Refuge", wintering habitat for migratory birds; renamed NWR 1940; 86,000+ acres in Wakulla, Jefferson, Taylor; about 43 miles of Gulf coast; >17,000 acres wilderness | USFWS refuge page fws.gov/refuge/st-marks/about-us | OK |

## Ground full of holes (karst)
| Fact | Value | Source | Status |
|---|---|---|---|
| Wakulla Springs | first-magnitude (64.6 M gal/day or more); average flow ~623 cfs, ~400 M gal/day; one of 31 first-magnitude springs in Florida; vent ~180 ft below land surface, opening into a large cave network | NWFWMD Wakulla Springs page | OK |
| Aucilla River | crosses karst, disappears underground and reappears ~30 times in the Aucilla River Sinks; last return above ground at Nuttall Rise before the Gulf | Wikipedia citing SRWMD 1991 SWIM plan p. 8 and FWC paddling trail guide | CHECK -> attribute ("the river goes underground again and again") |
| Woodville Karst Plain | thin sand over the limestone aquifer; Wacissa and St Marks rivers also sink and rise | WFSU, UF/IFAS (secondary) | CHECK (general wording only) |
| USGS FS 151-95 (Florida springs) | PDF 403 to our fetch | - | not used |

## People (Census Bureau population estimates, vintage 2024; base = April 2020)
| Place | 2020 base | 2024 | Status |
|---|---|---|---|
| Florida | 21,538,192 | 23,372,215 | OK |
| Jefferson / Taylor / Dixie / Levy counties | 14,512 / 21,797 / 16,756 / 42,913 | 15,921 / 21,843 / 17,614 / 47,765 (sum 103,143) | OK |
| Wakulla County | 33,766 | 37,115 | OK |
| Pinellas County | 959,111 | 965,870 | OK |
| Cedar Key city | 685 | 736 | OK |
| Horseshoe Beach town | 166 | 173 | OK |
| Yankeetown 588 -> 633; St Marks 277 -> 312; Perry 6,863 -> 7,306; Cross City 1,693 -> 1,816; Crystal River 3,554 -> 3,661 | | | OK |
| Cedar Key historical census | 1870 440, 1900 739, 1910 864, 1920 695, 1930 1,066, 1950 900 | Wikipedia table citing US Census | CHECK (no 1880/1890; competitor "5,000 in 1888" unverified: do not use) |

## History (Cedar Key)
| Fact | Value | Source | Status |
|---|---|---|---|
| Florida Railroad | Yulee's line Fernandina -> Cedar Key; first train 1 March 1861 | Wikipedia citing Turner 2003 | CHECK -> attribute or find Florida Memory |
| Pencil mills | Faber and Eagle Pencil cedar-slat mills on Atsena Otie / Way Key from the late 1850s-60s | Wikipedia citing McCarthy 2006 | CHECK |
| Plant | Plant's railroad to Tampa (reached 1884; service/steamships 1886) took Cedar Key's shipping | Wikipedia (1886) vs competitors (Jan 1884) | CHECK: say "in the 1880s" |
| 1896 hurricane | 29 Sep 1896; landfall winds ~125 mph; surge 10.5 ft above MSL at Cedar Key, ~12.6 ft at Yankeetown; death toll ~100, mostly surge | NWS Tampa Bay fact sheet (PDF read) | OK |
| After 1896 | Eagle mill destroyed, Faber closed 1898 (cedar shortage); town rebuilt on Way Key, Atsena Otie abandoned | Wikipedia (1896 hurricane; Cedar Key) | CHECK |
| Net ban -> clams | statewide net ban 1 July 1995; ~90 % of Florida's farmed clams from Cedar Key | Wikipedia citing Global Seafood Alliance | CHECK |

## Hurricanes (NHC Tropical Cyclone Reports, PDFs read)
| Fact | Value | Status |
|---|---|---|
| Idalia | landfall near Keaton Beach ~1145 UTC 30 Aug 2023, 100 kt (cat 3); "third-strongest hurricane to affect the Big Bend region", behind the 1896 Cedar Key Hurricane and Easy (1950); surge inundation 8-12 ft AGL Keaton Beach-Steinhatchee; Cedar Key gauge 6.89 ft above MHHW (at low tide: surge 8.91 ft above normal tide); 12 deaths, $3.6 B US | OK |
| Debby | landfall just west of Steinhatchee 1100 UTC 5 Aug 2024, 70 kt (cat 1); up to 6 ft AGL Keaton Beach-Cedar Key | OK |
| Helene | landfall ~10 n mi SW of Perry ~0310 UTC 27 Sep 2024, cat 4 (peak 120 kt 6 h before; 939 mb); "the strongest landfalling hurricane in the Florida Big Bend region since reliable records began around 1900"; 12-16 ft AGL from just west of Keaton Beach through Steinhatchee; 8-12 ft south of Steinhatchee through Cedar Key incl. Horseshoe Beach; Cedar Key gauge 9.30 ft above MHHW, "highest recorded water level since the station started reporting in 1914", breaking Idalia's 6.89 ft; ~25 % of homes in Cedar Key destroyed (media, per NHC); 14 surge deaths, all in Florida; 18 direct deaths in Florida; >=175 direct US deaths | OK |
| Three landfalls in 13 months | Idalia 30 Aug 2023, Debby 5 Aug 2024, Helene 27 Sep 2024 | OK (arithmetic) |

## Surge basics (pass 3)
| Fact | Value | Source | Status |
|---|---|---|---|
| Definitions | storm surge = "the rise in seawater level caused solely by a storm", "primarily by a storm's winds pushing water onshore"; its amplitude depends on coast orientation vs track, the storm's intensity, size and speed, "and the local bathymetry"; storm tide = surge + astronomical tide | NOAA NOS oceanservice.noaa.gov/facts/stormsurge-stormtide.html (read 2026-11-21) | OK |
| Helene stirred the shelf | NASA EO (PACE, 28 Sep 2024): Helene's winds and waves "churned up sediment from the seafloor along shallow coastal areas", making the water look bright | NASA EO image 153390 caption (Commons file description) | OK |
| Shelf amplifies surge (mechanism) | NHC surge page 403 to our fetch; not said as a sourced fact: narration says only "NOAA lists the shape of the seafloor" + our measurements + the gauge record | - | framing only |

## Not confirmed (pass 3, 2026-11-21)
Florida State Parks, Florida Memory and FWC pages refused our fetch (403). Not confirmed from an official page: Yulee railroad date,
pencil mills, Atsena Otie abandonment, Tampa 1880/1890 counts, clam share. Narration: attribute ("according to the town's
historians", "census counts") or leave out. Net ban: Florida Constitution Art. X s.16, adopted 1994 (flsenate.gov, summary
reading only) -> say "in the mid-1990s". UF/IFAS shellfish page: clam farming spread from the Indian River Lagoon (do not say it began at Cedar Key).

## Own measurement: Cedar Key gauge annual maxima (NOAA CO-OPS 8727520, monthly "highest", ft above MHHW, 1914-2025, 101 years)
Top: 2024-09 9.30 | 2023-08 6.84 | 2016-09 5.98 | 1996-10 5.15 | 1993-03 5.13 | 1972-06 4.21 | 2018-10 4.04 | 1966-06 4.00 | 2005-07 3.99.
The two highest in 101 years came in the last two. (Monthly product 6.84 vs NHC 6.89 for Idalia: use NHC values in narration.)

## Other attempts (pass 2)
| Fact | Value | Source | Status |
|---|---|---|---|
| Plant / Tampa | Plant bought control of the South Florida Railroad in 1883; it reached Port Tampa by the end of 1883; full Sanford-Tampa service began 1884 | UF Libraries, Ingraham expedition page "South Florida Railroad" | OK (say "in 1884") |
| Tampa population | 720 in 1880, 5,532 in 1890 | US census, via several sources | CHECK (secondary; fine to attribute) |
| Cross Florida Barge Canal | New Deal start in the 1930s, stalled after ~3 years; revived 1964 (Johnson); Nixon "permanently halted construction" in 1971 citing ecological damage, 28 % complete, $75 M spent; corridor now the Marjorie Harris Carr Cross Florida Greenway, >70,000 acres, 110 miles | Florida Museum (UF), "Florida Environmental History: The Cross Florida Barge Canal" | OK |
| Foley mill | Georgia-Pacific announced 18 Sep 2023 it would permanently close the Foley Cellulose mill in Perry; ~525 jobs; UF/IFAS estimated 1,879 potential job losses statewide; about two weeks after Idalia | GP news release 2023-09; UF/IFAS FRE report 2023 | OK |

## To do
- Night-lights view (pipeline layer "night") for the dark arc; Sentinel-2 Keaton Beach / Steinhatchee / Horseshoe Beach before-after Helene (Sep 2024 vs Oct 2024).
- Foley mill closure (Georgia-Pacific release 2023, jobs); Cross Florida Barge Canal (halt 1971, deauthorized 1990, Greenway); Wakulla/Aucilla karst (USGS/FGS); Plant/Tampa date; St Marks NWR; Sanborn maps Cedar Key (LOC).
