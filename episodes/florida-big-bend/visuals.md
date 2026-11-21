# Florida Big Bend: visual inventory (2026-11-21)

All photos: Commons, licence checked (PD, CC0, CC BY only; scratch catlist.py uses pipeline/commons._allowed), sizes from the
Commons API. Candidate lists: build/media/bb (find_media q1-q30, cats.txt; not committed). Contact sheets looked at by eye.
Satellite tests: scratch bbsat.py (pipeline/sentinel.py + landsat.py), 2026-11-21.

## Satellite (tested)
| View | Result | Use |
|---|---|---|
| Big Bend coast wide, S2 2025-03-11, span 0.9 (Keaton Beach-Steinhatchee) | **strong**: no beach anywhere, a ragged marsh fringe, the sea pale and green for miles (shallow, seagrass) | ch. 1 "no beach" proof, hook |
| Cross Florida Barge Canal Gulf end, S2 2025-04-17 (span 0.22) and Landsat 5 1985-01-16 | **strong**: the dead-straight channel with its spoil islands running ~10 km into the Gulf; power plant canals beside it; 1985 almost identical | ch. 4 (the canal that stops) |
| Foley mill, S2 2025-05-05 (span 0.10) | clear: the mill, its ponds, Perry airport | ch. 4 |
| St Marks lighthouse / river mouth, S2 2025-05-05 (span 0.22) | clear: marsh lobes, lighthouse point, river | ch. 2 / refuge |
| Aucilla mouth, S2 2025-05-05 (span 0.25) | clear: river ends in a maze of marsh islands | ch. 2 |
| Steinhatchee, S2 2025-04-12 (span 0.12) | clear: town on the river, marsh shore | ch. 5 |
| Keaton Beach, S2 2024-09-01/24 -> 2024-09-28/10-25 | **moderate**: after Helene the marsh behind the town is brown (salt burn) and the shore paler; houses too small to read at 10 m | ch. 5 wipe (say "the marsh turned brown", not "houses gone") |
| Horseshoe Beach, same dates | **moderate**: sand washed over the point and the marsh edge, water browner | ch. 5 wipe |
| Cedar Key, S2 2025-03/05 | hazy purple water, town readable; try another window before use | ch. 3 |
| Night lights | pipeline `night` layer (VIIRS) for the dark arc | hook |

## Photos per part (all >= 1,400 px)
- **Hook**: `File:Florida Peninsula at night, 13 October 2014 (ISS041-E-74232).JPG` (PD NASA; the dark Big Bend arc is visible),
  `File:Cedar Key Florida01.jpg`..`04.jpg` (CC BY 2.5 Ebyabe, 2007: grass running straight into the water, no beach),
  `File:Flickr - ggallice - Hammock.jpg` (CC BY 2.0, Cedar Key salt marsh).
- **1 Shallow sea**: `File:A scenic view of white lighthouse.jpg` (St Marks light over marsh grass), `File:Refuge boardwalks.jpg`,
  `File:Controlled burn in the salt marsh at St Marks NWR (7439799012).jpg` (PD USFWS), `File:Flickr - ggallice - Near lower Suwannee.jpg`,
  `File:Hurricane Helene Stirs Up Gulf Coast Waters (153390 - pace 20240928 lrg).jpg` (PD NASA EO; the shallow shelf lit up by stirred sediment),
  `File:Apalachee Bay, Florida-Georgia, satellite image map - NASA LANDSAT-1, 1-500,000, N3015W08346 LOC 79695112.jpg` (PD, 1970s false-colour).
  **Gap**: no free underwater photo of Big Bend seagrass (Commons seagrass divers are elsewhere) -> satellite + preserve stat card.
- **2 Ground full of holes**: `File:Big Bend Scenic Byway - Leon Sinks Geological Site - NARA - 7717294.jpg` (PD), Natural Bridge
  (`File:Natural Bridge Battlefield Historic State Park Pano.jpg`, `...Natural Bridge01.jpg`, CC BY: where the St Marks River goes
  underground), Wakulla (`File:Wakulla-springs 2009-05-03T23 48 20.jpg`, `...18 58 57.jpg`, `...19 12 53.jpg`, CC BY 3.0),
  `File:Wacissa river.jpg` (1200x1600, soft: probably skip), `File:Suwanee River tannic acid.JPG`, `File:St Marks River at Newport, Florida.jpg`.
- **3 Cedar Key boom**: `File:Bird's eye view of Cedar-Key, Fla., Levy Co. LOC 77690244.jpg` (PD 1884, 7440 px: the town at its peak),
  `File:Cedar Keys, Florida LOC 99447268.jpg` (1861 chart), `File:1852 U.S. Coast Survey Map of Cedar Key...` (PD),
  `File:Birds eye view of Florida and part of Georgia and Alabama LOC 99447266.jpg` (PD 1861 panorama),
  `File:Florida Railroad, from Cedar Key Extension to Tampa Bay - NARA - 102256504.jpg` (PD, very wide survey strip),
  `File:David Levy Yulee - Brady-Handy.jpg` (PD), `File:Yulee Sugar Mill Ruins01.jpg` (CC BY), `File:Old Tampa Bay Hotel.jpg` (Plant's hotel),
  Sanborn 1909 / 1920 / 1933 plates (PD), `File:After Great Hurricane of 1896 WDL4032.png` (PD, 1665 px; Cedar Key per WDL? check caption),
  `File:September 29, 1896 hurricane weather map.jpg` (PD), `File:Indian mound, Cedar Key, Fla, from Robert N. Dennis collection of stereoscopic views.jpg` (PD),
  `File:Atsena Otie Key Island.jpg` (CC BY 2.0 aerial), `File:Florida - Brandenton through Clearwater - NARA - 23936569 (cropped).jpg` (PD old aerial "CEDAR KEYS").
  **Gap**: no free photo of the pencil mills -> 1884 bird's-eye detail + stat card.
- **4 Every plan after it**: `File:Cross Florida Barge Canal ACoE.jpg` (PD route map), `File:Cross Fla Barge canal SR19E-02.jpg`, `...SR19W-03.jpg`
  (CC BY 2.5: the finished cut), `File:Santos CFBC trail 01.jpg` (Greenway), `File:Florida I75sb Cross Florida Greenway Overpass.jpg`,
  `File:Fenholloway River east of Perry Florida.jpg` (CC0; the mill's river). **Gap**: Foley mill only from orbit (S2).
- **5 Hurricanes**: `File:Florida National Guard in Keaton Beach, Florida (Hurricane Helene).jpg` (CC BY 2.0, 8256 px, 27 Sep 2024),
  `File:President Joe Biden surveys damage ... Keaton Beach ....jpg` (PD White House, damage street; frame without naming politics),
  Idalia Steinhatchee: `File:Florida National Guard (Idalia response).jpg`, `File:Florida National Guard - 53155016685.jpg`,
  `File:Florida National Guard - 53154586186.jpg` (CC BY 2.0, 30 Aug 2023), Perry power lines `File:Florida National Guard - 53153543735.jpg`,
  `File:Hurricane Idalia’s damage around Faraway Inn, Cedar Key, Florida.jpg` (PD NOAA aerial 31 Aug 2023),
  `File:Hurricane Idalia Makes Landfall Along the Coast of Florida’s Big Bend (CIRA 2023-08-30).png`, `File:Hurricane Helene Approaches the Florida Coast (CIRA 2024-09-27).png` (PD, 1920),
  `File:Hurricane Idalia Batters the Southeastern United States (MODIS).jpg` (PD).
- **Ending**: Steinhatchee river (`File:Steinhatchee River from Fort Steinhatchee Pier.jpg`, `...looking west from Roy's Restaurant.jpg`, CC BY 4.0),
  St Marks light (`File:St Marks Light - Florida.jpg`, HABS `...LCCN2011632986.tif`), `File:Deadman Bay, Stephensville and Steinhatchee historical marker.jpg`.

## Gaps
- Seagrass underwater, pencil mills, Foley mill on the ground, Horseshoe Beach on the ground: none free -> satellite, cards, maps.
- Own chart: Cedar Key annual maxima (research.md) as a bar/line chart; own map: distance to the 10 m contour (ETOPO) as labels.
