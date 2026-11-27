# Wyoming: visual inventory (2026-11-27)

Licences: PD / CC0 / CC BY only (pipeline/commons.py checks; scratch picksheet.py checked all 74 picks). Search: scratch
catlist.py (Commons categories / searches) and wpimg.py (images used in the English Wikipedia articles on each subject,
licence-checked on Commons). Every file in build_script passed episode_check's sharpness test (detail >= 0.65).

## Sources that carried the episode
- **NPS / BLM trail photos (PD)**: South Pass saddle and overlook, South Pass ACEC, Bedlam ruts; BLM "mypubliclands"
  replica wagons on the Emigrant Trail (Wyoming); Guernsey ruts (CC0 / CC BY 3.0); Register Cliff.
- **Andrew J. Russell, Union Pacific 1868 (PD)**: Casement's track crew, Citadel Rock at Green River, Dale Creek Bridge;
  W. H. Jackson: Fort Laramie 1868, granite cut west of Cheyenne; Grant/Sherman/Dodge at Fort Sanders 1868 (LOC);
  "Cheyenne, Wyo., 1876" (NARA). Alfred Jacob Miller's Fort Laramie (Walters, PD).
- **Johnson County War**: "Invaders.gif" (672 px, the 1892 group photo) and the TA Ranch siege plan (656 px) are small:
  the pipeline upscales them; no other free picture of Champion, the KC or the TA Ranch exists on Commons.
- Women at the polls in Cheyenne (Frank Leslie's 1888, LOC; page cut with `#crop=0.12,0.22,0.12,0.06`).
- Teapot Dome: Harris & Ewing (LOC) portraits of Albert Fall, Sinclair at the hearings, Fall after the 1929 verdict.
- Coal: Peabody Energy's own CC BY 3.0 photos of North Antelope Rochelle (haul truck, mine, dragline).
- Modern Wyoming: Tony Webster CC BY 2.0 (I-80, Laramie, Gillette, UW), Chevsapher CC0 (Jeffrey City, Casper),
  USFWS (Seedskadee, Red Desert sage-grouse, sagebrush, Elk Refuge, Pinedale cattle drive), HABS Moulton Ranch (PD).

## Rejected
Soft (detail < 0.65): Fort Bridger croquet 1873, Bear River City restaurant, Russell's Church Buttes, Laramie depot 1885,
Hayden survey at Yellowstone Lake, NARA oil wells near Teapot Dome, Gillette aerial postcard. Wrong place: "Bear River
City.jpg" (a modern building), the "Teapot Rock" photos at Green River (not the Teapot Rock of Teapot Dome), the Keeney
Historic Site trail photos (Oregon, not Wyoming), "Dugout home2.jpg" (not Wyoming). Unclear or dull: Bierstadt's dark
Oregon Trail, Oregon Buttes, stereo pairs, mounted album pages, the Upper Geyser Basin map.

## Satellite (Sentinel-2), scratch wysat.py, window 2025-07-01/2025-09-20
Clear: South Pass, Guernsey, Great Divide Basin, Benton site (Sinclair), Cheyenne, Elk Mountain, Yellowstone Lake (small
cloud), Jackson Hole (small cloud), Jeffrey City, North Antelope Rochelle, Gillette, Chokecherry site, Naughton plant at
Kemmerer, Rock Springs, Iowa farms, central range, Teapot Dome, Casper, Fort Laramie, Kaycee (KC Ranch).
Laramie: cloud in 2025 -> 2024-07-01/2024-09-15 (2024-07-29 clear).

## Painted layers (geo/make_regions.py, numbers in make_regions.txt)
Federal land and BLM from BLM's Surface Management Agency service (47.0 % federal), Teton County 91.9 % federal, the
1868 line and its 20 km band (M1), counties (Census), the UK moved onto Wyoming at true size, and an ILLUSTRATIVE
checkerboard of one-mile squares at Elk Mountain (labelled "illustration" on screen; not surveyed parcels).

## Gaps
No free photo of Benton, Nate Champion, the KC Ranch, Fort McKinney, the Cheyenne Club, the 1886-87 winter, Teton Pass
or the Natrium site: maps, cards and present-day satellite views carry those sentences.
