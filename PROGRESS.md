# PROGRESS

## Status (2026-11-08, late session)
- Render review of ep 8 found map flaws, all fixed in the engine (MapBlock.tsx, so every later episode gets them):
  a close view's Sentinel-2 image sat as a rectangle on wider views and during flights (now each image fades by its
  width against the camera's, and the layer by how much of the frame it fills), and Blue Marble's 500 m pixels showed
  as blocks under dives (now blurred by the data's pixels on screen; judging by file pixels left close tiles sharp).
  Stat cards no longer count dates, year ranges or whole numbers under 10 ("May 0, 2026", "1 wars").
- Shorts re-rendered and checked by frames at a923430: releases ep-indus-waters-short-tunnel-42519635849 and
  ep-indus-waters-short-dam-42519639578, in Videos\yt-pipeline. Older Shorts releases of these slugs are superseded.
- Tunnel Short cover: new `thumbnail.focus` [lon, lat, span] shows one spot in both panels (a plain split missed the
  reservoir); text "RIVER TAKEN?" (the video's own question) replaced the overstated "RIVER GONE?".
- Long episode re-rendered at a923430 (the first render had the patch at 465.5 s, Ratle dive): release
  ep-indus-waters-42520507017, 16:10, 469 MB, in Videos\yt-pipeline\indus-waters; frames checked. Audio not checked.
- Uploaded 2026-11-09, private: long nbB4DKNWp7Y; Shorts PqqVvJZd_18 (tunnel), 9P8EDcca-bY (dam), which carry a
  all three scheduled by the user for 15:00 UTC 9 Nov (18:00 TR). Descriptions cleaned in Studio. Still to do once the
  long video is public or unlisted: Related video on both Shorts (Studio only, no documented API) and pinned comments.
  Blocker: Related video opens "one-time verification required" (advanced features); only the user can complete it.
- Topic radar: tools/topic_radar.py (34 search calls a run; first output docs/topic-radar-2026-11-08.md). Leads offered to
  the user with a first source check: Ogallala aquifer (recommended, Landsat pivots), Kansai airport, Medog / Siang
  dams. Word estimates are from one search each, not a research dossier; do that after the user picks.
- Episode 9 ogallala-aquifer made overnight at the user's request (2026-11-09) and uploaded PRIVATE, not scheduled: long 903F5prq9EM (15:40, run 42543077201), Shorts CLGm0e1-SFY (orbit), LBTVfQGwVYA (farmers). The user reviews them; publishing, pinned comments and Related video are still to do. Sound not checked.
  Package: "Kansas Rejected Farmers' Plan to Save Their Water" + UNUSABLE?. Own measurement (tools/ogallala_green.py) overturned the first hook: green land grew near Dalhart (17 to 58 %), it did not shrink; all seven boxes were down in 2026, unexplained, said so in the video. Scripts come from build_script.py and build_shorts.py.
  Engine: `map.cut` (a straight cut, no flight through coarse imagery between close views), a compare that cannot be built now stops the render, ranges like 500-1,300 do not count up. Lessons: check real pictures and measure before writing a hook; automatic filler must follow the sentence and never interrupt a document, wipe or chart.
- Advanced features verified by the user 2026-11-09: docs/youtube-feature-access.md.
- Descriptions now hold intro + chapters + tags only (the user's decision; credits.txt keeps the sources).
- API upload built at the user's request (2026-11-09): tools/yt_upload.py, private only (fixed in the code), reads the
  privacy back after the upload; the user reviews and publishes in Studio. Own write token token_upload.json; the
  analytics token stays read-only. YouTube's revision history, 2 Nov 2026: uploads from unverified API projects are no
  longer locked private; videos.insert has its own bucket (1 unit, 100 calls a day).
- Watermark: tools/watermark.py -> Videos\yt-pipeline\channel\watermark.png (600 x 600, transparent, flat shapes; the
  profile picture turns to mud at watermark size). The user adds it in Studio > Customization > Branding.
- Analytics API set up 2026-11-08 (API instead of Chrome as videos grow): Google Cloud project ink-orbit-analytics,
  OAuth app in production (privacy policy: a secret gist on otomasyon497; unverified-app warning is expected), read-only
  token in %USERPROFILE%\.yt-pipeline, tested on the real channel. `auth` now refuses any channel but Ink & Orbit.
  The account holds several channels: the chooser lists Ink & Orbit as "Echoes of Revenge" (its older name, it seems).
- CTR: the Analytics API answers 400 to videoThumbnail* metrics, so tools/yt_analytics.py shows none. It is in the
  Reporting API; jobs channel_reach_basic_a1 and channel_reach_combined_a1 were created 2026-11-08 21:02 UTC (backfill
  30 days, within about 2 days; reports kept 60 days, 30 for backfill, so store the downloads).
- Next for analytics: from ~10 Nov read the reach reports, compare CTR with Studio, then add the download and the
  one-page weekly report (48 h / 7 d / 28 d checks, outliers only) to tools/yt_analytics.py.

## Status (2026-11-08, earlier)
- Episode 8 indus-waters (Indus Waters Treaty, India's "abeyance", Hague award 31 Aug 2026) produced without gates at
  the user's request. Script 2,114 words, 16.2 min real (storyboard log); factcheck.md complete (no FIX); research
  R1-R20; package "India Froze a 65-Year-Old Water Treaty With Pakistan" + "ACT OF WAR?"; log in
  episodes/indus-waters/PLAN.md. Shorts rendered: releases ep-indus-waters-short-dam-42514172243 and
  ep-indus-waters-short-tunnel-42514175494 (each with cover_short.jpg). Long render run 42514168881 was still running.
- Half done / next step: when run 42514168881 succeeds, `tools/fetch_episode.ps1` the three slugs to
  Videos\yt-pipeline, open thumbnail_D.jpg and both cover_short.jpg, pull frames around transitions, then tell the
  user (they asked for everything downloaded; they upload by hand). If it fails: `gh run view 42514168881 --log-failed`.
- New this session: vertical Shorts covers (thumbnails.make_short_cover, Remotion ThumbnailVertical 1080x1920);
  render.yml `thumbs_only`; Indus river lines in pipeline/lines.json; legacy episodes' photo check is a note only;
  Studio analytics -> docs/analytics-2026-11-08.md (conflict titles win; search viewers leave at 0:25); caspian,
  great-salt-lake and colorado repackaged (old titles in youtube.title_v1), the user updated Studio 2026-11-08.
- Lessons ep 8: undated views under ~2 degrees use multi-day "recent" Sentinel mosaics with seams, so give them a date
  or keep them over 2 degrees; a close dated raster shows as a patch on wider views in the same map block; country
  labels duplicate the basemap's own; check Commons photos for promo text. The scratchpad venv was eaten by Temp
  cleanup: heavy local tools now use %USERPROFILE%\.yt-pipeline\venv (run with -I).
- Waiting: aral-sea uploaded (check CTR at 48 h ~10 Nov; Test & Compare titles in its PLAN.md); recheck repackaged
  videos' CTR ~15 Nov. Great-salt-lake old gate-2 item is moot (uploaded).

## Stock-free phase (approved 2026-11-05: "kesin %0 olsun, araçları kurmaya başla")
- Decision: no stock video or images (and no AI images) in episodes from now on; every shot shows the real place,
  thing or data. Also: 15-20 min per episode, so gate 1 shows the research's word budget (2,300-3,000 words).
- Measured before: stock was 28 % of colorado-river v2's shots, 44 % of great-salt-lake's.
- Steps (each committed and logged here):
  1. Ban `stock` and `ai_image` shots in new scripts (legacy flag for old episodes); script rules updated.
  2. tools/find_media.py: public-domain / CC0 / CC BY candidates for a query from Wikimedia Commons, the NASA Image and
     Video Library, the Internet Archive and the Library of Congress, with a thumbnail contact sheet; the pipeline
     takes NASA images and videos as `photo` / `film` sources with credits.
  3. Landsat before/after (Collection 2 Level-2 via Microsoft Planetary Computer's free STAC; 1982 on): compare
     source "landsat", so wipes can go back to the 1980s.
  4. `profile` shot: an elevation cross-section (Copernicus DEM GLO-30, AWS open data) with level lines and water
     filling to them (lake levels, dead pool lines).
  5. 3D terrain flyover (DEM + satellite texture, three.js in Remotion).
  6. Demo episode exercising all of them, then the user's review (gate).
- Log: step 1 done (commit 50750be): schema rejects stock / ai_image unless `legacy_stock` (set on the 8 older
  episodes that used them); docs/script-rules.md "Real pictures only".
- Log: step 2 done: tools/find_media.py (Commons, NASA, Internet Archive; the Library of Congress API answers 403
  from the PC) and `nasa:<id>` photo / film sources (pipeline/nasa_media.py).
- Log: step 3 done: compare source "landsat" (pipeline/landsat.py); test: Great Salt Lake on 2 Aug 1986 (Landsat 5,
  the flood: Antelope Island ringed by water, Farmington Bay full) against 27 Oct 2026 (Landsat 9, the bay a salt
  flat). Next: step 4 (profile shot).

## Colorado River v2 (2026-11-05)
- Why: the user found v1's transitions heavy and preferred the feature-demo's pace.
- Done: narration 1.08 with shorter pauses, flights 0.7-1.9 s, 1.8-s chapter cards; every stretch over 8 s got a beat
  on the word it shows (places and icons on their names, chart bars on their numbers, stat cards, quote cards started
  just before the quote, quick cuts under the viewer questions). 45 long holds -> 0; 89 -> 162 shots; 17:04 -> 16:08.
- New engine features: `chart.reveal` (bars / points appear with the narration, counted as beats, own storyboard
  stills) and `compare.until` (the before image holds through label steps). Fixed: line charts drew their last point
  at half opacity (every episode so far).
- Lessons: spoken numbers run longer than 0.4 s a word (estimate them generously); stock queries naming a place
  still return other countries (prefer Commons photos, maps or our own cards where a viewer could misread the place).

## Channel research (2026-11-04; the user approved R1 and R2 together, and thumbnail D for colorado-river)
- The user asked for an analysis of similar channels (videos, transitions, materials, methods, thumbnails), skills to
  install, and production changes that keep viewers watching. Evidence and plan: docs/channel-analysis-2026-11.md.
- Measured: our pictures change in 71-83 % of 10-s steps against 89-98 % in the sample, narration about 136 words/min
  against 165-185; their thumbnails are template maps with 1-3 words, ours AI images; their materials add archival
  film, highlighted documents, diagrams, map icons and tilted 3D maps.
- Thumbnail D for colorado-river: our own 2019 | 2026 split from the cold-open wipe (in the episode folder).
- Skills: youtube-scriptwriting and thumbnail-design chosen after reading them; the install was blocked by the
  session's permission check, so the user runs the two `npx skills add` commands in the analysis file.
- Next: phases R1 (packaging, hook and pace rules, 8-s picture-change warning), R2 (document cards, public-domain
  archival film, stat cards, glowing lines, map icons), R3 (tilted maps, profile diagrams, "ink" style, terrain test).
- R1 + R2 built 2026-11-04 (commits 15d8715..f38a9bb): 8-s hold warning, title length warning, `voice_speed` + pace
  samples (render.yml `pace_samples`), shot types `stat`, `document` (pypdfium2 page + marked lines, or a clipping
  card in EB Garamond) and `film` (Commons archival video), map place `icon` (22 Lucide icons, ISC), glowing routes,
  thumbnail D (before | after split from the episode's first compare), docs/script-rules.md. Review episode
  episodes/feature-demo: storyboard + pace samples run 41818951663, full render 41818957292. GitHub had a Git/Actions
  incident that day (pushes failed for a while).
- Demo review: thumbnail D came out automatically like the hand-made one; stat, document (both lines of Reclamation's
  memo found), clipping, icons and glowing routes work. Fixed after the first render: the film started on a government
  building (now 615 s, dam construction), the zoomed page hid the source panel (bottom gradient, less zoom), the
  clipping card touched the question card (lower), film shots lacked their label. Final demo render 41820302063 in
  Videos\yt-pipeline\feature-demo (with pace_samples\: 1.00 / 1.08 / 1.15 = 122 / 128 / 133 words/min incl. pauses).
  Wikimedia rate-limits ffmpeg's default user agent (429): sample remote films with -user_agent.
- 2026-11-04/05: the user chose narration 1.08 (config: TTS_SPEED 1.08, paragraph pause 0.38 s, chapter pause 0.6 s)
  and episode 4 with the new rules; topic: the Great Salt Lake (over Central Valley subsidence, the Outer Banks
  houses and Greenland). Plan: episodes/great-salt-lake/PLAN.md. Colorado-river release waits for the user's upload.

## Episode 3: colorado-river (started 2026-11-04)
- The user asked for a topic that grabs American viewers and picked the Colorado River (my recommendation) over the
  Outer Banks house collapses, sinking US cities and Greenland, with "start now".
- Hook: Interior's Record of Decision (21 Aug 2026) cuts the Lower Basin 1.25 million acre-feet a year in 2027-2028
  and leaves the Upper Basin uncut; Nevada sued, Arizona and CAP joined; both reservoirs hit record lows.
- Data: Reclamation daily CSVs (usbr.gov/uc/water/hydrodata, public domain) and the October 2026 24-Month Study
  (PDF text via pypdf installed in the session scratchpad, not in the repo).
- New: `.github/workflows/tools.yml` ("Data tools", workflow_dispatch with an allowlisted tool) runs one-off data
  preparation on Actions and uploads out/ as an artifact; first tool tools/powell_shoreline.py (USGS 2017 Lake Powell
  bathymetry -> lake extent and dry bed at given elevations). ScienceBase blocks curl from the PC (Cloudflare) but
  works from Actions.
- New engine bits: a "credit" property in an episode's geo/*.geojson and lines.json "_credits" go into the video
  credits; lines.json gained Colorado River, Green River (Natural Earth) and CAP, Colorado River Aqueduct,
  All-American Canal (USGS NHD, chained with a pure-Python script). tools/colorado_numbers.py reproduces the own numbers.
- Gate 1 approved 2026-11-04 ("Onaylıyorum, devam et"); script 2,310 words, title "Lake Mead and Lake Powell Both Hit
  Record Lows in 2026" (yt-package 98/100). Voice profile for yt-package written to ~/.claude/youtube/voice.md.
- Final-render review (2026-11-04), frames pulled from the MP4 on the PC: five flaws, two of them visible on the
  storyboard too and missed there. Engine fixes for all episodes:
  - MapBlock: where a dated MODIS image covers the frame, Sentinel-2 fades out at 2.0-2.6 degrees (it sat on the
    3.1-degree Lake Powell view as a sharp rectangle); blended by MODIS's share of the frame.
  - sentinel.py: window mosaics start from the clearest day whose passes cover the whole box (then the highest sun;
    two satellites minutes apart count as one day), so tiles of two dates no longer meet in a seam (the delta, March
    vs May); one scene per tile and acquisition; pixels the cloud mask removed that nothing else filled keep their
    first observation (Sen2Cor flags bright ground as cloud; a safeguard, not the cause of anything seen here).
  - maps.py: S2 views wider than 1.5 degrees keep lakes (land_mask(lakes=False)). Natural Earth draws reservoirs at
    full pool, so the "land minus lakes" cut showed Blue Marble's 2004 Lake Powell inside the full-pool outline.
  - maps.py: "map warning: ... Sentinel-2 scenes of N days" for every S2 image stitched from several days.
  - Script rules learned: date a compare step with its "after" window (the backdrop shows when the compare fades);
    give a wipe time to finish before the next cut; a one-day window "D/D" picks one clear day with the normal tone.
- Actions: storyboards about 17 min, full render about 56 min, stills runs about 12 min.

## Episode 2: caspian-sea (started 2026-11-03)
- The user picked "the shrinking Caspian" from three proposals: Antelope Reef (China's new island in the Paracels, my
  recommendation), Afghanistan's Qosh Tepa canal on the Amu Darya, and the Caspian (record low in 2026, the lowest
  political risk of the three). Same process as gerd-nile: research -> outline (gate 1) -> script -> storyboard -> render.
- New engine features: Compare.source "modis" (NASA MODIS Terra, day vs day, wide views, since 2000); a MODIS backdrop
  for a single-day date on views wider than 2 degrees (avoid it on whole-sea views: clouds and swath edges); highlight
  "seafloor:<basin>:<m>" (pipeline/bathy.py, NOAA ETOPO 2022); Volga line; line charts on a true time axis; bar charts
  size the label column from the longest label. tools/caspian_numbers.py reproduces the episode's own calculations.
- Actions: storyboards about 30 min each (2 rounds), final render about 50 min.
- 2026-11-04: approved ("güzel olmuş") and uploaded by the user; release ep-caspian-sea-41715843282 and its tag deleted.

## Shorts (2026-11-03, phase S1; dropped by the user the same day)
- Outcome: the user did not like the first Short much and dropped Shorts altogether. Its release is deleted (the local
  copy stays in Videos\yt-pipeline\gerd-nile-short-lake\); the vertical mode stays in the code, unused.
- The user chose native vertical Shorts (maps redrawn for a phone screen) over YouTube's clip tool or a letterboxed crop
  of the long video. First Short: "Göl beliriyor" (episodes/gerd-nile-short-lake), facts from the fact-checked gerd-nile.
- Format switch: script.json `"format": "short"`. run.py reads it before the modules import config, so YTP_FORMAT=short
  gives 1080x1920, UI scale 1.4 (map labels, markers, lines), lead-in 0.15 s, paragraph pause 0.25 s, end pad 1.6 s
  (closing loop wipe), TTS speed 1.06, Shorts safe areas (hook line on top; YouTube's title and buttons at the bottom
  and right). Shorts get no custom thumbnail; prepare() refuses Shorts over 180 s.
- Remotion: geometry.setFrame(width, height, uiScale) from the timeline; vertical layouts for the on-screen text
  (Bebas headline near the top; the first one is the hook, on screen from frame 0), captions (4 words, 64 px, above
  YouTube's UI) and the question card; map labels stay inside a per-block labelBox.
- Limits: a Short takes map shots only for now (charts, photos, stock and cards have no vertical layout yet).
- Render 1 review (frames pulled from the MP4 on the PC) found: frame 0 showed the 2026 lake under the hook "no lake
  here" (overlays faded in from frame 0), the last frames faded back to the lake (loop broken), a map label behind the
  captions, and captions that stranded words. Fixed: overlays present at a block's first frame / lasting to its end no
  longer fade (MapBlock life()), the Short label box ends above the captions (y 1250), and Short captions split each
  clause into even pieces of up to 4 words. Also a shorter opening line and a 2.0 s wipe (lake complete at about 4.6 s).
- Render 2: 41.1 s, -14.5 LUFS, clean first and last frame (2020 valley, so the loop is seamless). Known: while the
  camera dives back to the lake (about 34.6 s) the Sentinel-2 mosaic shows as a soft-edged rectangle for about 0.25 s
  (same as in the long video). A fix (fade S2 in only once a mosaic covers the frame) needs testing on long-form pans.
- Actions: about 6 min per Short render (both runs; the second one reused the cached Sentinel-2 mosaics).
- Dropped plan: 2-3 Shorts per episode (a satellite surprise, an own calculation, a two-sided debate), one every 2-3
  days, each pointing to the long video.

## Channel brand (2026-11-02, adopted by the user 2026-11-03)
- Brief from the user: an original, memorable, evergreen name (not tied to today's format) whose profile picture and banner
  evoke it. Proposed **Ink & Orbit**, tagline "Drawn in ink. Checked from orbit.": the map drawn in ink plus the view from
  orbit, which is the method of every video. Rejected: Map Verdict (tied to the format), The Why of Where (too close to
  Geography by Geoff's tagline), Watershed (name taken by others).
- Correction (2026-11-03): web searches had missed @InkOrbit ("Ink Orbit", empty) and @InkandOrbit (a small art Shorts
  channel); both are unrelated to our topics. The user's channel: id UC1h2p6x09doXZRvG4d4M0Sg, handle typed as
  `@ınkorbııt` (Turkish dotless ı; `/@inkorbiit` redirects to it). Suggested a Latin handle, e.g. @InkOrbitMaps (free).
- tools/channel_art.py renders three files:
  - profile_800.png: an orthographic globe, one half drawn in ink on paper with waterlining, the other half NASA Blue
    Marble, with the amber wipe line, an amber orbit ring and a satellite.
  - banner_2560x1440.jpg: a Mediterranean band. One side is an engraved ink map with a compass rose and hand-lettered sea
    names, the other is Blue Marble. INK sits on the paper, ORBIT on the satellite image, and the amber "&" on the wipe
    line. Text stays inside the 1546 x 423 safe area.
  - preview.png: desktop, phone and TV views, and the avatar at 240/98/48/32 px on dark and light backgrounds.
- Palette and fonts follow remotion/src/theme.ts (navy, cream and amber; Bebas Neue and Inter). EB Garamond Italic is used
  for the map lettering. Data: Natural Earth and NASA GIBS. Fonts are under the OFL. The script runs locally in seconds.
- Files are in C:\Users\MONSTER\Videos\yt-pipeline\channel\, including channel.txt (name, handles, an 887-character
  description and 341 characters of keywords).

## Pilot episode: gerd-nile (2026-11-02, user: "make it original and watchable; you decide the process")
- Process (decided with the user): research dossier with sources and own calculations -> visual inventory (Sentinel-2
  dates, licence-checked Commons, data) -> outline (gate 1, non-blocking) -> script written to the visuals we can show ->
  fact-check against research.md -> pacing check (layout notes: no hold over ~14 s) -> storyboard self-review -> render.
  Files: episodes/gerd-nile/{PLAN.md, research.md, outline.md, script.json}.
- New features: map step `compare` (Sentinel-2 before/after wipe, date windows, month labels from the scenes used);
  Nile / Blue Nile / White Nile lines; charts with source line, threshold line, highlight, data-driven decimals;
  `Shot.where` locator inset (pipeline/locator.py); `Script.look` grade + vignette on footage; chapter cards over a
  blurred image of what comes next; compact credits when the description passes 5,000 characters.
- Fixes found by the storyboard: S2 mosaics wider than ~2 deg mixed dates into a patchwork, and S2 patches stayed visible
  as pale rectangles when the camera pulled back (S2_MAX_SPAN 6 -> 2; S2 layer fades out between 2.6 and 4.5 deg;
  this was also the "pale patch" of suez-v3). Wipe now starts from frame 0 on the before image.
- Runs: storyboard 41366768916 (40.8 min, 9 sheets), render 41370991970 (38.8 min). Result: 15:54, 1080p24, 424 MB,
  91 shots / 75 units, 4 question cards, 1 subscribe line; release ep-gerd-nile-41370991970; downloaded to
  Videos\yt-pipeline\gerd-nile (video, youtube.txt 3.8 kB, credits.txt, 3 thumbnails).
- Known flaw: two lake views at 1.4-1.5 deg still show darker S2 tile blocks ("recent" mosaics pick the least cloudy
  scene per tile over two years). Fix ready to apply with the user's notes: allow date windows in MapStep.date and give
  those views the compare's "after" window.
- Actions minutes for the pilot: about 80 (storyboard + render); a fix re-render with warm caches is about 40.
- Review round 1 (user, screenshot görsel1): arrows, routes and highlighted areas were cut at the frame edges, and maps
  should name the surrounding countries and cities. Engine fixes (all episodes): explicit views zoom out until every
  overlay of the step fits (arrow bulge included); auto-framing keeps the overlays that are on screen; fit margin 1.16 and
  bottom safe 200 px; context labels (ISO-coded countries, the biggest on screen; cities by Natural Earth scale rank and
  zoom; lowest label priority, never next to a story marker); map steps take Sentinel-2 date windows (the 1.4-1.5 deg
  lake views now use the compare's 'after' scenes: no tile blocks). Storyboard 41382000745, render 41383490424
  (release ep-gerd-nile-41383490424, 15:54, 418 MB), downloaded over the first version. The first release
  (ep-gerd-nile-41370991970) and its tag were deleted at the user's request.
- Verdict on v2: approved by the user. Found on delivery: youtube.txt and credits.txt listed the Sentinel-2 credit twice
  ("2020, 2026" and "2020, 2023, 2024, 2026") because each map block added it while the set of years was still growing.
  run.py now adds it once after all blocks; the delivered files and the release copies were corrected.

## Phase 1 (approved)
- [x] Repo, pipeline, Remotion project, workflow; secrets set by user
- [x] End-to-end run on Actions green (run 41201330118): 1920x1080 / 24 fps H.264+AAC, ~70.6 s, artifact `nokia-intro`
      (final.mp4, credits.txt, voice_samples/ with bm_george, am_michael, am_onyx)
- [x] Measured: job 6m07s (billed ~7 min). Prepare 1m39s (tts 55s, captions 13s, media 14s warm cache, samples 14s),
      Remotion render 2m27s for 1694 frames (~11.5 fps on 2 vCPU), setup (apt+pip+npm) ~1m50s.
      First (cold-cache) run: job ~6m, render 2m52s for 2035 frames.
- Music: /music was still empty on 2026-10-31 (user said tracks were added, none found in the working tree); so the test video has narration only (ducking/mix path not yet exercised with a real track).

## Decisions
- Map style: user chose `satellite` (NASA Blue Marble) as the channel default on 2026-11-01 (config.MAP_STYLE default).
  `atlas` and `midnight` stay available per episode (`map_style` in script.json) or per run (render.yml `map_style`).
- Voice: user chose `am_michael` as default for all episodes (config.DEFAULT_VOICE, schema default). Voice samples are now opt-in (`VOICE_SAMPLES=1`).
- AI images: `CF_IMAGE_MODEL=@cf/black-forest-labs/flux-1-schnell` set in workflow (user chose licence caution over
  flux-2-klein-4b, whose hosted terms on Cloudflare are unclear). Klein code path remains (switch by changing env), unverified in practice.
  schnell: 1024x1024 centre-cropped to 16:9, upscaled to 1080p; no `seed` field accepted.
- 24 fps; render concurrency 2, jpeg frames, x264 veryfast crf 20; audio muted in Remotion, mixed + muxed by ffmpeg.
- Secrets are sanitised (pasted curly quotes broke the Pexels header once) via `config.secret()`.
- Remotion licence: free for individuals / companies up to 3 people.
- YouTube "altered content" question (YouTube Help 14328491, checked 2026-11-02): answer "No" for our usual episode. A
  synthetic narrator that imitates no real person, real (tone-mapped) satellite imagery, procedural background music and
  AI thumbnails do not need disclosure. Answer "Yes" if a video shows a realistic AI scene, alters footage of a real
  place or event, or makes AI music the main focus. Disclosure alone does not limit reach or monetisation.
  The description already says "Narration: synthetic voice".
- Cache: actions/cache `assets-<run_id>` + prefix restore; HF models separate.
- Test script facts are illustrative (see `sources`) - fact-check before real use.

## Known issues / notes for later phases
- Final-render checklist (the storyboard has one still per stop and cannot show these): what is under a compare when
  it fades; whether each wipe and route finishes before the next cut; overlay-only steps (no camera stop); the S2
  images named in the "Sentinel-2 scenes of N days" map warnings. Pull frames with Remotion's ffmpeg and check them;
  `tools/seam_scan.py VIDEO --at s1,s2,...` measures straight colour steps (real seams: 13-16 in blue; rivers, shores
  and border lines fire too, so look at every hit).
- Inside a window mosaic, pixels the mask flags as cloud on bright ground can still be filled from another day (only
  when the best day's scene reports 2 % cloud or more). If that shows up: mask only SCL 3/9/10, not 8.
- true_size: the moved country's label can land under a water or region label at the destination (caspian-sea
  1:36-1:46: CASPIAN SEA over GERMANY), and the user could not tell the move was a size comparison. Before the next
  true_size shot: hide labels under the moved shape while it is on screen and add a short "<country>, to scale" tag.
- `keep: true` carries the previous shot's overlays and `clear` only removes overlays from the shot's own steps, so a
  carried ring cannot be cleared (caspian-sea 13:44-13:56, -14 m ring next to -10 m). Turn `keep` off on that shot,
  or let `clear` also drop carried overlays.
- New channels lack YouTube "advanced features" (YouTube Help 9890437, checked 2026-11-03): pinning comments, chapters,
  a Related Video link on Shorts, A/B thumbnail tests and clickable description links all need them. Unlock with ID or
  video verification (review usually 24 h, not offered everywhere) or wait for channel history. Phone verification only
  gives intermediate features (videos over 15 min, custom thumbnails).
- Kokoro runs ~1x real time on CPU: a 15-min video needs ~15 min TTS + ~30 min render + captions ~3 min -> close to the
  workflow `timeout-minutes: 60`; raise it (job limit is 6 h) or split TTS/render jobs for long episodes.
- Narration pace is ~2.05 words/s at speed 0.95; budget ~125 words per 60 s plus ~0.9 s per scene overhead.
- spaCy model is downloaded at runtime by Kokoro/misaki (adds ~seconds each run); could be pinned in requirements.
- Remotion preview of stock `Video` from @remotion/media worked in SSR (no OffthreadVideo fallback needed so far).

## Phase 3D - delivery and review (2026-11-02, approved by the user: "3D'ye geç")
- Full renders publish a private pre-release `ep-<slug>-<run_id>` (video, youtube.txt, credits.txt, thumbnails) with the
  PowerShell download command in the notes; artifacts only for stills/storyboard runs. tools/fetch_episode.ps1 downloads
  the newest release of a slug (optionally deletes it). Tested: run 41355109348 (map-demo, 53 s, 42 MB, job ~5 min),
  downloaded with gh, test release deleted.
- Storyboard mode (render.yml input `storyboard`): one still per shot plus one per map camera stop, labelled contact
  sheets (time, shot, narration). Tested: run 41355101323 (suez-v3): 38 frames on 3 sheets.
- Minutes summary in every job summary (job time; prepare step timings).
- Not done: parallel render chunks (only wall-clock gain; same billed minutes).

## Test episode 3: suez-v3 (2026-11-02, script rewritten with the user's CTA course; Pixabay added)
- Script rules (memory: script-engagement): in-content two-sided questions with on-screen question cards (`ask`),
  retention bridges, one content-tied subscribe line, no generic end CTA, pinned comment in youtube.txt; facts unchanged.
- Pixabay = second stock source (PIXABAY_API_KEY set by the user); clips now ranked by tag/slug relevance after Pixabay
  returned a cruise ship for "container ship" and a marina buoy for "cargo ship sailing" in this render.
- Sentinel-2 views less than 90% filled are skipped (a half-filled mosaic showed as a pale patch on the 1956 map).
- Run 41351345204: 201.8 s, 22 units from 26 shots, 3 question cards, 35 SFX; prepare ~4 min, render 7m16s.
  Delivered to C:\Users\MONSTER\Videos\yt-pipeline\suez-v3\. The reference video was transcribed with
  tools/transcribe.py (transcribe.yml; audio via the private "inputs" release, asset deleted afterwards).

## Test episode 2: suez-v2 (2026-11-01, user: "more realistic, more watchable; Sentinel-2; redo everything")
- New script written for retention (cold open on the real event, open question, human story, callbacks), 326 words.
- Sentinel-2 (pipeline/sentinel.py): ESA Copernicus L2A 10 m from the AWS Open Data copy (Earth Search STAC,
  collection sentinel-2-c1-l2a, public COGs, no account). Per view: per-tile best scenes (full scenes first: orbit-edge
  slivers report ~0 % cloud), windowed + decimated COG reads, reprojected to Web Mercator, composited until the view is
  filled; Sen2Cor cloud mask only on cloudy scenes and never on event dates (it flags bright sand and dust); filmic tone
  curve; land-only on views wider than 1.5 degrees (sea from Blue Marble). Map steps take `date` for real-event imagery:
  the Ever Given is visible on 24 Mar 2021 (S2A, tile 36RVU) and 29 Mar 2021; the queue of ships in Suez Bay too.
  Credit: "Contains modified Copernicus Sentinel data <years>" (free incl. commercial use).
- Archive photos (pipeline/commons.py, shot type `photo`): exact Wikimedia Commons files, licence read from the API,
  only public domain / CC0 / CC BY accepted (BY-SA, NC, ND refused); framed over a blurred copy or full frame; credits
  listed in credits.txt. Skipped a 1956 newsreel clip: labelled public domain but it is Movietone footage (Content ID risk).
- Procedural music (pipeline/music.py, music "procedural" or "auto" with empty /music): one music_lab bed per chapter
  mood, 2 s crossfades, bed 10 dB under the measured narration + sidechain ducking; mix is stereo now.
- Map labels: place kind `label` (text-only callout, e.g. "EVER GIVEN" above the ship).
- Evidence: run 41345404099 (final; first pass 41343940945): 161.8 s video, 20 units from 23 shots, 4 chapters with
  procedural music (bed -20.6 dB applied, 10 dB under the -27.2 LUFS voice), job 10m51s (prepare 2m56s incl. 9
  Sentinel-2 views with 1-30 scenes each, render 5m45s, thumbnails 14 s). Event imagery needed a percentile stretch
  (the 24 March scene is full of dust). Delivered to C:\Users\MONSTER\Videos\yt-pipeline\suez-v2\.
- Known: wide Sentinel-2 mosaics can still show a thin seam/sliver where scenes from different days meet.

## Phase 3B - map engine v2 + "more attention, more flow" (2026-11-01)
User feedback on 3A: "izledim güzel olmuş" + make it more attention-grabbing and fluid.
- Data: Natural Earth 5.1.2 GeoJSON (public domain; pinned tag, cached in .cache/geo) for countries 10m/50m/110m, land,
  coast, borders, lakes, rivers, admin-1, populated places, marine + region names. NASA GIBS WMS (EPSG:3857) imagery:
  Blue Marble shaded relief + bathymetry (day), VIIRS Black Marble 2016 (night lights), ASTER GDEM greyscale relief
  (NASA/METI, no redistribution limits since v3). GIBS acknowledgement goes into credits.txt automatically.
- Sea routes: `searoute` (Apache-2.0 code; Eurostat MARNET network, EUPL-1.2 - commercial use allowed, only rendered lines
  leave the pipeline). Curated lines in pipeline/lines.json (Suez Canal traced from ASTER relief), curated places in
  pipeline/gazetteer.json (Wikipedia coordinates).
- Script: `map.steps[]` (each anchored to a word like shots): focus / view {lon, lat, span} / world, highlight
  (country, state or `file:x.geojson` from episodes/<slug>/geo/ for historical borders), dim, places (gazetteer names
  or lon/lat; kinds city/capital/port/site/event/sea), routes (sea/air/line, avoid passages, curated path), arrows,
  choropleth (inline values or World Bank indicator + year, CC BY 4.0, log/linear), true_size, layer day/night,
  `globe: true` intro. v2 `highlight/points` shorthand still works. Script-level `map_style`.
- Engine: consecutive map shots form one map block with one continuous camera (van Wijk smooth zoom/pan, eased,
  slow push-in while holding); overlays of the previous shot clear (min 1.6 s on screen); camera auto-reframes when new
  content is outside the safe area (captions band kept clear). Python (pipeline/maps.py) pre-computes everything
  (camera keyframes, LOD layers clipped + simplified, imagery per view, label anchors); Remotion (src/map/) only draws.
  Labels: deterministic widths, greedy collision placement per camera "epoch", kept in place between epochs.
- Styles: satellite (Blue Marble, grade baked in), atlas (light vector + relief), midnight (dark vector + relief).
  Relief is masked to Natural Earth land. Default MAP_STYLE=satellite until the user picks.
- Flow: TTS speed 0.95 -> 1.0, paragraph pause 0.55 -> 0.45 s, chapter pause 0.9 -> 0.75 s, cards 2.6 -> 2.4 s,
  dissolves 10 -> 8 frames, chapter cards punch in (scale + fade), stock clips slow push-in, lower-thirds count numbers up
  ("About $9.6 billion" - never bare years), procedural SFX (pipeline/sfx.py, numpy only): whoosh on camera flights,
  long whoosh on globe dives, pops on markers, thump on highlights, swoosh on routes/arrows, hit on cards, ticks on counters.
  Mixed under the voice (SFX_LEVEL_DB -17, not ducked). `SFX=0` disables.
- Tooling: render.yml inputs `map_style`, `stills` (render chosen frames only, e.g. "0,12.5s"; ~1-3 s per frame) and
  `thumbnails`; remotion/stills.mjs. Removed unused world-atlas/topojson deps.
- Evidence: stills runs 41290179584 (satellite) and 41290703460 / 41290708422 / 41290713167 (3 styles): prepare 1m39s
  for the 53.5 s demo (tts 44 s, maps + imagery 51 s cold), map block JSON 0.4-1.2 MB, stills ~1-3 s each.
  Full renders: map-demo x3 styles (41292624753 / 41292630139 / 41292635397; first pass 41291136970: 1284 frames in
  1m58s, ~10.9 fps). suez-canal 41292641100: 173.1 s video (3A: 181.2 s), 26 units from 28 shots, 38 SFX,
  job 8m54s warm (prepare 45 s, render 6m11s for 4154 frames ~11.2 fps, thumbnails 14 s); cold TTS at speed 1.0 = 152 s
  (run 41291150896). Audio now: mix -> measured loudness -> one linear gain (+13.4 dB) + -1 dBFS limiter.
  Found and fixed on the way: SFX were placed at absolute levels while Kokoro's raw narration is -27.4 LUFS, so after
  normalisation they sat ~13 dB too hot (card hit louder than the voice). Now sfx.build_track shifts them by the measured
  narration loudness. Final renders 41293856270 / 41293861365 / 41293866811 (demo x3) and 41293872223 (suez): card hit
  peaks about -25 dB (0.1 s RMS) vs speech about -15.7 dB RMS; true peak -0.9 dBFS. SFX_LEVEL_DB tunes the whole bed.
- Delivered: C:\Users\MONSTER\Videos\yt-pipeline\suez-canal-3b\ (final.mp4, youtube.txt, credits.txt, thumbnails) and
  C:\Users\MONSTER\Videos\yt-pipeline\map-styles\ (satellite.mp4, atlas.mp4, midnight.mp4: same 53 s demo per style).
- Style decided: satellite. Next: user's notes on suez-canal-3b + approval, then 3C (music library + chapter crossfades).
- Known limits: views crossing the antimeridian get vector wrap but only one imagery tile; satellite imagery is 500 m
  (soft below ~3 degree spans); historical borders need your own GeoJSON (OpenHistoricalMap import not automated).

## Phase 3A - long-form engine (done 2026-10-31, waiting for user approval)
- script.json v2 (chapters -> paragraphs -> word-anchored shots), paragraph TTS, chapter cards, global word-by-word captions,
  pronunciation dictionary (pipeline/pronunciations.json + per-episode overrides), youtube.txt (title, description with
  chapters + credits, tags). YouTube API upload removed: the user uploads manually with final.mp4 + youtube.txt + thumbnails.
- Evidence: run 41226922614 (suez-canal): 181.2 s, 27 shots, 4 chapters. Job 11m52s = prepare 3m33s (tts 155 s for 158 s
  of narration, media 51 s) + render 5m52s (4,350 frames, ~12.4 fps) + thumbnails 21 s. final.mp4 87.8 MB (~3.9 Mbps),
  so 15-20 min would be ~350-470 MB: Release delivery (3D) is required.
- Kokoro returns word timestamps: all 19 paragraphs used them and Whisper never ran (kept only as a fallback).
- Pronunciation overrides confirmed in Kokoro's phoneme output ("Port Said", "Lesseps").
- Findings: map labels overlap and zoom stays too wide (3B). Pexels returns wrong specific places (a US dam for the Nile,
  the Elbe canal for "desert canal"), so use stock only for generic concepts, maps or illustrations for specific places,
  and add storyboard review (3D). A chart shot stayed 12.9 s (pacing rule for 2C). TTS is ~1x real time (optimisation candidate).
- Fixed after the run, not yet re-rendered: the quote author appears only after the quote text has revealed.
- Delivered to the PC: C:\Users\MONSTER\Videos\yt-pipeline\suez-canal\ (final.mp4, youtube.txt, credits.txt, thumbnails).

## Phase 3 plan - long form (proposed 2026-10-31, awaiting approval; no code yet)
Flow per episode: topic -> script (Claude Code session: outline, facts.json with >=2 sources per number, chapter-by-chapter
writing, check_script.py, separate verifier, user approval) -> storyboard preview on Actions -> full render -> private Release
-> download to C:\Users\MONSTER\Videos\yt-pipeline\<slug>\ -> user watches -> upload private to YouTube -> delete Release.
- 3A: script.json v2 (chapters -> paragraphs -> shots anchored to words), paragraph-level TTS (pauses ~0.6 s / ~1.5 s),
  word-anchored cuts, pronunciation dictionary (Kokoro inline phonemes, to verify), YouTube chapters in the description.
  Keep Whisper unless Kokoro exposes timestamps (not documented on the model card). Evidence: a 3-4 min sample video.
- 3B: map engine v2: Natural Earth layers (admin-0/1, places, rivers, lakes, marine, relief), globe intro, region focus,
  animated routes, choropleths (OWID / World Bank, CC BY 4.0), markers/labels, true-size compare, historical borders
  (OpenHistoricalMap CC0 or own GeoJSON); static layers pre-rendered; 2-3 style frames for the user to choose.
- 3C: music library v1 (8 tracks x 3 moods, ~4 min, A/B sections) generated once, private Release; chapter crossfades; ~-20 dB under voice.
- 3D: Release delivery + PC download, storyboard step, upload.yml reads from the Release, per-run Actions-minutes summary.
- 3E: first full 15-20 min pilot (script generation + render + review + private upload). Needs phone-verified channel + 2B OAuth.
Budget per video (estimate): Actions 45-80 min; Pexels ~100 requests; schnell ~1,000-1,500 neurons; YouTube API ~51 units.

## Direction change (2026-10-31, discussion with user)
- Target: 15-20 min videos, map-heavy niche as a MIX (economic geography, geopolitics, empires, border oddities), ~20/month
  (suggested ramp: start 8-12/month; Actions estimate ~45-80 min per video vs 2,000 min/month).
- Review flow: render -> private GitHub Release (<2 GiB/file) -> download to the user's PC
  (C:\Users\MONSTER\Videos\yt-pipeline\<slug>\) -> user watches -> upload workflow sends it to YouTube as private.
  Avoid large artifacts (500 MB storage metered hourly; overrun behaviour unclear).
- Long-form needs (not built yet): phone-verified channel (>15 min uploads, custom thumbnails); chapter/paragraph narration
  with word-timed visual cuts instead of per-scene 0.9 s gaps; YouTube chapters; several music beds per video; higher-detail
  Natural Earth layers, globe intro, routes, choropleths. Historical borders: avoid aourednik/historical-basemaps (GPL-3.0);
  OpenHistoricalMap is mostly CC0.

## Music lab (experiment, 2026-10-31)
- `tools/music_lab.py`: procedural music from scratch with numpy (wavetable pads, Karplus-Strong plucks, FM bells, ticks,
  booms, risers, synthetic convolution reverb, mastering EQ). No samples, so no licence terms and no Content ID matches.
- Moods: calm (A minor, 66 BPM), curious (D major, 100 BPM, plucked arpeggio), tension (D harmonic minor, 84 BPM, ostinato,
  ticks, booms, risers). Output 48 kHz stereo, RMS -19 dBFS, peak about -9 dBFS; analysis PNG (spectrogram + loudness) and report.json.
- First pass was too dark (94-97% of energy below 1 kHz); rebalanced to 1-4 kHz 7-9% and 4-12 kHz 2-3% for calm/curious.
- Speed: ~0.3x real time on the PC (~23 s per 75 s track). Rendering per video on Actions would add ~6 min for 20 min of music,
  so a pre-generated, user-curated library may be better.
- Waiting for the user's listening feedback (files in C:\Users\MONSTER\Videos\yt-pipeline\music-lab\). Not integrated into the pipeline.
- Decision (user delegated it on 2026-10-31, "you decide"): own procedural music is the default source.
  Reasons: zero licence and Content ID risk for a monetised channel, no manual downloads, a consistent channel sound,
  and the user did not reject the sound.
  - Moods by chapter: calm = default (explanations), curious = map journeys / "how it works", tension = wars, crises, collapses
    (tame tension low end: <80 Hz is currently 21% of energy).
  - Level: about -20 dB under the voice while speaking (bed about -11 dB, ducked about 9 dB); adjustable.
  - Production: a pre-generated library (about 8 tracks x 3 moods, about 4 min each, A/B sections for variety), generated once
    on Actions and stored as a private Release asset. Each video picks tracks per chapter mood and crossfades at chapter
    boundaries, so there is no per-video generation cost. Refresh/extend the library periodically.
  - YouTube Audio Library tracks the user adds manually remain supported via /music + credits.json.

## Phase 2A (done 2026-10-31, except real-music test)
- [x] render.yml: `timeout-minutes: 150`; caches restored with `actions/cache/restore` and saved in final `if: always()` steps
      (assets always; HF models only on miss). Verified on run 41206608587: assets-41201330118 + hf-models-v1 restored, new assets key saved.
      Not exercised: a deliberately failed run (save-on-failure relies on `always()`; a hard timeout kill may skip it).
- [x] Default voice am_michael verified end-to-end (same run): job 4m49s, prepare 1m02s (tts 37s, captions 11s, media 10s), render 2m02s (1674 frames), video 69.8 s.
- [x] Ducking: `tools/ducking_test.py` + `audio-test.yml` call the real `media.mix_audio()` with synthetic narration/music and measure
      the 200 Hz music band in speech vs silence: 8.6 dB average (~9.8 dB excluding the fade-out window). Run 41206551954.
      Local ffmpeg (Remotion's bundled build) lacks sidechaincompress/volumedetect, so this must run on Actions.
- [ ] Real-music test: /music still has no tracks. When added: commit them, fill credits.json, run render.yml, listen to the result.

## Phase 2B (code done 2026-10-31; upload NOT yet run against YouTube)
- [x] Thumbnails: `pipeline/thumbnails.py` + Remotion `Thumbnail` still (1280x720). 3 variants (A left / B center / C right) with
      schnell backgrounds (`THUMB_STYLE`), 68-101 KB each. Verified on run 41207658895 (+22 s, ~175 neurons). script.json needs a `thumbnail` block.
- [x] `pipeline/youtube_upload.py` + `.github/workflows/upload.yml` (inputs: slug, render_run_id, thumbnail A/B/C, dry_run default TRUE, force).
      Always `privacyStatus=private`, `selfDeclaredMadeForKids=false`, `containsSyntheticMedia` from script (default true), no publishAt.
      Refuses a duplicate title unless force. Thumbnail failure (e.g. unverified channel, 403) only warns. Workflow inputs go through env (no shell injection).
- [x] `tools/youtube_auth.py`: run on the user's PC; sets YT_CLIENT_ID / YT_CLIENT_SECRET / YT_REFRESH_TOKEN via gh without printing them.
- [x] script.json `youtube` block (title <=100, description intro, tags, category 27); credits.txt is appended to the description.
- Verified docs: thumbnails.set JPEG/PNG <=50 MB, 50 quota units; videos.insert 1 unit (own bucket, 100/day);
  Testing-mode refresh tokens expire in 7 days. NOT confirmed this session: exact unverified-app limits in production, channel-verification rule for thumbnails.
- [ ] User: Google Cloud project + OAuth client + `python tools/youtube_auth.py client_secret.json` (steps given in chat).
- [ ] Then: dry run, then a real private upload of nokia-intro (needs the user's go-ahead).

## Phase 2 plan (approved decisions)
Decisions: (1) script generation runs in the Claude Code session (research -> facts.json with >=2 sources per number ->
script.json -> deterministic check_script.py -> separate verifier agent -> user review); (2) timeout: single job,
`timeout-minutes: 150`, cache saved with `if: always()`.
- 2A: timeout/cache fix; music + ducking test (needs tracks in /music; measure music level during narration vs silence).
- 2B: thumbnail (Remotion still 1280x720, AI background, 2-3 variants) + `upload.yml` (YouTube Data API, privacyStatus=private,
  OAuth refresh token as secret; consent screen must be "In production" because Testing tokens expire in 7 days).
  To verify before coding: thumbnails.set channel-verification requirement, containsSyntheticMedia field, production-app limits.
- 2C: script generation flow (facts.json, check_script.py, verifier pass, review gate).
- Risk: YouTube monetisation policy on mass-produced / inauthentic content; keep original scripts + disclose synthetic media.
Each sub-phase stops for user approval.
