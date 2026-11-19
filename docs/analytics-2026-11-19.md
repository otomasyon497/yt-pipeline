# Channel analytics, 2026-11-19 (API, read-only)

Sources: YouTube Analytics API (1 Oct - 16 Nov; the API lags 2-3 days, so the uploads of 17-18 Nov are barely in it),
Reporting API reach reports (thumbnail impressions and CTR, 2-17 Nov; Shorts-feed views have no thumbnail
impressions), Data API counters. Scripts: scratchpad chan_analysis.py / reach.py. Previous report:
docs/analytics-2026-11-08.md (Studio, 11 Oct - 7 Nov).

## Channel
- 771 subscribers, 3,071 lifetime views, 29 uploads (the channel was created 2025-07-07 under an older name).
  Country US, default language en-GB.
- Subscribers in the window: +1 / -1. Viewers who are subscribed: 14 views of 3,023. The 771 subscribers are an
  older audience that does not watch these videos.

## Then and now
| | 8 Nov report (28 d) | Now (1 Oct - 16 Nov) |
|---|---|---|
| Views | 172 | 3,029 (2,749 Shorts, 309 long) |
| Watch time | 3.9 h | 17.4 h |
| Long videos: average view | 3:21 | 3:20 (21 % of the video) |
| Thumbnail impressions / CTR | 2,271 / 2.4 % | 8,250 / 2.0 % (2-17 Nov) |
| Subscribers gained | 0 | +1 (-1) |
| Main traffic | home feed (browse) | Shorts feed (2,412 views) |

## Long videos (views, average view, % watched, impressions, CTR)
| Video | Length | Views | Avg view | % | Impr. | CTR |
|---|---|---|---|---|---|---|
| Egypt Called This Dam an Existential Threat (GERD) | 15:54 | 142 | 4:02 | 25 | 1,301 | 2.9 % |
| The US Cut Arizona's Water (Colorado) | 16:09 | 44 | 1:07 | 7 | 730 | 1.5 % |
| Why Japan's $20 Billion Airport Is Sinking (Kansai) | 15:33 | 33 | 3:48 | 24 | 1,663 | 1.1 % |
| 32 Houses Fell Into the Atlantic (Outer Banks) | 15:53 | 20 | 2:10 | 14 | 449 | 1.6 % |
| Nepal's Flood Warning Came 38 Minutes Too Late | 16:08 | 16 | 4:17 | 27 | 177 | 2.8 % |
| Indonesia Is Building a 575 km Wall | 15:37 | 16 | 3:04 | 20 | 291 | 2.8 % |
| India Froze a 65 Year Old Water Treaty | 16:11 | 11 | 6:15 | 39 | 59 | 11.9 % |
| In 25 Years, Dubai Built a Manhattan | 11:14 | 7 | 3:08 | 28 | 188 | 2.7 % |
| Utah Once Pumped This Lake (Great Salt Lake) | 10:16 | 6 | 4:38 | 45 | 144 | 1.4 % |
| Kansas Rejected Farmers' Plan (Ogallala) | 15:41 | 6 | 0:56 | 6 | 301 | 0.7 % |
| Louisiana Had a Plan to Save Its Coast | 15:52 | 5 | 4:28 | 28 | 270 | 0.7 % |
| Why Almost Nobody Lives in Most of Australia | 15:41 | 5* | - | - | 186 | 1.6 % |
| Why Almost Nobody Lives in Most of Nevada | 15:29 | 19* | - | - | 82 | 1.2 % |
| Why Almost Nobody Lives in Northern Maine | 15:41 | 9* | - | - | - | - |
| Aral, USSR nukes (Caspian), NEOM, Mongolia | | 0-2 | | | 30-142 | 0 % |
\* Data API counter; Analytics has not caught up with the newest uploads.

## Shorts (top)
Indonesia Built a New Capital 1,333 views (105 % watched: rewatched); This Dam Sends a River Into a Mountain 312
(66 %); This Sea Turned Into a Desert 287 (44 %); Indonesia's Sea Wall / Row of Trees 222 (69 %); Afghanistan's
New Canal 216 (59 %); Kansas farmers 102 (98 %). Shorts average 80 % watched, 37 s. Not one subscriber came from them.

## Where viewers are
| Country | Views | Avg view |
|---|---|---|
| Turkey | 1,153 | 1:13 |
| Indonesia | 264 | 0:22 |
| India | 247 | 0:28 |
| United States | 78 | 1:24 |
| Philippines | 41 | 0:24 |
Mobile 2,574 views (0:52), desktop 200 (2:37), TV 64 (2:27), tablet 184. Viewers 25-34 male 38 %, 35-44 male 22 %,
45-54 male 18 %; women about 18 % in total.

Traffic: Shorts feed 2,412 (0:38), search 296 (0:48), browse/home 164 (2:41), suggested 92 (3:43), external 25.
Search terms that brought viewers: "indus water treaty", "lake powell", "qosh tepa canal afghanistan", "indonesia
one tower", "indonesia new capital city", "lake mead", "jakarta is sinking", "flood in nepal". A few Turkish terms
("haber global", "beşiktaş", "kuralsızlar") point to Turkish-language accounts, possibly our own testing.

## What it says
1. **The Shorts carry the reach, the long videos do not get it.** 91 % of views are Shorts; the Shorts feed sends
   no one to the long videos and no subscribers. Shorts audiences are mostly Turkey, Indonesia and India, viewing
   on phones; the long-video target (US / UK) sent 78 views in total.
2. **Turkey is the biggest market by far (38 % of views)** although the channel is set to the US and English. Most
   likely the Shorts feed seeds a new channel near the uploader's location and language signals. US/UK are tiny.
3. **CTR fell from 2.4 % to 2.0 %.** The painted-map covers of 13 Nov on are not ahead so far: Kansai 1.1 % on
   1,663 impressions, Louisiana 0.7 %, Nevada 1.2 %, Australia 1.6 %, while photo / story covers earlier reached
   2.7-2.9 % (GERD, Nepal, Indonesia, Dubai). Samples are small (under 2,000 impressions each), but this is the
   first comparison and it does not favour the map covers yet.
4. **Retention of the long videos: 20-28 % of a 15-16 min video (3-4 min) is the norm; benchmarks for this length
   are around 30-40 %.** Kansas and Arizona collapse in the first minute (6-7 %): policy-news titles that the
   opening did not deliver on. Indus (39 %, 11 views) and Nepal (27 %) hold best.
5. **Suggested traffic watches longest (3:43) and home feed second (2:41)**: when YouTube recommends us next to
   other videos, people stay. Search viewers leave fast (0:48).
6. **The old 771 subscribers are dead weight** (14 views from them); nothing to do except keep publishing for the
   new audience.

## Actions (proposed to the user)
- Run YouTube's Test & Compare on one map-cover long video (Kansai or Nevada): map cover vs a photo cover, to
  settle the cover question with data instead of guessing.
- Keep the stronger cold-open hooks (rule added 2026-11-19) and check the first-60-s retention of Netherlands.
- Shorts: end each Short with a reason to watch the long one (Related video link is set in Studio by the user);
  consider fewer Shorts if they only feed a Turkish / Indonesian audience that never watches the long videos.
- Re-read at ~26 Nov when Analytics has the Australia / Nevada / Maine / Mongolia / Mediterranean data.
