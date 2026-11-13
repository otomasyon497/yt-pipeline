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

The topic decides the views before anything we render (research 2026-11-13: our policy-news topics, "Kansas
Rejected Farmers' Plan to Save Their Water", got 0-13 views with clean videos; a 528-subscriber channel got
133K with "Why Almost NOBODY Lives On Florida's Big Bend Coast"). So every candidate must pass three tests:

- **A place the viewer already knows, one "why".** The subject is a state, coast, sea, city or country a
  general English-speaking viewer can point to, and the question is one they could ask themselves: why is it
  empty, why is it sinking, why does the border bend, why did the city fail. A dispute between agencies is a
  chapter inside such a video, not its topic.
- **Demand:** `python tools/topic_radar.py --check "<topic said one way>" "<said another way>"` must print
  `demand: PASS` (3 comparable videos at 3x their channel's subscribers in a year). Read the titles it lists:
  they must really be about this topic. Show the line with the proposal. A FAIL topic is not offered.
- **Title first.** Write the title before the outline: "Why ..." or "How ..." plus the place, 55 characters
  at most, no date, no agency name, and the number only if it is the surprise. If no such title is honest for
  the material, the topic is wrong. Then the cover idea in one line (`cover-map` skill): which region is red,
  which two words.

Then, for every candidate topic that passes, before offering it:
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

- **Painted maps carry the explanation, satellite views are the evidence.** Every chapter opens on a map step
  with the chapter's region in `highlight` and, where something moves or points, `arrows`; the hook's first map
  repeats the cover's view and red region. Close Sentinel-2 / Landsat views follow as proof. Never more than
  two close satellite views in a row without a painted step, a card, a chart or a photo between them.
- Dark ground (marsh, forest, open water at night-like tones) is not a picture: put a `highlight`, a place label
  or a route on it, or choose a view with settlements, fields or a coastline in it.

### The "why" episode shape (docs/reference-videos-2026-11-13.md)
- **Hook, in this order, question by 0:30:** a scale fact about the known place; "But" + the surprise; two or three
  concrete teasers; the question said aloud; one line of promise; then "The first reason ...".
- **Body = 4-6 numbered reasons**, each a small story (a person, a date, a number), not a chronology. Each reason
  opens on a painted map: `highlight: ["<region>@red"]` (other regions `@alt`, `@blue`), with its label.
- **A third of the shots are ground-level photographs** of the place (Commons / NASA / government; run
  `tools/find_media.py` per reason and keep only files over 1,400 px), in frames, spread through the video. Satellite
  close views are evidence for a sentence, never filler under a sentence about something else or another year.
- **2,750-3,000 words** (the references speak 181-187 words a minute; real narration decides, not the estimate).
- **No filler machinery (user, 2026-11-13: "the same or similar pictures come too often, it gets boring").** Every
  shot is placed by hand under the words it shows (episodes/australia-interior/build_script.py is the model): a photo
  at most twice, a map frame at most twice and 60 s apart (`tools/episode_check.py` enforces both), a new picture
  every 5-7 s. Wide painted maps get a new framing each time (`fresh()`); a single-view map shot held over 16 words
  gets a push-in step instead of a second picture of something else. Long quote cards are cut away from by hand.
- **Painted regions come from data, not from drawing:** `geo/make_regions.py` in the episode (buffers, Natural
  Earth regions) or an official layer (Geoscience Australia drainage divisions); print the areas for the fact check.
- **Dated wide views:** pick clear MODIS days by looking at them first (scratch script against GIBS), e.g. the
  green/brown edge on Goyder's Line (2025-09-02) or a full Lake Eyre (2025-07-12).

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
  problems (the audit also flags `dark` map stretches: fix the view, do not accept them): blurry or empty maps, labels that do not match the words, cards cut off, counters mid-count,
  repeats. Fix, re-render, audit again; then `--approve "what was checked"`. `tools/yt_upload.py` refuses any
  file without an approved audit of that exact render.

- The cover: `cover-map` skill, `cover.json` in the episode folder, cover.jpg checked at 320 px.

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

