# Script rules (from docs/channel-analysis-2026-11.md, approved 2026-11-04)

These add to the standing rules (two-sided questions, retention bridges, one content-tied subscribe line, no generic
end CTA, the closing question as the pinned comment, never bend facts).

## Hook (first 30 s)
1. Sentence one carries tension or a curiosity gap, not a description ("Something strange is happening...",
   "a powerhouse, but with a fatal flaw").
2. A scale anchor the target audience knows (the Caspian laid over the United States; "enough water for X homes").
3. A "but" turn within about 15 s.
4. The video's question or promise said aloud by 0:30. Visual proof (a before/after wipe) belongs in the first 15 s.

## Body
- Re-hook at every chapter turn: an open question the chapter answers, said in our voice (no stock phrases such as
  "here's where it gets interesting"; the humanizer pass removes them).
- Set up, then pay off: name the number or the turn early, show it later.
- Second-best point first, best point second.
- A new picture at least every 8 s: a cut, a map step (place, route, highlight, compare), a question card or a new
  shot type. prepare prints "holds ... without a cut, map step or question" for every longer stretch; fix them all
  before the storyboard.

## Real pictures only (the user's decision, 2026-11-05)
- No stock footage or images and no AI images in episodes: every shot shows the real place, thing, person or data.
  The schema rejects `stock` and `ai_image` shots unless a script carries `legacy_stock` (episodes made before).
- Sources, in this order: our own satellite views (Sentinel-2, Landsat back to the 1980s, MODIS), maps, charts and
  cards; public-domain photos and film of the subject itself (US federal agencies, NARA, the Library of Congress,
  Commons PD / CC0 / CC BY; tools/find_media.py); documents.
- A sentence that cannot be shown with a real picture gets rewritten around something that can be shown.
- Gate 1 shows the visual inventory with counts (archive photos and film, satellite views, own graphics) and the word
  budget: 15-20 minutes is 2,300-3,000 words at our pace; say so when the research cannot carry that.

## Shot types to mix in (R2)
- `stat`: one big number on its own screen, for the two or three figures the video turns on.
- `document`: a public-domain page (U.S. federal PDFs) with the key line marked, or a `text` clipping card for a
  short quote from a copyrighted source. Never screenshot a news page.
- `film`: public-domain archival film from Wikimedia Commons (NARA, NASA, Reclamation), checked like photos.
- Map places take `icon` (22 Lucide icons); routes glow.
- `chart.reveal`: anchors for the last items of a chart, so each bar / point appears when the narration says its
  number (each reveal counts as a beat). Order the data in narration order when the chart is built this way.
- `compare.until`: the 'at' of a later step in the same map shot; the 'before' image holds through the steps in
  between (labels, icons, no camera moves) and the wipe starts there. Use it to put a label on the before image
  without starting the wipe early.

## Beats, as the Colorado River remake did them (2026-11-05)
- Write a beat where the narration names something: a place appears on its word, a bar on its number, a quote card
  when the quote is spoken, a stat card for a number the chapter turns on.
- Long quotes: start the clipping card a few words before the highlighted phrase (the marker sweeps about 2 s in).
- Questions to the viewer: one or two quick cuts under the question card.
- `holds` notes come from prepare; while writing, an estimate at about 0.4 s a word (150 words/min) keeps every
  stretch under about 16 words.

## Packaging
- Title 35-50 characters: a question or stakes, plus a name or a number; yt-package scores the pairing.
- Thumbnail: our own imagery first (variant D, the before | after split when the episode has a compare), 1-3 words,
  a consistent template (amber wipe line). AI variants A-C are the fallback.

## Pace
- Narration speed per episode (`voice_speed`); similar channels run 165-185 words/min, ours ran about 136 at 1.0.
  Choose by ear from the pace samples (render.yml `pace_samples`).

## After each upload
- Export the Studio retention report; yt-retention finds the dips; "Intro" (share still watching at 30 s) is the
  first number to watch.

## Length, transitions and photos (the user's review of episode 6, 2026-11-08)
- Every long episode runs 15-20 minutes: about 2,000-2,700 words at our pace. The topic is chosen with that
  estimate (`tools/episode_check.py --words N`); a subject that cannot carry it gets a wider scope, never filler.
  prepare stops a render outside 15-20 min (episodes made before carry `legacy_length`).
- `python tools/episode_check.py <slug>` before every storyboard or render: length, wipes cut off by the next
  shot, holds over 6.5 s, photo quality. prepare repeats the length and wipe checks on the real narration.
- Dated views of one place are chained `compare` wipes; consecutive wipes cut straight from one to the next.
- A wipe needs its `seconds` + 1 s before the next cut.
- No "CHAPTER N" cards: the title shows as a small tag over the chapter's first picture (`card: true` brings a
  full card back for one chapter).
- Photos: soft or upscaled files are refused (detail ratio < 0.65, or under 1,400 px); hazy astronaut photos get
  a levels stretch; NASA images are taken from the original file, not the 1,920 px rendition.
- Fact-check before the storyboard: `python tools/claim_log.py <slug>` lists every claim into
  episodes/<slug>/factcheck.md; each gets verified / attributed / own, none may stay FIX (skill: fact-check,
  adapted from jamditis/claude-skills-journalism, MIT).

## From the retention curves (read 2026-11-08: episodes/gerd-nile/retention.md, colorado-river/retention.md)
- After the hook, no background lecture: in gerd-nile half of the viewers still there at 0:30 left by 2:34, during
  a geography chapter; colorado-river lost 43 % -> 14 % at the same kind of turn. The first two minutes after the
  hook carry the conflict or a measured surprise; geography comes later, one fact at a time.
- No spec dumps: a paragraph of five dimensions in a row (gerd-nile 7:42) lost a third of the remaining viewers.
  One number per point, always with what it means.
- Viewers who pass the middle stay to the end (gerd-nile flat from 8:30): the fight is the first 3 minutes.
- Episodes with fewer than ~50 views give no usable curve; reach (title and thumbnail) is the bigger problem
  while views stay that low.

