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
