# outer-banks: plan and log

Episode 11, chosen by the user 2026-11-10 ("Outer Banks, başla") from a YouTube scan: coastal-erosion videos at 50-290x
views per subscriber (e.g. "America Built a Highway That Disappears Into the Atlantic", 288k on 263 subs; Hatteras/Rodanthe,
Dana Point, Laguna). Langtang stays episode 10. Gate 1 approved by the user 2026-11-10 ("Onaylıyorum, senaryoya geç").

Frame: on Hatteras Island the ocean keeps coming and three things stand in its way: a lighthouse (moved in 1999), a road
(NC 12, rebuilt, bridged, closed again in Oct 2026) and the houses (32 collapsed since 2020). The lighthouse got out of the
way; the road and the houses are still deciding, and federal flood insurance only pays once a house has fallen.

| # | Chapter | Sourced material (research.md) | Words |
|---|---|---|---|
| 1 | Hook: 2 June 2026, 46000 Ocean Drive, Buxton; 32 houses since 2020, 11 in two days of autumn 2025; our Landsat: the shoreline at Rodanthe ~155 m (~510 ft) inland since 1985 | NPS list; own measurement | 230 |
| 2 | Islands that walk: barrier islands roll landward through overwash and inlets; Isabel cut a 2,000 ft inlet in 2003 (Landsat before/after) | USGS/NPS (TODO V), NASA EO 12156 | 300 |
| 3 | The lighthouse that moved: 1,500 ft in 1870, 120 ft in 1970, groins and a seawall debate, the 1988 Academy report, 2,900 ft in 23 days in 1999 | NPS (V) | 320 |
| 4 | The only road: NC 12; Bonner Bridge 1963 -> Basnight 2019 ($252M); Irene 2011; Jug Handle 2022; 24 Sep and 26 Oct 2026 closures, emergency ferry | NCDOT (V), news (A) | 380 |
| 5 | Two villages on the front line: Rodanthe (12) and Buxton (20); owners Foreman and McDaniel; our measurement per site | NPS, NPR (A), own | 330 |
| 6 | The insurance trap: NFIP pays after collapse; Upton-Jones 1988-1994; the 2025 bill; the county's and FEMA's side | NPR (A) | 330 |
| 7 | Buy sand or back off: Buxton/Avon nourishment $45-65M, sand that lasted under three years, Rodanthe $40M, NPS buyouts, $1M for three houses (30 Oct) | Island Free Press, PRE (A), NPS (V) | 330 |
| 8 | Ending: the lighthouse already answered the question once; who should decide (viewer question) | | 200 |
| | **Total** | `episode_check --words 2420` -> ~18.2 min | **2,420** |

Own measurement (shoreline.json): retreat 1985 -> 2026 Rodanthe ~155 m (~510 ft), Pea Island ~100 m, Buxton ~85 m
(with a seaward jump after ~2017 that was gone within a few years), Avon ~0. Chapter 1 hook and a chart in chapter 7.

Visuals: Landsat wipes 1985 -> 2026 at Rodanthe, Buxton (old lighthouse site), Pea Island; Isabel Inlet 2002 -> 2003;
Jug Handle bridge appearing (2021 -> 2023); NC 12 route + ferry route map; stat cards; NPS public-domain collapse photos;
lighthouse move photos (NPS). No people's faces, no private photos.

Package ideas (score with yt-package): "32 Houses Fell Into the Atlantic. Insurance Paid Only After" / "The Ocean Took 500
Feet of This Island" / "They Moved a Lighthouse. Now It's the Town's Turn". Thumbnail: own Landsat 1985 | 2026 Rodanthe, 1-2 words.

Risks: crowded topic on small channels (often low-quality); our edge is own measurement + the insurance story. Quotes come
from NPR via a summary: re-read exact words before any quote card. Sea-level rate unresolved (do not use).

## Thumbnail (2026-11-10, after the Studio check: long-form CTR 1.5-3 %, few impressions)
- Chosen: A "PAID TO WAIT" on the NPS photo of the collapsed house at 23228 East Point Dr., Rodanthe, 13 Mar 2023
  (public domain). Shows what the title tells; the text is the twist (insurance pays only after collapse), not a repeat.
- Test & Compare in Studio: A vs B ("32 GONE. WHO'S NEXT?" — B repeats the title's number, so it is the weaker control).
- Rejected: the own-Landsat split (the pipeline's variant D): at 30 m the 155 m retreat is a few blurry pixels on a phone.
- Files: Videos\yt-pipeline\outer-banks\thumbnails\ (made by make_thumbs.py, Bebas Neue, 1280x720). At upload copy
  thumb_A_paid_to_wait.jpg over thumbnail_D.jpg so tools/yt_upload.py sets it.
