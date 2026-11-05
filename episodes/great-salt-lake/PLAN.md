# great-salt-lake: production plan

Resume from the first unchecked box. Every step ends with a commit and a log line.

Working question (to be tested by the research, not assumed): the Great Salt Lake sat inches above its 2021 low in
August 2026 after the record-low snowpack winter, and Utah's own officials call a 2027 record "unavoidable" after one
more dry winter. Forty years ago the lake was flooding and Utah pumped it into the desert. What changed, what does an
exposed lakebed mean for the 2.5 million people downwind, and what would refill it?

Audience: American viewers first. First episode written to docs/script-rules.md (hook by 0:30, re-hooks at chapter
turns, a new picture every 8 s, stat / document / film shots and map icons, title 35-50 characters, thumbnail D),
narration at 1.08 with the shorter pauses (config, 2026-11-04).

## Steps
- [x] 1. Research dossier (`research.md`): every number with a source (two where possible); current level (fall 2026)
      from USGS gauges (public domain); 2-3 own calculations, maths shown
- [ ] 2. Visual inventory (in `research.md`): Sentinel-2 / MODIS before-after dates (high 2017?, low Nov 2022, 2026),
      the railroad causeway's two colours, public-domain US documents (USGS, federal) for document shots, archival
      film or photos on Commons (1980s flood, West Desert Pumping Project), data series, stock queries
- [x] 3. Outline (`outline.md`), Turkish summary to the user (gate 1: approved 2026-11-05)
- [ ] 4. Features the outline needs
- [ ] 5. Script (`script.json`), humanizer pass on the narration
- [ ] 6. Fact-check pass: every claim against `research.md`
- [ ] 7. Storyboard run, self-review of every frame, fixes; then the final-render checklist (PROGRESS.md)
- [ ] 8. Full render, download to `Videos\yt-pipeline\great-salt-lake`, user review (gate 2)

## Log
- 2026-11-05: topic chosen by the user over Central Valley subsidence, the Outer Banks houses and Greenland
  (my recommendation). Leads from the topic search: level 4,190.40 ft in mid-August 2026 against the 2021 low of
  4,190.20 and the all-time low of 4,188.5 ft (November 2022, Salt Lake Tribune); state officials: no new record
  expected in 2026, but a 2027 record "unavoidable" after another dry winter; arsenic in the exposed lakebed's dust.
- 2026-11-05: research started. USGS gauge (south arm, provisional): 2026 low 4,189.4 ft on 10 Oct, below the 2021
  low and 0.9 ft above the all-time 4,188.5 (Nov 2022); 22.2 ft below the 1986 peak (4,211.6). research.md lists the
  open research items.
- 2026-11-05: research R5-R9 written (Wurtsbaugh 2017: ~11 ft from water development; 1987-1989 pumps $60 million;
  800 sq mi of exposed bed, arsenic, and the state's PM10 view; economy $1.3-1.9 billion a year; 2024 strategic plan
  4,198-4,205 ft). Visual inventory started (MODIS Sep 2000 vs Oct 2026; S2 Jun 2017 vs Oct 2026; causeway). Next:
  the causeway and its colours, birds, the 2025-26 snowpack link, 2026 policy, Commons archival search, GIBS days,
  then outline.md and the gate-1 summary to the user.
- 2026-11-05: research R10-R12 (causeway, birds, 2026 snowpack and session) and outline.md (8 chapters, new rules).
  Waiting for gate 1. Still open in step 2: Commons archival search, GIBS days, the area at today's level (verify).
- 2026-11-05: gate 1 approved ("Onaylıyorum, devam et"). Next: finish step 2 (Commons archival search for the
  1983-1987 flood and the pumps, GIBS MODIS days around Sep 2000 and Oct 2026, S2 one-day windows for Jun 2017 and
  Oct 2026 on Farmington Bay / Antelope Island / the causeway, the area at today's level), then the script (step 5).
- 2026-11-05: script skeleton (8 chapters, 843 words, valid). Step 5 continues:
  1. expand to ~2,200 words with sourced detail (1983-87 flood damage, the water balance, Grineski / Putman dust
     studies, brine shrimp 35-40 % of the world's eggs and $57 million, magnesium, birds, lake-effect snow, strike team
     2055 / 800,000 AF, the November reading), a re-hook at every chapter turn, a new picture every 8 s;
  2. verify before the storyboard: the exact NARA causeway file name (search titles were cut), what NASA EO's "A New
     Delta in the Desert" shows (assumed: the pumped water's trace), the pumping station's location (-113.03, 41.43
     assumed), "water reached roads and rail lines" (no source yet), the USACE PDF's text layer for the highlight, and
     the level chart (mixes peaks and lows: label or restrict to yearly lows/highs);
  3. humanizer pass, fact-check (step 6), yt-package pairing (title draft "The Great Salt Lake Is a Foot From Its
     Record Low", 49 chars; thumbnail D from the opening compare), storyboard (step 7).
- 2026-11-05: verified: NASA EO "A New Delta in the Desert" is Egypt's New Delta farm project, not the pumps: removed
  (placeholder stock until a public-domain photo of the pumps turns up); NARA causeway photo = "... BALANCE OF THE LAKE
  - NARA - 544761.jpg" (fixed). Still open: pump location, "roads and rail lines" source, USACE text layer, chart.
- 2026-11-05: pump location: CLUI ("the south end of Hogup Ridge, a few miles further down the causeway northwest of
  Lakeside"; 6.5 miles of canals) and a University of Utah record (about 41 deg 15' N, 113 deg 4' W) agree, so the
  script uses (-113.07, 41.25) instead of the guess (-113.03, 41.43); confirm the station and canals on the
  Sentinel-2 close-up at the storyboard. Still open: "roads and rail lines" source, USACE text layer, level chart.
- 2026-11-05: the BLM West Desert Pumping Project FEIS on Commons (92 pages) has an OCR text layer and page 1 holds
  "WEST DESERT PUMPING PROJECT" exactly: the document shot works as written. Roads and rail lines: UGS (R14) has
  I-80 raised up to 8 ft, the railroad causeway raised in 1983-87 and lined with 1,430 boxcars. Level chart: yearly
  highs 1963-1986 for the flood (research.md table). Open: $60 vs $65 million (R6 vs R14) in the fact-check.
- 2026-11-05: step 5 (script) written to the new rules: 1,431 words in 8 chapters, 106 shots with beats from the
  start (chart reveals, stat and quote cards, map steps on their words), estimated longest stretch 7.7 s. New sources:
  USGS WRI 99-4189 (Lake Bonneville, 1963 vs 1986-87 size, 2.9 MAF inflow, killifish 1986, phalaropes 1991; R15) and
  Owens Lake (R16). GIBS: 2026-10-10 is under cloud, the script uses 2026-10-15. Fact-check fixes: the causeway was
  built by the Southern Pacific (R10 corrected), "diluted enough" for the 1986 killifish, "estimated" 600,000
  phalaropes, Lake Bonneville "poured out" (not drained), the 1984 breach "during the flood". Shorter than the outline
  (about 12 min instead of 15-16): no unsourced padding. Packaging draft (yt-package): "How the Great Salt Lake Lost
  22 Feet" (36 chars, 100/100) + thumbnail "WHO DRAINED IT?" (98/100); the user decides at gate 2. Next: storyboard.
- 2026-11-05: storyboard 41939995135: 10:15, 113 shots, 4 holds (8.1-9.5 s). Found: no usable Sentinel-2 day in June
  2017, so the cold-open wipe was dropped (window now 15 May-31 Jul 2017, narration "the summer of 2017"); arrows and
  a label in the caption band pulled two cameras out of their views (onto a 2023 Sentinel-2 mosaic and Blue Marble):
  views widened, label moved, the canal step has its own dated view; chart values over 1,000 lost their decimals
  (4,212 for 4,211.6: Remotion fix) and the 2025 / 2026 labels collided (the goal chart now ends on 2025); stock that
  showed deep snow for a record-low winter, a garden hose for the pumps, a red-rock river for the lake's inflow, other
  countries' streets, a great crested grebe for eared grebes: replaced, some by maps (the Bonneville flood, the pumps,
  the inflow arrows). Holds fixed with a stock cut, a $240 million stat and an on-screen line. Storyboard 2 next.
