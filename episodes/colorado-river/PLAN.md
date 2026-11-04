# colorado-river: production plan

Resume from the first unchecked box. Every step ends with a commit and a log line.

Working question (to be tested by the research, not assumed): in August 2026 Washington imposed the first cuts on
the Colorado River after the seven states failed to agree, with Lake Powell and Lake Mead holding less water together
than at any time since Lake Powell began filling in 1963. Is the river that built the American Southwest running out,
and who gives up water first?

Audience: American viewers first (user, 2026-11-04). Familiar places (Las Vegas, Phoenix, Los Angeles, Denver, the
Grand Canyon, Hoover Dam) carry the hook; every number in US units first (feet, acre-feet), metric where it helps.

## Steps
- [x] 1. Research dossier (`research.md`): every number with a source (two where possible); 2-3 own calculations, maths shown
- [x] 2. Visual inventory (in `research.md`): Sentinel-2 before/after sites and dates, GIBS MODIS years, public-domain
      US government photos (USBR, NPS, USGS, NASA, Library of Congress), Commons PD/CC0/CC BY files, data series, stock queries
- [x] 3. Outline (`outline.md`), Turkish summary to the user (gate 1: approved 2026-11-04)
- [x] 4. Features the outline needs: Lake Powell at lower levels (tools/powell_shoreline.py on Actions, geo/*.geojson),
      canal and river lines (lines.json), basin outlines (geo/), credits for file: areas and NHD lines, tools/colorado_numbers.py
- [x] 5. Script (`script.json`), humanizer pass on the narration
- [x] 6. Fact-check pass: every claim against `research.md`
- [x] 7. Storyboard run, self-review of every frame, fixes (2 rounds)
- [ ] 8. Full render, download to `Videos\yt-pipeline\colorado-river`, user review (gate 2)

## Log
- 2026-11-04: topic chosen by the user (over the Outer Banks house collapses, sinking US cities and Greenland), with
  "start now". Research started. Hook: Interior's Record of Decision (21 Aug 2026), 1.25 million acre-feet Lower
  Basin cut in 2027 and 2028, Nevada's lawsuit (24 Aug 2026).
- 2026-11-04: research.md and outline.md done. Fresh facts: both record lows from Reclamation's daily data (Powell
  3,516.62 ft on 15 Sep, Mead 1,037.16 ft on 22 Oct), Arizona and CAP joined the suit (16 Oct), Minute 334 with
  Mexico (2 Sep), the late-October storm, the Compact's ten-year "tripwire". Own numbers: combined storage -74 %
  since 2000, Powell's surface -63 %, evaporation 638,000 AF vs the cuts, 80.0 MAF past the dam in ten years.
  Scratch script: session scratchpad colorado/levels.py (moves into tools/ in step 4). Waiting for gate 1.
- 2026-11-04: gate 1 approved. Step 4: ScienceBase works from Actions (blocked from the PC), so the USGS 2017
  bathymetry (414 MB) is read on Actions; our areas are within 2 % of the USGS 2018 table. Steps 5-6: script 2,310
  words in 8 chapters (est. 15.9 min), 4 asks, one subscribe line; photos all PD (NARA, NPS, USBR, DPLA) checked on
  Commons; MODIS days screened with GIBS (Powell 2000-09-09 / 2026-09-10, Mead 2000-09-09 / 2026-08-22). Fact-check
  fixed six wordings (unregulated inflow, release-cut timing, houseboats, "dry years", Flaming Gorge, "by next
  summer"). Title by yt-package: "Lake Mead and Lake Powell Both Hit Record Lows in 2026" + "WHO GETS CUT?". Next:
  storyboard (step 7).
- 2026-11-04: storyboard run 41769780405 failed in prepare (GEOS "side location conflict": powell_dry_3490 and
  lower_basin had self-touching rings); maps.py now repairs file: areas with make_valid. Also added visual beats where
  a shot held 20-35 s (prepare notes). Storyboard 1 (run 41772809879): 16:58, 75 units from 85 shots. Fixed: no usable
  Sentinel-2 scene in summer 2017 (cold open now summer 2019, about 3,620 ft); bar-chart reference label ran off the
  right edge (ChartScene puts it left of the line near the edge); Lake Mead chart 2022/2026 labels collided (axis
  from 1983); off-topic stock (desert power lines for canals, snowy peaks for the record-low snowpack, another dam for
  Hoover, rice paddies for Arizona) replaced by NARA canal / Imperial Valley photos, a MODIS snow comparison of
  Colorado's mountains (19 Mar 2023 vs 25 Mar 2026, picked by eye from GIBS), Sentinel-2 close-ups of Hoover Dam and
  Yuma; labels or markers in the caption band zoomed cameras out (Morelos, Las Vegas intakes, the delta): moved; the
  whole-lake Powell views need about 3.1 degrees for every overlay, so they use the MODIS day 2026-09-10 instead of
  Sentinel-2; the dead-pool layer stayed on in the next paragraph (keep + clear): keep off; the 1.25 MAF bar read "1.3"
  (now acre-feet). Next: storyboard 2.
- 2026-11-04: storyboard 2 (run 41774639045): 17:04, 71 units from 85 shots, no map warnings. Confirmed: July 2019
  cold-open wipe, reference label inside the frame, Mead chart labels apart, MODIS snow comparison, NARA canal and
  Imperial Valley photos, Hoover / Yuma / delta close-ups, cuts chart in acre-feet, cameras no longer pulled out by
  labels. The Powell lower-level steps add overlays without a camera stop, so the storyboard has no still of them
  (storyboard 1 showed both layers drawing correctly); check them in the final MP4. Next: full render (step 8).
- 2026-11-04: render 41776212017 (17:04, 328 MB, -14.5 LUFS, true peak -0.3 dBTP) reviewed from frames pulled out of
  the MP4. Fine: the Powell lower-level steps (3,490 ft layer at 09:08, dead pool at 09:14, P5.4 with the 3,490 layer
  only), the cold-open wipe, the MODIS / snow / Overton compares, the canal lines, charts, closing card. Found (both
  were on storyboard 2 as well, missed in that review): a sharp Sentinel-2 rectangle around Glen Canyon Dam on the
  3.1-degree MODIS views (08:52-09:30; S2 only faded out from 2.6 degrees) and a straight seam down the delta close-up
  (16:40-16:52; the eastern tiles from 6 May, the western from 10 March). Fixes: MapBlock fades S2 out at 2.0-2.6
  degrees where a MODIS image covers the frame; the delta view uses 2026-10-03, when S2A and S2B (10 minutes apart)
  cover its whole box. Pipeline: window mosaics now start from the clearest day that covers the whole box (then the
  highest sun), and maps.py notes S2 images stitched from several days. The Flaming Gorge route now starts at the dam
  (it ran from the Green River's source in Wyoming). Stills run 41784500831 to check, full render 41784506403.
- 2026-11-04: stills 41784500831 confirmed both fixes (no rectangle at 09:00-09:25, the delta in one piece) and the
  route from the dam. Its new map notes listed 8 S2 images stitched from several days; checking those views and the
  moments between storyboard stops in the MP4 found three more flaws, so render 41784506403 was cancelled:
  P5.7 (10:36-10:49) showed Lake Powell's bed as a blurred band (first read as Sen2Cor's cloud mask; see the next
  entry for the real cause; view on 2026-09-20); the 2023 backdrop under the cold-open compare showed a
  fuller lake for a moment as the compare faded (00:16; the step now uses the after month), and the same at the Powell
  MODIS compare (06:56; 2.05 degrees + the after day, so the backdrop is that MODIS image); and the chart cut in before
  the snow wipe reached March 2026 (wipe 2.4 s, chart at "the runoff headed"). Mexicali, Flaming Gorge, Yuma and the
  July 2019 image mix days without a visible seam. Stills 41786439077, full render 41786443194.
- 2026-11-04: stills 41786439077 confirmed the cold-open and P4.3 fades (the backdrop now matches the after image) and
  the snow wipe (March 2026 whole for about 2.5 s), but P5.7 still had the band, so render 41786443194 was cancelled.
  Real cause: S2 views wider than 1.5 degrees are cut to Natural Earth land minus lakes, and Natural Earth draws Lake
  Powell at full pool, so Blue Marble's 2004 lake showed inside the full-pool outline (the mask over P5.7's box has
  exactly the band's shape). S2 now keeps lakes (land_mask(lakes=False)); the first-observation fill for cloud-masked
  holes stays as a safeguard. Stills 41788062439, full render 41788066410.
- 2026-11-04: stills 41788062439: P5.7 shows the real lake now, but measuring the frame found a straight seam at
  -111.0 degrees (luminance +9, blue +20 across the 12SVG/12SWG boundary: S2A and S2B passes 11 minutes apart, filled
  tile by tile in cloud order); the delta has a fainter one (blue +10). Render 41788066410 cancelled. One-day and
  covering-day mosaics now fill pass by pass, the pass covering most of the box first (_by_pass), and a hand-picked
  one-day window skips the cloud mask. P5.7 (-111.06, 37.32, 1.55) and the delta (-114.90, 31.92, 0.9) moved slightly
  so that S2A's pass covers 99.7-99.9 % of the frame (the new boxes also mean fresh mosaics). Stills and full render
  dispatched next.
