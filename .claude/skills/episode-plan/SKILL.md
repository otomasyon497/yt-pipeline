---
name: episode-plan
description: >-
  Plan and check an Ink & Orbit episode so it always lands at 15-20 minutes with clean pictures: topic
  proposals with a research-depth estimate, the gate-1 word budget, and the pre-render check
  (tools/episode_check.py: length, cut-off wipes, picture holds, photo quality). Use when proposing a new
  topic, writing an outline or script, before any render or storyboard, and before gate 2.
---

# episode-plan

The user's rule (2026-11-08): every long episode runs **15-20 minutes**, consistently, and never pads to get
there. Episode 6 (NEOM) came out at 10:10 because its sourced material only carried ~1,350 words; that was only
discovered after the topic was chosen. This skill moves the length decision to the start and puts the checks
in code, so nothing reaches the user that fails them.

## 1. Topic proposals (before the user picks)

For every candidate topic, before offering it:
- Sketch the chapters the sources can carry and estimate words per chapter from what is actually findable
  (dated events, numbers, two-sided positions, own measurements). Count only sourced material.
- Run `python tools/episode_check.py --words N` on the total. A topic must reach **2,000-2,700 words**
  (the estimate the tool prints for 15-20 min). If one subject cannot, widen its scope with a natural frame
  (NEOM alone ~1,350 words -> "Saudi Arabia's giga-projects": The Line, Trojena, OXAGON, Sindalah, Red Sea
  Global). Never propose a topic you cannot fill.
- Show the user the estimate with each proposal ("~2,400 words, ~18 min: chapters ...").

## 2. Gate 1 (outline)

- The outline's word budget must pass `tools/episode_check.py --words N`. Show the printed line at gate 1.
- Visual inventory counts include moving evidence: chained Sentinel-2 / Landsat wipes (time series), archive
  film, maps with routes. Photos are checked in step 4.

## 3. Script

- Write to the budget; if a draft falls short, go back to research (another chapter, another measurement),
  not to filler or a slower voice.
- Dated imagery of one place: only as `compare` wipes, chained (2021 -> 2022, then 2022 -> 2023 ...). Two map
  steps of the same view with different `date`s show the same image (rasters stack by size, not by date).
- A wipe needs its `seconds` plus 1 s before the next cut. Give the paragraph enough words after the wipe
  starts, or start it earlier with `hold` / `until`.
- No "CHAPTER N" cards: the chapter title shows as a small tag over the chapter's first picture.

## 3b. Fact-check

Run the `fact-check` skill (tools/claim_log.py -> episodes/<slug>/factcheck.md) once the script is written;
no empty Status and no FIX rows before the storyboard.

## 4. Before every render (storyboard or full)

```bash
python tools/episode_check.py <slug>
```

It must print `OK, ready to render`. It estimates the length from the words (calibrated on episode 6),
lists wipes the next cut would interrupt, stretches over 6.5 s on one picture, and downloads every photo to
refuse soft or upscaled files (hazy ones get a levels stretch automatically). prepare on GitHub Actions
repeats the length and wipe checks on the real narration and stops the render if they fail.

## 5. Before gate 2

- Pull frames around every transition with the scratchpad frames_sheet.py (Remotion's ffmpeg) and look at
  them: map-to-map wipes, chapter starts, the cut after every wipe. The user should never be the one who
  finds a transition glitch.
- Report the real length from the render log (`length: N min`).
- **Every finished render, long or Short, is audited second by second before upload** (the user's rule,
  2026-11-09): `tools\fetch_episode.ps1 <slug>`, then
  `%USERPROFILE%\.yt-pipeline\venv\Scripts\python.exe -I tools/frame_audit.py <slug>`. Look at every contact
  sheet from 0:00 to the end (one frame per second, shot id and spoken words under each), not only at known
  problems: blurry or empty maps, labels that do not match the words, cards cut off, counters mid-count,
  repeats. Fix, re-render, audit again; then `--approve "what was checked"`. `tools/yt_upload.py` refuses any
  file without an approved audit of that exact render.

## 6. After upload (2-3 days later)

The user chose (2026-11-08) to have the curve read from YouTube Studio through Claude in Chrome, read-only:
Studio -> the video -> Analytics -> Etkileşim -> "Kitleyi elde tutma"; hover the chart for (time, %) points.
Map the times to paragraphs with `tools/yt_analytics.py`'s `script_times(slug, real_seconds)` and write
episodes/<slug>/retention.md like episodes/gerd-nile/retention.md. (The API route, `python tools/yt_analytics.py
retention <slug>`, needs a Google Cloud OAuth client the user found too complicated; keep it unused unless asked.)
Under ~50 views the curve is noise: say so instead of drawing lessons.
Read the drops (time, chapter, the narration there), write the "Lessons for the next script" section, and
carry rules that repeat across episodes into docs/script-rules.md. Read retention.md of the last episodes
before writing a new outline.

