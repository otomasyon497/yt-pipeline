# PROGRESS

## Status (Phase 1 approved; Phase 2 planning)
- [x] Repo, pipeline, Remotion project, workflow; secrets set by user
- [x] End-to-end run on Actions green (run 41201330118): 1920x1080 / 24 fps H.264+AAC, ~70.6 s, artifact `nokia-intro`
      (final.mp4, credits.txt, voice_samples/ with bm_george, am_michael, am_onyx)
- [x] Measured: job 6m07s (billed ~7 min). Prepare 1m39s (tts 55s, captions 13s, media 14s warm cache, samples 14s),
      Remotion render 2m27s for 1694 frames (~11.5 fps on 2 vCPU), setup (apt+pip+npm) ~1m50s.
      First (cold-cache) run: job ~6m, render 2m52s for 2035 frames.
- Music: /music was still empty on 2026-10-31 (user said tracks were added, none found in the working tree); so the test video has narration only (ducking/mix path not yet exercised with a real track).

## Decisions
- Voice: user chose `am_michael` as default for all episodes (config.DEFAULT_VOICE, schema default). Voice samples are now opt-in (`VOICE_SAMPLES=1`).
- AI images: `CF_IMAGE_MODEL=@cf/black-forest-labs/flux-1-schnell` set in workflow (user chose licence caution over
  flux-2-klein-4b, whose hosted terms on Cloudflare are unclear). Klein code path remains (switch by changing env), unverified in practice.
  schnell: 1024x1024 centre-cropped to 16:9, upscaled to 1080p; no `seed` field accepted.
- 24 fps; render concurrency 2, jpeg frames, x264 veryfast crf 20; audio muted in Remotion, mixed + muxed by ffmpeg.
- Secrets are sanitised (pasted curly quotes broke the Pexels header once) via `config.secret()`.
- Remotion licence: free for individuals / companies up to 3 people.
- Cache: actions/cache `assets-<run_id>` + prefix restore; HF models separate.
- Test script facts are illustrative (see `sources`) - fact-check before real use.

## Known issues / notes for later phases
- Kokoro runs ~1x real time on CPU: a 15-min video needs ~15 min TTS + ~30 min render + captions ~3 min -> close to the
  workflow `timeout-minutes: 60`; raise it (job limit is 6 h) or split TTS/render jobs for long episodes.
- Narration pace is ~2.05 words/s at speed 0.95; budget ~125 words per 60 s plus ~0.9 s per scene overhead.
- spaCy model is downloaded at runtime by Kokoro/misaki (adds ~seconds each run); could be pinned in requirements.
- Remotion preview of stock `Video` from @remotion/media worked in SSR (no OffthreadVideo fallback needed so far).

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
