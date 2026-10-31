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

## Phase 2 plan (approved decisions, not started)
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
