# PROGRESS

## Status (2026-11-11 ~15:00Z; start here)
- User (17:30 TR): fix + re-render both, upload long + Shorts scheduled for TODAY as soon as audited ("hazır olur olmaz").
  Renders: outer-banks v2 run 43039219958, langtang v2 43043483123, Shorts outer-banks-short-wait 43043739181,
  langtang-collapse-short-alert 43043744672. Next: fetch_episode.ps1 -Delete -> frame_audit -> review every sheet ->
  --approve -> yt_upload --publish-at (soonest sensible time today) -> verify via API.

## Status (2026-11-11 morning)
- Full renders audited (visual pass on every sheet, subagents + spot checks): langtang-collapse run 42897868958 (16:09)
  and outer-banks run 42902634439 (15:54). Both NOT approved. Audio fine on both; all "flash" flags are cuts.
- Shared root causes: (1) too few distinct photos/map crops for 16 min -> heavy repeats (Langtang: Lirung photo x8,
  Kyanjin snow series x17 standing in for Chamoli/Sikkim/Thame, Rasuwagadhi/Gyirong/north-face crops cycling;
  Outer Banks: 5 Rodanthe photos x8-12 from 7:37, lighthouse set x4-6, Rodanthe photos under Buxton narration);
  (2) count-ups on addresses, "~"/"+"/"up to" values, time offsets, and count cards cut before they finish
  (OB 7:29 ~100 m, 13:31 ~$40M, 15:26 100+ homes; Langtang 9:22 1.5x); (3) holds >8 s on one view.
- Outer Banks specific: purple 2026 Landsat (4:50 Buxton, 7:26 Pea Island); wrong place on map (4:54, 8:59 Rodanthe
  for Buxton; 14:34 Buxton for Avon); 9:15 address counts up; 4:36 keepers' houses over Ocean Drive debris photo.
- Langtang specific: blurry holds 5:24 (mc04p02s01) and 5:58-6:01 (Landsat 8 Oct 2015 zoomed past resolution).
- User chose: engine first, then both episodes. Engine done (b9b863c): count-up rules, chart labels, pre-2016 dated
  views via Landsat, episode_check repeats/holds/stat/compare checks. Purple Landsat = winter dormant marsh (measured),
  not a sensor fault: check now demands growing-season, same-season compares. NEXT: fix both build_script.py files
  until episode_check is clean (OB 147 FIX, Langtang 116 FIX: mostly repeats from POOLS cycling), re-render, audit.
- Covers (6aad8a0): yt_upload now takes cover.jpg before thumbnail_D.jpg. cover.jpg placed: Langtang ISS
  iss074e0603585 "FROM TIBET" (langtang-collapse	humbnails), Outer Banks "PAID TO WAIT".

## Status (2026-11-10, ~19:45 UTC; start here)
- 2026-11-11: Studio check (lifetime to 9 Nov): long videos got only ~2,400 impressions in total, CTR 1.5-3 %.
  New thumbnails set via the API (thumbnails.set) on all 9 long videos: public-domain NASA/ISS images + 2-3 words
  (files + generator in Videos\yt-pipeline	humbnails-2026-11-11). Outer Banks cover: NPS collapse photo, "PAID TO WAIT".
  Re-check CTR/impressions in Studio around 2026-11-18.
- Ogallala long: old 903F5prq9EM went PUBLIC 10 Nov 15:00Z with the old errors (1 view at 19:00Z); Shorts CBB6a3OKlv4,
  YIkaJyUoHAQ public too. v3 (run 42703344451) audited sheet by sheet and approved (audit.json), but the user chose
  "Eskisi kalsın": v3 is NOT uploaded, the old one stays. Do not re-offer unless asked.
- Episode 11 outer-banks (user chose 2026-11-10 from a YouTube scan; coastal erosion): research.md + PLAN.md (gate-1 draft,
  ~2,420 words / ~18.2 min). Own measurement tools/outer_banks_shoreline.py -> episodes/outer-banks/shoreline.json
  (Landsat MNDWI shoreline; Rodanthe ~155 m, Pea Island ~100 m, Buxton ~85 m, Avon ~0, 1985-2026). Gate 1 approved
  2026-11-10. Script built (build_script.py, 2,160 words, ~15.8 min, episode_check OK), factcheck.md complete (0 FIX).
  Next: storyboard render (after the public-repo switch, Actions minutes), frame check, full render, audit, gate 2.
- Still pending from before: public-repo switch (delete old releases, OUT_REPO_TOKEN, render.yml -> yt-pipeline-out,
  make repo public), Langtang storyboard review (run 42700740718 succeeded) and full render, Indus pinned comments.

## Status (2026-11-09, ~22:00 UTC; start here)
- NEW RULE (user, 2026-11-09): every render is audited second by second before upload: tools/frame_audit.py
  (venv python -I) -> look at EVERY sheet -> fix -> re-render -> audit -> `--approve "note"`. yt_upload refuses
  files without an approved audit of that exact render. Releases now carry timeline.json.
- Ogallala replacement, all three videos (user approved re-upload of long + both Shorts and deleting the old ones
  903F5prq9EM, CLGm0e1-SFY, LBTVfQGwVYA, 2026-11-09). Old ones are private, scheduled 2026-11-10T15:00Z.
  Audit of render 42694905414 found: count-ups through ranges ("10% to 58%", "704 to 50") and IDs ("HB 795"),
  patent Fig. 1 out of frame, decline chart shown/cut/restarted, 27.7 % and 18-32 % cards held 7-8 s. All fixed
  (timeline.py count_up; build_script.py). Long v3 render run 42703344451; Shorts v3 runs 42703523429 (orbit),
  42703530084 (farmers): earlier Short v2 audit found hazy Garden City / SW Kansas views -> clear day 2024-08-02.
  DONE Shorts (2026-11-09 ~22:00Z): audited + approved; uploaded private, publishAt 2026-11-10T15:00Z:
  orbit CBB6a3OKlv4, farmers YIkaJyUoHAQ; old CLGm0e1-SFY and LBTVfQGwVYA permanently deleted in Studio.
  Long video still to do (run 42703344451). Next per video: fetch_episode.ps1 -> frame_audit -> review all sheets -> --approve ->
  `python tools/yt_upload.py <slug> --force --publish-at 2026-11-10T15:00:00Z` -> verify publishAt via API ->
  delete the old video in Studio (Chrome) -> report.
- Episode 10 langtang-collapse (Nepal-Tibet flood of 26 Aug 2026): topic from the radar, gate 1 approved by the user
  2026-11-09. Script 2,229 words (~16.4 min), episode_check OK, factcheck.md complete (no FIX). Storyboard run
  42700740718 in progress; next: look at the contact sheets, fix, full render, gate 2 with the user.
- Indus went public 9 Nov 15:00Z; pinned comments and Related video still not done (needs the user's go-ahead).

## Check (2026-11-09, 20:30 UTC)
- API: Indus long nbB4DKNWp7Y and both Shorts went PUBLIC at 15:00Z (long not moved to 14:50Z). Views at 20:20Z:
  long 3, tunnel Short 200, dam Short 20; 0 comments, so pinned comments are not posted; Related video still to do.
- Ogallala three videos: private, publishAt 2026-11-10T15:00Z, processed.
- Sound checked on all six local files (first time; tools: Remotion's ffmpeg has no ebur128/s16le, so WAV -> numpy):
  speech RMS about -18 dBFS, peaks -0.7 to -0.9 dBFS, no clipping, no silent gap over 1.6 s, mono in stereo. Levels
  only; nobody listened for voice errors.
- Ogallala frames 3:06-3:51: "Near Dimmitt" no longer sits over the Colorado map (fixed). Still there: the same
  pivot photo "A center pivot today" holds 3:15-3:22 and comes back at 3:27 after the date card, while the narration
  is about Zybach in 1947-52 (minor; would need a re-render and re-upload before 10 Nov 15:00Z).

## Status (2026-11-09, 04:04 UTC / 07:04 TR; start here)
Checked through the API at that time; nothing below has been published by Claude. Uploads stay private; the user schedules.

**Indus Waters (episode 8): finished, uploaded, waiting to go public today.**
- Long nbB4DKNWp7Y, Shorts PqqVvJZd_18 (tunnel), 9P8EDcca-bY (dam): private, processed, publishAt 2026-11-09T15:00Z (18:00 TR).
- The user planned to move the long one to 17:50 TR (14:50Z) so the Shorts can link to it. Not moved yet: still 15:00Z.
- Half done: when the user says "yayında", add Related video on both Shorts -> nbB4DKNWp7Y (Studio via Chrome, no documented API; needs the long video public or unlisted), then post and pin the three comments (text in each youtube.txt). A session does not wake by itself at that hour.

**Ogallala (episode 9): finished, uploaded, scheduled.**
- Long 903F5prq9EM (15:40), Shorts CLGm0e1-SFY (orbit), LBTVfQGwVYA (farmers): private, processed, publishAt 2026-11-10T15:00Z (18:00 TR). Claude uploaded them unscheduled, so the schedule is the user's own; confirm that with them.
- Half done: the same Related video and pinned comment work after they go public.
- Not verified: sound (on no video so far); the final long render had a blur measurement and a look at its softest frames, while the full picture review (checks A-G) ran on the render before it. That review's leftovers are not rechecked: pivot photo holding about 11 s at 3:16-3:27, "Near Dimmitt" over a Colorado map at 3:09. The two Shorts predate `map.cut` and keep a few flights. Gate 1 was skipped at the user's overnight request.

**Next steps, in order**
1. Indus today, as above; ask whether the user reviewed the Ogallala videos and wants changes before 10 Nov 15:00Z.
2. ~10-11 Nov: read the reach reports, compare CTR with Studio, add download/storage and the weekly report to tools/yt_analytics.py. Aral 48 h check (Chrome if the reports are not ready). Find out why Shorts show 0.0 % watched in `videos`.
3. ~15 Nov: recheck CTR of the repackaged videos.

**Open questions for the user:** remove credits from older videos' descriptions too? (offered, no answer). Old superseded releases remain; the user deletes them.

**Corrections to the section below:** the Related video "Blocker" is gone (verification done 2026-11-09); Ogallala is no longer "not scheduled".

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
- Uploaded 2026-11-09, private: long nbB4DKNWp7Y; Shorts PqqVvJZd_18 (tunnel), 9P8EDcca-bY (dam),
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

## 2026-11-12 (01:00-02:10 UTC)
- Outer Banks day (published 2026-11-11T23:00Z): long 6zrm-jh4Lo4, Shorts 95VaTlND_nM (paid to wait) and EaHxN9OKqYA (lighthouse). Comments posted via `yt_upload.py comment`; pinning is manual in Studio.
- Langtang day (2026-11-12T23:00Z): long 7j0S1PUwPvU (v3, audit approved), Shorts g37VSZhYDMk (38 minutes) and Wd1R0AzmQYY (three times).
- Next: Jakarta sinking (2026-11-13T23:00Z = 14 Nov 02:00 TR): research.md done; script, own measurements, 2 Shorts.
- Release rule: one topic per day, 1 long + 2 Shorts at 23:00 UTC. Studio audience: TR 39 % of views but 8 % of watch time.

## 2026-11-12 (evening)
- Jakarta day (2026-11-13T23:00Z = 14 Nov 02:00 TR): long ucTWIvj9Xf0 (v3, cover "SINKING CITY"), Shorts c2teJHHPgn8 (trees) and hVoZOMcuRZ4 (capital). Lessons: dry-season Sentinel-2 composites leave seams/no-data wedges in the tropics -> single clear days per area (day_for); but one day per area makes fillers look like one scene -> spread filler points over distinct places.
- Louisiana day (2026-11-14T23:00Z = 15 Nov 02:00 TR): script 2,092 words (fact-checked), own Landsat measurement (IdJC -45 %, Wax Lake + Atchafalaya +115 km2, Barataria -16 % since 1990), clear day LA_DAY 2026-10-13. Shorts island + cure re-rendering; storyboard running.

## 2026-11-13 (early UTC)
- Louisiana long v3 (d991ba0) audited: one real defect, a straight seam at 90.1 W through every Barataria Bay view (tiles 15RYN / 16RBT of the same 13 Oct pass, Sen2Cor corrects each UTM zone's tile on its own). Fix: `sentinel._match_overlap` colour-matches later tiles of a picked-day mosaic in their overlap (cache key v2m); local test step 1.58 -> 0.28 grey levels.
- Re-rendering long (run 43354580656) and cure Short (run 43354585035, has a -90.05 wide view). Island Short audited and approved as is.
- Next: fetch both with -Delete, audit, approve, upload long + 2 Shorts scheduled 2026-11-14T23:00Z.
- Later the same night: the user asked for more watchable videos and better covers. Research (API outlier scan, see
  .claude/skills/cover-map and episode-plan step 1) -> new production logic for NEW videos only: `tools/cover_map.py`,
  `topic_radar.py --check` demand test, painted map steps open chapters, brighter imagery (sentinel v3 cache, lighter
  Blue Marble and vignette), `dark` audit flag (Louisiana v3 had 28 dark stretches).
- Louisiana re-rendering with the brighter look: long 43356342349, cure Short 43356346844, island Short 43356351460
  (the earlier island approval is void). Cover: episodes/louisiana-land-loss/cover.json ("IT HAD / A CURE").
- First topic under the new logic: waiting for the user's pick (Kansai sinking airport passed the demand check).

## 2026-11-13 (morning UTC)
- Louisiana: the brighter render (43356342349) had 0 dark flags (v3: 28), but the Barataria seam was still there. Cause: two
  satellites on the picked day (S2B 16:42 tile 16RBT ends at 90.09 W, S2A 16:55 tile 15RYN covers those views whole);
  `sentinel._by_pass` now puts the scene that covers the view alone first (cache v4). Final render running: 43376713212.
  Shorts are NOT uploaded (the user stopped Shorts from Louisiana on, 2026-11-12); their re-renders were my mistake.
  Then: fetch -Delete, audit all sheets, cover from episodes/louisiana-land-loss/cover.json, upload scheduled 2026-11-14T23:00Z.
- Kansai airport (first episode under the new logic; gate 1 approved by the user): research.md with the operator's own
  December 2025 measurements, Air & Space 2018 and the Mesri & Funk paper, all read in the user's Chrome (the sites refuse our
  fetcher). script 2,315 words, `episode_check` OK, factcheck.md 105 verified / 14 attributed / 6 own, no FIX.
  Own evidence: Landsat 1985-08-24, 1989-09-04 (seawall ring), 1990-08-06 (half filled), 1995-08-04, 2004-08-12, 2026-08-25.
  Storyboard running: 43380484708. Then: storyboard self-review, full render, audit, cover (cover.json: "45 FEET / DOWN",
  13.72 m = 45.0 ft), gate 2 for the user.
- Lesson: a search summary gave a wrong forecast (15.7 / 24.9 m); the paper says 17.6 / 24.4 m. Numbers from summaries
  stay TODO until the page itself is read.
- Louisiana UPLOADED: video CKHRMZp-s0M, private, publishAt 2026-11-14T23:00:00Z (15 Nov 02:00 TR), map cover
  "IT HAD / A CURE" set (cover.jpg from cover.json). Final render 43376713212 audited on all 32 sheets: seam gone, 0 dark
  flags. Pinned comment still to post/pin: "Open the river and change the fishing towns for good, or keep today's coast and
  watch it shrink?" (`yt_upload.py comment`, pin by hand in Studio). No Shorts for this topic.
- Kansai: storyboard run 43382820808 finished OK (first try 43380484708 failed in prepare: the 2004 -> 2026 wipe was cut
  0.4 s short on the real narration; its `seconds` is now 1.2). Narration: 824.7 s at speed 1.08 before pauses.
  NEXT: download the storyboard artifact, look at every sheet (island views repeat? photos sharp? painted steps read?),
  fix, full render, frame audit, cover.jpg via cover_map (cover.json: "45 FEET / DOWN"), gate 2 with the user.
  Planned slot (not yet confirmed by the user): 2026-11-15T23:00Z = 16 Nov 02:00 TR.
- Kansai: storyboard run 43382820808 had in fact failed in prepare (14.1 min, under the 15-minute rule). Script is now
  2,550 words (10 more fact-check rows, 135 in all, no FIX); WORDS_PER_SEC 2.22 -> 2.65. Storyboard run 43417425663 running.
- Kansai storyboard OK (run 43417425663): prepare passed, length 15.5 min (913 s of narration, 295 shots). Sheets downloaded
  to Videos\yt-pipeline\kansai-airport-storyboard, artifact deleted. NEXT (after a context compact): look at every
  storyboard sheet, fix, `gh workflow run render.yml -f slug=kansai-airport`, fetch -Delete, frame audit, cover_map, gate 2.
- Kansai storyboard: 10 of 35 sheets reviewed (episodes/kansai-airport/PLAN.md), fixes applied (photo fillers limited,
  Narita views, 1995 view in the hook, seawall paragraph), check OK. Full render started; the audit must cover the rest.
- 17 Nov 02:00 TR slot: australia-interior (user's pick; Kansai must stay on 16 Nov). Reference-video study done
  (docs/reference-videos-2026-11-13.md): hook template, numbered reasons, 2,750-3,000 words, a third ground photos,
  solid painted regions (`highlight: ["Region@red"]`, new in maps.py / MapBlock.tsx, not yet seen in a render).
  episodes/australia-interior/research.md holds the gate-1 outline and TODO facts. Waiting for the user's OK on the
  outline and on narration speed (168 -> ~180 wpm?). Skills registry searched: nothing worth installing
  (iart-ai map-animation is Google Earth Studio / After Effects guidance).
- Kansai full render 43475114378 was still running at this point; then fetch -Delete, audit (sheets 11-35 of the
  storyboard were never reviewed), cover_map, gate 2.
- Kansai render 43475114378 fetched (release deleted): 934 s, audio OK, 0 dark flags, 7 flash, 29 soft, 1 short document.
  The 32 audit sheets are NOT yet looked at (context was full): look at all of them, then --approve, cover_map, gate 2,
  upload with --publish-at 2026-11-15T23:00:00Z.
- User approved the Australia outline and narration speed 1.15 (from Australia on; set it in that script, Kansai stays 1.08).

## 2026-11-13 (late) — Kansai audited, at gate 2
- All 32 audit sheets of render 43475114378 viewed; `frame_audit.py --approve` recorded. No technical defects.
  Weak points (old production logic): open-water fillers at 0:53-1:00, 9:26-9:35, 14:28-14:34; four terminal photos
  reused 3-4 times each; Kansai close views under the Istanbul / Maldives / Brisbane sentence (15:05-15:16).
- Cover rendered (`cover.jpg`, "45 FEET / DOWN"). Dry run OK: "Why Japan's $20 Billion Airport Is Sinking",
  publish 2026-11-15T23:00Z. Waiting for the user's gate-2 answer (upload as is, or cut the repeats and re-render).
- User feedback 2026-11-13: earlier videos show the same or similar pictures too often. For Australia: no filler
  machinery, a view at most twice and 60 s apart, 160-180 distinct shots of 5-7 s, at most two satellite shots in a row;
  enforce in episode_check.py. Diagram cards if time allows.

## 2026-11-14 — Kansai re-edit rendering, Australia at storyboard
- User chose "cut the repeats and re-render" for Kansai. Done in build_script.py: photos at most twice (6 new Commons
  pictures: bridge 2007 and 2013, NASA MODIS image of Typhoon Jebi, Terminal 2, wing, apron), filler views only on the
  two islands and on coasts, the Istanbul / Maldives / Brisbane airports shown under their sentence. Storyboard
  43496913477 looked at (sheets 3, 28, 34) and deleted. FULL RENDER 43520192764 running: fetch
  (`tools/fetch_episode.ps1 kansai-airport -Delete`), audit all sheets, `--approve`, cover exists, then gate 2 and
  upload with `--publish-at 2026-11-15T23:00:00Z`.
- Australia interior: research read (research.md, V/A/OWN), regions built (geo/), script written by hand (2,782
  words, 220 shots: 145 map, 55 photo, 12 stat, 6 quote, 2 chart; voice_speed 1.15), factcheck.md 115 rows (65
  verified, 24 attributed, 26 own, no FIX), episode_check OK, cover.jpg ("WHY SO / EMPTY?"). STORYBOARD RUN
  43523089329 running: download the artifact, look at every sheet (painted regions and `@tint` colours are new,
  MODIS dates 2018-05-15 / 2019-05-15 / 2025-07-12 / 2025-09-02, far airports and mine views), fix, then full render.
  Photos are 25 % of the shots, not the third the rule asks for: sharp licensed files ran out (each at most twice).
- episode_check.py: PHOTO_MAX_USES 2, VIEW_MAX_USES 2, seconds per word scaled by voice_speed.
- 2026-11-14: Kansai re-edit audited (32 sheets), approved, UPLOADED: video WhvKbsw_z0Q, private, publishAt
  2026-11-15T23:00:00Z, cover set. Pin by hand in Studio. Release deleted. Australia storyboard 43523089329 downloaded
  (26 sheets, narration 920.9 s at 1.15 = 181 wpm; 30 mixed-day map warnings on wide Sentinel views): review is next.
- 2026-11-14: Australia storyboard 1 (26 sheets) all looked at: painted regions, tints, MODIS days and far views are
  good. Fixed: a dark vertical strip at the right of the EAST view for ~2 s after a cut (1:43, 4:59, 14:53; the Blue
  Marble raster itself is clean, cause unknown) -> EAST narrowed to end at 155.5 E; channel route drawn in 1.2 s; the
  cable-car photo caption. STORYBOARD 2 = run 43576512125: look at the EAST shots (sheets ~4, 9, 24); if the strip
  is gone start the full render, then fetch, audit, approve, gate 2, upload with --publish-at 2026-11-16T23:00:00Z.
- 2026-11-14: storyboard 2 still showed the dark strip (it sits between the regional raster and the world image while
  the camera eases in from wide on a 25-30 degree view). EAST is now continent-wide (lon 137, span 54) like AUS, which
  was clean. FULL RENDER started (see `gh run list --workflow render.yml`): fetch with -Delete, audit all sheets
  (check 1:43, 4:59, 14:53 for the strip), approve, gate 2 with the user, upload --publish-at 2026-11-16T23:00:00Z.
  Engine bug left open: dark strip at regional-raster edge during ease-in on mid-wide satellite views.
- 2026-11-14: Australia render 43580725109 fetched (942 s), all 32 audit sheets viewed (dark strip gone), approved,
  UPLOADED: video 1PkX-Z5feoQ, private, publishAt 2026-11-16T23:00:00Z (17 Nov 02:00 TR), cover set. Pin by hand:
  "If money were no object, would you build Bradfield's canal and try to green the middle, or leave the empty heart
  of the continent as it is?". Next slot (18 Nov) has no topic yet.
- 2026-11-14: 18 Nov topic = Nevada (user chose it from a demand check of ten candidates). episodes/nevada-empty/
  research.md has the gate-1 outline (hook + 5 reasons, about 2,850 words) and facts so far. Next: user approves the
  outline, then read primary sources (CRS R42346, NOAA NCICS, LCB 2020 table, NPS Rhyolite, USGS Cold War craters),
  regions (Clark/Washoe/federal land/Great Basin), script built like australia-interior/build_script.py.
- 2026-11-14: Nevada outline approved by the user. research.md has the facts read (NOAA, NPS Rhyolite, USGS craters,
  NNSS 928 tests, SNWA 90 %, Census shares 88.6 %, Lahontan 8,500 sq mi, gold 68 %). geo/ has Sierra, Great Basin,
  Black Rock. Photo search running into scratchpad/nv (24 subjects). NEXT: pick photos (>=1400 px, sharp), MODIS/
  Landsat dates (Sedan crater, Lake Mead), write build_script.py modelled on australia-interior (hand-placed, no
  fillers, voice_speed 1.15), episode_check, claim_log + factcheck, cover.json, storyboard.
- 2026-11-14: Nevada build_script.py draft 1 builds (1,360 words, 94 shots: 49 map, 32 photo). TOO SHORT: needs
  2,750-2,900 words. Expand with SOURCED material only (read sources first, add to research.md): Comstock (Mark Twain
  in Virginia City, statehood 1864 "Battle Born"), Nevada's population fall after 1880 (census 62,266 in 1880 ->
  42,335 in 1900), Lake Lahontan shorelines, Pyramid Lake cui-ui / Paiute reservation, Lake Mead record low 2022,
  Las Vegas growth (1940 8,422 -> today), Yucca Mountain nuclear waste plan, Area 51 (CIA 2013), Hoover Dam 1936,
  BLM wild horses, US 50 "Loneliest Road" (LIFE 1986). Then episode_check, claim_log/factcheck, cover.json, storyboard.
- 2026-11-14: Nevada draft 2 = 1,618 words, 110 shots. STILL ~1,200 words short. Next sourced additions to research
  (read, add to research.md, then paragraphs): Derby Dam / Newlands Project 1905 and Pyramid Lake's fall (Paiute,
  cui-ui fish); Burning Man's temporary city on the Black Rock playa (attendance figure); Great Basin bristlecone pines
  and the Prometheus tree on Wheeler Peak (1964); BLM wild horses (Nevada's share); Las Vegas growth 1940 -> 2020;
  Hoover Dam 1931-36; Area 51 (CIA 2013). Keep every shot hand-placed; then episode_check, claim_log, cover, storyboard.
- 2026-11-14: Nevada draft 3 = 1,974 words, 128 shots. episode_check: 36 FIX (long holds in c05/c06, photos over the
  2-use limit: US 50 x4, Las Vegas air x3, Black Rock x3, ranch road x3). TODO: (1) more alternate photos (other
  Great Basin NP / Rhyolite / Las Vegas files from scratchpad/nv, check sharpness), (2) split long holds with extra
  hand-placed satellite views, (3) ~800 more sourced words (candidates: Hoover Dam 1931-36 and Boulder City, Area 51,
  Lahontan shorelines, Carson City as capital), then claim_log/factcheck, cover.json, storyboard.
- 2026-11-15: Nevada draft 4: 2,683 words, 205 hand-placed shots; added Las Vegas 1905 + Mormon fort, 1931 gambling
  and divorce laws, Hoover Dam (official 96 deaths), Area 51 (CIA 2013), Pony Express, atomic tourism, AB 356 turf law,
  Carlin 100 M oz, Pyramid Lake Paiute reservation. episode_check "OK, ready to render" (est. 16.9 min; Australia ran
  at 0.9x its estimate -> expect about 15.2 min). factcheck.md: 55 verified, 52 attributed, 16 own. Cover rendered.
  Storyboard run 43676024317 started.
- 2026-11-15: Nevada storyboard (run 43676876783, 23 sheets, ~15.5 min) all viewed; artifact deleted. Fixed: county
  highlights (engine has no county data), WRONG PHOTO "Hoover Dam Ohio.JPG" (the Ohio dam) -> "Hoover Dam
  (6917293059).jpg", Pyramid north-end seam, framed Tonopah panorama, washed Rhyolite close-up, empty playa close-up
  (-> Gerlach), repeated Nevada paints at the end, 1859 Humboldt sketch caption. Full render next.
- 2026-11-15: Nevada full render 43679027846 audited (31 sheets); one fix (Burning Man paint push-in filled the frame
  red) -> re-render 43681238201, sheet 29 re-checked, approved. UPLOADED: video MhYL1LwTY5I, private, publishAt
  2026-11-17T23:00:00Z (18 Nov 02:00 TR), map cover set. Releases and artifacts deleted. Pin the comment by hand in
  Studio (pinned_comment in build_script.py). Note: real length ran at 0.92x of episode_check's estimate (15.5 vs 16.9).
- 2026-11-15: 19 Nov topic = Northern Maine (user chose it from four demand-checked candidates; outline approved).
  episodes/northern-maine-empty: research.md, geo/ (Census 2020 UT, Aroostook, Piscataquis, Cumberland+York),
  build_script.py (2,689 words, 223 hand-placed shots, episode_check "OK, ready to render", est. 16.9 min -> about
  15.5 real), factcheck.md (177 claims: 61 verified, 89 attributed, 27 own, 0 FIX), cover.json ("NO TOWNS?").
  Storyboard next.
- 2026-11-15: Northern Maine storyboard (run 43699243263, 24 sheets, ~15.6 min) all viewed; artifact deleted. Fixed:
  too many look-alike green forest close-ups (21 now use October foliage or winter snow dates), Massachusetts and
  Idaho/Maine push-ins losing their subject, 1783 Quebec highlight and two UT paints filling the frame, St. John
  caption orientation, East Millinocket view (was a lake), Atlantic view now shows Europe. Full render next.
- 2026-11-15: Northern Maine render 43701801553 (15:42) audited, all 32 sheets viewed. Fix: painted maps no longer get
  the automatic push-in (Massachusetts, 1783, budworm and closing UT paints filled the frame red); hand-placed camera
  steps instead; "But first" map paints Maine instead of Quebec. Re-render next.
- 2026-11-15: Northern Maine re-render 43704740020 approved (changed sheets 4, 10, 21, 31 re-checked; audio peak
  -0.59 dBFS, no clipping). UPLOADED: video MaiFqokoUdM, private, publishAt 2026-11-18T23:00:00Z (19 Nov 02:00 TR),
  map cover set. Releases and artifacts deleted. Pin the comment by hand in Studio. Next free slot: 20 Nov.
- 2026-11-15: 20 Nov topic = Mongolia (user chose it; outline approved). episodes/mongolia-empty/research.md has the
  gate-1 outline (hook + 5 reasons: high/dry/cold, herds not farms, dzud, empire->Soviet->1990, one city + mining) and
  facts read. Photo search running into scratchpad/mn (28 subjects). NEXT: quality-check photos (q2.py, >=1400 px,
  detail >=0.65), contact sheets, build_script.py modelled on northern-maine-empty (hand-placed, seasonal dates for
  look-alike views, no push-in on paints), episode_check, claim_log + rules script (mefact.py pattern), cover.json
  (Mongolia red, "SO EMPTY?"), storyboard, render, audit, upload publishAt 2026-11-19T23:00:00Z.
- 2026-11-15: Mongolia build_script.py draft 1 (1,578 words, 120 shots) + geo/gobi.geojson. TOO SHORT: needs
  ~2,750. Photos chosen (constants in build_script). Next: add ~1,150 sourced words (candidates: Khövsgöl lake,
  Kazakh eagle hunters of Bayan-Ölgii, Trans-Mongolian rail 1949/1955 detail, Choibalsan/1990 hunger strike,
  Ulaanbaatar inversion/coal ban 2019, Tavan Tolgoi rail 2022, Gobi wildlife, Naadam, sheep/cashmere prices,
  urban share 69 %), fix holds, episode_check, claim_log/rules, cover, storyboard.
- 2026-11-15: Mongolia draft 2 = 2,059 words, 154 shots (added borders/census, Khövsgöl+Altai, eagle hunters,
  record herd/overgrazing, dzud schools, 1990 hunger strike, 2019 coal ban, Tavan Tolgoi rail cost). STILL ~650 words
  short (target 2,750) and ~20 long holds (episode_check). Patch scripts in scratchpad (mnpatch1.py). Next: +650
  sourced words, fix holds, then claim_log/rules, cover, storyboard.
- 2026-11-15: Mongolia draft 3 = 2,303 words, 185 shots (mnpatch2.py: Oviraptor 1993, horses outnumber people,
  230,800 herding households, dzud history + warming >2 C since 1940, empire Korea-Hungary, rail 1949/1955, Darkhan
  1961/Erdenet, Örgöö 1639, poverty third, 2025 growth 6.8 %, solar-panel close). Still ~400 words short (est 14.5
  min -> real ~13.3) and 14 FIX (holds; Sheep herd and Ger district photos used 3x). Next: +400 sourced words, fixes.
- 2026-11-15: Mongolia draft 4 = 2,570 words, ~214 shots, episode_check clean (est 16.2 min -> ~15.1 real).
  Next: claim_log + rules script (pattern scratchpad/mefact.py), cover.json, storyboard.
- 2026-11-15: Mongolia draft 4 final: 2,562 words, 214 shots, episode_check "OK, ready to render" (est 16.1 min);
  factcheck.md 157 claims (25 verified, 116 attributed, 16 own, 0 FIX; rules in scratchpad/mnfact.py); cover.json
  ("SO EMPTY?", Mongolia red, no labels). Storyboard next.
- 2026-11-15: Mongolia storyboard run 43725966843 done (23 sheets in scratchpad/mnsb/*/storyboard), artifact
  deleted. NEXT: view all sheets, fix (patch build_script), full render `gh workflow run render.yml -f
  slug=mongolia-empty`, fetch_episode.ps1 -Delete + delete artifacts, frame_audit (venv), approve, audio check
  (remotion ffmpeg -> wav, venv numpy), upload `python tools/yt_upload.py mongolia-empty --publish-at 2026-11-19T23:00:00Z`.
- 2026-11-15: Mongolia storyboard sheets 1-12 viewed: winter-dated flat-steppe views render blank white -> mnpatch6.py
  switched them to October/summer with honest labels; Oviraptor beige run and cloudy Bayanzag view replaced; camp
  labels made honest. Sheets 13-23 still to view before the full render.
- 2026-11-15: Mongolia storyboard all 23 sheets viewed; fixes: blank-white winter views on flat steppe and small ger
  views -> October/summer, honest labels, Oviraptor run, cloudy Bayanzag. Full render next.
- 2026-11-15: Mongolia full render 43729927782 fetched to Videos/yt-pipeline/mongolia-empty, release + artifacts
  deleted, frame_audit ran (31 sheets in audit/, flags mostly soft/flash at stat-card cuts). NEXT: view all 31 sheets,
  approve (--approve/--accept-flags), audio check, upload --publish-at 2026-11-19T23:00:00Z.
- 2026-11-15: Mongolia audit: sheets 1-28 of 31 viewed, clean. Continue with sheet_29 onward in
  C:\Users\MONSTER\Videos\yt-pipeline\mongolia-empty\audit, then approve, audio check, upload.
- 2026-11-15: Mongolia render 43729927782 audited (31 sheets, all clean; audio peak -0.67 dBFS, 15:12). UPLOADED:
  video rziBDyJaeqk, private, publishAt 2026-11-19T23:00:00Z (20 Nov 02:00 TR), map cover set. Releases and
  artifacts deleted. Pin the comment by hand in Studio. Next free slot: 21 Nov.
- 2026-11-15: 21 Nov topic = "How the Mediterranean Sea Dried Up" (Messinian salinity crisis + Zanclean flood),
  chosen by the user from docs/topic-candidates-2026-11-21.md. NEXT: research (Hsü & Ryan DSDP Leg 13 1970,
  evaporites ~1 M km3, Nile canyon under Cairo (Chumakov), Rhône canyon, Garcia-Castellanos 2009 Nature flood,
  Malta 2024 study, Gibraltar strait), gate-1 outline to user, then build like mongolia-empty.
- 2026-11-15: Mediterranean outline approved by the user ("Uygun, motoru da genişlet"): extend pipeline/bathy.py with
  a "mediterranean" basin (box about (-6,30,36.5,46), seed point in the Ionian Sea, current level 0 m) and allow
  drops up to ~3,000 m (today `0 < drop <= 200`); keep caspian behaviour unchanged; test with a storyboard of the
  hook. Then photos, build_script.py (pattern mongolia-empty), checks, cover, storyboard, render, audit, upload
  publishAt 2026-11-20T23:00:00Z.
- 2026-11-15: pipeline/bathy.py extended: BASINS entries may carry land-fill cut boxes and a max drop;
  "mediterranean" basin added (Atlantic and Black Sea cut out, max 4,000 m). Tested (venv python): -200 m -> about
  568,000 km2 dry, -1,500 m -> about 1.8 M km2; caspian -20 m unchanged (121,192 km2). Use highlight
  "seafloor:mediterranean:1500@red" in maps. NEXT: photo search (Glomar Challenger, Gibraltar, Realmonte salt mine,
  Nile delta ISS, Messinian gypsum Sicily/Spain), build_script like mongolia-empty.
- 2026-11-15: Mediterranean photo search done; passing list in scratchpad/md_ok.txt (re-run q2 if scratchpad lost).
- 2026-11-16: Mediterranean build_script.py written (2,681 words, 231 shots, episode_check OK at about 16.9 min),
  research.md additions, factcheck.md filled (no FIX rows), cover.json (seafloor:mediterranean:1500 red, arrow to
  Gibraltar, "DRIED UP?"). tools/cover_map.py accepts {"seafloor": "basin:m"}. bathy.exposed fixed: parts of a basin
  that stay deeper than the new level stay wet as separate lakes (before, only water connected to the seed counted;
  caspian -20 m unchanged). NEXT: storyboard, review, full render, audit, upload publishAt 2026-11-20T23:00:00Z.
- 2026-11-16: Mediterranean storyboard 1 failed at 14.9 min -> script lengthened to 2,830 words; storyboard 2 OK
  (15.7 min). Fixes after review: pipeline/maps.py no longer auto-frames on seafloor:<basin> highlights when the
  step has its own view (close drawdown views were being zoomed out to the whole basin); Sicily views on spring
  imagery (summer read as flat beige); Cape Bon coordinates. NEXT: full render, audit, upload 2026-11-20T23:00Z.
- 2026-11-16: Mediterranean UPLOADED: TXF3-pYORUs, private, publishAt 2026-11-20T23:00:00Z (21 Nov 02:00 TR),
  15:41, cover set. Frame audit approved (32 sheets), audio peak -0.8 dBFS. Release/artifacts deleted.
  Pin the comment by hand in Studio.
- 2026-11-16: 22 Nov topic = "When the Sahara Was Green" (African Humid Period), chosen by the user from
  docs/topic-candidates-2026-11-22.md. NEXT: research (AHP timing ~11-5 ka, Mega-Chad, Gobero, Wadi Howar, Tassili
  rock art / Cave of Swimmers, orbital precession + monsoon, abrupt vs gradual end, dust to the Amazon), gate-1 outline.
- 2026-11-16: Green Sahara outline approved ("Uygun, senaryoya geç"). geo/make_regions.py: megachad.geojson (ETOPO
  cells <320 m connected to Lake Chad, ~331,000 km2; 325 m spills south) and sahara.geojson (Natural Earth).
  cover.json done ("A SEA IN THE / SAHARA?", Mega-Chad red). Photo search running into scratchpad/gs.
  NEXT: photo QC, build_script like mediterranean-dried, checks, storyboard, render, audit, upload 2026-11-21T23:00Z.
- 2026-11-16: Green Sahara build_script.py written (2,745 words, 252 shots, episode_check OK at 17.3 min), research
  additions, factcheck.md filled (rules in scratchpad gsfact.py). NEXT: storyboard, review, render, audit, upload
  publishAt 2026-11-21T23:00:00Z.
- 2026-11-16: Green Sahara storyboard OK at 15:44 (run 43834667672, artifacts deleted). Review of sheets 1-12: Sentinel
  close views (span < ~2) of hyper-arid desert render blank/washed-out beige with tile seams (Gilf Kebir, Ténéré/Gobero,
  Wadi Howar, Mega-Chad floor, Bodélé 1.2, Ounianga). Fix: widen those to span >= 3.5 (basemap) or replace with
  maps/stats; first Ounianga sat had wrong lon (18.5 -> 20.5). Green/feature areas (Lake Chad, Ennedi, Tibesti, Nile,
  Sahel) render fine. Sheets 13-27 still to review.
- 2026-11-16: Green Sahara: 45 close desert sat views widened to span 1.8 (script rule in build_script; kept Sahel,
  Nile, Ennedi, Emi Koussi, Oweinat, coasts). Full render started; audit all sheets before upload.
- 2026-11-16: Green Sahara full render 1 audit: views at span 1.8 still use Sentinel (S2_MAX_SPAN 2.0 in maps.py) and
  show date-mosaic seams in hyper-arid desert -> all widened desert sats set to span 2.2 (basemap). Re-render needed.

## HANDOFF 2026-11-16 (session end) — read this first

Done this session (all private, scheduled 23:00 UTC = 02:00 TR):
- Mediterranean "How the Mediterranean Sea Dried Up": TXF3-pYORUs, publishAt 2026-11-20T23:00:00Z, 15:41, cover set.
  Engine changes: pipeline/bathy.py separate lakes (deep parts stay wet), pipeline/maps.py seafloor highlights do not
  override a hand-picked view, tools/cover_map.py {"seafloor": "basin:m"} subject.
- Green Sahara (22 Nov slot): topic chosen by the user (docs/topic-candidates-2026-11-22.md), research.md, geo
  (megachad.geojson ETOPO <320 m ~331,000 km2; sahara.geojson), build_script.py (2,745 words, 252 shots, check OK
  17.3 min), factcheck.md filled, cover.json done ("A SEA IN THE / SAHARA?").

Half done:
- Green Sahara full render #2 running: run 43846972915 (fix: 47 widened desert views at span 2.2, because Sentinel
  below S2_MAX_SPAN 2.0 showed date-mosaic seams in render #1 / run 43841211081, which was NOT approved).
  Render #1 files in Videos\yt-pipeline\green-sahara are superseded (fetch -Delete overwrites).

Next steps (in order):
1. When run 43846972915 succeeds: `powershell -File tools/fetch_episode.ps1 green-sahara -Delete`, delete its
   artifacts (gh api .../runs/43846972915/artifacts), run frame_audit, view ALL 32 sheets (check the widened desert
   views: Gilf Kebir 1:15-1:50, Ounianga ~0:36 and ~6:00, Ténéré ~3:05-3:45, Wadi Howar ~4:00, Bodélé ~6:20 and
   ~9:38), audio peak check, --approve, then `python tools/yt_upload.py green-sahara --publish-at 2026-11-21T23:00:00Z`.
2. Lesson for desert episodes: hyper-arid close views (span < 2) render blank or seamed; use span >= 2.2 there.
3. Next slot after 22 Nov: ask the user for a topic (Netherlands below sea level and Doggerland passed demand).

Pin comments by hand in Studio: Louisiana, Kansai, Australia, Nevada, Northern Maine, Mongolia, Mediterranean
(text = youtube.pinned_comment in each build_script.py), and Green Sahara after upload.

Indus Waters (episode 8) status: long nbB4DKNWp7Y + Shorts PqqVvJZd_18 (tunnel), 9P8EDcca-bY (dam) uploaded
2026-11-09, scheduled by the user for 15:00 UTC 9 Nov (public since then). Still open: Related video link on both
Shorts (Studio only; blocked by YouTube "one-time verification", only the user can complete it) and the pinned
comment. Audio of the long render was never checked. No further work planned unless the user asks.

## 2026-11-16 (after handoff) — Green Sahara render 2 rejected, render 3 running
- Render 2 (run 43846972915) fetched + audited (32 sheets, audio peak -0.78 dBFS, 15:46): NOT approved. Hard-edged
  patches at 4:52, 5:32, 6:12, 6:33, 7:52, 8:04, 9:41, 11:30, 13:11. Cause: build_script's automatic push-in took
  2.2-degree views to 1.364 (x0.62), below S2_MAX_SPAN 2.0, so multi-day Sentinel mosaics were fetched (run log
  "map warning: ... Sentinel-2 scenes of N days"). Fix: push_span() keeps views above 2.0 at >= 2.05; Gulf of
  Guinea, Sahel fields, Manaus, Lake Chad views widened to 2.2. Lesson for every episode: check the push-in target
  too, not only the hand-picked span; read the run log's mixed-day warnings before auditing.
- RENDER 3 = run 43853198269. Next: fetch -Delete, delete artifacts, frame_audit, view all sheets (check the times
  above), --approve, upload --publish-at 2026-11-21T23:00:00Z.
- 2026-11-16: Green Sahara render 3 (run 43853198269, 15:46) fetched, release deleted (no artifacts), all 32 sheets
  viewed: render-2 seams gone; audio peak -0.78 dBFS. Approved and UPLOADED: video Mw00DGzLiV8, private, publishAt
  2026-11-21T23:00:00Z (22 Nov 02:00 TR), map cover set. Pin the comment by hand in Studio. Note: yt_upload.py runs
  with the system `python` (the venv has no google libs). Next free slot: 23 Nov (candidates: Netherlands below sea
  level, Doggerland).
- 2026-11-16: 23 Nov topic = Netherlands below sea level (user chose it). Demand PASS (7 at 3x). Title "Why the
  Netherlands Sank Below the Sea". episodes/netherlands-below-sea/research.md has the gate-1 outline (hook + 5 reasons,
  2,800 words, episode_check OK at 17.6 min) and the facts read (PBL 26 %/59 %, Erkens 2016 1.9 m / 19.8 km3, Beemster,
  Cruquius, 1953, Delta/Zuiderzee Works). NEXT: user approves the outline, then the "To read next" list, regions,
  photos, build_script like green-sahara (push_span!), checks, cover, storyboard, upload 2026-11-22T23:00:00Z.
- 2026-11-16: Netherlands outline APPROVED by the user. research.md rounds 2-4 added (Schiphol, Haarlemmermeer, 1836
  storms, 1916/Lely/Afsluitdijk 28 May 1932, Delta barriers, Twee Gebroeders 1953, Ouwerkerk caissons, terps, NAP/Hudde
  1684, palace piles, Walcheren 1944, Wieringermeer 1945, 1995, Groningen, KNMI'23, Sand Motor, Rli). Narration draft
  2,618 words in drafts/narration.md (every sentence from research.md). geo/make_regions.py -> belowsea.geojson
  (ETOPO <0 m, 34-36 %, labelled approx.). Photo search done (scratchpad nl/, quality check running).
  NEXT: pick photos, build_script.py (copy helpers + push_span from green-sahara), episode_check, claim_log/factcheck,
  cover.json, storyboard.

## 2026-11-19 — Netherlands: script ready, storyboard running
- build_script.py: automatic camera beats (any map shot holding one framing > 14 words gets push-in / pull-back
  steps; painted views stay > 2.5, others above 2.05 when > 2.0), plus 27 hand-placed shots and 9 new Commons photos
  (NAP Stopera, 1916 breach, Den Bommel 1953, Slochteren 1963, Spiegelwaal, Sand Motor x2, Thwaites, Hogebeintum).
  episode_check OK: 2,623 words, 196 shots, ~16.5 min. factcheck.md 144 rows, 0 FIX (9 attributed/own).
  Cover: belowsea red, "THEIR OWN / FAULT?" (title already says "Below the Sea"); checked at 320 px.
- Storyboard run 44588904220. NEXT: fetch sheets, review, full render, frame_audit, approve,
  `python tools/yt_upload.py netherlands-below-sea --publish-at 2026-11-22T23:00:00Z` (23 Nov 02:00 TR).
- 2026-11-19: render.yml: earshot sound check after Finalize on full renders (user asked to run it on the render
  machine, not the PC). earshot pinned to 4ac3d2a (0.4.1, MIT), models cached as earshot-0.4.1-v1; writes
  sound_measure.json/.txt (LUFS, true peak), sound_timeline.json/.txt (listening transcript, sync to cuts) and
  sound_sheet.png into the release; continue-on-error, 30 min cap. First real test: the Netherlands full render.
  Local clone for reading only: C:\projeler\earshot.
- 2026-11-19 (evening): user asked for stronger hooks / curiosity (memory script-engagement updated). Netherlands
  narration: cold open on the 1953 barge (paid off in ch. 4), teasers, chapter-end bridges, mid re-hook, ask card
  "Would you live on the old sea floor?"; 2,770 words. Storyboard 44588904220 reviewed (21 sheets): fixed
  Maeslantkering coords (was Maasvlakte), close views >= 0.08 deg (0.035-0.06 blurry), no bare push on painted maps
  (engine fits the region, a move without it jumped in), cloudy Flevoland. FULL RENDER = run 44596070222 (first
  earshot sound check). NEXT: fetch -Delete, frame_audit, all sheets, sound_* files, approve, upload
  --publish-at 2026-11-22T23:00:00Z.
- New pipeline options (user: "4ünü de ekle, sonraki videoda hepsini deneriz"), all OFF by default:
  sfx_bank "earshot" (stereo designed effects), music "library" (music/library/<mood>/, beds from music_gen.yml =
  ACE-Step 1.5 MIT, CPU), photo_upscale (Real-ESRGAN x4plus BSD via spandrel, 600-1400 px photos), photo_motion
  "parallax" (Depth Anything V2 SMALL only = Apache; ParallaxPhoto.tsx CPU canvas), map_relief (ASTER relief
  soft-light over satellite). Tests: music_gen run 44596331171 (calm, 60 s), feature-test render 44596802494 (no
  relief yet; relief committed after). Untested until those finish.
- 2026-11-19 (night): Netherlands FULL RENDER 1 = run 44596070222 (15:57, -14.4 LUFS, peak -0.7 dBFS; earshot files
  in the release folder). Fetched, release deleted, frame_audit done. Sheets 1-20 viewed; NOT approved yet. Fixes
  found so far: (1) 2:11 stat "500 BC" counts up ("459 BC") -> years with BC/AD must not count (timeline count_up);
  (2) 7:46-7:54 and 8:20-8:26 ZZ wide map (Zuiderzee) is dark, blurry Blue Marble for ~9 s, nothing painted ->
  paint the former Zuiderzee (geo) or give the wide views a clear MODIS date; 9:02 and 9:38 SW maps also dark.
  Sheets 21-32 still to view. Then fix, render 2, audit, approve, upload --publish-at 2026-11-22T23:00:00Z.
- Cover for Netherlands = cover.jpg made by tools/cover_photo.py ("THEY SANK THEIR OWN COUNTRY", Zaanse Schans CC0);
  user's choice; future covers = curiosity photo covers (memory thumbnail-style). Kansai/old videos untouched.
- Running: music_gen run 44598481947 (3 moods x 2 x 150 s), feature-test render 44598395837 (relief + parallax +
  upscale + earshot sfx). Report both to the user when done.
- 2026-11-20 (early UTC): render 1 audit complete (all 32 sheets). Only 2 issues -> fixed: BC/AD years never count
  (timeline.count_up), wide unpainted maps get MODIS 2025-06-30 (CLEAR_DAY in build_script). RENDER 2 = run
  44608226546. NEXT: fetch -Delete, frame_audit, check 2:11 (500 BC), 7:46-8:26 (Zuiderzee), 9:02, 9:38, 14:08,
  15:03 maps, then --approve and upload --publish-at 2026-11-22T23:00:00Z (cover.jpg already the user's choice).
- 2026-11-20: feature-test 1 (44598395837): upscale OK, earshot OK, parallax never triggered (only cover photos).
  Fixed: parallax also for framed photos (ParallaxPhoto framed mode). feature-test 2 running (also first map_relief).
- 2026-11-20: music_gen 44598481947 OK: 6 ACE-Step beds (calm/curious/tension x2, 150 s) in
  Videos\yt-pipeline\music-candidates\music-beds\<mood>\ (artifact deleted). User listens, good ones -> music/library/<mood>/.
  Netherlands UPLOADED 2026-11-20: render 2 audited (32 sheets) + approved, https://studio.youtube.com/video/oz6fFSsriRw/edit, publishAt 2026-11-22T23:00Z, cover B set. TODO user: pin comment by hand. Feature test 2 fetched (-Delete): framed parallax renders correctly.

## 2026-11-20 — Venice (venice-sinking): script ready, storyboard running
- Topic chosen by user from radar (Venice PASS, 4 videos at 3x). New skill baoyu-youtube-transcript installed (user: "YouTube agent");
  5 competitor transcripts -> episodes/venice-sinking/competitors.md (edge: maps/satellite, the river diversions, MOSE trade-off).
- research.md (47 OK rows; CPSM flood table, MOSE log row 37 read by eye: 173 cm CNR / 204 Malamocco), visuals.md
  (Landsat 2002 vs S2 2025 at the Lido inlet = MOSE island wipe; no S2 on 22 Nov 2022).
- Narration 2,671 words (~16.8 min), build_script.py 236 shots, photo_upscale ON (1966 archive photos 900-1200 px),
  factcheck 185 rows (181 verified, 4 own), episode_check OK.
- Storyboard run 44755829540. NEXT: fetch sheets, review, full render, frame_audit, cover_photo ("THE SEA IS WINNING"), upload.
- Leftover: empty folder chain C:/c/Users/... from a path slip (files moved; safety check blocked rm), user to delete.
- Storyboard 1 failed (portrait MOSE diagram soft after upscale -> landscape panel; episode_check now flags upscales under
  1600 px wide). Storyboard 44759303949 OK, 15.8 min (949.9 s). Review of 23 sheets: NADR/scirocco unpainted views were
  cloudy on MODIS 2025-07-12 -> CLEAR_DAY 2025-08-10 (scored Jun-Sep 2025 against GIBS, cloud-free over Adriatic + Italy);
  chart units spaced (" million m³", " cm"); two MOSE photo labels made accurate; stat source named.
- Full render run 44770324546. Cover: cover_photo.json (November in Venice, "THE SEA / IS WINNING").
  NEXT: fetch -Delete, frame_audit, approve, upload date from the user (23:00 UTC).
- Render 44770324546 audited (32 sheets): clouds gone; one label error (Zattere photo called St Mark's Square, x2) ->
  fixed, factcheck row 95 updated. Render 2 run 44776122744. User chose upload 2026-11-23T23:00:00Z (24 Nov 02:00 TR).
- Venice UPLOADED 2026-11-20: render 2 (44776122744) audited 32 sheets + approved; https://studio.youtube.com/video/msZ2iXpOyEA/edit,
  private, publishAt 2026-11-23T23:00Z (24 Nov 02:00 TR), photo cover "THE SEA IS WINNING" set. TODO user: pin comment by hand.

## mississippi-old-river: "Why the Mississippi Wants to Leave New Orleans" (started 2026-11-20)
- Demand PASS (5 videos at 3x). competitors.md (5 transcripts), research.md (Corps brochure 2009 + Fisk 1952 read in
  full, NASA EO, USGS SIM 3381, USACE sill releases, NPS), outline.md, visuals.md (35 Commons searches, satellite tests:
  Old River 1985->2025 and Atchafalaya/Wax Lake deltas 1986->2025 wipes are strong; Morganza 2011 Landsat cloudy).
- Own measurement reused from louisiana-land-loss/landloss.json: deltas +115 km² 1985-2026 = 2.8 km²/yr (= LSU/NASA).
- Script 2026-11-21: 2,665 words, 8 chapters, 214 hand-placed shots; episode_check OK (16.9 min est.); 18 soft photos
  replaced (all NARA 1973 DOCUMERICA scans fail detail 0.65 -> exact-text quote cards + Landsat 1973 + maps);
  factcheck 184 claims (177 verified, 7 own, 0 FIX). CLEAR_DAY 2025-10-14 (MODIS, scored Sep-Nov 2025).
- Storyboard run 44878550992. NEXT: review sheets, full render, audit, cover_photo.json, upload date from the user.
- Render 44881792324 (15:47) fetched -Delete, audited 32 sheets + approved (flags = count-ups/crossfades). Description
  wording made accurate ("one of the few parts of the coast still growing"). UPLOADED 2026-11-21:
  https://studio.youtube.com/video/DQ2vDBnWafM/edit, private, publishAt 2026-11-24T23:00Z (25 Nov 02:00 TR), photo cover
  "IT WANTS / OUT" set. TODO user: pin comment by hand.

## florida-big-bend: "Why Almost Nobody Lives on Florida's Big Bend Coast" (started 2026-11-21)
- Demand PASS (214x, 185x, 28.8x). competitors.md (4 transcripts), research.md pass 1+2 (NHC TCRs Idalia/Debby/Helene,
  Cedar Key gauge 1914-2025 annual maxima = own chart, ETOPO shelf measurement = own, Census 2024, USGS OFR 01-303,
  FDEP preserve, UF Florida Museum barge canal, GP Foley mill), outline.md = gate-1 draft (~2,700 words, 6 parts).
- GATE 1 APPROVED by the user 2026-11-21 (title, cover words, 6 parts as in outline.md). Open before script: karst source (USGS/FGS), St Marks NWR (USFWS), photo licences
  (Florida Memory / LOC), night-lights view, S2 before/after Helene. Then visuals.md, narration, build_script, factcheck.
- 2026-11-21: research pass 3 (St Marks NWR = USFWS, Wakulla = NWFWMD, NOAA NOS surge definition; Florida State Parks /
  Florida Memory / FWC 403 -> railroad date, pencil mills, Tampa census only attributed), visuals.md (Commons sheets,
  S2 tests: Cedar Key low tide 2025-01-25, Keaton/Horseshoe pre/post Helene moderate), geo/make_regions.py (ETOPO
  shallower-than-10 m shelf 26,985 km2, coast strip), narration 2,718 words (cold open on the Cedar Key gauge),
  build_script.py 235 shots, episode_check OK (~17.1 min est.), factcheck 175 rows (133 verified, 33 own, 9 attributed, 0 FIX).
  CLEAR_DAY 2025-04-17 (MODIS, by eye). Storyboard run 44908368320. NEXT: review sheets (check MODIS 2024-09-26/27/28
  views, post-Helene S2 dates, Landsat 1985 summer canal), full render, frame_audit, cover_photo.json, upload date from user.
- Storyboard 3 (44910042528) OK after two stops (canal wipe cut at real pace): 15.7 min (941.5 s). Review of 23 sheets ->
  fixed: SPRING window 04-10..05-31 (March scenes purple), Pensacola push into open sea, duplicate lighthouse photo,
  MODIS swath gaps (FL painted; Helene 26/27 Sep views moved; P32 MODIS 27 Sep, not 28 = cloudy), cloudy 1985 canal Landsat
  dropped. FULL RENDER = run 44912685105. NEXT: fetch -Delete, frame_audit, all sheets, approve, cover (cover_photo.json
  = St Marks lighthouse, NO BEACH / NO TOWNS), ask the user for the upload date (23:00 UTC slot).
- Render 1 (44912685105, 15:41, -14.4 LUFS) fetched -Delete, audited 32 sheets, NOT approved: April-May Sentinel made the
  sea purple with seams (fixed: SEA = March 2025 window on 20 sea-heavy views, scratch bbsea.py), ending night view off the
  Big Bend (9 s black), Helene 26 Sep swath corner, 1884 bird's-eye shown twice (grey copy), short document card.
  RENDER 2 = run 44917500417. NEXT: fetch -Delete, frame_audit, check sea views / ending, approve, ask upload date.
- Render 2 (44917500417) fetched -Delete, audited: sea views fixed, ending fixed; one seam left on the canal 0.45/0.7 views.
  User (2026-11-21): fix it (render 3) and schedule upload 2026-11-25T23:00:00Z. Canal views -> single day 2025-01-25
  (seamless, scratch canal/sheet.jpg). RENDER 3 running. NEXT: fetch -Delete, frame_audit, check 9:45-10:00, approve,
  `python tools/yt_upload.py florida-big-bend --publish-at 2026-11-25T23:00:00Z`, verify via API.
- 2026-11-21: Render 3 (44924820062, 15:43) fetched -Delete (release deleted), all 32 sheets audited, canal 9:47-9:59 seamless;
  approved (--accept-flags: cross-fades/fade-ins). UPLOADED: video DcTptiHYqZQ, private, publishAt 2026-11-25T23:00:00Z
  (26 Nov 02:00 TR), photo cover "NO BEACH / NO TOWNS" set. Pin the comment by hand in Studio. Florida Big Bend DONE.
- 2026-11-21: Next topic = Permian Basin / West Texas (user chose West Texas first, Florida Keys after it; docs/topic-candidates-2026-11-26.md). topic_radar hit the daily search quota (429). episodes/permian-basin/research.md: round-1 facts + gate-1 outline (~2,750 words, 7 chapters). NEXT: demand check after quota reset, user approves outline (gate 1), "To read next" list.
- 2026-11-21: Permian gate 1 APPROVED by the user. research.md rounds 2-3 (NPS peak, basin size, 2022 quake, Wink Sink 2, Midland/Odessa, Great Dying, PUF 1876/1883, Loving County, flaring). drafts/narration.md 2,898 words, 7 chapters + hook. NEXT: demand check (quota), photos (Commons/NPS/LoC), geo regions (basins, reef), build_script from florida-big-bend, episode_check, claim_log/factcheck, cover_photo.json, storyboard.
- 2026-11-22: Permian: photos chosen (visuals.md), EIA 2017 shapefiles -> geo/*.geojson, build_script.py (240 shots), episode_check clean (18.3 min est.), factcheck.md 143 rows (139 verified, 4 attributed, 0 FIX), USGS event tx2022wmmd: quake ~24 mi from Mentone (narration fixed), cover_photo.json (pumpjack, 48% OF U.S. OIL FROM HERE). Storyboard render started. NEXT: storyboard review, fixes, full render, audit, upload slot (ask user).
- 2026-11-22: Permian storyboard (run 44953344086; first run failed on a soft upscaled NASA photo -> small archive photos replaced) reviewed, 23 sheets: fixed painted-map steps that filled the screen, chapter starts on stat cards (P3, P20), a 2-day seam (P27 -> single day 2025-10-03), pine-forest flare photo, Wink map without the EIA reef band (Wink lies outside it). factcheck 141 rows, 0 empty, 3 attributed. FULL RENDER started.
- 2026-11-22: Permian render 1 (44955661669, 17:02) fetched -Delete, all 35 sheets audited: map steps still filled the screen (maps.py fits the base view to the highlight, so step spans must be wider than the fitted view: now 7.5-16), near-duplicate Guadalupe photos swapped, Midland map label (shows 1930). Audio clean. Upload slot chosen by user: 2026-11-27T23:00:00Z. RENDER 2 started.
- 2026-11-22: Permian render 2 (44982545488, 17:02) fetched -Delete, changed parts re-audited, approved. UPLOADED: video DY9tPP97kDo, private, publishAt 2026-11-27T23:00:00Z (28 Nov 02:00 TR), photo cover "48% OF U.S. OIL FROM HERE". Pin the comment by hand. Demand check still not run (search quota). NEXT topic: Florida Keys (user: after West Texas).
- 2026-11-22: Keys research started: the 238-288x lead was the Chesapeake Bay Bridge-Tunnel video, not the Keys (transcript). User: wait for the demand check (both topics), then choose. Background job runs topic_radar --check after the quota reset (~08:06 UTC). Seeds: docs/topic-seeds-keys-chesapeake.md.
- 2026-11-22: Permian RESCHEDULED to 2026-11-26T23:00:00Z (27 Nov 02:00 TR) at the user's request: TR 27 Nov was empty. Schedule (UTC 23:00): 22 Netherlands, 23 Venice, 24 Mississippi, 25 Big Bend, 26 Permian. Demand check done: Chesapeake PASS (20 at 3x+, TitanFold 420x), Keys PASS but mostly off-topic hits; user chose CHESAPEAKE BAY BRIDGE-TUNNEL (slug chesapeake-bay-bridge-tunnel). Rival transcripts read -> competitors.md; angle: impact crater + drowned Susquehanna valley + sinking Hampton Roads, then the crossing. Next: research.md round 1 (USGS crater, NOAA Sewells Point, CBBT history, ship strikes), then gate 1.
- 2026-11-22: Chesapeake GATE 1 APPROVED (user). research.md rounds 1-3 (USGS crater, NPS bay formation, NOAA sea-level API own ranking: Sewells Point fastest of 23 long-record Atlantic gauges, CBBT gauge 2.42 in/decade since 1975; CBBT history/news, HRNM Yancey account, CBBT wind rules). drafts/narration.md 2,820 words, 7 chapters + hook/ending; weak facts attributed (Navy objection, 1962 damage, 7 deaths). NEXT: visuals.md (Sentinel views of the 4 islands and portals, crater/bay maps, Commons/NARA/LoC 1960s photos, NOAA chart), geo regions (crater ring, channels), build_script.py from permian helpers, claim_log, episode_check, storyboard.
- 2026-11-22: Chesapeake build_script.py 239 shots (121 map, 70 photo, 47 stat, 1 chart), episode_check clean (17.8 min est.), factcheck 160 rows 0 empty (17 attributed, 16 own), visuals.md, cover_photo.json ("THE ROAD GOES UNDER" on the tunnel-portal photo). Narration softened: "the big ships reach the Atlantic through one deep, dredged path"; anchor "lost long ago" (date unknown). STORYBOARD run 45026618250 started.
- 2026-11-22: Chesapeake storyboard 1 (45026618250, artifact deleted) audited, all 25 sheets: wide views cloudy on 2025-10-31 (date rule removed: default basemap), Cape Charles-area views -> 2025-10-16, crater label from geojson ("CRATER_OUTER" fixed), band photo (CVN 69 file) replaced, chapter-start stat (P17), 5 captions, near-duplicate trestle photo, chart 2 s -> ~5 s. episode_check clean, factcheck 0 empty. FULL RENDER next.
- 2026-11-22: Chesapeake render 1 (45030289629) LOST: mp4 download failed and fetch_episode deleted the release anyway -> fetch_episode.ps1 now checks every asset's size before deleting. Render 2 (45032623924) fetched, all 32 audit sheets looked at: clouds on the Cape Charles views (2025-10-16) -> 2025-10-21 (tested clear, scratch cbsat2.py), "sabotage" map recentred on Norfolk, Gulf step into empty ocean removed. Duration 935 s (15.6 min), -14.4 LUFS. RENDER 3 next.
- 2026-11-22: Chesapeake render 3 (45036174298) fetched (size-checked), changed parts re-audited, approved. UPLOADED: video CN8g4i3Hq14, private, publishAt 2026-11-27T23:00:00Z (28 Nov 02:00 TR), photo cover "THE ROAD GOES UNDER". Pin the comment by hand ("Should the next tunnel be built for today's sea, or the sea of 2100?"). Schedule (UTC 23:00): 22 NL, 23 Venice, 24 Mississippi, 25 Big Bend, 26 Permian, 27 Chesapeake. NEXT: topic research (Florida Keys stays a candidate; not right after Big Bend).
- 2026-11-22: Next topic: radar + demand checks (docs/topic-candidates-2026-11-22.md); user chose RUSSIA'S FAR EAST (slug russia-far-east). Rival transcripts read (Unlikely Latitudes 385x covers most of the story) -> our angle: the climate paradox (Vladivostok vs Nice at 43 N, Siberian High, Okhotsk ice). Research round 1 in research.md. GATE 1 APPROVED by user. NEXT: research round 2 (Rosstat/Demoscope 1989 tables, NOAA normals, NASA EO Okhotsk, Britannica Siberian High/treaties, BAM, hectare, China NE census, USGS pt25210002, permafrost extent), then narration.
- 2026-11-22: Russia's Far East research round 2 done (1989 census table decoded from Demoscope: Magadan -65 %, Chukotka -70 %, Kamchatka -37 %, Sakhalin -34 %; NASA EO Okhotsk "lowest latitude for seasonal sea ice"; USGS us6000qw60 M8.8; NBS NE China 98.5 M; hectare 151,103 by Aug 2025). Not confirmed, kept out: permafrost share of Russia, BAM cost/volunteer counts, hectare ownership rule. drafts/narration.md written: hook + 8 chapters + ending, 2,952 words. NEXT: visuals.md, Sentinel date tests, Commons photos, build_script.py.
- 2026-11-22: Russia's Far East: visuals (Commons search, MODIS/Sentinel date tests: Okhotsk ice 2024-03-08 vs open 2024-09-15, Amur Bay frozen 2024-01-20), geo/make_regions.py (FEFD, China NE, 1858 approx., Primorye), build_script.py 243 shots, episode_check clean (18.7 min est.), factcheck 157 rows 0 empty (133 verified, 20 own, 4 attributed), cover "SAME LATITUDE AS NICE" on Abashiri drift ice. STORYBOARD run 45069171028 started.
