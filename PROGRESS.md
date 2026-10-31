# PROGRESS

## Status (Phase 1)
- [x] Repo `otomasyon497/yt-pipeline` (private) created, code pushed
- [x] Python pipeline (TTS, captions, Pexels, Workers AI, audio mix, timeline) written, compile-checked
- [x] Remotion project written, `tsc --noEmit` clean
- [x] Workflow `.github/workflows/render.yml` (workflow_dispatch, input `slug`)
- [ ] Secrets set by user: PEXELS_API_KEY, CF_ACCOUNT_ID, CF_API_TOKEN
- [ ] First end-to-end run on Actions + fixes
- [ ] Measure Actions minutes, report voice samples + final.mp4

## Decisions
- Default voice `bm_george`; `am_michael` + `am_onyx` ~10 s samples are rendered into the artifact (`voice_samples/`).
- AI images: `@cf/black-forest-labs/flux-2-klein-4b` (weights Apache 2.0; accepts width/height 256-1920 so 16:9 is native)
  at 1536x864 (6 output tiles ~ 156 neurons/image). Automatic fallback to `flux-1-schnell` + 16:9 centre-crop.
  Open point: Cloudflare points to BFL Terms of Service for the hosted model and those terms do not
  explicitly cover third-party hosts; weights licence itself is clean.
- 24 fps (20% fewer frames than 30). Render: concurrency 2, jpeg frames, x264 veryfast crf 20, audio muted in
  Remotion and mixed/muxed with ffmpeg; stock clips pre-normalised with ffmpeg; no gradients/blur/shadows in React.
- Remotion licence: free for individuals / companies up to 3 people.
- Pexels uses `/v1/videos/search`; local limiter 150 req/h; search results + clips cached.
- Cache: actions/cache with `assets-<run_id>` + prefix restore; HF models cached separately.
- Test script facts are illustrative (see `sources` in script.json) - fact-check before real use.

## Next steps
1. User runs the three `gh secret set` commands.
2. `gh workflow run render.yml -f slug=nokia-intro`, read `gh run view --log-failed` (last ~100 lines only).
3. Fix failures, measure per-step minutes, report to user, wait for approval before Phase 2.
