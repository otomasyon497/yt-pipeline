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
- [ ] 7. Storyboard run, self-review of every frame, fixes
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
