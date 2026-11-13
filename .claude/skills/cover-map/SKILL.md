---
name: cover-map
description: >-
  Make the cover (thumbnail) of an Ink & Orbit long video as a painted map: amber land, navy sea, the subject
  in red, one white arrow, one or two words in a box (tools/cover_map.py from episodes/<slug>/cover.json).
  Use when a new episode needs its cover, when the user asks for a more clickable thumbnail, and before any
  long-video upload.
---

# cover-map

Research on 2026-11-13 (222 long videos in our niche since March 2026, ranked by views per subscriber): the
videos that broke out for small channels (Land & Consequence, 528 subscribers, 133K views in 11 days; Explains-it;
Geography By Geoff; The Hidden States) share one cover grammar: a flat bright map, the subject region solid red,
a curved white arrow, one or two words in a box. A viewer sees *where* and *what* at feed size. Our photo covers
(a satellite picture plus two words) never said where; long videos sat at 0-13 views. The template alone does
not make a hit (the same channels' other videos get 100-2,000 views): the topic and title decide first, see the
`episode-plan` skill.

## Steps

1. Write `episodes/<slug>/cover.json` (fields: the docstring of `tools/cover_map.py`).
2. `%USERPROFILE%\.yt-pipeline\venv\Scripts\python.exe tools/cover_map.py <slug>` writes
   `Videos\yt-pipeline\<slug>\cover.jpg`, which `tools/yt_upload.py` uses before any other thumbnail.
3. Look at the file, then shrink it to 320 px wide and look again: that is what the feed shows.

## Rules

- **One subject, in red.** The thing the title is about: a coast strip, a state, a lake, a river corridor
  (`line` with `km`). If two things are red, nothing is. A second actor gets `outline` only.
- **The view shows where.** Wide enough that a viewer recognises the country or coast without a label; the
  subject fills between a tenth and a third of the picture. One `labels` entry at most, a city people know.
- **One or two words, three at the very most**, and they do not repeat the title: the title names the place,
  the cover names the tension ("FORGOTTEN", "RUNNING DRY", "NO WAY OUT"). The second line carries the twist in
  the red box. Words must be readable at 320 px: `text_size` 110-150.
- **The arrow starts at the words and ends on the subject.** It must not cross the label or the words.
- **Honest.** The red area is the real place at its real size, and the words are something the video shows.
  No skulls, no "they lied to you", no "nobody talks about", no faces of real people, no borrowed logos or
  another channel's corner mark. A cover the video cannot keep costs retention in the first 30 s.
- **Same map opens the video.** The first map step after the hook's proof shows this view with the same region
  highlighted (`highlight` + `arrows` in the map step), so the click lands on what it promised.
- Shorts keep their own-imagery covers (`make_short_cover`); this template is for long videos.

## Check before upload

- At 320 px: can you name the place and read every word? If not, widen the view or cut a word.
- Does the title + cover pair pass the `yt-package` lint (no duplicated words, no truncation at 55 characters)?
- Photo covers (NASA / ISS public-domain pictures) remain allowed only when the picture itself is the story and
  says where without help; say why in the episode's PLAN.md.
