# What the watched "why nobody lives in ..." videos do (2026-11-13)

Asked by the user: study watched videos and update how we make ours. Read from public pages only (captions and the
scrubbing previews, one frame every ~10 s); nothing downloaded. Scripts in the session scratchpad (ref.py, sb.py).

| Video | Length | Words | Words/min | Picture changes per 10 s step | Brightness | Saturation |
|---|---|---|---|---|---|---|
| Geography By Geoff, "Why Almost NOBODY Lives On Australia's West Coast" (10.6 M views in 44 days) | 15.2 min | 2,762 | 181 | 0.98 | 62 | 124 |
| Land & Consequence, "Why Almost NOBODY Lives On Florida's Big Bend Coast" (133 K, 529 subscribers) | 16.6 min | 3,062 | 184 | 0.97 | 118 | 76 |
| GeoLex, "Why Almost Nobody Lives In Northern Idaho" (336 K) | 20.2 min | 3,773 | 187 | - | - | - |
| Ink & Orbit, louisiana-land-loss | 15.9 min | 2,343 | 147 overall (168 while speaking) | 0.99 | 57 | 99 |

## The hook is one template (all three)
1. A scale fact about a place everybody knows ("the second largest administrative division on Earth").
2. "But" + the surprise ("it is exceptionally empty").
3. Two or three concrete teasers of what is coming (rivers that vanish underground, a town of a thousand people).
4. The question, said aloud, by 0:30 ("So why is ... still almost completely empty?").
5. One line of promise, then straight in: "The first reason why ... is ...".
The body is a numbered list of reasons (4-6), each a small story with its own map and pictures, not a chronology.

## Pictures
- Geoff: the same dark satellite globe we use, but every subject region is painted in ONE solid bright colour
  (red, mint, orange) with thick labels lying on the map, the camera tilted; real ground photos in white frames between
  map shots; a presenter. Brightness is no higher than ours: the solid regions and big labels carry the picture.
- Land & Consequence (no presenter, closest to us): about 60 % ground-level and drone pictures, old engravings and
  archive photos; light-background diagram cards (a state outline with one number, a cut-away block of ground, a
  simple cross-section); few plain map shots.
- Ours: 90 % close satellite views. Sharp and bright enough now, but a viewer never sees the place from the ground
  and the map never says "this region" in colour.

## What changes in our production (applied the same day)
- Map: `highlight: ["Western Australia@red"]` paints a region solid (accent | alt | red | blue | neutral) with a white
  edge (pipeline/maps.py, MapBlock.tsx). Every "reason" opens on such a painted map.
- Pictures: at least a third of the shots are ground-level photographs of the place (Commons / NASA / government,
  licence-checked), in frames, spread through the video; satellite close views are the evidence, not the filler.
- Script: the hook template above; the body as numbered reasons; 2,750-3,000 words.
- Still to decide with the user: narration speed (we speak at 168 wpm, the references at 181-187).

## Skills looked at
find-skills listing reviewed on 2026-11-04 (docs/channel-analysis-2026-11.md); nothing new found that draws maps or
edits Remotion scenes better than our own engine. The gap is in our rules and engine, so the rules went into
`episode-plan` and `cover-map` instead of a new third-party skill.
