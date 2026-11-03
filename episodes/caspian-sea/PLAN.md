# caspian-sea: production plan

Resume from the first unchecked box. Every step ends with a commit and a log line.

Working question (to be tested by the research, not assumed): the Caspian, the world's largest lake, fell to its
lowest level in decades in 2026 and is still falling. Is this one more swing of a sea that has always risen and
fallen, or the start of a decline it will not recover from, and who pays first?

## Steps
- [x] 1. Research dossier (`research.md`): every number with a source (two where possible); 2-3 own calculations, maths shown
- [x] 2. Visual inventory (in `research.md`): Sentinel-2 before/after sites and dates, GIBS MODIS years, Commons PD/CC0/CC BY files, data series, stock queries (S2 dates are picked in step 4)
- [x] 3. Outline (`outline.md`), Turkish summary to the user (gate 1: approved 2026-11-03)
- [x] 4. Features the outline needs: MODIS compare + dated MODIS backdrops (gibs.py, maps.py, schema Compare.source),
      seafloor highlights "seafloor:<basin>:<m>" (bathy.py), Volga line (lines.json), year time axis in line charts
- [x] 5. Script (`script.json`): 2,160 words, 44 paragraphs, about 15.6 min; humanizer pass on the narration
- [x] 6. Fact-check pass: every claim against `research.md`
- [x] 7. Storyboard run, self-review of every frame, fixes (2 rounds)
- [ ] 8. Full render, download to `Videos\yt-pipeline\caspian-sea`, user review (gate 2)

## Log
- 2026-11-03: topic chosen by the user (over Antelope Reef and the Qosh Tepa canal). Research started.
- 2026-11-03: research.md and outline.md done. Fresh hooks: new islands off Kulaly (Euronews, 7 Oct 2026) and the
  first Caspian Environmental Summit (Avaza, 9 Oct 2026). Own checks: MODIS 2000 vs 2025 water count (about 15,700 km2
  lost in the NE box), ETOPO 2022 future shorelines (northern basin about 96 % gone at -10 m), about 913 km3 lost
  since 1996 (12 GERD reservoirs). Scratch scripts (session scratchpad: gibs_screen.py, water_area.py, ETOPO probe) move into tools/ in step 4. Waiting for gate 1.
- 2026-11-03: gate 1 approved. Steps 4-6 done. Features type-check / py_compile, not rendered yet (storyboard tests
  them). Script 2,160 words; humanizer pass (staged openers, "That is" chains, a forced triad, vague attributions).
  Fact-check fixed: "every clear day" (we sampled every third day), the 5 m shelf wording (84 % of the north gone),
  the -10 m remainder (full 1-arc-minute grid: under 4,000 km2, not 2,000). Own numbers reproducible with
  tools/caspian_numbers.py (MODIS medians 57,982 -> 44,606 km2; seafloor table in research.md). Title chosen with
  yt-package: "The Caspian Sea Just Broke Its 1977 Record Low" (94/100). Next: storyboard run (step 7).
- 2026-11-03: storyboard 1 (run 41707278080, about 32 min, 105 frames on 7 sheets): 14:57, 61 units from 76 shots.
  New features work: MODIS wipe with month labels, seafloor highlights (-5 m 66,900 km2, -10 m 88,700, -14 m
  105,500 with smoothing), Volga line, chart time axis, all Commons files PD / CC BY 4.0. Fixed: bar labels ran off
  the left edge (ChartScene sizes the label column from the longest label), whole-sea views cut off Iran (focus on the
  sea's corners), basin labels zoomed into open water (frame the sea first), 2020 / 2025 labels collided on the level
  chart (2020 dropped; the next shot gives 2020-2025), question card over a locator inset, an off-topic dam clip
  (camera move down the Volga), dated MODIS backdrop patchwork when the camera went wider than its image (future-shore
  map in its own block, framed on the whole sea; no zoom-out in the last shot), length under 15 min (about 150 words of
  sourced material added: est. 15:55). Next: storyboard 2.
- 2026-11-03: storyboard 2 (run 41713319434): 15:51, 63 units from 79 shots. Earlier fixes confirmed (Iran in frame,
  bar labels, level chart, question card, Volga camera move, Ural map, Kulaly 2026 after-image clean). Last fix: the
  MODIS day 2025-08-24 is clear over the sea but cloudy over the Caucasus with a swath edge in the east, so the
  whole-sea future-shore map and the closing shot use Blue Marble (no date). Step 7 done; next: full render (step 8).
- 2026-11-04: final render 41715843282 (release ep-caspian-sea-41715843282): 15:51, 354 MB, -14.0 LUFS; downloaded to
  Videos\yt-pipeline\caspian-sea (video, youtube.txt, credits.txt, thumbnails A/B/C "GONE BY 2100?"). Key frames
  checked: Durneva Aug 2026 and Gorgan Aug 2025 after-images clean, -5/-10/-14 m rings on Blue Marble, closing card.
  Known: the Leeds ten-metre paragraph shows the -10 m ring with the -14 m ring still on (keep + clear only clears
  its own shot); fix with keep off on that shot in the next render. Waiting for the user's review (gate 2).
