# gerd-nile: production plan

Resume from the first unchecked box. Every step ends with a commit and a log line.

Working question (to be tested by the research, not assumed): Ethiopia finished Africa's biggest dam on the
river Egypt cannot live without. Did the feared catastrophe happen, and what will the next long drought decide?

## Steps
- [x] 1. Research dossier (`research.md`): every number with a source; 2-3 own calculations, maths shown
- [x] 2. Visual inventory (in `research.md`): Sentinel-2 before/after dates, Commons PD/CC0/CC BY files, data series, stock queries
- [x] 3. Outline (`outline.md`), Turkish summary to the user (gate 1, non-blocking unless they object)
- [x] 4. Feature: Sentinel-2 before/after wipe on a map step
- [x] 5. Feature: animated chart scene (bar / line)
- [x] 6. Feature: "where are we" locator inset on stock and photo shots
- [x] 7. Feature: one episode look (same grade on stock and archive; chapter cards over blurred satellite)
- [x] 8. Script (`script.json`): about 2,500 words, 16-18 min, each paragraph written to a visual we can show
- [x] 9. Fact-check pass: every claim against `research.md`
- [x] 10. Storyboard run, self-review of every frame, fixes
- [x] 11. Full render, download to `Videos\yt-pipeline\gerd-nile`, user review (gate 2)

## Log
- 2026-11-02: started. Claude Code auto-continue is on (`autoContinue: true`); a keep-awake process runs for this session.
- 2026-11-02: research.md (sources, own calculations, visual inventory) and outline.md done; S2 before 2020-03-05, after 2026-03-09.
- 2026-11-02: step 4 done (map step `compare`, commit af20fbd) and Nile / Blue Nile / White Nile lines in lines.json; step 5 done (chart: source line, `ref` threshold line, `highlight`, thousands separators, kept above the captions). Both type-check; not rendered yet (check them in the step 10 storyboard).
- Next (step 6): new `pipeline/locator.py` drawing a small PIL mini map (ne_50m land, the country containing the point in accent, a dot) into PUBLIC_MEDIA; `Shot.where: PlaceRef` resolved with maps.resolve_point; timeline passes {src, label}; an Episode overlay at top right on stock / photo / ai_image shots.
- 2026-11-02: steps 6-7 done: `Shot.where` locator inset (pipeline/locator.py, PIL mini map with the Nile lines), `Script.look` warm|cool grade + vignette on footage, chapter cards over a blurred image of what comes next (`cardBg`). Type-check and py_compile pass; first real test in the storyboard.
- 2026-11-02: steps 8-9 done: script.json (2,198 words, 52 paragraphs, about 16 min, 4 asks, 1 subscribe line), every claim checked against research.md; 3 wordings tightened. Next: storyboard run (step 10).
- 2026-11-02: pacing pass: longest hold without a cut 28 s -> 14 s (91 shots, 75 units).
- 2026-11-02: storyboard 1 (run 41366768916, 954 s, 9 sheets) reviewed. Fixed: lake visible before the wipe, date tags under the lower-thirds, S2 patchwork (S2 only up to 2 deg, fades out when zooming out), 2011 view showed the later lake, chart labels (150.6, clipping, threshold label), Blue Nile photo instead of European stock, ISS Aswan photo instead of a random turbine hall, description over 5,000 chars (compact credits).
- 2026-11-02: render 41370991970 (38.8 min): 15:54, 424 MB, release ep-gerd-nile-41370991970, downloaded to Videos\yt-pipeline\gerd-nile. Key frames checked (wipe from frame 0, labels, charts, no pale patches). Open: S2 tile blocks on two 1.4-1.5 deg lake views; waiting for the user's review (gate 2).
- 2026-11-02 (user review 1): arrows / routes / areas were cut at the frame edges (screenshot görsel1: the Upstream arrow). Fixed in the engine: content always fits (explicit views zoom out), auto-framing keeps earlier overlays, more margin; quiet context labels (neighbouring countries with ISO codes, big cities by scale rank); date windows on the GERD lake views. Next: storyboard 2, then final render.
- 2026-11-02: storyboard 2 (run 41382000745) checked: arrows/routes/areas fully in frame, context labels read well, lake views clean. Last fix: reframing keeps only overlays that are on screen (10:35 had zoomed out to the whole world). Final render next.
- 2026-11-02: final render 41383490424 (release ep-gerd-nile-41383490424) downloaded; key frames checked (06:36 arrow, 00:38, 01:55, 03:09, 10:35, 12:30, 13:30, 15:24). Waiting for the user's OK.
- 2026-11-02 (gate 2): the user approved v2 ("izledim güzel olmuş"). First release deleted. The duplicate Sentinel-2 credit line was removed from youtube.txt / credits.txt (on the PC and in the release); code fixed in run.py / maps.py. Next: manual upload by the user.
