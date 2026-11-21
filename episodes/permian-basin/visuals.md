# Permian Basin: visual inventory (2026-11-22)

All photos: Commons, licence checked (PD, CC0, CC BY only; scratch catlist.py / tools/find_media.py use pipeline/commons._allowed),
contact sheets looked at by eye; episode_check detail ratios all >= 0.65 (soft files dropped: CIRA VIIRS PNGs, 1924 Carlsbad
scans, rig 33, halite crystal, Wall Tower crop, EPA 1972 cantina, the fracking schematic, Pump Jack 8744524982).

## Painted regions
geo/make_regions.py from the EIA "Permian Basin: boundary, structure and tectonic features" shapefiles (Dec 2017, public domain,
https://www.eia.gov/maps/map_data/PermianBasin_Boundary_Structural_Tectonic.zip): basin extent (63,820 sq mi in EIA's outline),
Delaware Basin 12,026 sq mi, Central Basin Platform 6,212 sq mi, Midland Basin 12,608 sq mi, Capitan Reef trend (northern
Delaware rim only; narration's 400 miles is the NPS figure for the whole complex).

## Satellite (Sentinel-2, scratch pbsat.py 2026-11-21)
| View | Result |
|---|---|
| Loving County pads (-103.65, 31.82) 0.25 / 0.10 | **strong**: pale pads in rows, roads on a grid; 2025-10-03 single day, colours richer than May |
| Midland, Odessa (0.20-0.25) | clear, cities and the pad grid around them |
| Guadalupe Mountains (0.30), El Capitan (0.10) | **strong**: the escarpment and the reef tip, salt flat to the west |
| Carlsbad area (0.30) | clear, Dark Canyon; cavern view re-centred to -104.44, 32.17 |
| WIPP (0.08) | **strong**: the plant, its roads and pads |
| Wink (0.08) | **strong**: Wink Sink 2 visible as a dark water-filled circle (2025-10-03) |
| Big Lake / Santa Rita area, Yates field | clear; old field patterns |
| Salt Basin flats west of the Guadalupes (0.40) | **strong**: white playa, pivots |
| Night | pipeline `night` layer for the Permian glow (replaces the soft CIRA PNGs) |

## Photos by part
- Hook: Pecos County panorama (CC0), Whites City flare 1 and 2 (CC BY 2.0, Permian Basin, NM), Midland skyline (CC BY 4.0),
  Loving County road (CC BY 2.0), horse-head pumpjack at night (CC BY 2.0).
- Reef: El Cap GUMO, El Capitan 4389347934 and 9330499901, Guadalupe Mountains NP 53196... (CC BY 2.0), LoC Highsmith views (PD),
  Guadalupe Peak (PD), Guadalupe escarpment (CC BY 2.0), stylolites in Capitan/Lamar limestone (CC BY 2.0).
- Caves: Big Room set (NPS, PD), Lechuguilla overview (PD), Parks Ranch gypsum cave (BLM, PD), Carlsbad Caverns NP / White's City
  set (CC BY 2.0).
- Salt: WIPP mining photos and 2004 plant photo (DOE, PD), Permian rock salt (Austria, CC BY 2.0), halite (CC BY 2.0).
- Boom: Santa Rita No. 1 front/side/marker/plaque (CC BY 4.0), Texon derrick (CC BY 2.0), Reagan County courthouse (CC BY 4.0),
  Odessa postcard, Superior Oil 1949, jackknife rigs near Midland (no known restrictions), Gulf Oil plant 1956, Midland 1928 map
  (NARA, PD), Highsmith pumpjack (LoC, PD; Runnels County, labelled "West Texas").
- Bill: Mentone sign, Loving County courthouse / water tower / line (CC BY 2.0), Wink signs and Highsmith Wink window (PD),
  Winkler County courthouse (LoC, PD), ISS-65 Odessa (PD).
- Gap: no free photo of a modern Permian frac spread or a Wink sinkhole from the ground -> satellite views instead.
