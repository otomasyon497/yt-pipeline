# caspian-sea: production plan

Resume from the first unchecked box. Every step ends with a commit and a log line.

Working question (to be tested by the research, not assumed): the Caspian, the world's largest lake, fell to its
lowest level in decades in 2026 and is still falling. Is this one more swing of a sea that has always risen and
fallen, or the start of a decline it will not recover from, and who pays first?

## Steps
- [x] 1. Research dossier (`research.md`): every number with a source (two where possible); 2-3 own calculations, maths shown
- [x] 2. Visual inventory (in `research.md`): Sentinel-2 before/after sites and dates, GIBS MODIS years, Commons PD/CC0/CC BY files, data series, stock queries (S2 dates are picked in step 4)
- [x] 3. Outline (`outline.md`), Turkish summary to the user (gate 1: waiting)
- [ ] 4. Features the outline needs (decided after step 3)
- [ ] 5. Script (`script.json`): about 2,300-2,500 words, 16-18 min, each paragraph written to a visual we can show; humanizer pass on the narration
- [ ] 6. Fact-check pass: every claim against `research.md`
- [ ] 7. Storyboard run, self-review of every frame, fixes
- [ ] 8. Full render, download to `Videos\yt-pipeline\caspian-sea`, user review (gate 2)

## Log
- 2026-11-03: topic chosen by the user (over Antelope Reef and the Qosh Tepa canal). Research started.
- 2026-11-03: research.md and outline.md done. Fresh hooks: new islands off Kulaly (Euronews, 7 Oct 2026) and the
  first Caspian Environmental Summit (Avaza, 9 Oct 2026). Own checks: MODIS 2000 vs 2025 water count (about 15,700 km2
  lost in the NE box), ETOPO 2022 future shorelines (northern basin about 96 % gone at -10 m), about 913 km3 lost
  since 1996 (12 GERD reservoirs). Scratch scripts (session scratchpad: gibs_screen.py, water_area.py, ETOPO probe) move into tools/ in step 4. Waiting for gate 1.
