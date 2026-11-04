# Similar channels: packaging, structure, materials (2026-11-04)

Asked by the user: analyse channels like ours (videos, transitions, materials, how they are made, thumbnails), find
skills worth installing, and shape our production so viewers stay. This file holds the evidence; the plan is at the end.

## Method
- Read public pages only. No video or audio was downloaded: channel "Videos" tabs (titles, lengths, views),
  thumbnails (mqdefault), YouTube's scrubbing previews (storyboard sprites, one frame every 10 s, 160 x 90),
  auto-captions (youtube-transcript-api), chapters and "most replayed" markers. Scripts and sheets stay in the
  session scratchpad (`yt/tools/channels.py`, `yt/tools/videos.py`).
- 11 channels, the 30 newest long videos each; 8 sample videos measured in depth, two of them on our own topics:
  RealLifeLore "Caspian Sea Situation Is Insane" and Wendover "California's Water Problem".
- "Change ratio" = share of 10-s preview pairs whose picture changed (mean abs difference > 12 on 64 x 36 grey).
  Our own videos were measured the same way from the delivered MP4s.

## Numbers (newest 30 long videos per channel)

| Channel | Subs | Median length | Median views | Title length (median chars) | "Why/How..." titles |
|---|---|---|---|---|---|
| RealLifeLore | 7.93M | 32 min | 1.15M | 46 | 19/30 |
| Wendover Productions | 4.92M | 19 min | 1.05M | 33 | 18/30 |
| Johnny Harris (on camera) | 8.01M | 43 min | 3.6M | 36 | 12/29 |
| Real Engineering | 5.12M | 23 min | 1.6M | 38 | 10/30 |
| fern | 5.65M | 28 min | 4.0M | 34 | 6/30 |
| Mustard | 2.4M | 13.5 min | 6.9M | 37 | 10/30 |
| Economics Explained | 2.89M | 18 min | 572K | 44 | 15/30 |
| PolyMatter | 1.93M | 19 min | 286K | 36 | 19/30 |
| CaspianReport | 1.85M | 16 min | 312K | 34 | 21/30 |
| Geography by Geoff | 1.13M | 17 min | 618K | 44 | 19/30 |
| Kraut | 602K | 23 min | 294K | 32 | 4/30 |
| **Ink & Orbit** | 771 | 16 min | 56 (GERD, day 1) | 52 | 0/2 |

Sample videos:

| Video | Length | Words/min | Change ratio | Chapters | Sponsor read |
|---|---|---|---|---|---|
| RealLifeLore, Caspian Sea Situation Is Insane | 19:13 | 176 | 0.89 | 9 | end (17.3 min) |
| Wendover, California's Water Problem | 19:35 | 186 | 0.96 | 11 | end (Nebula) |
| Geography by Geoff, Kenya | 18:51 | 176 | 0.98 | 4 | 5.6 min |
| fern, NATO's Plan for War With Russia | 17:32 | 164 | 0.92 | 0 | 3.4 min |
| Mustard, The Navy's Secret Plan For WW III | 15:18 | 137 | 0.96 | 0 | 14.6 min |
| PolyMatter, Why the Average New Car Costs $50,000 | 16:28 | 130 | 0.96 | 10 | 14.9 min |
| Johnny Harris, The REAL reason China built so much | 50:25 | 174 | 0.91 | 10 | none |
| **Ink & Orbit, colorado-river** | 17:04 | ~136 | **0.72** (longest still stretch 30 s) | 8 | none |
| **Ink & Orbit, caspian-sea** | 15:52 | ~130 | **0.71** (60 s) | 8 | none |
| **Ink & Orbit, gerd-nile** | 15:54 | ~125 | **0.83** (20 s) | 7 | none |

## Titles
- Short: median 32-46 characters (ours 46-59). Curiosity or stakes, often a question word: "Caspian Sea Situation Is
  Insane", "California's Water Problem", "Why the Average New Car Costs $50,000". Numbers and ALL-CAPS words are rare.
- RealLifeLore covered our Caspian topic (0.66M views) with a 31-character title and a 2026 | 2050 split-map thumbnail.

## Thumbnails
- Each channel keeps one template, recognisable at feed size:
  - RealLifeLore: saturated relief map, subject in red, big white arrow or red ring, 2-3 words with one highlighted
    ("IT'S OVER", "600,000 PEOPLE LIVE HERE"), meme faces now and then.
  - Geography by Geoff: the same yellow-land / blue-sea map every time, subject solid red, a curved white arrow,
    1-2 dramatic words ("NATURE'S GLITCH", "UNLIVABLE"), globe logo in a corner.
  - Wendover: photo composites, logo top left, a diagonal colour stripe in the corner, 3-5 word headline.
  - CaspianReport: cut-out leaders over grey maps, two words on a yellow bar ("THE IRAN PARADOX").
  - PolyMatter: editorial graphics with logo; fern: dark cinematic objects with one red word ("HACKED");
    Johnny Harris: his face plus a dollar figure.
- Common rules: one focal point, 1-3 words, strong colour contrast, the map itself as the picture in map channels.
- Ours: AI canyon images plus "WHO GETS CUT?"; no map, no real imagery, no template. We own real before/after
  satellite views that this niche's thumbnails imitate. Thumbnail D for colorado-river (2019 | 2026 split from the
  cold-open wipe, amber line, the same three words) is built from them.

## Hooks (first 30 s)
- RealLifeLore: "Something strange is happening right now in Central Asia that has so far escaped most of the world's
  attention." Then the sea placed over the United States as a scale anchor, then the loss.
- Wendover: "California, by just about any metric, is a powerhouse. But it's also a state with an inherent and perhaps
  fatal flaw." Then "Just look at..." on screen and the thesis in one line by 0:25.
- Geography by Geoff: situation, "But Kenya also has a plan", then the video's two questions said aloud by 0:30.
- Mustard: in medias res, "In 1955, this was America's nightmare." fern: "There are new American intelligence
  reports, and they are deeply worrying." PolyMatter: a counter-intuitive figure.
- Ours (colorado-river): a strong visual proof in the first 15 s, but the stakes and the question arrive about 1:00.
- Pattern: tension in sentence one, a relatable anchor for the audience, a "but" turn, the promise or question by 0:30.

## Pictures, materials and transitions
- RealLifeLore (Caspian): about 45 % maps (dark satellite base like ours, subject red or teal, glowing route lines,
  inset comparisons), 40 % drone/stock footage, 10 % charts and real documents with yellow highlights, dated satellite
  images; sponsor read at the end.
- Wendover (California): about 65 % footage, much of it archival film (1950s Los Angeles, aqueduct construction in black
  and white) and on-topic footage (the aqueduct itself, pumping plants, Hoover Dam); 3D tilted satellite maps with
  glowing lines and perspective text; a highlighted document; a pumping-plant elevation profile; a separate flat map
  style for the water-rights section.
- Geography by Geoff: satellite globe base, saturated regions, animated icons on the map (people, ships, flags, mountains
  rising, big numbers), drone footage, presenter segments, a newspaper clipping.
- Mustard: one art direction for everything: archival film with grain, newspaper clippings with highlights, technical
  blueprints, retro maps, reports on a desk, 3D renders.
- Production methods on record: Johnny Harris's maps are After Effects with the GEOlayers plugin and Google Earth Studio
  camera data (PremiumBeat, aescripts case study). None of these tools fit our free, automated pipeline; the looks they
  produce (tilted 3D maps, glowing lines, highlighted documents, map icons) can be built in Remotion.

## Gaps, largest first
1. Visual pace: our picture changes in 71-83 % of 10-s steps, theirs in 89-98 %; our longest still stretches are 20-60 s.
2. Material range: maps, stock, photos and charts only. Missing: archival film, documents with highlights, diagrams
   (profiles, cross-sections), animated map icons, full-screen stat cards, tilted 3D maps.
3. Packaging: long statement titles; AI thumbnails without a map; no channel template.
4. Hook: the stakes and the question come about 30 s later than in the sample.
5. Narration pace: about 136 words/min against 165-185 for RealLifeLore, Wendover, Geoff, fern.
6. Identity: "ink" is in the name and the channel art but not in the videos.

## Plan (proposed, each phase stops for approval)
- R1 (packaging and script, little code): thumbnails from our own imagery in pipeline/thumbnails.py (split from the
  episode's main compare, highlighted map with arrow), one channel template with the amber wipe line; title rule
  (35-50 characters, a question or stakes, a name or number); hook rule (tension line, audience anchor, "but", the
  question by 0:30); re-hooks at chapter turns; prepare warns at 8 s without a picture change (now 14 s); a pace test
  (TTS 1.0 -> 1.08, shorter pauses) judged by ear.
- R2 (new shot types): document cards (pages of public-domain US government PDFs or our own clipping card) with an
  animated highlighter; public-domain archival film (NARA and Prelinger films on Commons and the Internet Archive,
  NASA, Reclamation) through the photo licence checks; full-screen stat cards; glowing route lines; icon markers on
  maps (MIT/ISC icon sets).
- R3 (bigger looks, experimental): tilted map camera (CSS perspective in MapBlock); elevation profile and cross-section
  diagrams (dam intakes, pumping lifts); an "ink" style for diagrams and cards; a CesiumJS terrain flyover test with
  open elevation data (no Cesium ion: its free plan is non-commercial).
- After every upload: the user exports Studio retention; yt-retention reads the dips and "Intro" (share still watching
  at 30 s), and the findings feed the next script.

## Skills
- Installed already: find-skills, humanizer, remotion-best-practices (includes remotion-maps), yt-package, yt-retention.
- Chosen, install blocked by the session's permission check (external code), so the user runs:
  `npx skills add cdeistopened/skill-stack@youtube-scriptwriting -y` (hooks, re-hooks, setups and payoffs; use its
  structure, not its stock phrases) and `npx skills add social-media-skills/skills@thumbnail-design -y` (CLICK
  framework, mobile legibility, A/B plans for YouTube's Test & Compare).
- Not taken: higgsfield-youtube-thumbnail (paid API), charlie947 youtube-thumbnail (needs a creator photo),
  YouTube downloader/transcript skills (against the no-download rule), editing-montage and documentary-montage
  (30 KB each, aimed at ads), video-motion-graphics (After Effects), data-storytelling (business reports).

## Sources
- YouTube channel pages, thumbnails, previews and captions of the channels above (read 2026-11-04).
- YouTube Help, "Measure key moments for audience retention": https://support.google.com/youtube/answer/9314415
- PremiumBeat, "Making maps for Johnny Harris": https://www.premiumbeat.com/blog/making-maps-for-johnny-harris/
- aescripts, "Making maps for Johnny Harris - Volcanoes": https://aescripts.com/learn/making-maps-for-johnny-harris---volcanoes/
- skills.sh listings and the skills' SKILL.md files on GitHub (read before choosing).
